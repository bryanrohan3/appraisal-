from rest_framework import permissions
from .models import *

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS', 'POST')

class IsManagementDealerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == SAFE_METHODS:
            return True
        if view.action == 'create' and request.data.get('role') == 'M':
            return True
        return request.user and request.user.is_authenticated

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

# def create(self, request, *args, **kwargs):
#         role = request.data.get('role')
#         dealerships = request.data.get('dealerships', [])

#         if not request.user.is_authenticated:
#             return Response({"error": "Authentication required to create this user."}, status=status.HTTP_403_FORBIDDEN)

#         if role != 'M' and not all(Dealership.objects.filter(id=dealership_id, management_dealers__user=request.user).exists() for dealership_id in dealerships):
#             return Response({"error": "You can only create dealers for your dealerships."}, status=status.HTTP_403_FORBIDDEN)

#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


#  def create(self, request, *args, **kwargs):
#         # No need to check for management dealer role here anymore
#         dealership_ids = request.data.get('dealerships', [])
#         for dealership_id in dealership_ids:
#             if dealership_id not in request.user.dealerprofile.user.managed_dealerships.values_list('id', flat=True):
#                 return Response({"error": "You can only assign dealerships you manage."}, status=status.HTTP_403_FORBIDDEN)

#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)

#         instance = serializer.instance
#         instance.dealerships.set(dealership_ids)

#         return Response(serializer.data, status=status.HTTP_201_CREATED)
