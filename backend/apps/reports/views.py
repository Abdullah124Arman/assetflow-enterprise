from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Q
from apps.assets.models import Asset, AssetCategory
from apps.allocations.models import Allocation
from apps.bookings.models import Booking
from apps.maintenance.models import MaintenanceRequest
from apps.org.models import Department
from common.permissions import IsAuthenticated
import datetime

class UtilizationReportView(APIView):
    permission_classes = [IsAuthenticated]
    schema_name = 'report_utilization'

    def get(self, request):
        user = request.user
        role = user.role
        
        categories = AssetCategory.objects.all()
        report_data = []
        for cat in categories:
            assets_q = Asset.objects.filter(category=cat)
            
            if role in ['dept_head', 'employee']:
                dept_id = getattr(user, 'department_id', None)
                if dept_id:
                    assets_q = assets_q.filter(department_id=dept_id)
                else:
                    assets_q = assets_q.none()
                    
            total = assets_q.count()
            if total == 0:
                continue
            allocated = assets_q.filter(status='allocated').count()
            utilization = round((allocated / total) * 100, 2)
            report_data.append({
                'name': cat.name,
                'total_assets': total,
                'allocated_assets': allocated,
                'utilization_percentage': str(utilization)
            })
            
        return Response({
            'data': {
                'categories': {
                    'category': report_data
                }
            }
        })

class MaintenanceFrequencyReportView(APIView):
    permission_classes = [IsAuthenticated]
    schema_name = 'report_maintenance_frequency'

    def get(self, request):
        user = request.user
        role = user.role
        one_year_ago = timezone.now() - datetime.timedelta(days=365)
        
        assets_q = Asset.objects.all()
        if role in ['dept_head', 'employee']:
            dept_id = getattr(user, 'department_id', None)
            if dept_id:
                assets_q = assets_q.filter(department_id=dept_id)
            else:
                assets_q = assets_q.none()
                
        assets = assets_q.annotate(
            maintenance_count=Count('maintenance_requests', filter=Q(maintenance_requests__created_at__gte=one_year_ago))
        ).filter(maintenance_count__gt=0).order_by('-maintenance_count')[:50]
        
        report_data = []
        for asset in assets:
            report_data.append({
                'tag': asset.tag,
                'name': asset.name,
                'maintenance_count': asset.maintenance_count
            })
            
        return Response({
            'data': {
                'assets': {
                    'asset': report_data
                }
            }
        })

class IdleAssetsReportView(APIView):
    permission_classes = [IsAuthenticated]
    schema_name = 'report_idle_assets'

    def get(self, request):
        user = request.user
        role = user.role
        
        assets_q = Asset.objects.filter(status='available')
        if role in ['dept_head', 'employee']:
            dept_id = getattr(user, 'department_id', None)
            if dept_id:
                assets_q = assets_q.filter(department_id=dept_id)
            else:
                assets_q = assets_q.none()
                
        assets = assets_q[:50]
        
        report_data = []
        for asset in assets:
            last_alloc = asset.allocations.order_by('-actual_return_date').first()
            if last_alloc and last_alloc.actual_return_date:
                days_idle = (timezone.now().date() - last_alloc.actual_return_date).days
            elif asset.acquisition_date:
                days_idle = (timezone.now().date() - asset.acquisition_date).days
            else:
                days_idle = 0
                
            report_data.append({
                'tag': asset.tag,
                'name': asset.name,
                'days_idle': days_idle
            })
            
        report_data.sort(key=lambda x: x['days_idle'], reverse=True)
            
        return Response({
            'data': {
                'assets': {
                    'asset': report_data
                }
            }
        })

class RetirementWatchReportView(APIView):
    permission_classes = [IsAuthenticated]
    schema_name = 'report_retirement_watch'

    def get(self, request):
        user = request.user
        role = user.role
        three_years_ago = timezone.now().date() - datetime.timedelta(days=3*365)
        
        assets_q = Asset.objects.filter(acquisition_date__lt=three_years_ago).exclude(status__in=['retired', 'disposed'])
        if role in ['dept_head', 'employee']:
            dept_id = getattr(user, 'department_id', None)
            if dept_id:
                assets_q = assets_q.filter(department_id=dept_id)
            else:
                assets_q = assets_q.none()
                
        assets = assets_q[:50]
        
        report_data = []
        for asset in assets:
            age_years = round((timezone.now().date() - asset.acquisition_date).days / 365, 1) if asset.acquisition_date else 0
            report_data.append({
                'tag': asset.tag,
                'name': asset.name,
                'acquisition_date': str(asset.acquisition_date),
                'age_years': str(age_years)
            })
            
        return Response({
            'data': {
                'assets': {
                    'asset': report_data
                }
            }
        })

class AllocationSummaryReportView(APIView):
    permission_classes = [IsAuthenticated]
    schema_name = 'report_allocation_summary'

    def get(self, request):
        user = request.user
        role = user.role
        
        depts_q = Department.objects.all()
        if role in ['dept_head', 'employee']:
            dept_id = getattr(user, 'department_id', None)
            if dept_id:
                depts_q = depts_q.filter(id=dept_id)
            else:
                depts_q = depts_q.none()
                
        report_data = []
        for dept in depts_q:
            total_allocations = Allocation.objects.filter(asset__department=dept, status='active').count()
            report_data.append({
                'name': dept.name,
                'total_allocations': total_allocations
            })
            
        return Response({
            'data': {
                'departments': {
                    'department': report_data
                }
            }
        })

class BookingHeatmapReportView(APIView):
    permission_classes = [IsAuthenticated]
    schema_name = 'report_booking_heatmap'

    def get(self, request):
        user = request.user
        role = user.role
        today = timezone.now().date()
        report_data = []
        
        for i in range(7):
            day = today - datetime.timedelta(days=i)
            bookings_q = Booking.objects.all()
            if role in ['dept_head', 'employee']:
                dept_id = getattr(user, 'department_id', None)
                if dept_id:
                    bookings_q = bookings_q.filter(resource_asset__department_id=dept_id)
                else:
                    bookings_q = bookings_q.none()
                    
            count = bookings_q.filter(start_time__date__lte=day, end_time__date__gte=day).count()
            report_data.append({
                'date': str(day),
                'booking_count': count
            })
            
        return Response({
            'data': {
                'days': {
                    'day': report_data
                }
            }
        })
