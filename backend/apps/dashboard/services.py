import logging
from django.utils import timezone
from django.db import transaction
from apps.allocations.models import Allocation
from apps.bookings.models import Booking
from apps.maintenance.models import MaintenanceRequest
from apps.notifications.models import Notification
from apps.org.models import Department, ActivityLog
from apps.auth.models import User

logger = logging.getLogger(__name__)

def check_overdue_allocations():
    today = timezone.now().date()
    overdue_allocations = Allocation.objects.filter(
        status='active',
        expected_return_date__lt=today
    )
    count = 0
    with transaction.atomic():
        for alloc in overdue_allocations:
            alloc.status = 'overdue'
            alloc.save()
            count += 1
            
            # Determine who to notify
            notify_user = None
            if alloc.holder_type == 'department':
                dept = Department.objects.filter(id=alloc.holder_id).first()
                if dept and dept.head:
                    notify_user = dept.head
            else:
                notify_user = User.objects.filter(id=alloc.holder_id).first()
                
            if notify_user:
                Notification.objects.create(
                    user=notify_user,
                    type='alerts',
                    message=f"Allocation for asset {alloc.asset.tag} is overdue.",
                    entity_type='allocation',
                    entity_id=alloc.id
                )
    return count

def sync_booking_status():
    now = timezone.now()
    count_ongoing = 0
    count_completed = 0
    
    with transaction.atomic():
        # Upcoming to Ongoing
        upcoming = Booking.objects.filter(status='upcoming', start_time__lte=now)
        for booking in upcoming:
            booking.status = 'ongoing'
            booking.save(update_fields=['status'])
            count_ongoing += 1
            
            ActivityLog.objects.create(
                user=booking.booked_by,
                action="booking.ongoing",
                entity_type="booking",
                entity_id=booking.id,
                metadata={"reason": "Automatic schedule sync to ongoing"}
            )
            
            Notification.objects.create(
                user=booking.booked_by,
                type="bookings",
                message=f"Your booking for asset {booking.resource_asset.tag} has started.",
                entity_type="booking",
                entity_id=booking.id
            )
            
        # Ongoing/Upcoming to Completed
        ongoing = Booking.objects.filter(status__in=['ongoing', 'upcoming'], end_time__lte=now)
        for booking in ongoing:
            old_status = booking.status
            booking.status = 'completed'
            booking.save(update_fields=['status'])
            count_completed += 1
            
            ActivityLog.objects.create(
                user=booking.booked_by,
                action="booking.completed",
                entity_type="booking",
                entity_id=booking.id,
                metadata={"reason": "Automatic schedule sync to completed", "previous_status": old_status}
            )
            
            Notification.objects.create(
                user=booking.booked_by,
                type="bookings",
                message=f"Your booking for asset {booking.resource_asset.tag} is now completed.",
                entity_type="booking",
                entity_id=booking.id
            )
            
    return count_ongoing, count_completed

def send_booking_reminders():
    now = timezone.now()
    tomorrow = now + timezone.timedelta(hours=24)
    # Find upcoming bookings starting in the next 24 hours that haven't had a reminder sent
    bookings_needing_reminder = Booking.objects.filter(
        status='upcoming',
        start_time__gt=now,
        start_time__lte=tomorrow,
        reminder_sent=False
    )
    count = 0
    with transaction.atomic():
        for booking in bookings_needing_reminder:
            booking.reminder_sent = True
            booking.save(update_fields=['reminder_sent'])
            count += 1
            
            ActivityLog.objects.create(
                user=booking.booked_by,
                action="booking.reminder",
                entity_type="booking",
                entity_id=booking.id
            )
            
            Notification.objects.create(
                user=booking.booked_by,
                type="bookings",
                message=f"Reminder: Your booking for asset {booking.resource_asset.tag} starts at {booking.start_time}.",
                entity_type="booking",
                entity_id=booking.id
            )
    return count

def check_maintenance_sla():
    # Flag pending requests older than 24 hours
    threshold = timezone.now() - timezone.timedelta(hours=24)
    pending = MaintenanceRequest.objects.filter(status='pending', created_at__lt=threshold)
    count = 0
    with transaction.atomic():
        for req in pending:
            # Check if notification already exists to enforce idempotency
            exists = Notification.objects.filter(
                user=req.raised_by,
                type='alerts',
                entity_type='maintenance_request',
                entity_id=req.id,
                message__contains="longer than expected"
            ).exists()
            
            if not exists:
                Notification.objects.create(
                    user=req.raised_by,
                    type='alerts',
                    message=f"Maintenance request for asset {req.asset.tag} is taking longer than expected.",
                    entity_type='maintenance_request',
                    entity_id=req.id
                )
                count += 1
    return count
