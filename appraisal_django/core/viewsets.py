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
from rest_framework import status
from django.db import transaction
from rest_framework.pagination import PageNumberPagination
from django.utils.dateparse import parse_datetime
from django.db.models import Count


class CustomPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'
    max_page_size = 1000

class PaginationMixin:
    pagination_class = CustomPagination

    def paginate_queryset(self, queryset, request):
        paginator = self.pagination_class()
        return paginator.paginate_queryset(queryset, request)

    def get_paginated_response(self, data):
        paginator = self.pagination_class()
        return paginator.get_paginated_response(data)


class DealershipViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Dealership.objects.all()
    serializer_class = DealershipSerializer
    permission_classes = [permissions.IsAuthenticated, IsDealer]
    serializer_classes = {
        'default': DealershipSerializer,
        'dealers': DealerProfileSerializer,
        'search': DealershipBasicSerializer
    }
    pagination_class = CustomPagination


    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.serializer_classes['default'])


    def get_queryset(self):
        """
        Restricts the returned queryset to dealerships the user is associated with.
        """
        user = self.request.user
        queryset = Dealership.objects.none()  # Start with an empty queryset
        
        if user.is_authenticated:
            try:
                dealer_profile = user.dealerprofile
                queryset = dealer_profile.dealerships.all()  # Only dealerships associated with the dealer
            except DealerProfile.DoesNotExist:
                pass  # Return empty queryset if dealer profile doesn't exist
       
        return queryset
    
    def filter_queryset(self, queryset):
        """
        Apply filtering to the queryset based on query parameters.
        """
        dealership_id = self.request.query_params.get('dealership_id')
        if dealership_id:
            queryset = queryset.filter(id=dealership_id)
        return queryset
    

    @action(detail=True, methods=['get'], permission_classes=[IsDealer])
    def wholesalers(self, request, pk=None):
        """
        Retrieve wholesalers associated with a specific dealership.
        """
        dealership = self.get_object()
        wholesaler_profiles = WholesalerProfile.objects.filter(wholesaler_dealerships=dealership)

        # Apply Pagination
        page = self.paginate_queryset(wholesaler_profiles)
        if page is not None:
            serializer = WholesalerProfileSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = WholesalerProfileSerializer(wholesaler_profiles, many=True)
        return Response(serializer.data)
    

    @action(detail=False, methods=['get'], permission_classes=[IsWholesaler])
    def search(self, request):
        """
        Custom action to search for dealerships by name or other parameters.
        """

        serializer = DealershipSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        queryset = Dealership.objects.all()

        dealership_name = validated_data.get('dealership_name')
        if dealership_name:
            queryset = queryset.filter(dealership_name__icontains=dealership_name)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

    @action(detail=True, methods=['get'], permission_classes=[IsDealer])
    def dealers(self, request, pk=None):
        """
        Retrieve dealers associated with a specific dealership.
        """
        dealership = self.get_object()  # Get the Dealership instance

        # TODO: Use filter_queryset to apply any filtering logic (if any)
        queryset = DealerProfile.objects.filter(dealerships=dealership)
        filtered_queryset = self.filter_queryset(queryset)

        dealer_profile = request.user.dealerprofile  # Directly access the dealer profile
        if dealership not in dealer_profile.dealerships.all():
            return Response({'detail': 'Not authorized to view dealers of this dealership.'}, status=403)
        
        # Apply pagination to the filtered queryset
        page = self.paginate_queryset(filtered_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Use get_serializer to serialize the data
        serializer = self.get_serializer(filtered_queryset, many=True)
        return Response(serializer.data)


    @action(detail=True, methods=['PATCH'], url_path='deactivate', permission_classes=[IsManagement])
    def deactivate(self, request, pk=None):
        """
        Action to deactivate a dealership. Only Management Dealers from the specific dealership can perform this action.
        """
        dealership = self.get_object()
        
        #TODO: Use filter_queryset to validate access
        queryset = self.filter_queryset(self.get_queryset())
        if dealership not in queryset:
            return Response({"message": "You do not have permission to deactivate this dealership"}, status=status.HTTP_403_FORBIDDEN)
        
        dealership.is_active = False
        dealership.save()
        return Response({'status': 'Dealership deactivated'}, status=status.HTTP_200_OK)

    
class UserViewSet(viewsets.GenericViewSet):
    """
    ViewSet for managing users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    serializer_classes = {
        'login': UserLoginSerializer,
    }

    def get_serializer_class(self):
        """
        Override to use different serializer classes based on action.
        """

        return self.serializer_classes.get(self.action, self.serializer_class)

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


class DealerProfileViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    """
    ViewSet for managing dealer profiles.
    """

    queryset = DealerProfile.objects.all()
    serializer_class = DealerProfileSerializer

    def get_queryset(self):
        """
        Override queryset to filter based on the authenticated user's dealership.
        If the user is not authenticated, return an empty queryset.
        """
        if not self.request.user.is_authenticated:
            return DealerProfile.objects.none()  # Return an empty queryset

        queryset = super().get_queryset()
        user = self.request.user

        if hasattr(user, 'dealerprofile'):
            dealer_profile = user.dealerprofile
            queryset = queryset.filter(dealerships__in=dealer_profile.dealerships.all())
        
        return queryset
    

    @action(detail=True, methods=['PATCH'], permission_classes=[IsManagement], url_path='deactivate')
    def deactivate_dealer(self, request, pk=None):
        """
        Action to deactivate (soft delete) a dealer's profile and user.
        Only a Management Dealer can deactivate any dealer, including other Management Dealers,
        within the same dealership. Sales Dealers cannot deactivate their own account or any other account.
        """
        try:
            dealer_profile = self.get_object()  # Get the dealer profile specified by the URL

            dealer_profile.is_active = False
            dealer_profile.save()

            user = dealer_profile.user
            user.is_active = False
            user.save()

            return Response({'status': 'Dealer and user deactivated'}, status=status.HTTP_200_OK)
        except DealerProfile.DoesNotExist:
            return Response({'error': 'Dealer profile not found or not in the same dealership'}, status=status.HTTP_404_NOT_FOUND)
        
    # TODO: use correct detail route
    # TODO: Use the get_queryset to validate access
    @action(detail=True, methods=['POST'], url_path='promote', permission_classes=[IsManagement])
    def promote_dealer(self, request, pk=None):
        """
        Action to promote a Sales Dealer to Management Dealer by a Management Dealer.
        """
        queryset = self.get_queryset()

        try:
            dealer_to_promote = queryset.get(pk=pk, role='S')
        except DealerProfile.DoesNotExist:
            return Response({"error": "Dealer not found"}, status=status.HTTP_404_NOT_FOUND)

        if not dealer_to_promote:
            return Response({"error": "Dealer not found"}, status=status.HTTP_404_NOT_FOUND)

        dealer_to_promote.role = 'M'
        dealer_to_promote.save()
        serializer = self.get_serializer(dealer_to_promote)
        return Response(serializer.data)


class WholesalerProfileViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    """
    ViewSet for managing wholesaler profiles.
    """
    serializer_class = WholesalerProfileSerializer
    permission_classes = [IsWholesaler]

    def get_queryset(self):
        """
        This viewset should return only the profiles for the current authenticated user.
        """
        user_id = self.request.user.id
        return WholesalerProfile.objects.filter(user_id=user_id)


    @action(detail=True, methods=['put'], url_path='deactivate', permission_classes=[IsWholesaler])
    def deactivate_profile(self, request, pk=None):
        """
        Deactivate the wholesaler profile by setting is_active to False.
        """
        instance = self.get_object()
    
        instance.is_active = False
        instance.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class AppraisalViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin):
    queryset = Appraisal.objects.all()
    serializer_class = AppraisalSerializer
    pagination_class = CustomPagination


    def get_queryset(self):
        user = self.request.user

        # TODO: Change for the offer one2one thing
        if hasattr(user, 'wholesalerprofile'):
            invited_appraisal_ids = AppraisalInvite.objects.filter(wholesaler=user.wholesalerprofile).values_list('appraisal_id', flat=True)
            queryset = Appraisal.objects.filter(id__in=invited_appraisal_ids)

        elif hasattr(user, 'dealerprofile'):
            user_dealership_ids = user.dealerprofile.dealerships.values_list('id', flat=True)
            queryset = Appraisal.objects.filter(dealership_id__in=user_dealership_ids)

        else:
            queryset = Appraisal.object.none()

        return self.filter_queryset(queryset)
    
    
    def filter_queryset(self, queryset):
        """
        Apply filtering to the queryset based on query parameters.
        """
        dealership_id = self.request.query_params.get('dealership_id')
        if dealership_id:
            queryset = queryset.filter(dealership_id=dealership_id)
        
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(Q(initiating_dealer__user__id=user_id) | Q(last_updating_dealer__user__id=user_id))

        return queryset


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
        data['appraisal'] = appraisal.id  # This associates the comment with the correct appraisal

        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=user, is_private=True)  # Save the comment, setting user and is_private
            return Response({"message": "Private comment added successfully."}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['PATCH'], url_path='deactivate', permission_classes=[IsManagement])
    def deactivate(self, request, pk=None):
        """
        Action to deactivate an appraisal. Only Management Dealers can perform this action.
        """
        appraisal = self.get_object()
        user = request.user
        appraisal.is_active = False
        appraisal.save()

        return Response({'status': 'Appraisal deactivated'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def add_general_comment(self, request, pk=None):
        appraisal = self.get_object()
        user = request.user
        data = request.data
        data['appraisal'] = appraisal.id  # This associates the comment with the correct appraisal

        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=user)  # Save the comment, setting user and is_private
            return Response({"message": "General comment added successfully."}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # TODO: Take a full queryset, and handle a whole csv
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

        wholesaler_profile = user.wholesalerprofile
        data = request.data
        amount = data.get('amount')

        # Check if there's an existing offer where the user has passed
        # TODO: Can get rid of all of this with the single table offer invite
        offer = Offer.objects.filter(appraisal=appraisal, user=wholesaler_profile).first()

        if offer:
            if offer.passed:
                # If previously passed, reset passed to False and update amount
                offer.passed = False
                offer.amount = amount
                offer.save()
                serializer = OfferSerializer(offer)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # If offer exists and was not passed, update the amount
                offer.amount = amount
                offer.save()
                serializer = OfferSerializer(offer)
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Create a new offer if none exists
            serializer = OfferSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                serializer.save(appraisal=appraisal, user=wholesaler_profile)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'], url_path='pass', permission_classes=[IsWholesaler])
    def pass_offer(self, request, pk=None):
        appraisal = self.get_object()
        user = request.user

        wholesaler_profile = user.wholesalerprofile
        # Check if an offer already exists
        offer, created = Offer.objects.get_or_create(
            appraisal=appraisal, user=wholesaler_profile,
            defaults={'passed': True, 'amount': None}
        )

        if not created:
            offer.passed = True
            offer.amount = None  # Ensure amount is cleared
            offer.save()

        serializer = OfferSerializer(offer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['PATCH'], url_path='update_offer/(?P<offer_id>\d+)', permission_classes=[IsManagement])
    def update_offer(self, request, pk=None, offer_id=None):
        appraisal = self.get_object()
        try:
            offer = appraisal.offers.get(id=offer_id)
        except Offer.DoesNotExist:
            return Response({"detail": "Offer not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdjustedAmountSerializer(offer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    # Has Pagination /api/{id}/offers/?page=?
    @action(detail=True, methods=['get'], url_path='offers', permission_classes=[IsManagement])
    def list_offers(self, request, pk=None):
        appraisal = self.get_object()
        offers = Offer.objects.filter(appraisal=appraisal)

        # Apply Pagination
        page = self.paginate_queryset(offers)
        if page is not None:
            serializer = OfferSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = OfferSerializer(offers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['POST'], url_path='duplicate', permission_classes=[IsDealer])
    def duplicate(self, request, pk=None):
        instance = self.get_object()

        dealer_profile = request.user.dealerprofile

        # Duplicate the appraisal instance
        instance.id = None  # Reset ID to create a new instance
        instance.pk = None  # Ensure primary key is set to None
        instance.start_date = timezone.now()  # Set a new start date
        instance.last_updated = timezone.now()  # Set the current time for the last update
        instance.is_active = True  # Ensure the new appraisal is active
        instance.save()  # Save the new instance to create a new record

        # Clear offers related to the new appraisal
        instance.offers.set([])  # Clear offers to reset them to an empty list

        # Update the last_updated field again
        instance.last_updated = timezone.now()
        instance.save()

        # Serialize the new instance to return in the response
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # TODO: Wrong URL path    
    @action(detail=True, methods=['POST'], url_path='select_winner/(?P<offer_id>\d+)', permission_classes=[IsManagement])
    def select_winner(self, request, pk=None, offer_id=None):
        # TODO: Use a serializer        
        appraisal = self.get_object()

        if not offer_id:
            return Response({"error": "Offer ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            selected_offer = appraisal.offers.get(id=offer_id)
        except Offer.DoesNotExist:
            return Response({"error": "Offer not found"}, status=status.HTTP_404_NOT_FOUND)

        appraisal.winner = selected_offer
        appraisal.save()

        return Response({"message": "Winning offer selected successfully"}, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['post'], permission_classes=[IsManagement])
    def invite_wholesaler(self, request, pk=None):
        appraisal = self.get_object()
        user = request.user


        #TODO: Serializer        
        wholesaler_ids = request.data.get('wholesalers', [])
        if not wholesaler_ids:
            return Response({"message": "No wholesalers provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the dealership associated with the appraisal
        dealership = appraisal.dealership

        # TODO: This can be handled in the serializer using the FK serializer. The one i wrote was for dealership, so write your own for wholesalers        # Get the list of wholesaler IDs associated with the dealership
        dealership_wholesaler_ids = dealership.wholesalers.values_list('id', flat=True)
        invited_wholesalers = []
        for wholesaler_id in wholesaler_ids:
            if wholesaler_id not in dealership_wholesaler_ids:
                return Response({"message": f"Wholesaler {wholesaler_id} is not associated with the dealership"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Fetch wholesaler profile directly
                wholesaler = WholesalerProfile.objects.get(id=wholesaler_id)
                
                # Create or get the invite
                invite, created = AppraisalInvite.objects.get_or_create(appraisal=appraisal, wholesaler=wholesaler)
                if created:
                    invited_wholesalers.append(wholesaler_id)
            except WholesalerProfile.DoesNotExist:
                return Response({"message": f"Wholesaler profile for ID {wholesaler_id} does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"invited_wholesalers": invited_wholesalers}, status=status.HTTP_201_CREATED)


    # Pagination Applied => api/offers/list_invites/?page={}
    @action(detail=False, methods=['get'], url_path='list_invites', permission_classes=[permissions.IsAuthenticated])
    def list_invites(self, request):
        if not hasattr(request.user, 'wholesalerprofile'):
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        invites = AppraisalInvite.objects.filter(wholesaler=request.user.wholesalerprofile)

        # Apply pagination
        page = self.paginate_queryset(invites)
        if page is not None:
            serializer = AppraisalInviteSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)


        serializer = AppraisalInviteSerializer(invites, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        appraisal = self.get_object()
        user = request.user

        # Check for Dealer profile
        if hasattr(user, 'dealerprofile'):
            status = self.get_dealer_status(appraisal)
        
        # Check for Wholesaler profile
        elif hasattr(user, 'wholesalerprofile'):
            status = self.get_wholesaler_status(appraisal, user.wholesalerprofile)
        
        else:
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        # Debug output
        print(f"Appraisal ID: {appraisal.id}")
        print(f"Offers: {appraisal.offers.all()}")
        print(f"Invites: {appraisal.invites.all()}")
        print(f"Status: {status}")

        return Response({'status': status})

    def _parse_date_range(self, request):
        date_from = request.query_params.get('from')
        date_to = request.query_params.get('to')

        if not date_from or not date_to:
            return None, Response({"error": "Both 'from' and 'to' parameters are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date_from = parse_datetime(date_from)
            date_to = parse_datetime(date_to)

            if date_from > date_to:
                return None, Response({"error": "'from' date must be earlier than 'to' date"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return None, Response({"error": "Invalid date format. Use ISO 8601 format."}, status=status.HTTP_400_BAD_REQUEST)

        return (date_from, date_to), None

    @action(detail=False, methods=['get'], url_path='count_and_list_by_date_range')
    def count_and_list_by_date_range(self, request, *args, **kwargs):
        date_range, error_response = self._parse_date_range(request)
        if error_response:
            return error_response

        date_from, date_to = date_range
        user = request.user

        if hasattr(user, 'dealerprofile'):
            dealer_id = user.dealerprofile.id
            queryset = Appraisal.objects.filter(initiating_dealer_id=dealer_id, start_date__range=[date_from, date_to])
            serializer = self.get_serializer(queryset, many=True)

            page = self.paginate_queryset(serializer.data)
            if page is not None:
                return self.get_paginated_response(page)

            appraisal_count = queryset.count()

            return Response({
                "appraisal_count": appraisal_count,
                "appraisals": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User does not have a valid dealer profile"}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['get'], url_path='most_common_cars_by_date_range')
    def most_common_cars_by_date_range(self, request, *args, **kwargs):
        date_range, error_response = self._parse_date_range(request)
        if error_response:
            return error_response

        date_from, date_to = date_range
        user = request.user

        if hasattr(user, 'dealerprofile'):
            dealer_id = user.dealerprofile.id
            queryset = Appraisal.objects.filter(initiating_dealer_id=dealer_id, start_date__range=[date_from, date_to])

            car_counts = (queryset
                        .values('vehicle_make', 'vehicle_model')
                        .annotate(count=Count('id'))
                        .order_by('-count'))

            return Response({
                "car_counts": car_counts
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User does not have a valid dealer profile"}, status=status.HTTP_403_FORBIDDEN)
        
    @action(detail=False, methods=['get'], url_path='best_performing_wholesalers')
    def best_performing_wholesalers(self, request, *args, **kwargs):
        date_range, error_response = self._parse_date_range(request)
        if error_response:
            return error_response

        date_from, date_to = date_range
        user = request.user

        if hasattr(user, 'dealerprofile'):
            dealer_id = user.dealerprofile.id
            queryset = Appraisal.objects.filter(
                initiating_dealer_id=dealer_id,
                start_date__range=[date_from, date_to]
            ).select_related('winner')  # Optimize query to fetch related 'winner'

            # Count by winner's profile ID and get username
            wholesaler_counts = (queryset
                                .values('winner__user_id', 'winner__user__wholesaler_name')  # Access winner's profile ID and username
                                .annotate(count=Count('winner__user_id'))  # Count how many times each ID appears
                                .order_by('-count'))

            return Response({
                "wholesaler_counts": wholesaler_counts
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User does not have a valid dealer profile"}, status=status.HTTP_403_FORBIDDEN)


class RequestViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    permission_classes_by_action = {
        'respond_to_friend_request': [IsManagement | IsWholesaler],
        'list_sent_requests': [IsWholesaler],
        'list_received_requests': [IsManagement],
    }
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, 'wholesalerprofile'):
            # User is a wholesaler
            return FriendRequest.objects.filter(
                Q(sender=user.wholesalerprofile) |
                Q(recipient_wholesaler=user.wholesalerprofile)
            )
        elif hasattr(user, 'dealerprofile'):
            # User is a dealer, filter based on their dealerships
            dealerships = user.dealerprofile.dealerships.all()
            return FriendRequest.objects.filter(
                Q(dealership__in=dealerships)
            )
        else:
            return FriendRequest.objects.none()



    # TODO: Chnage to a mixin and validate in serializer
    # def perform_create(self, serializer):
    #     user = self.request.user
    #     try:
    #         wholesaler_profile = user.wholesalerprofile
    #     except WholesalerProfile.DoesNotExist:
    #         raise serializers.ValidationError({'error': 'Only wholesalers can send friend requests.'})

    #     recipient_wholesaler = self.request.data.get('recipient_wholesaler')
    #     dealership_id = self.request.data.get('dealership')

    #     if recipient_wholesaler:
    #         recipient_wholesaler = get_object_or_404(WholesalerProfile, id=recipient_wholesaler)
    #         serializer.save(sender=wholesaler_profile, recipient_wholesaler=recipient_wholesaler)
    #     elif dealership_id:
    #         dealership = get_object_or_404(Dealership, id=dealership_id)
    #         serializer.save(sender=wholesaler_profile, dealership=dealership)
    #     else:
    #         raise serializers.ValidationError({'error': 'Recipient wholesaler or dealership must be specified.'})

    @action(detail=True, methods=['put'], url_path='respond')
    def respond_to_friend_request(self, request, pk=None):
        friend_request = get_object_or_404(FriendRequest, id=pk)
        
        response_status = request.data.get('status')
        if response_status not in ['accepted', 'rejected']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        # TODO: A lot of this would be handled for free if we use the get_queryset function
        if friend_request.recipient_wholesaler:
            try:
                wholesaler_profile = request.user.wholesalerprofile
                if friend_request.recipient_wholesaler != wholesaler_profile:
                    return Response({'error': 'You can only respond to requests sent to you'}, status=status.HTTP_403_FORBIDDEN)
            except WholesalerProfile.DoesNotExist:
                return Response({'error': 'Only the recipient wholesaler can respond to this request'}, status=status.HTTP_403_FORBIDDEN)
        elif friend_request.dealership:
            try:
                dealer_profile = request.user.dealerprofile
                if dealer_profile.role != 'M':
                    return Response({'error': 'Only dealership managers can respond to this request'}, status=status.HTTP_403_FORBIDDEN)
                if friend_request.dealership not in dealer_profile.dealerships.all():
                    return Response({'error': 'Dealer does not belong to the specified dealership.'}, status=status.HTTP_403_FORBIDDEN)
            except DealerProfile.DoesNotExist:
                return Response({'error': 'Only a dealership manager can respond to this request'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
        
        friend_request.status = response_status
        friend_request.save()

        if response_status == 'accepted':
            if friend_request.recipient_wholesaler:
                # Update wholesaler friends list
                sender = friend_request.sender
                recipient = friend_request.recipient_wholesaler
                sender.friends.add(recipient)
                recipient.friends.add(sender)
                sender.save()
                recipient.save()
            elif friend_request.dealership:
                # Update the dealership's wholesalers list
                dealership = friend_request.dealership
                wholesaler_profile = friend_request.sender
                dealership.wholesalers.add(wholesaler_profile.user)
                dealership.save()

        serializer = self.get_serializer(friend_request)
        return Response(serializer.data)


    # TODO: Will get a lot for free with get_queryset - only stuff available to what you own
    @action(detail=False, methods=['get'], url_path='sent', permission_classes=[IsWholesaler])
    def list_sent_requests(self, request):
        queryset = self.get_queryset()
        
        if hasattr(request.user, 'wholesalerprofile'):
            sent_requests = queryset.filter(sender=request.user.wholesalerprofile)
        else:
            return Response({'error': 'User does not have a wholesaler profile.'}, status=status.HTTP_400_BAD_REQUEST)

        # Apply Pagination
        page = self.paginate_queryset(sent_requests)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sent_requests, many=True)
        return Response(serializer.data)


    @action(detail=False, methods=['get'], url_path='received', permission_classes=[IsWholesaler | IsManagement])
    def list_received_requests(self, request):
        user = request.user

        queryset = self.get_queryset()  # Use the optimized queryset from get_queryset

        if hasattr(user, 'dealerprofile'):
            # If the user is a dealer, handle dealership filtering
            dealer_profile = user.dealerprofile

            dealership_id = request.query_params.get('dealership')
            if not dealership_id:
                return Response({'error': 'Dealership ID must be provided.'}, status=status.HTTP_400_BAD_REQUEST)

            dealership = get_object_or_404(Dealership, id=dealership_id)
            if dealership not in dealer_profile.dealerships.all():
                return Response({'error': 'Dealer does not belong to the specified dealership.'}, status=status.HTTP_403_FORBIDDEN)

            # Filter requests related to the specified dealership
            received_requests = queryset.filter(dealership=dealership)

        elif hasattr(user, 'wholesalerprofile'):
            # If the user is a wholesaler, list all requests received by this wholesaler
            received_requests = queryset.filter(recipient_wholesaler=user.wholesalerprofile)

        else:
            return Response({'error': 'User must be a dealer or wholesaler.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Apply Pagination
        page = self.paginate_queryset(received_requests)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(received_requests, many=True)
        return Response(serializer.data)




