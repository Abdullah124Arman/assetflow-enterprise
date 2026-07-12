from django.db import models
import uuid

class AssetCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(unique=True)
    custom_fields = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'asset_categories'

    def __str__(self):
        return self.name


class Asset(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('allocated', 'Allocated'),
        ('reserved', 'Reserved'),
        ('under_maintenance', 'Under Maintenance'),
        ('lost', 'Lost'),
        ('retired', 'Retired'),
        ('disposed', 'Disposed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag = models.TextField(unique=True)
    name = models.TextField()
    category = models.ForeignKey(
        AssetCategory, 
        on_delete=models.RESTRICT, 
        db_column='category_id',
        related_name='assets'
    )
    serial_number = models.TextField(null=True, blank=True)
    qr_code = models.TextField(unique=True, null=True, blank=True)
    acquisition_date = models.DateField(null=True, blank=True)
    acquisition_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    condition = models.TextField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    is_bookable = models.BooleanField(default=False)
    department = models.ForeignKey(
        'org.Department',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column='department_id',
        related_name='assets'
    )
    custom_field_values = models.JSONField(default=dict)
    photo_url = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assets'

    def __str__(self):
        return f"{self.tag} - {self.name}"
