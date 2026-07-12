from django.db import models
import uuid

class Allocation(models.Model):
    HOLDER_TYPE_CHOICES = [
        ('employee', 'Employee'),
        ('department', 'Department'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.RESTRICT,
        db_column='asset_id',
        related_name='allocations'
    )
    holder_type = models.CharField(max_length=15, choices=HOLDER_TYPE_CHOICES)
    holder_id = models.UUIDField()
    allocated_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField(null=True, blank=True)
    actual_return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    checkin_notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'allocations'


class TransferRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.RESTRICT,
        db_column='asset_id',
        related_name='transfer_requests'
    )
    from_holder_id = models.UUIDField()
    to_holder_id = models.UUIDField()
    requested_by = models.ForeignKey(
        'assetflow_auth.User',
        on_delete=models.RESTRICT,
        db_column='requested_by',
        related_name='transfer_requests_made'
    )
    reason = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(
        'assetflow_auth.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column='approved_by',
        related_name='transfer_requests_approved'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'transfer_requests'
