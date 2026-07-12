from django.db import models
import uuid

class Department(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    head = models.ForeignKey(
        'assetflow_auth.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='headed_departments',
        db_column='head_id'
    )
    parent_dept = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='sub_departments',
        db_column='parent_dept_id'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'departments'

    def __str__(self):
        return self.name


class ActivityLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'assetflow_auth.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='activity_logs',
        db_column='user_id'
    )
    action = models.TextField()
    entity_type = models.TextField()
    entity_id = models.UUIDField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'activity_logs'
