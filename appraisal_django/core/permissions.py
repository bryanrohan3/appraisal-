from rest_framework import permissions
from .models import *

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS', 'POST')



class IsManagementDealerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow management dealers to create new users.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        try:
            dealer_profile = DealerProfile.objects.get(user=request.user)
            return dealer_profile.role == 'M'
        except DealerProfile.DoesNotExist:
            return False


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


class IsDealerFromSameDealership(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.dealerprofile.role == 'M':
            user_dealership_ids = request.user.dealerprofile.dealerships.values_list('id', flat=True)
            return obj.dealership.id in user_dealership_ids
        return False


class IsWholesalerOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD, or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the profile.
        return obj.user == request.user
    

class IsManagementDealerFromSameDealership(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and hasattr(request.user, 'dealerprofile')

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        try:
            dealer_profile = DealerProfile.objects.get(user=request.user)
            print(f"User: {request.user.username}, Role: {dealer_profile.role}, Dealerships: {dealer_profile.dealerships.all()}")
            return dealer_profile.role == 'M' and obj in dealer_profile.dealerships.all()
        except DealerProfile.DoesNotExist:
            return False