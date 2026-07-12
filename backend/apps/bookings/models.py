from django.db import models
import uuid

class Booking(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resource_asset = models.ForeignKey(
        'assets.Asset', 
        on_delete=models.RESTRICT,
        db_column='resource_asset_id',
        related_name='bookings'
    )
    booked_by = models.ForeignKey(
        'assetflow_auth.User', 
        on_delete=models.RESTRICT,
        db_column='booked_by',
        related_name='bookings'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    purpose = models.TextField(null=True, blank=True)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bookings'
        
        # Constraints are managed by bootstrap_schema.sql, but we can define standard ones here for django's benefit
        # Constraint valid_range CHECK (end_time > start_time)
        # Exclusion constraint no_overlap is managed in the database

    def __str__(self):
        return f"{self.resource_asset.tag} - {self.start_time} to {self.end_time}"
