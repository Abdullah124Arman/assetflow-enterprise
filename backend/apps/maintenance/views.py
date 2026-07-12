from rest_framework import generics, views, status
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from .models import MaintenanceRequest
from apps.assets.models import Asset
from apps.org.models import ActivityLog
from apps.notifications.models import Notification
from .serializers import MaintenanceRequestSerializer
from common.permissions import IsAuthenticated, IsAssetManagerOrAdmin

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

class MaintenanceRequestListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MaintenanceRequestSerializer

    def get_queryset(self):
        queryset = MaintenanceRequest.objects.all()
        user = self.request.user
        
        # Scope by department for dept_head and employee
        if user and user.is_authenticated and user.role in ['dept_head', 'employee']:
            queryset = queryset.filter(asset__department_id=user.department_id)
            
        asset_id = self.request.query_params.get('asset_id')
        if asset_id:
            queryset = queryset.filter(asset_id=asset_id)
            
        req_status = self.request.query_params.get('status')
        if req_status:
            queryset = queryset.filter(status=req_status)
            
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        asset_id = data.get('asset_id')
        user = request.user
        
        try:
            asset = Asset.objects.get(id=asset_id)
        except Asset.DoesNotExist:
            return xml_error("NOT_FOUND", "Asset not found", status_code=status.HTTP_404_NOT_FOUND)
            
        if user.role in ['dept_head', 'employee'] and asset.department_id != user.department_id:
            return xml_error("FORBIDDEN", "Not authorized for this department", status_code=status.HTTP_403_FORBIDDEN)
            
        # create the request
        mr = MaintenanceRequest.objects.create(
            asset=asset,
            raised_by=user,
            issue=data.get('issue', ''),
            priority=data.get('priority', 'medium'),
            # status='pending' (default)
        )
        
        ActivityLog.objects.create(
            user=user,
            action="maintenance.create",
            entity_type="maintenance_request",
            entity_id=mr.id
        )
        
        serializer = self.get_serializer(mr)
        return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)

class MaintenanceRequestActionView(views.APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        action = request.data.get('action')
        user = request.user
        
        try:
            with transaction.atomic():
                mr = MaintenanceRequest.objects.select_for_update().get(id=pk)
                asset = Asset.objects.select_for_update().get(id=mr.asset_id)
                
                # Scope by department for dept_head and employee
                if user.role in ['dept_head', 'employee'] and asset.department_id != user.department_id:
                    return xml_error("FORBIDDEN", "Not authorized for this department", status_code=status.HTTP_403_FORBIDDEN)
                    
                if action in ['approve', 'reject']:
                    if user.role not in ['admin', 'asset_manager']:
                        return xml_error("FORBIDDEN", "Only asset manager or admin can approve/reject", status_code=status.HTTP_403_FORBIDDEN)
                        
                    if action == 'approve':
                        if mr.status != 'pending':
                            return xml_error("INVALID_STATE", "Only pending requests can be approved")
                        mr.status = 'approved'
                        mr.approved_by = user
                        asset.status = 'under_maintenance'
                        asset.save()
                    elif action == 'reject':
                        if mr.status != 'pending':
                            return xml_error("INVALID_STATE", "Only pending requests can be rejected")
                        mr.status = 'rejected'
                        
                elif action == 'assign':
                    if mr.status != 'approved':
                        return xml_error("INVALID_STATE", "Only approved requests can be assigned")
                    mr.status = 'technician_assigned'
                    mr.technician_name = request.data.get('technician_name')
                    
                elif action == 'resolve':
                    if mr.status not in ['technician_assigned', 'in_progress', 'approved']:
                        return xml_error("INVALID_STATE", "Request cannot be resolved from this state")
                    mr.status = 'resolved'
                    mr.resolved_at = timezone.now()
                    asset.status = 'available'
                    asset.save()
                    
                else:
                    return xml_error("INVALID_ACTION", "Action must be approve, reject, assign, or resolve")
                    
                mr.save()
                
                ActivityLog.objects.create(
                    user=user,
                    action=f"maintenance.{action}",
                    entity_type="maintenance_request",
                    entity_id=mr.id
                )
                Notification.objects.create(
                    user=mr.raised_by,
                    type=f"maintenance_{action}",
                    message=f"Your maintenance request has been {action}d.",
                    entity_type="maintenance_request",
                    entity_id=mr.id
                )
                
        except MaintenanceRequest.DoesNotExist:
            return xml_error("NOT_FOUND", "Maintenance request not found", status_code=status.HTTP_404_NOT_FOUND)
            
        serializer = MaintenanceRequestSerializer(mr)
        return Response({'data': serializer.data})
