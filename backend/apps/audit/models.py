import uuid
from django.db import models
from django.utils import timezone
from apps.org.models import Department
from apps.auth.models import User
from apps.assets.models import Asset

class AuditCycleStatus(models.TextChoices):
    OPEN = 'open', 'Open'
    CLOSED = 'closed', 'Closed'

class AuditVerification(models.TextChoices):
    PENDING = 'pending', 'Pending'
    VERIFIED = 'verified', 'Verified'
    MISSING = 'missing', 'Missing'
    DAMAGED = 'damaged', 'Damaged'

class AuditCycle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    scope_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_cycles')
    scope_location = models.TextField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=AuditCycleStatus.choices, default=AuditCycleStatus.OPEN)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_audit_cycles', db_column='created_by')
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    auditors = models.ManyToManyField(User, through='AuditAuditor', related_name='assigned_audit_cycles')

    class Meta:
        db_table = 'audit_cycles'

class AuditAuditor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    audit_cycle = models.ForeignKey(AuditCycle, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'audit_auditors'
        unique_together = (('audit_cycle', 'user'),)

class AuditItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    audit_cycle = models.ForeignKey(AuditCycle, on_delete=models.CASCADE, related_name='items')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='audit_items')
    verification = models.CharField(max_length=20, choices=AuditVerification.choices, default=AuditVerification.PENDING)
    notes = models.TextField(null=True, blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_audit_items', db_column='verified_by')
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'audit_items'
        unique_together = (('audit_cycle', 'asset'),)

class AuditDiscrepancyReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    audit_cycle = models.ForeignKey(AuditCycle, on_delete=models.CASCADE, related_name='discrepancy_reports')
    generated_at = models.DateTimeField(default=timezone.now)
    report_json = models.TextField() # Storing XML as raw text here based on TRD

    class Meta:
        db_table = 'audit_discrepancy_reports'
