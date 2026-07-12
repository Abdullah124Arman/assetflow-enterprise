from rest_framework import serializers
from .models import AuditCycle, AuditAuditor, AuditItem, AuditDiscrepancyReport

class AuditCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditCycle
        fields = '__all__'

class AuditItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditItem
        fields = '__all__'

class AuditDiscrepancyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditDiscrepancyReport
        fields = '__all__'
