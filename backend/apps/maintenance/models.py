from django.db import models
import uuid

class MaintenanceRequest(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('technician_assigned', 'Technician Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.RESTRICT,
        db_column='asset_id',
        related_name='maintenance_requests'
    )
    raised_by = models.ForeignKey(
        'assetflow_auth.User',
        on_delete=models.RESTRICT,
        db_column='raised_by',
        related_name='maintenance_requests_raised'
    )
    issue = models.TextField()
    priority = models.CharField(max_length=15, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(
        'assetflow_auth.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column='approved_by',
        related_name='maintenance_requests_approved'
    )
    technician_name = models.TextField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'maintenance_requests'
