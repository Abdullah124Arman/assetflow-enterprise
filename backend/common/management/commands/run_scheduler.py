from django.core.management.base import BaseCommand
from apps.dashboard.services import check_overdue_allocations, sync_booking_status, check_maintenance_sla, send_booking_reminders

class Command(BaseCommand):
    help = 'Runs the AssetFlow scheduler tasks to update statuses and trigger notifications.'

    def handle(self, *args, **options):
        self.stdout.write('Running AssetFlow Scheduler...')
        
        try:
            # Check overdue allocations
            overdue_count = check_overdue_allocations()
            self.stdout.write(self.style.SUCCESS(f'Marked {overdue_count} allocations as overdue.'))
            
            # Sync booking statuses
            ongoing, completed = sync_booking_status()
            self.stdout.write(self.style.SUCCESS(f'Synced {ongoing} bookings to ongoing, {completed} to completed.'))
            
            # Send booking reminders
            reminder_count = send_booking_reminders()
            self.stdout.write(self.style.SUCCESS(f'Sent {reminder_count} booking reminders.'))
            
            # Check maintenance SLA
            sla_count = check_maintenance_sla()
            self.stdout.write(self.style.SUCCESS(f'Flagged {sla_count} pending maintenance requests past SLA.'))
            
            self.stdout.write(self.style.SUCCESS('Scheduler completed successfully.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Scheduler failed with error: {e}'))
