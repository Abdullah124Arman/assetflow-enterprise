from rest_framework import generics, views, status
from rest_framework.response import Response
from django.db import transaction, IntegrityError
from django.utils import timezone
from .models import Allocation, TransferRequest
from apps.assets.models import Asset
from apps.org.models import ActivityLog
from .serializers import AllocationSerializer, TransferRequestSerializer
from common.permissions import IsAssetManagerOrAdmin, IsAuthenticated

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

class AllocationCreateView(views.APIView):
    permission_classes = [IsAssetManagerOrAdmin]

    def post(self, request):
        data = request.data
        asset_id = data.get('asset_id')
        holder_type = data.get('holder_type')
        holder_id = data.get('holder_id')
        expected_return_date = data.get('expected_return_date')
        
        try:
            with transaction.atomic():
                asset = Asset.objects.select_for_update().get(id=asset_id)
                if asset.status != 'available':
                    try:
                        current = Allocation.objects.get(asset=asset, status='active')
                        # Note: We simulate current_holder block. Fetching user/dept is needed if we want name
                        return xml_error(
                            "ALREADY_ALLOCATED", 
                            "Asset is already allocated", 
                            {"current_holder": {"holder_type": current.holder_type, "holder_id": current.holder_id}}, 
                            status.HTTP_409_CONFLICT
                        )
                    except Allocation.DoesNotExist:
                        return xml_error("ALREADY_ALLOCATED", "Asset is not available", status_code=status.HTTP_409_CONFLICT)
                        
                try:
                    allocation = Allocation.objects.create(
                        asset=asset, 
                        holder_type=holder_type,
                        holder_id=holder_id,
                        expected_return_date=expected_return_date,
                    )
                except IntegrityError:
                    return xml_error("ALREADY_ALLOCATED", "Asset is already allocated (race)", status_code=status.HTTP_409_CONFLICT)
                
                asset.status = 'allocated'
                asset.save()
                
                ActivityLog.objects.create(
                    user=request.user if request.user.is_authenticated else None, 
                    action="asset.allocate", 
                    entity_type="asset",
                    entity_id=asset.id
                )
                
        except Asset.DoesNotExist:
            return xml_error("NOT_FOUND", "Asset not found", status_code=status.HTTP_404_NOT_FOUND)
            
        serializer = AllocationSerializer(allocation)
        return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)

class AllocationReturnView(views.APIView):
    permission_classes = [IsAssetManagerOrAdmin]

    def post(self, request, pk):
        data = request.data
        checkin_notes = data.get('checkin_notes', '')
        
        try:
            with transaction.atomic():
                allocation = Allocation.objects.select_for_update().get(id=pk, status='active')
                asset = Asset.objects.select_for_update().get(id=allocation.asset_id)
                
                allocation.status = 'returned'
                allocation.actual_return_date = timezone.now().date()
                allocation.checkin_notes = checkin_notes
                allocation.save()
                
                asset.status = 'available'
                asset.save()
                
                ActivityLog.objects.create(
                    user=request.user if request.user.is_authenticated else None, 
                    action="asset.return", 
                    entity_type="asset",
                    entity_id=asset.id
                )
        except Allocation.DoesNotExist:
            return xml_error("NOT_FOUND", "Active allocation not found", status_code=status.HTTP_404_NOT_FOUND)
            
        serializer = AllocationSerializer(allocation)
        return Response({'data': serializer.data})


class TransferRequestListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransferRequestSerializer

    def get_queryset(self):
        queryset = TransferRequest.objects.all()
        user = self.request.user
        
        if user and user.is_authenticated and user.role in ['dept_head', 'employee']:
            queryset = queryset.filter(asset__department_id=user.department_id)
            
        return queryset

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        # We need the user to be a valid user object or ID
        if user:
            tr = serializer.save(requested_by=user)
        else:
            tr = serializer.save()
        ActivityLog.objects.create(
            user=user, 
            action="transfer_request.create", 
            entity_type="transfer_request",
            entity_id=tr.id
        )

class TransferRequestActionView(views.APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        action = request.data.get('action') # approve | reject
        user = request.user
        
        try:
            with transaction.atomic():
                tr = TransferRequest.objects.select_for_update().get(id=pk, status='pending')
                
                # Check permissions (role-gated to asset_manager/admin or scoped dept_head)
                if user.role not in ['admin', 'asset_manager']:
                    if user.role == 'dept_head':
                        asset = Asset.objects.get(id=tr.asset_id)
                        if asset.department_id != user.department_id:
                            return xml_error("FORBIDDEN", "Not authorized for this department", status_code=status.HTTP_403_FORBIDDEN)
                    else:
                        return xml_error("FORBIDDEN", "Not authorized", status_code=status.HTTP_403_FORBIDDEN)
                
                if action == 'approve':
                    tr.status = 'approved'
                    tr.approved_by = request.user if request.user.is_authenticated else None
                    tr.resolved_at = timezone.now()
                    
                    # Re-allocate
                    asset = Asset.objects.select_for_update().get(id=tr.asset_id)
                    # Close current allocation
                    try:
                        current_alloc = Allocation.objects.get(asset=asset, status='active')
                        current_alloc.status = 'returned'
                        current_alloc.actual_return_date = timezone.now().date()
                        current_alloc.checkin_notes = "Transferred via request"
                        current_alloc.save()
                    except Allocation.DoesNotExist:
                        pass
                        
                    # Create new allocation
                    Allocation.objects.create(
                        asset=asset,
                        holder_type='employee', # simplification, might need real type
                        holder_id=tr.to_holder_id
                    )
                    asset.status = 'allocated'
                    asset.save()
                    
                elif action == 'reject':
                    tr.status = 'rejected'
                    tr.resolved_at = timezone.now()
                else:
                    return xml_error("INVALID_ACTION", "Action must be approve or reject")
                    
                tr.save()
                ActivityLog.objects.create(
                    user=request.user if request.user.is_authenticated else None, 
                    action=f"transfer_request.{action}", 
                    entity_type="transfer_request",
                    entity_id=tr.id
                )
        except TransferRequest.DoesNotExist:
            return xml_error("NOT_FOUND", "Pending transfer request not found", status_code=status.HTTP_404_NOT_FOUND)
            
        serializer = TransferRequestSerializer(tr)
        return Response({'data': serializer.data})
