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
        if request.user.dealerprofile.role in ['M', 'S']:
            user_dealership_ids = request.user.dealerprofile.dealerships.values_list('id', flat=True)  # Get the IDs of the user's dealerships
            print("User:", request.user.username)  # Log the user's username
            print("User Role:", request.user.dealerprofile.role)
            print("User Dealership IDs:", list(user_dealership_ids))
            print("Object Dealership ID:", obj.dealership.id)

            if obj.dealership.id in user_dealership_ids:
                print("Access Granted")
                return True
            else:
                print("Access Denied: Dealership Mismatch")
                return False
        else:
            print("Access Denied: Role Not Authorized")
            return False
