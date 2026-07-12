from rest_framework import views, status
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from .models import Booking
from .serializers import BookingSerializer, BookingRequestSerializer
from apps.org.models import ActivityLog
from common.permissions import IsAuthenticated

class BookingListView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        resource_id = request.query_params.get('resource_id')
        date_param = request.query_params.get('date')
        
        queryset = Booking.objects.all()
        
        # Scope by department for dept_head and employee roles
        if request.user.role in ['dept_head', 'employee']:
            if request.user.department_id:
                queryset = queryset.filter(resource_asset__department_id=request.user.department_id)
            else:
                queryset = queryset.none()
                
        if resource_id:
            queryset = queryset.filter(resource_asset_id=resource_id)
        if date_param:
            queryset = queryset.filter(start_time__date=date_param)
            
        now = timezone.now()
        for booking in queryset:
            if booking.status == 'upcoming' and booking.start_time <= now < booking.end_time:
                booking.status = 'ongoing'
                booking.save(update_fields=['status'])
            elif booking.status in ['upcoming', 'ongoing'] and booking.end_time <= now:
                booking.status = 'completed'
                booking.save(update_fields=['status'])
                
        serializer = BookingSerializer(queryset, many=True)
        return Response({"data": serializer.data})

    def post(self, request):
        serializer = BookingRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            booking = Booking.objects.create(
                resource_asset_id=serializer.validated_data['resource_asset_id'],
                booked_by=request.user,
                start_time=serializer.validated_data['start_time'],
                end_time=serializer.validated_data['end_time'],
                purpose=serializer.validated_data.get('purpose'),
            )
            ActivityLog.objects.create(
                user=request.user, 
                action="booking.create", 
                entity_type="booking",
                entity_id=booking.id
            )
            
            # Reminder logic computed on dashboard load or via scheduler command
            
        return Response({"data": BookingSerializer(booking).data}, status=status.HTTP_201_CREATED)

class BookingDetailView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({'error': {'code': 'NOT_FOUND', 'message': 'Booking not found', 'details': {}}}, status=status.HTTP_404_NOT_FOUND)
            
        # Ownership and role validation
        if request.user.role not in ['admin', 'asset_manager'] and booking.booked_by_id != request.user.id:
            return Response({'error': {'code': 'FORBIDDEN', 'message': 'You do not have permission to modify this booking', 'details': {}}}, status=status.HTTP_403_FORBIDDEN)
            
        start = request.data.get('start_time')
        end = request.data.get('end_time')
        purpose = request.data.get('purpose')
        status_val = request.data.get('status')
        
        with transaction.atomic():
            if start or end or (purpose is not None):
                new_start = start or booking.start_time
                new_end = end or booking.end_time
                
                req_ser = BookingRequestSerializer(data={
                    "resource_asset_id": booking.resource_asset_id,
                    "start_time": new_start,
                    "end_time": new_end,
                    "purpose": purpose if purpose is not None else booking.purpose
                })
                req_ser.is_valid(raise_exception=True)
                
                booking.start_time = req_ser.validated_data['start_time']
                booking.end_time = req_ser.validated_data['end_time']
                if purpose is not None:
                    booking.purpose = req_ser.validated_data.get('purpose')

            if status_val:
                booking.status = status_val
                
            booking.save()
            
            action_name = "booking.cancel" if status_val == "cancelled" else "booking.update"
            ActivityLog.objects.create(
                user=request.user, 
                action=action_name,
                entity_type="booking",
                entity_id=booking.id
            )
            
        return Response({"data": BookingSerializer(booking).data})
