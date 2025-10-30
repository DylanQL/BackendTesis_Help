# permissions.py en tu app
from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    """Permite acceso solo a usuarios con rol 'superadmin'."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.rol == 'superadmin')

class IsAdminOrSuperAdmin(BasePermission):
    """Permite acceso a usuarios con rol 'admin' o 'superadmin'."""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.rol in ['admin', 'superadmin']
        )

class IsSupervisorOrAdmin(BasePermission):
    """Permite acceso a usuarios con rol 'supervisor', 'admin' o 'superadmin'."""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.rol in ['supervisor', 'admin', 'superadmin']
        )

# Puedes añadir más permisos según necesites (e.g., IsEncargadoOrReadOnly, etc.)