from rest_framework import serializers
from .models import Department, ActivityLog
from apps.auth.models import User

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'head_id', 'parent_dept_id', 'status', 'created_at', 'updated_at']

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'department_id', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'name', 'email', 'department_id', 'status', 'created_at', 'updated_at']

class EmployeeRolePatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['role']
