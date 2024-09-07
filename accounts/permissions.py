from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'admin'

class IsBorrowerUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'borrower'