from rest_framework import viewsets, permissions, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from .models import *
from .serializers import *
from .permissions import *
from django.db.models import Q
from django.http import HttpResponse
import csv
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import IntegrityError


# TODO: Very important: Start pagination early
# TODO: Use the generic view set instead of the modelviewset, and use mixins
# We actually don't need list
# For dealership lookups, you can use an action route, accept a search param. ?name=asdf 
class DealershipViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Dealership.objects.all()
    serializer_class = DealershipSerializer
    permission_classes = [permissions.IsAuthenticated, IsDealer]
    serializer_classes = {
        'default': DealershipSerializer,
        'search': DealershipBasicSerializer
    }


    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.serializer_classes['default'])


    def get_queryset(self):
        """
        Restricts the returned queryset to dealerships the user is associated with.
        """
        user = self.request.user
        if user.is_authenticated:
            try:
                dealer_profile = DealerProfile.objects.get(user=user)
                return dealer_profile.dealerships.all()  # Only dealerships associated with the dealer
            except DealerProfile.DoesNotExist:
                return Dealership.objects.none()  # If dealer profile doesn't exist, return empty queryset
        return Dealership.objects.none()  # Return empty queryset for anonymous users
    

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific dealership by ID.
        """
        return super().retrieve(request, *args, **kwargs)


    @action(detail=False, methods=['get'], permission_classes=[IsDealer])
    def search(self, request):
        """
        Custom action to search for dealerships by name or other parameters.
        """
        queryset = self.get_queryset()

        dealership_name = request.query_params.get('dealership_name')
        if dealership_name:
            queryset = queryset.filter(dealership_name__icontains=dealership_name)

        serializer = self.get_serializer(queryset, many=True)
        # serializer = DealershipBasicSerializer(queryset, many=True)
        return Response(serializer.data)
    

    @action(detail=True, methods=['get'], permission_classes=[IsDealer])
    def dealers(self, request, pk=None):
        """
        Retrieve dealers associated with a specific dealership.
        """
        dealership = self.get_object()

        try:
            dealer_profile = DealerProfile.objects.get(user=request.user)
            if dealership not in dealer_profile.dealerships.all():
                return Response({'detail': 'Not authorized to view dealers of this dealership.'}, status=403)
        except DealerProfile.DoesNotExist:
            return Response({'detail': 'Not authorized to view dealers of this dealership.'}, status=403)

        dealers = DealerProfile.objects.filter(dealerships=dealership)
        serializer = DealerProfileSerializer(dealers, many=True)
        return Response(serializer.data)
    
    
#  TODO: Get rid of create update and list
class UserViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin):
    """
    ViewSet for managing users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    serializer_classes = {
        'login': UserLoginSerializer,
    }


    def get_serializer_class(self):
        """
        Override to use different serializer classes based on action.
        """

        return self.serializer_classes.get(self.action, self.serializer_class)


    # # TODO: Remove create, move to dealerprofileviewset
    # def create(self, request, *args, **kwargs):
    #     return super().create(request, *args, **kwargs)
    
    # # api/dealership/?dealship_id=1 -> 
    # # api/dealership/1 
    # # TODO: Remove update and move to dealerprofileviewset and wholesalerprofileviewset
    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     if request.user != instance:
    #         return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    #     return super().update(request, *args, **kwargs)


    @action(detail=False, methods=['POST'], permission_classes=[])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
        if user:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'message': 'Login successful', 'user': UserSerializer(user).data, 'token': token.key})
        else:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)


class DealerProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing dealer profiles.
    """

    queryset = DealerProfile.objects.all()
    serializer_class = DealerProfileSerializer
    

    def create(self, request, *args, **kwargs):
        """
        Custom create method to handle creation of dealer profiles.
        For 'M' (Management Dealer), authentication is bypassed.
        """
        if request.data.get('role') == 'M':
            # Bypass authentication for 'M' role during creation
            self.request.user = None
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def get_queryset(self):
        """
        Override queryset to filter based on the authenticated user's dealership.
        """
        queryset = super().get_queryset()

        if self.request.user.is_authenticated:
            user = self.request.user
            if hasattr(user, 'dealerprofile'):
                dealer_profile = user.dealerprofile
                queryset = queryset.filter(dealerships__in=dealer_profile.dealerships.all())

        return queryset
    

    @action(detail=False, methods=['PATCH'], url_path='deactivate')
    def deactivate_dealer(self, request):
        """
        Action to deactivate (soft delete) the authenticated dealer's profile and user.
        """
        try:
            dealer_profile = self.request.user.dealerprofile
            dealer_profile.is_active = False
            dealer_profile.save()

            user = dealer_profile.user
            user.is_active = False
            user.save()

            return Response({'status': 'Dealer and user deactivated'}, status=status.HTTP_200_OK)
        except DealerProfile.DoesNotExist:
            return Response({'error': 'Dealer profile not found'}, status=status.HTTP_404_NOT_FOUND)


    @action(detail=False, methods=['POST'], url_path='(?P<user_id>[^/.]+)/promote')
    def promote_dealer(self, request, user_id=None):
        """
        Action to promote a Sales Dealer to Management Dealer by a Management Dealer.
        """
        try:
            management_dealer = self.request.user.dealerprofile
            
            # Use filter_queryset to get the queryset of dealers that the management dealer can promote
            queryset = self.filter_queryset(self.get_queryset())
            dealer_to_promote = queryset.get(user_id=user_id, dealerships=management_dealer.dealerships.first(), role='S')
        except DealerProfile.DoesNotExist:
            return Response({'error': 'Dealer not found or not promotable'}, status=status.HTTP_404_NOT_FOUND)
        
        if management_dealer.role != 'M':
            return Response({'error': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
        
        dealer_to_promote.role = 'M'
        dealer_to_promote.save()

        serializer = self.get_serializer(dealer_to_promote)
        return Response(serializer.data)
    
        # Whole request can be boiled down to:
        # dealer_to_promote = self.get_object() -> only work if we have the filter_queryset
        # DealerProfile.objects.filter(id=dealer_to_promote.id).update(role='M')
        # serializer = self.get_serializer(dealer_to_promote)
        # return Response(serializer.data)


# Use the generic, + mixins
class WholesalerProfileViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin):
    """
    ViewSet for managing wholesaler profiles.
    """
    queryset = WholesalerProfile.objects.all()
    serializer_class = WholesalerProfileSerializer
    permission_classes = [IsWholesaler]

    # TODO: Set this in the serializer, we actually dont need this at all. 
    # def perform_create(self, serializer):
    #     # Automatically set the current user as the owner of the profile
    #     serializer.save(user=self.request.user)
    #     # eg:
    #     # inside WholesalerProfileSerializer
    #     # def save(self, validated_data, args, kwargs)
    #     # get request from context
        # validated_data["user"] = self.request.user


    @action(detail=False, methods=['GET'])
    def current_user_profile(self, request):
        """
        Retrieve the profile of the current authenticated user.
        """
        user_id = request.user.id
        try:
            wholesaler_profile = WholesalerProfile.objects.get(user_id=user_id)
            serializer = self.get_serializer(wholesaler_profile)
            return Response(serializer.data)
        except WholesalerProfile.DoesNotExist:
            return Response({'error': 'Wholesaler Profile not found for the authenticated user'}, status=status.HTTP_404_NOT_FOUND)


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Ensure only the owner can update their profile
        if request.user != instance.user:
            return Response({'error': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


    @action(detail=True, methods=['put'], url_path='deactivate')
    def deactivate_profile(self, request, pk=None):
        """
        Deactivate the wholesaler profile by setting is_active to False.
        """
        instance = self.get_object()
        
        # Ensure only the owner can deactivate their profile
        if request.user != instance.user:
            return Response({'error': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        instance.is_active = False
        instance.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class AppraisalViewSet(viewsets.GenericViewSet, viewsets.mixins.CreateModelMixin, viewsets.mixins.RetrieveModelMixin, viewsets.mixins.UpdateModelMixin, viewsets.mixins.ListModelMixin):
    queryset = Appraisal.objects.all()
    serializer_class = AppraisalSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_queryset(self):
        user = self.request.user

        if hasattr(user, 'wholesalerprofile'):
            return Appraisal.objects.all()

        elif hasattr(user, 'dealerprofile'):
            user_dealership_ids = user.dealerprofile.dealerships.values_list('id', flat=True)
            queryset = Appraisal.objects.filter(dealership_id__in=user_dealership_ids)

            dealership_id = self.request.query_params.get('dealership_id')
            if dealership_id:
                queryset = queryset.filter(dealership_id=dealership_id)

            user_id = self.request.query_params.get('user_id')
            if user_id:
                queryset = queryset.filter(Q(initiating_dealer__user__id=user_id) | Q(last_updating_dealer__user__id=user_id))

            return queryset

        return Appraisal.objects.none()
    

    def get_serializer_class(self):
        if self.action == 'list_offers' and self.request.user.dealerprofile.role == 'S':
            return SalesSerializer
        return self.serializer_class


    @action(detail=True, methods=['POST'], permission_classes=[IsDealer])
    def custom_list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        keyword = request.query_params.get('filter')
        if keyword:
            queryset = self.filter_queryset_by_keyword(queryset, keyword)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    # TODO: Sales Dealers can still see Offers here which defeats the purpose of list_offers below
    @action(detail=True, methods=['POST'], permission_classes=[IsDealer])
    def custom_retrieve(self, request, *args, **kwargs):
        appraisal = self.get_object()  # Get the object from the queryset
        dealership_id = appraisal.dealership.id  # Get the ID of the dealership associated with the object

        # Check permissions for management dealers
        self.check_object_permissions(request, appraisal) 

        # Debug statement
        print(f"Retrieving appraisal for user {request.user.username}") 

        serializer = self.get_serializer(appraisal)  # Serialize 
        return Response(serializer.data) 


    @action(detail=True, methods=['POST'], permission_classes=[IsManagement])
    def custom_update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Check if the user is a Sales Dealer
        if request.user.dealerprofile.role == 'S':
            return Response({"message": "Sales Dealers are not allowed to update appraisals"}, status=status.HTTP_403_FORBIDDEN)

        # Check if the user is a Management Dealer
        if request.user.dealerprofile.role == 'M':
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            return Response({"message": "You do not have permission to update this appraisal"}, status=status.HTTP_403_FORBIDDEN)


    @action(detail=True, methods=['POST'], permission_classes=[IsManagement])
    def custom_partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.dealerprofile.role == 'S':
            return Response({"message": "Sales Dealers are not allowed to update appraisals"}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


    def filter_queryset_by_keyword(self, queryset, keyword):
        # Filter queryset to find exact match for dealership name
        partial_match_query = Q(dealership__dealership_name__icontains=keyword) | Q(vehicle_vin__icontains=keyword) | Q(vehicle_registration__icontains=keyword) | Q(vehicle_make__icontains=keyword) | Q(vehicle_model__icontains=keyword)
        queryset = queryset.filter(partial_match_query)
        return queryset
    

    @action(detail=True, methods=['POST'], permission_classes=[IsDealer])
    def add_private_comment(self, request, pk=None):
        appraisal = self.get_object()
        user = request.user
        data = request.data

        if 'comment' not in data:
            return Response({"error": "Comment data not provided"}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(user=user, comment=data['comment'])
        appraisal.private_comments.add(comment)

        return Response({"message": "Private comment added successfully."}, status=status.HTTP_201_CREATED)
    

    @action(detail=True, methods=['PATCH'], url_path='deactivate', permission_classes=[IsManagement])
    def deactivate(self, request, pk=None):
        """
        Action to deactivate an appraisal. Only Management Dealers can perform this action.
        """
        try:
            appraisal = self.get_object()
            user = request.user

            if not hasattr(user, 'dealerprofile') or user.dealerprofile.role != 'M':
                return Response({"message": "Only Management Dealers can deactivate appraisals"}, status=status.HTTP_403_FORBIDDEN)

            appraisal.is_active = False
            appraisal.save()

            return Response({'status': 'Appraisal deactivated'}, status=status.HTTP_200_OK)
        except Appraisal.DoesNotExist:
            return Response({'error': 'Appraisal not found'}, status=status.HTTP_404_NOT_FOUND)


    @action(detail=True, methods=['POST'], permission_classes=[IsDealer, IsWholesaler])
    def add_general_comment(self, request, pk=None):
        appraisal = self.get_object()
        user = request.user
        data = request.data

        if 'comment' not in data:
            return Response({"error": "Comment data not provided"}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(user=user, comment=data['comment'])
        appraisal.general_comments.add(comment)

        return Response({"message": "General comment added successfully."}, status=status.HTTP_201_CREATED)
    

    @action(detail=True, methods=['post'], url_path='csv', permission_classes=[IsManagement])
    def download_csv(self, request, pk=None):
        appraisal = self.get_object()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="appraisal_{appraisal.id}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Field', 'Value'])
        writer.writerow(['ID', appraisal.id])
        writer.writerow(['Start Date', appraisal.start_date])
        writer.writerow(['Last Updated', appraisal.last_updated])
        writer.writerow(['Is Active', appraisal.is_active])
        writer.writerow(['Dealership', appraisal.dealership.dealership_name])
        writer.writerow(['Initiating Dealer', f"{appraisal.initiating_dealer.user.first_name} {appraisal.initiating_dealer.user.last_name}"])
        writer.writerow(['Last Updating Dealer', f"{appraisal.last_updating_dealer.user.first_name} {appraisal.last_updating_dealer.user.last_name}"])
        writer.writerow(['Customer First Name', appraisal.customer_first_name])
        writer.writerow(['Customer Last Name', appraisal.customer_last_name])
        writer.writerow(['Customer Email', appraisal.customer_email])
        writer.writerow(['Customer Phone', appraisal.customer_phone])
        writer.writerow(['Make', appraisal.vehicle_make])
        writer.writerow(['Model', appraisal.vehicle_model])
        writer.writerow(['Year', appraisal.vehicle_year])
        writer.writerow(['VIN', appraisal.vehicle_vin])
        writer.writerow(['Registration', appraisal.vehicle_registration])
        writer.writerow(['Color', appraisal.color])
        writer.writerow(['Odometer Reading', appraisal.odometer_reading])
        writer.writerow(['Engine Type', appraisal.engine_type])
        writer.writerow(['Transmission', appraisal.transmission])
        writer.writerow(['Body Type', appraisal.body_type])
        writer.writerow(['Fuel Type', appraisal.fuel_type])
        writer.writerow(['Damage Description', appraisal.damage_description])
        writer.writerow(['Damage Location', appraisal.damage_location])
        writer.writerow(['Repair Cost Estimate', appraisal.repair_cost_estimate])
        writer.writerow(['Reserve Price', appraisal.reserve_price])

        # Write comments
        writer.writerow([])
        writer.writerow(['General Comments'])
        for comment in appraisal.general_comments.all():
            writer.writerow([comment.comment_date_time, comment.comment])

        return response
    

    @action(detail=True, methods=['POST'], url_path='make_offer', permission_classes=[IsWholesaler])
    def make_offer(self, request, pk=None):
        appraisal = self.get_object()
        user = request.user

        # Ensure only Wholesalers can make an offer
        if not hasattr(user, 'wholesalerprofile') or not user.wholesalerprofile.is_wholesaler:
            return Response({"detail": "Only wholesalers can make an offer."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        serializer = OfferSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(appraisal=appraisal)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    @action(detail=True, methods=['get'], url_path='offers', permission_classes=[IsManagement])
    def list_offers(self, request, pk=None):
        appraisal = self.get_object()
        offers = Offer.objects.filter(appraisal=appraisal)
        serializer = OfferSerializer(offers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['POST'], url_path='duplicate', permission_classes=[IsDealer])
    def duplicate(self, request, pk=None):
        instance = self.get_object()

        # Retrieve authenticated user's DealerProfile
        dealer_profile = DealerProfile.objects.get(user=request.user)

        # Create a new Appraisal instance with copied fields
        new_appraisal = Appraisal(
            initiating_dealer=instance.initiating_dealer,
            dealership=instance.dealership,
            last_updating_dealer=dealer_profile,
            customer_first_name=instance.customer_first_name,
            customer_last_name=instance.customer_last_name,
            customer_email=instance.customer_email,
            customer_phone=instance.customer_phone,
            vehicle_make=instance.vehicle_make,
            vehicle_model=instance.vehicle_model,
            vehicle_year=instance.vehicle_year,
            vehicle_vin=instance.vehicle_vin,
            vehicle_registration=instance.vehicle_registration,
            color=instance.color,
            odometer_reading=instance.odometer_reading,
            engine_type=instance.engine_type,
            transmission=instance.transmission,
            body_type=instance.body_type,
            fuel_type=instance.fuel_type,
            reserve_price=instance.reserve_price,
            start_date=timezone.now(),
            last_updated=timezone.now(),
            is_active=True,
        )

        # Save the new appraisal instance to assign it an ID
        new_appraisal.save()

        # Clear offers related to the new appraisal (assuming a related_name 'offers')
        new_appraisal.offers.set([])  # Set an empty list to clear all related offers

        # Update last_updated to current time
        new_appraisal.last_updated = timezone.now()

        # Save the new appraisal instance again to update last_updated
        new_appraisal.save()

        # Serialize the new instance to return in response
        serializer = self.get_serializer(new_appraisal)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class RequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    permission_classes_by_action = {
        'create': [IsWholesaler],
        'respond_to_friend_request': [IsManagement],
        'list_received_requests': [IsManagement],  # Ensure permission check for this action
    }


    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return super().get_permissions()


    def perform_create(self, serializer):
        user = self.request.user 
        try:
            wholesaler_profile = user.wholesalerprofile
        except WholesalerProfile.DoesNotExist:
            raise serializers.ValidationError({'error': 'Only wholesalers can send friend requests.'})

        dealership_id = self.request.data.get('dealership')  # Get the dealership ID from the request data
        dealership = get_object_or_404(Dealership, id=dealership_id)  # Get the dealership object
        serializer.save(sender=wholesaler_profile, dealership=dealership)  # Save the friend request


    @action(detail=True, methods=['put'], url_path='respond')
    def respond_to_friend_request(self, request, pk=None):
        friend_request = get_object_or_404(FriendRequest, id=pk)
        try:
            dealer_profile = request.user.dealerprofile
        except DealerProfile.DoesNotExist:
            return Response({'error': 'User does not have a dealer profile.'}, status=status.HTTP_403_FORBIDDEN)

        if dealer_profile.role != 'M':
            return Response({'error': 'Only dealership managers can respond to this request'}, status=status.HTTP_403_FORBIDDEN)

        response_status = request.data.get('status')
        if response_status not in ['accepted', 'rejected']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request.status = response_status
        friend_request.save()

        if response_status == 'accepted':
            # Update the dealership's wholesalers list
            dealership = friend_request.dealership
            wholesaler_profile = friend_request.sender
            dealership.wholesalers.add(wholesaler_profile.user)
            dealership.save()

        serializer = self.get_serializer(friend_request)
        return Response(serializer.data)


    @action(detail=False, methods=['get'], url_path='sent')
    def list_sent_requests(self, request):
        try:
            wholesaler_profile = request.user.wholesalerprofile
        except WholesalerProfile.DoesNotExist:
            return Response({'error': 'User does not have a wholesaler profile.'}, status=status.HTTP_400_BAD_REQUEST)

        sent_requests = FriendRequest.objects.filter(sender=wholesaler_profile)
        serializer = self.get_serializer(sent_requests, many=True)
        return Response(serializer.data)


    @action(detail=False, methods=['get'], url_path='received')
    def list_received_requests(self, request):
        try:
            dealer_profile = request.user.dealerprofile
        except DealerProfile.DoesNotExist:
            return Response({'error': 'User does not have a dealer profile.'}, status=status.HTTP_403_FORBIDDEN)

        # Check if dealer is a manager
        if dealer_profile.role != 'M':
            return Response({'error': 'Only dealership managers can view received friend requests.'}, status=status.HTTP_403_FORBIDDEN)

        dealership_id = request.query_params.get('dealership')
        if not dealership_id:
            return Response({'error': 'Dealership ID must be provided.'}, status=status.HTTP_400_BAD_REQUEST)

        dealership = get_object_or_404(Dealership, id=dealership_id)

        # Ensure the dealer is associated with the dealership
        if dealership not in dealer_profile.dealerships.all():
            return Response({'error': 'Dealer does not belong to the specified dealership.'}, status=status.HTTP_403_FORBIDDEN)

        received_requests = FriendRequest.objects.filter(dealership=dealership)
        serializer = self.get_serializer(received_requests, many=True)
        return Response(serializer.data)
    
