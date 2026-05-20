from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'super_admin'

class IsCompanyAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['super_admin', 'company_admin']

class IsCompanyMember(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in [
            'super_admin', 'company_admin', 'company_user'
        ]

class IsProjectClient(BasePermission):
    """Client can only read their own projects."""
    def has_object_permission(self, request, view, obj):
        return (
            request.user and request.user.is_authenticated and
            request.method in SAFE_METHODS and
            obj.client == request.user
        )
