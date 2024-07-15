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
        

class CanMakeOffer(permissions.BasePermission):
    """
    Custom permission to allow only users with is_wholesaler=True to make an offer.
    """

    def has_permission(self, request, view):
        # Allow safe methods (GET, HEAD, OPTIONS) without restrictions
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if the authenticated user is a wholesaler
        try:
            return request.user.wholesalerprofile.is_wholesaler
        except WholesalerProfile.DoesNotExist:
            return False
        

class IsDealerFromSameDealershipOrWholesaler(permissions.BasePermission):
    """
    Custom permission to allow only dealers from the same dealership to access, and wholesalers to read and make offers.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        # Allow safe methods for everyone
        if request.method in SAFE_METHODS:
            return True
        
        # Check if the user is a dealer and belongs to the same dealership
        if hasattr(user, 'dealerprofile'):
            dealer_profile = user.dealerprofile
            user_dealership_ids = dealer_profile.dealerships.values_list('id', flat=True)
            return obj.dealership.id in user_dealership_ids
        
        # Check if the user is a wholesaler
        if hasattr(user, 'wholesalerprofile'):
            return True  # Wholesalers can read and make offers (which is a non-safe method)
        
        return False

class CanMakeOffer(permissions.BasePermission):
    """
    Custom permission to allow only users with is_wholesaler=True to make an offer.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        try:
            return request.user.wholesalerprofile.is_wholesaler
        except WholesalerProfile.DoesNotExist:
            return False
        

class CanViewOffers(permissions.BasePermission):
    """
    Custom permission to allow only Management Dealers ('M' role) to view offers.
    """

    def has_permission(self, request, view):
        if request.user.dealerprofile.role == 'M':
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # Optionally, you can check object-level permissions here
        return self.has_permission(request, view)
