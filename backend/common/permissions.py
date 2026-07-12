from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')

class IsAdminOrAssetManagerOrReadOnly(permissions.BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    Write permissions are only allowed to admin and asset_manager roles.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
            
        if request.method in permissions.SAFE_METHODS:
            return True
            
        return request.user.role in ['admin', 'asset_manager']

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    Write permissions are only allowed to admin roles.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
            
        if request.method in permissions.SAFE_METHODS:
            return True
            
        return request.user.role == 'admin'

class IsAuthenticated(permissions.BasePermission):
    """
    Allows access only to authenticated users.
    We redefine it to ensure it uses our custom active status logic if needed.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
