from rest_framework import permissions
from .models import *

class IsManagementDealerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only management dealers to create sales dealers.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':  # Only allow creation for POST requests
            return request.user.dealerprofile.role == 'M'
        return True

    def has_object_permission(self, request, view, obj):
        # Check if the user has permission to access the object (if needed)
        return True  # Modify this if object-level permissions are required

class CanManageDealerships(permissions.BasePermission):
    """
    Custom permission to allow management dealers to manage dealerships.
    """

    def has_permission(self, request, view):
        # Check if the authenticated user is a management dealer ("M")
        return request.user.dealerprofile.role == 'M'

    def has_object_permission(self, request, view, obj):
        # Check if the management dealer manages the specified dealership
        if isinstance(obj, Dealership):
            return obj in request.user.dealerprofile.managed_dealerships.all()
        return False

class SalesDealerPermission(permissions.BasePermission):
    """
    Custom permission to disallow sales dealers from creating profiles.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':  # Only allow creation for POST requests
            return request.user.dealerprofile.role != 'S'
        return True

    def has_object_permission(self, request, view, obj):
        # Check if the user has permission to access the object (if needed)
        return True  # Modify this if object-level permissions are required
