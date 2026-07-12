from rest_framework import generics, views, status
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from .models import AuditCycle, AuditAuditor, AuditItem, AuditDiscrepancyReport, AuditCycleStatus
from apps.assets.models import Asset
from apps.auth.models import User
from apps.org.models import ActivityLog
from apps.notifications.models import Notification
from .serializers import AuditCycleSerializer, AuditItemSerializer, AuditDiscrepancyReportSerializer
from common.permissions import IsAuthenticated, IsAdminOrAssetManagerOrReadOnly
from .permissions import IsAssignedAuditor
import lxml.etree as etree

def xml_error(code, message, details=None, status_code=status.HTTP_400_BAD_REQUEST):
    if details is None:
        details = {}
    return Response({
        'error': {
            'code': code,
            'message': message,
            'details': details
        }
    }, status=status_code)

class AuditCycleCreateView(views.APIView):
    permission_classes = [IsAdminOrAssetManagerOrReadOnly]

    def get(self, request):
        cycles = AuditCycle.objects.all().order_by('-start_date')
        
        # We need to build XML response manually or use DRF serializer
        # Since this API uses XML, we'll return serializer data which our custom renderer handles
        serializer = AuditCycleSerializer(cycles, many=True)
        # We need to fetch items for active cycles to render on frontend
        data = serializer.data
        for cycle_data in data:
            items = AuditItem.objects.filter(audit_cycle_id=cycle_data['id']).select_related('asset')
            cycle_data['items'] = AuditItemSerializer(items, many=True).data
            
        return Response({'data': data})

    def post(self, request):
        data = request.data
        
        name = data.get('name')
        scope_department_id = data.get('scope_department_id')
        scope_location = data.get('scope_location')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if not name or not start_date or not end_date:
            return xml_error("VALIDATION_ERROR", "Missing required fields")

        with transaction.atomic():
            user = request.user if request.user.is_authenticated else None
            if user is None:
                return xml_error("UNAUTHORIZED", "Not authenticated", status_code=status.HTTP_401_UNAUTHORIZED)
            
            cycle = AuditCycle.objects.create(
                name=name,
                scope_department_id=scope_department_id,
                scope_location=scope_location,
                start_date=start_date,
                end_date=end_date,
                created_by=user
            )

            assets_qs = Asset.objects.all()
            if scope_department_id:
                assets_qs = assets_qs.filter(department_id=scope_department_id)
            if scope_location:
                assets_qs = assets_qs.filter(location=scope_location)

            audit_items = []
            for asset in assets_qs:
                audit_items.append(
                    AuditItem(
                        audit_cycle=cycle,
                        asset=asset,
                        verification='pending'
                    )
                )
            AuditItem.objects.bulk_create(audit_items)

            ActivityLog.objects.create(
                user=user,
                action="audit_cycle.create",
                entity_type="audit_cycle",
                entity_id=cycle.id
            )

        serializer = AuditCycleSerializer(cycle)
        return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)

class AuditCycleAuditorsView(views.APIView):
    permission_classes = [IsAdminOrAssetManagerOrReadOnly]

    def post(self, request, pk):
        try:
            cycle = AuditCycle.objects.get(id=pk)
        except AuditCycle.DoesNotExist:
            return xml_error("NOT_FOUND", "Audit cycle not found", status_code=status.HTTP_404_NOT_FOUND)

        if cycle.status == AuditCycleStatus.CLOSED:
            return xml_error("CONFLICT", "Cannot modify a closed audit cycle", status_code=status.HTTP_409_CONFLICT)

        user_ids = request.data.get('user_ids', [])
        if isinstance(user_ids, dict) and 'user_id' in user_ids:
            user_ids = user_ids['user_id']
            if not isinstance(user_ids, list):
                user_ids = [user_ids]

        with transaction.atomic():
            for uid in user_ids:
                try:
                    user = User.objects.get(id=uid)
                    AuditAuditor.objects.get_or_create(audit_cycle=cycle, user=user)
                    Notification.objects.create(
                        user=user,
                        type="audit_assigned",
                        message=f"You have been assigned to audit cycle {cycle.name}",
                        entity_type="audit_cycle",
                        entity_id=cycle.id
                    )
                except User.DoesNotExist:
                    pass

            ActivityLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action="audit_cycle.assign_auditors",
                entity_type="audit_cycle",
                entity_id=cycle.id
            )

        serializer = AuditCycleSerializer(cycle)
        # Manually embed auditors list for response based on standard
        data = serializer.data
        data['auditors'] = {'user_id': list(cycle.auditors.values_list('id', flat=True))}
        return Response({'data': data})

class AuditItemUpdateView(views.APIView):
    permission_classes = [IsAuthenticated, IsAssignedAuditor]

    def patch(self, request, pk):
        try:
            item = AuditItem.objects.select_related('audit_cycle').get(id=pk)
        except AuditItem.DoesNotExist:
            return xml_error("NOT_FOUND", "Audit item not found", status_code=status.HTTP_404_NOT_FOUND)

        # DRF permission check explicitly for object
        self.check_object_permissions(request, item)

        if item.audit_cycle.status == AuditCycleStatus.CLOSED:
            return xml_error("CONFLICT", "Cannot update items of a closed audit cycle", status_code=status.HTTP_409_CONFLICT)

        verification = request.data.get('verification')
        notes = request.data.get('notes', item.notes)

        if verification not in ['pending', 'verified', 'missing', 'damaged']:
            return xml_error("VALIDATION_ERROR", "Invalid verification status")

        item.verification = verification
        item.notes = notes
        item.verified_by = request.user
        item.verified_at = timezone.now()
        item.save()

        ActivityLog.objects.create(
            user=request.user,
            action="audit_item.update",
            entity_type="audit_item",
            entity_id=item.id
        )

        serializer = AuditItemSerializer(item)
        return Response({'data': serializer.data})

class AuditCycleCloseView(views.APIView):
    permission_classes = [IsAdminOrAssetManagerOrReadOnly]

    def post(self, request, pk):
        try:
            with transaction.atomic():
                cycle = AuditCycle.objects.select_for_update().get(id=pk, status=AuditCycleStatus.OPEN)
                
                missing_items = AuditItem.objects.filter(audit_cycle=cycle, verification='missing').select_related('asset')
                missing_asset_ids = missing_items.values_list('asset_id', flat=True)
                
                Asset.objects.filter(id__in=missing_asset_ids).update(status='lost')
                
                damaged_items = AuditItem.objects.filter(audit_cycle=cycle, verification='damaged').select_related('asset')

                # Build XML report via lxml
                root = etree.Element("discrepancy_report")
                etree.SubElement(root, "audit_cycle_id").text = str(cycle.id)
                generated_at = timezone.now()
                etree.SubElement(root, "generated_at").text = generated_at.isoformat()
                
                missing_node = etree.SubElement(root, "missing_items")
                for m_item in missing_items:
                    asset_node = etree.SubElement(missing_node, "asset")
                    etree.SubElement(asset_node, "id").text = str(m_item.asset.id)
                    etree.SubElement(asset_node, "tag").text = m_item.asset.tag
                    etree.SubElement(asset_node, "name").text = m_item.asset.name
                    if m_item.notes:
                        etree.SubElement(asset_node, "notes").text = m_item.notes

                damaged_node = etree.SubElement(root, "damaged_items")
                for d_item in damaged_items:
                    asset_node = etree.SubElement(damaged_node, "asset")
                    etree.SubElement(asset_node, "id").text = str(d_item.asset.id)
                    etree.SubElement(asset_node, "tag").text = d_item.asset.tag
                    etree.SubElement(asset_node, "name").text = d_item.asset.name
                    if d_item.notes:
                        etree.SubElement(asset_node, "notes").text = d_item.notes

                report_xml_str = etree.tostring(root, encoding='utf-8').decode('utf-8')
                
                report = AuditDiscrepancyReport.objects.create(
                    audit_cycle=cycle,
                    generated_at=generated_at,
                    report_json=report_xml_str
                )
                
                cycle.status = AuditCycleStatus.CLOSED
                cycle.closed_at = generated_at
                cycle.save()
                
                ActivityLog.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    action="audit_cycle.close",
                    entity_type="audit_cycle",
                    entity_id=cycle.id
                )
                
                if missing_items.exists() or damaged_items.exists():
                    Notification.objects.create(
                        user=cycle.created_by,
                        type="audit_discrepancy",
                        message=f"Audit cycle {cycle.name} closed with discrepancies.",
                        entity_type="audit_cycle",
                        entity_id=cycle.id
                    )
                
        except AuditCycle.DoesNotExist:
            return xml_error("NOT_FOUND", "Open audit cycle not found", status_code=status.HTTP_404_NOT_FOUND)

        serializer = AuditDiscrepancyReportSerializer(report)
        return Response({'data': serializer.data})
