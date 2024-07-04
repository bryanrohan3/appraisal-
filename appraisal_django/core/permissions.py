from rest_framework import permissions

class IsManagementDealer(permissions.BasePermission):
    """
    Custom permission to only allow management dealers to perform actions.
    """

    def has_permission(self, request, view):
        # Check if the user making the request is a management dealer
        return request.user.is_authenticated and request.user.dealer.role == 'management'
