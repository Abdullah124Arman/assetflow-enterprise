from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from apps.dashboard.services import check_overdue_allocations, sync_booking_status, check_maintenance_sla, send_booking_reminders
from apps.assets.models import Asset
from apps.allocations.models import Allocation, TransferRequest
from apps.bookings.models import Booking
from apps.maintenance.models import MaintenanceRequest
from apps.org.models import ActivityLog
from common.permissions import IsAuthenticated

class KPIView(APIView):
    permission_classes = [IsAuthenticated]
    schema_name = 'kpi_summary'
    
    def get(self, request):
        # Trigger inline syncs
        check_overdue_allocations()
        sync_booking_status()
        send_booking_reminders()
        check_maintenance_sla()
        
        user = request.user
        role = user.role
        
        # Base querysets
        assets_q = Asset.objects.all()
        allocs_q = Allocation.objects.filter(status='active')
        bookings_q = Booking.objects.filter(status='ongoing')
        transfers_q = TransferRequest.objects.filter(status='pending')
        upcoming_returns_q = Allocation.objects.filter(status='active', expected_return_date__gte=timezone.now().date())
        maintenance_q = MaintenanceRequest.objects.filter(created_at__date=timezone.now().date())
        overdue_q = Allocation.objects.filter(status='overdue')
        activity_q = ActivityLog.objects.all().order_by('-created_at')[:10]
        
        # Scoping rules: "dept_head or employee roles MUST scope by department_id. No exceptions."
        if role in ['dept_head', 'employee']:
            dept_id = getattr(user, 'department_id', None)
            if not dept_id:
                # Fallback to department where head is user
                from apps.org.models import Department
                dept = Department.objects.filter(head=user).first()
                if dept:
                    dept_id = dept.id
            
            if dept_id:
                assets_q = assets_q.filter(department_id=dept_id)
                allocs_q = allocs_q.filter(asset__department_id=dept_id)
                bookings_q = bookings_q.filter(resource_asset__department_id=dept_id)
                transfers_q = transfers_q.filter(asset__department_id=dept_id)
                upcoming_returns_q = upcoming_returns_q.filter(asset__department_id=dept_id)
                maintenance_q = maintenance_q.filter(asset__department_id=dept_id)
                overdue_q = overdue_q.filter(asset__department_id=dept_id)
            else:
                assets_q = assets_q.none()
                allocs_q = allocs_q.none()
                bookings_q = bookings_q.none()
                transfers_q = transfers_q.none()
                upcoming_returns_q = upcoming_returns_q.none()
                maintenance_q = maintenance_q.none()
                overdue_q = overdue_q.none()
        
        # Calculate KPIs
        kpis = {
            'available_assets': assets_q.filter(status='available').count(),
            'allocated_assets': assets_q.filter(status='allocated').count(),
            'active_bookings': bookings_q.count(),
            'pending_transfers': transfers_q.count(),
            'upcoming_returns': upcoming_returns_q.count(),
            'maintenance_today': maintenance_q.count()
        }
        
        # Overdue returns list
        overdue_returns = []
        for alloc in overdue_q:
            days_overdue = (timezone.now().date() - alloc.expected_return_date).days if alloc.expected_return_date else 0
            overdue_returns.append({
                'id': str(alloc.id),
                'asset_tag': alloc.asset.tag,
                'asset_name': alloc.asset.name,
                'holder_id': str(alloc.holder_id),
                'expected_return_date': str(alloc.expected_return_date),
                'days_overdue': days_overdue
            })
            
        # Recent activity
        recent_activity = []
        for act in activity_q:
            recent_activity.append({
                'id': str(act.id),
                'action': act.action,
                'entity_type': act.entity_type,
                'entity_id': str(act.entity_id) if act.entity_id else '',
                'created_at': act.created_at.isoformat()
            })
            
        # Ensure tags exist in response payload to comply with XSD sequence constraint
        return Response({
            'data': {
                'kpis': kpis,
                'overdue_returns': {
                    'allocation': overdue_returns
                },
                'recent_activity': {
                    'activity': recent_activity
                }
            }
        })
