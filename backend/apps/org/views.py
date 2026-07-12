from rest_framework import generics
from rest_framework.response import Response
from .models import Department, ActivityLog
from apps.auth.models import User, RefreshTokenModel
from .serializers import DepartmentSerializer, EmployeeSerializer, EmployeeRolePatchSerializer
from common.permissions import IsAdmin, IsAdminOrReadOnly
from rest_framework.permissions import IsAuthenticated

def log_activity(user, action, entity_type, entity_id=None, metadata=None):
    ActivityLog.objects.create(
        user=user,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata=metadata or {}
    )

def scope_queryset(queryset, request):
    user = request.user
    if user.role in ['dept_head', 'employee'] and user.department_id:
        if hasattr(queryset.model, 'department_id'):
            return queryset.filter(department_id=user.department_id)
        elif hasattr(queryset.model, 'head_id'): # For Department model filtering by itself
            return queryset.filter(id=user.department_id)
    return queryset

class DepartmentListCreateView(generics.ListCreateAPIView):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return scope_queryset(Department.objects.all(), self.request)

    def perform_create(self, serializer):
        dept = serializer.save()
        log_activity(self.request.user, "department.create", "department", dept.id)

class DepartmentDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return scope_queryset(Department.objects.all(), self.request)

    def perform_update(self, serializer):
        dept = serializer.save()
        log_activity(self.request.user, "department.update", "department", dept.id)

class EmployeeListView(generics.ListAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return scope_queryset(User.objects.all(), self.request)

class EmployeeRolePatchView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = EmployeeRolePatchSerializer
    permission_classes = [IsAdmin]

    def perform_update(self, serializer):
        user = serializer.save()
        log_activity(self.request.user, "employee.role_update", "user", user.id, {"new_role": user.role})
        # Role promotion invalidates existing refresh tokens
        RefreshTokenModel.objects.filter(user=user).delete()
