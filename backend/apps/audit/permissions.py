from rest_framework import permissions
from .models import AuditCycle

class IsAssignedAuditor(permissions.BasePermission):
    """
    Permission check that ensures the request.user is an assigned auditor for the cycle.
    For PATCH /audit-items/:id, the view will pass the AuditItem instance to `has_object_permission`.
    """
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
            
        # obj is AuditItem, its parent is AuditCycle
        cycle = obj.audit_cycle
        return cycle.auditors.filter(id=request.user.id).exists()
