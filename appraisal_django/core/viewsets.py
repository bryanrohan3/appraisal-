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
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import NotFound
from django.utils.dateparse import parse_date
from collections import Counter
from collections import defaultdict
from decimal import Decimal


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
        'dealers': DealerProfileSmallSerializer,
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

        queryset = DealerProfile.objects.filter(dealerships=dealership, is_active=True)
        filtered_queryset = self.filter_queryset(queryset)

        dealer_profile = request.user.dealerprofile  # Directly access the dealer profile
        if dealership not in dealer_profile.dealerships.all():
            return Response({'detail': 'Not authorized to view dealers of this dealership.'}, status=403)

        # Serialize the entire filtered queryset without pagination
        serializer = self.get_serializer(filtered_queryset, many=True)
        return Response(serializer.data)    


    @action(detail=True, methods=['PATCH'], url_path='deactivate', permission_classes=[IsManagement])
    def deactivate(self, request, pk=None):
        """
        Action to deactivate a dealership. Only Management Dealers from the specific dealership can perform this action.
        """
        dealership = self.get_object()
        
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset.filter(id=dealership.id).exists():
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
    
    @action(detail=False, methods=['get'], url_path='current', permission_classes=[permissions.IsAuthenticated])
    def current(self, request):
        """
        Retrieve the dealer profile of the currently authenticated user.
        """
        user = request.user
        if hasattr(user, 'dealerprofile'):
            serializer = self.get_serializer(user.dealerprofile)
            return Response(serializer.data)
        return Response({'detail': 'Dealer profile not found'}, status=status.HTTP_404_NOT_FOUND)
    

    @action(detail=True, methods=['PATCH'], permission_classes=[IsManagement], url_path='deactivate')
    def deactivate_dealer(self, request, pk=None):
        """
        Action to deactivate (soft delete) a dealer's profile and user.
        Only a Management Dealer can deactivate any dealer, including other Management Dealers,
        within the same dealership. Sales Dealers cannot deactivate their own account or any other account.
        """
        user = request.user

        if not hasattr(user, 'dealerprofile'):
            return Response({'error': 'User does not have a dealer profile'}, status=status.HTTP_403_FORBIDDEN)

        try:
            # Use get_queryset to filter the queryset based on the authenticated user's dealership
            queryset = self.get_queryset()
            # Filter by user ID instead of DealerProfile ID
            dealer_profile_to_deactivate = queryset.get(user_id=pk)  # Assuming pk is user_id

            # Deactivate the dealer profile
            dealer_profile_to_deactivate.is_active = False
            dealer_profile_to_deactivate.save()

            # Deactivate the associated user
            user_to_deactivate = dealer_profile_to_deactivate.user
            user_to_deactivate.is_active = False
            user_to_deactivate.save()

            return Response({'status': 'Dealer and user deactivated'}, status=status.HTTP_200_OK)
        except DealerProfile.DoesNotExist:
            return Response({'error': 'Dealer profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
    @action(detail=True, methods=['POST'], url_path='promote', permission_classes=[IsManagement])
    def promote_dealer(self, request, pk=None):
        """
        Action to promote a Sales Dealer to Management Dealer by a Management Dealer.
        """
        # Filter queryset to ensure the dealer is in the same dealership as the requesting user
        queryset = self.get_queryset()

        try:
            # Fetch dealer profile with the given user_id and ensure it is a Sales Dealer
            dealer_to_promote = queryset.get(user_id=pk, role='S')
        except DealerProfile.DoesNotExist:
            return Response({"error": "Dealer not found or not eligible for promotion"}, status=status.HTTP_404_NOT_FOUND)

        dealer_to_promote.role = 'M'
        dealer_to_promote.save()
        serializer = self.get_serializer(dealer_to_promote)
        return Response(serializer.data)
    

    @action(detail=True, methods=['POST'], url_path='demote', permission_classes=[IsManagement])
    def demote_dealer(self, request, pk=None):
        """
        Action to demote a Management Dealer to a Sales Dealer by another Management Dealer.
        """
        # Filter queryset to ensure the dealer is in the same dealership as the requesting user
        queryset = self.get_queryset()

        try:
            # Fetch dealer profile with the given user_id and ensure it is a Management Dealer
            dealer_to_demote = queryset.get(user_id=pk, role='M')
        except DealerProfile.DoesNotExist:
            return Response({"error": "Dealer not found or not eligible for demotion"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the dealer to demote is actually a Management Dealer
        if dealer_to_demote.role != 'M':
            return Response({"error": "Dealer is not a Management Dealer"}, status=status.HTTP_400_BAD_REQUEST)

        dealer_to_demote.role = 'S'
        dealer_to_demote.save()
        serializer = self.get_serializer(dealer_to_demote)
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

    def get_serializer_class(self):
        if self.action == 'simple_list':
            return SimpleAppraisalSerializer
        elif self.action == 'status_list':
            return AppraisalStatusSerializer
        return AppraisalSerializer


    @action(detail=False, methods=['get'], url_path='simple-list')
    def simple_list(self, request, *args, **kwargs):
        # Get the latest 8 appraisals
        queryset = self.filter_queryset(self.get_queryset()).order_by('-start_date')[:8]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='status-list')
    def status_list(self, request, *args, **kwargs):
        # Get 'from' and 'to' query parameters
        from_date = request.query_params.get('from', None)
        to_date = request.query_params.get('to', None)

        # Filter queryset based on date range if provided
        queryset = self.filter_queryset(self.get_queryset())

        if from_date and to_date:
            try:
                from_date = parse_datetime(from_date)
                to_date = parse_datetime(to_date)
                queryset = queryset.filter(start_date__range=(from_date, to_date))
            except ValueError:
                return Response({"detail": "Invalid date format. Use ISO 8601 format."}, status=status.HTTP_400_BAD_REQUEST)

        # Order by start_date or use any default ordering you need
        queryset = queryset.order_by('-start_date')

        # Serialize data
        serializer = self.get_serializer(queryset, many=True)
        
        # Extract status from the serialized data
        statuses = [item['status'] for item in serializer.data]
        
        # Count occurrences of each status
        status_counts = Counter(statuses)
        
        # Sort statuses by count (highest to lowest) and then by status name alphabetically
        sorted_statuses = sorted(status_counts.items(), key=lambda x: (-x[1], x[0]))
        
        # Convert to desired output format
        result = [{'status': status, 'count': count} for status, count in sorted_statuses]
        
        return Response(result)
    
    def get_queryset(self):
        user = self.request.user

        # TODO: Change for the offer one2one thing <<<<ASK ABOUT>>>>
        # if hasattr(user, 'wholesalerprofile'):
        #     invited_appraisal_ids = Offer.objects.filter(user=user.wholesalerprofile).values_list('appraisal_id', flat=True)
        #     queryset = Appraisal.objects.filter(id__in=invited_appraisal_ids)
        if hasattr(user, 'wholesalerprofile'):
        # Fetch appraisals that the wholesaler has made offers on
            queryset = Appraisal.objects.filter(offers__user=user.wholesalerprofile).distinct()

        elif hasattr(user, 'dealerprofile'):
            user_dealership_ids = user.dealerprofile.dealerships.values_list('id', flat=True)
            queryset = Appraisal.objects.filter(dealership_id__in=user_dealership_ids)

        else:
            queryset = Appraisal.object.none()

        queryset = self.filter_queryset(queryset)

        queryset = self.filter_queryset_by_keyword(queryset)

        return queryset
    
    
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


    def filter_queryset_by_keyword(self, queryset):
        filters = self.request.query_params.getlist('filter')  # Use getlist to get multiple filter values
        if filters:
            status_map = {
                'Trashed': 'Trashed',
                'Complete': 'Complete',
                'Active': 'Active',
                'Pending - Management': 'Pending - Management',
                'Pending - Sales': 'Pending - Sales',
                # Add more status mappings if needed
            }

            for keyword in filters:
                # Filter queryset based on the status keyword
                if keyword in status_map:
                    status = status_map[keyword]
                    queryset = queryset.filter(
                        Q(id__in=[appraisal.id for appraisal in queryset if appraisal.get_dealer_status() == status])
                    )
                else:
                    # Fallback to the existing keyword search if status does not match
                    queryset = queryset.filter(
                        Q(customer_email__icontains=keyword) |
                        Q(vehicle_make__icontains=keyword) |
                        Q(vehicle_model__icontains=keyword) |
                        Q(vehicle_year__icontains=keyword) |
                        Q(customer_last_name__icontains=keyword) |
                        Q(vehicle_vin__icontains=keyword) |
                        Q(customer_first_name__icontains=keyword) |
                        Q(vehicle_registration__icontains=keyword) |
                        Q(id__icontains=keyword)
                    )

        return queryset



    @action(detail=True, methods=['POST'], permission_classes=[IsDealer])
    def add_private_comment(self, request, pk=None):
        appraisal = self.get_object()
        user = request.user
        data = request.data
        data['appraisal'] = appraisal.id  # This associates the comment with the correct appraisal

        # Note: Ensure `user` is not part of the request payload as it's managed in the view
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

    @action(detail=True, methods=['POST'], permission_classes=[IsDealer])
    def add_general_comment(self, request, pk=None):
        appraisal = self.get_object()
        user = request.user
        data = request.data
        data['appraisal'] = appraisal.id  # This associates the comment with the correct appraisal

        # Make sure `user` is not in the payload data
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=user)  # Save the comment, setting user
            return Response({"message": "General comment added successfully."}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['get', 'post'], url_path='csv', permission_classes=[IsManagement])
    def download_csv(self, request, *args, **kwargs):
        if request.method == 'POST':
            # Handle CSV generation here
            start_date_str = request.query_params.get('start_date', None)
            end_date_str = request.query_params.get('end_date', None)
            
            # Convert strings to datetime objects if provided
            start_date = parse_datetime(start_date_str) if start_date_str else None
            end_date = parse_datetime(end_date_str) if end_date_str else None
            
            queryset = self.get_queryset()
            
            if start_date and end_date:
                queryset = queryset.filter(start_date__range=(start_date, end_date))
            
            queryset = self.filter_queryset_by_keyword(queryset)

            # Create a response object for CSV
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="appraisals.csv"'

            # Use pipe character as delimiter
            writer = csv.writer(response, delimiter=',')
            # Write headers
            writer.writerow(['ID', 'Start Date', 'Last Updated', 'Is Active', 'Dealership', 'Initiating Dealer',
                            'Last Updating Dealer', 'Customer First Name', 'Customer Last Name', 'Customer Email',
                            'Customer Phone', 'Make', 'Model', 'Year', 'VIN', 'Registration', 'Color',
                            'Odometer Reading', 'Engine Type', 'Transmission', 'Body Type', 'Fuel Type', 
                            'Reserve Price'])

            # Write data rows
            for appraisal in queryset:
                writer.writerow([
                    appraisal.id,
                    appraisal.start_date.isoformat() if appraisal.start_date else '',
                    appraisal.last_updated.isoformat() if appraisal.last_updated else '',
                    appraisal.is_active,
                    appraisal.dealership.dealership_name,
                    f"{appraisal.initiating_dealer.user.first_name} {appraisal.initiating_dealer.user.last_name}",
                    f"{appraisal.last_updating_dealer.user.first_name} {appraisal.last_updating_dealer.user.last_name}",
                    appraisal.customer_first_name,
                    appraisal.customer_last_name,
                    appraisal.customer_email,
                    appraisal.customer_phone,
                    appraisal.vehicle_make,
                    appraisal.vehicle_model,
                    appraisal.vehicle_year,
                    appraisal.vehicle_vin,
                    appraisal.vehicle_registration,
                    appraisal.color,
                    appraisal.odometer_reading,
                    appraisal.engine_type,
                    appraisal.transmission,
                    appraisal.body_type,
                    appraisal.fuel_type,
                    appraisal.reserve_price
                ])
            
            return response

        else:
            # Handle GET request (filtering and returning JSON)
            start_date_str = request.query_params.get('start_date', None)
            end_date_str = request.query_params.get('end_date', None)
            
            # Convert strings to datetime objects if provided
            start_date = parse_datetime(start_date_str) if start_date_str else None
            end_date = parse_datetime(end_date_str) if end_date_str else None
            
            queryset = self.get_queryset()
            
            if start_date and end_date:
                queryset = queryset.filter(start_date__range=(start_date, end_date))
            
            queryset = self.filter_queryset_by_keyword(queryset)

            # Paginate the queryset
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

    
    @action(detail=True, methods=['POST'], url_path='make-offer', permission_classes=[IsWholesaler])
    def make_offer(self, request, pk=None):
        appraisal = self.get_object()
        user = request.user
        wholesaler_profile = user.wholesalerprofile
        data = request.data
        amount = data.get('amount')

        # Use get_or_create to handle both existing and new offers
        try:
            offer, created = Offer.objects.get_or_create(
                appraisal=appraisal,
                user=wholesaler_profile,
                defaults={'amount': amount}
            )

            if not created:
                # Update the offer if it already exists
                offer.amount = amount
                offer.passed = False  # Reset passed status for existing offers
                offer.save()

            # Serialize and return the offer data
            serializer = OfferSerializer(offer)
            return Response(serializer.data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)
        
        except IntegrityError:
            # Handle potential integrity errors (e.g., duplicate entries)
            return Response({'error': 'An error occurred while processing the offer.'}, status=status.HTTP_400_BAD_REQUEST)

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
        

    @action(detail=True, methods=['get'], url_path='offers', permission_classes=[IsManagement])
    def list_offers(self, request, pk=None):
        appraisal = self.get_object()
        offers = Offer.objects.filter(
            Q(amount__isnull=False) | Q(passed=True),
            appraisal=appraisal  # This should be before keyword arguments if any.
        )

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
    

    @action(detail=True, methods=['post'], permission_classes=[IsManagement])
    def invite_wholesaler(self, request, pk=None):
        appraisal = self.get_object()
        user = request.user

        # Fetch the dealership associated with the appraisal
        dealership = appraisal.dealership

        serializer = WholesalerInviteSerializer(data=request.data, context={'appraisal': appraisal, 'dealership': dealership})
        if serializer.is_valid():
            invited_wholesalers = serializer.create_invites()
            return Response({"invited_wholesalers": invited_wholesalers}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # Pagination Applied => api/offers/list_invites/?page={}
    @action(detail=False, methods=['get'], url_path='list_invites', permission_classes=[permissions.IsAuthenticated])
    def list_invites(self, request):
        if not hasattr(request.user, 'wholesalerprofile'):
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        invites = Offer.objects.filter(user=request.user.wholesalerprofile)

        # Apply pagination
        page = self.paginate_queryset(invites)
        if page is not None:
            serializer = OfferSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)


        serializer = OfferSerializer(invites, many=True)
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
        # Get date_from and date_to from request query parameters
        date_from = request.query_params.get('from')
        date_to = request.query_params.get('to')

        # Parse dates if provided, otherwise set them to None
        date_from = parse_date(date_from) if date_from else None
        date_to = parse_date(date_to) if date_to else None

        user = request.user

        if hasattr(user, 'dealerprofile'):
            dealer_id = user.dealerprofile.id
            queryset = Appraisal.objects.filter(initiating_dealer_id=dealer_id)

            # Apply date range filter if both dates are provided
            if date_from and date_to:
                queryset = queryset.filter(start_date__range=[date_from, date_to])

            # Aggregate the counts of cars by make and model
            car_counts = (queryset
                        .values('vehicle_make', 'vehicle_model')
                        .annotate(count=Count('id'))
                        .order_by('-count'))
            
            # Paginate the results
            page = self.paginate_queryset(car_counts)
            if page is not None:
                return self.get_paginated_response(page)

            return Response({
                "car_counts": car_counts
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User does not have a valid dealer profile"}, status=status.HTTP_403_FORBIDDEN)

        
    @action(detail=False, methods=['get'], url_path='best-performing-wholesalers', permission_classes=[IsDealer])
    def best_performing_wholesalers(self, request, *args, **kwargs):
        # Get date_from and date_to from request query parameters
        date_from = request.query_params.get('from')
        date_to = request.query_params.get('to')

        # Parse dates if provided, otherwise set them to None
        date_from = parse_date(date_from) if date_from else None
        date_to = parse_date(date_to) if date_to else None

        user = request.user
        dealer_id = user.dealerprofile.id  # Assuming the permission class ensures that dealerprofile exists

        queryset = Appraisal.objects.filter(
            initiating_dealer_id=dealer_id
        ).select_related('winner')  # Optimize query to fetch related 'winner'

        # Apply date range filter if both dates are provided
        if date_from and date_to:
            queryset = queryset.filter(start_date__range=[date_from, date_to])

        # Count by winner's profile ID and get username
        top_wholesalers = (queryset
                        .values('winner__user_id', 'winner__user__wholesaler_name', 'winner__user__user__username')  # Access winner's profile ID and username
                        .annotate(count=Count('winner__user_id'))  # Count how many times each ID appears
                        .filter(winner__user_id__isnull=False)  # Exclude entries with null winner__user_id
                        .order_by('-count'))  # Order by count in descending order

        # Paginate the results
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(top_wholesalers, request)
        if page is not None:
            return paginator.get_paginated_response(page)

        return Response({
            "top_wholesalers": list(top_wholesalers)  # Convert queryset to list
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'], url_path='top-wholesaler')
    def top_wholesaler(self, request, *args, **kwargs):
        user = request.user

        if hasattr(user, 'dealerprofile'):
            dealer_id = user.dealerprofile.id
            queryset = Appraisal.objects.filter(
                initiating_dealer_id=dealer_id
            ).select_related('winner')  # Optimize query to fetch related 'winner'

            # Count by winner's profile ID and get username
            top_wholesaler = (queryset
                            .values('winner__user_id', 'winner__user__wholesaler_name')  # Access winner's profile ID and username
                            .annotate(count=Count('winner__user_id'))  # Count how many times each ID appears
                            .order_by('-count')
                            .first())  # Get only the top result

            if top_wholesaler:
                return Response({
                    "top_wholesaler": top_wholesaler
                }, status=status.HTTP_200_OK)
            else:
                return Response({"message": "No appraisals found for the specified dealer."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "User does not have a valid dealer profile"}, status=status.HTTP_403_FORBIDDEN)
        
    @action(detail=False, methods=['get'], url_path='top-car')
    def top_car(self, request, *args, **kwargs):
        user = request.user

        if hasattr(user, 'dealerprofile'):
            dealer_id = user.dealerprofile.id
            # Fetch the most common car across all appraisals
            queryset = Appraisal.objects.filter(initiating_dealer_id=dealer_id)
            
            car_counts = (queryset
                        .values('vehicle_make', 'vehicle_model')
                        .annotate(count=Count('id'))
                        .order_by('-count'))

            if car_counts:
                most_common_car = car_counts[0]  # Get the most common car
                return Response({
                    "vehicle_make": most_common_car['vehicle_make'],
                    "vehicle_model": most_common_car['vehicle_model'],
                    "count": most_common_car['count']
                }, status=status.HTTP_200_OK)
            else:
                return Response({"message": "No car data available"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "User does not have a valid dealer profile"}, status=status.HTTP_403_FORBIDDEN)
        
    @action(detail=False, methods=['get'], url_path='count')
    def count_appraisals(self, request, *args, **kwargs):
        # Extract query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Parse dates if provided
        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)

        # Filter queryset based on provided dates
        queryset = self.get_queryset()
        if start_date and end_date:
            queryset = queryset.filter(start_date__gte=start_date, start_date__lte=end_date)
        elif start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        elif end_date:
            queryset = queryset.filter(start_date__lte=end_date)

        # Count the number of filtered appraisals
        appraisal_count = queryset.count()

        return Response({"count": appraisal_count}, status=status.HTTP_200_OK)
    
    
    @action(detail=False, methods=['get'], url_path='profit-loss')
    def profit_loss(self, request, *args, **kwargs):
        # Get 'from' and 'to' query parameters
        from_date_str = request.query_params.get('from', None)
        to_date_str = request.query_params.get('to', None)

        # Convert query parameters to datetime objects
        try:
            from_date = parse_datetime(from_date_str) if from_date_str else None
            to_date = parse_datetime(to_date_str) if to_date_str else None
        except ValueError:
            return Response({"detail": "Invalid date format. Use ISO 8601 format."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate date range
        if from_date and to_date and from_date > to_date:
            return Response({"detail": "The 'from' date cannot be after the 'to' date."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the queryset
        queryset = self.filter_queryset(self.get_queryset())

        # Apply date range filters if provided
        if from_date and to_date:
            queryset = queryset.filter(start_date__range=(from_date, to_date))
        elif from_date:
            queryset = queryset.filter(start_date__gte=from_date)
        elif to_date:
            queryset = queryset.filter(start_date__lte=to_date)

        # Aggregate profit/loss by day
        daily_profit = defaultdict(Decimal)
        total_profit_or_loss = Decimal('0.0')

        for appraisal in queryset:
            if appraisal.winner:
                profit_loss = Decimal(appraisal.winner.amount) - Decimal(appraisal.reserve_price)
                total_profit_or_loss += profit_loss
                day = appraisal.start_date.strftime('%Y-%m-%d')  # Format date as 'YYYY-MM-DD'
                daily_profit[day] += profit_loss

        # Prepare the final response
        response_data = {
            'total_profit_or_loss': float(total_profit_or_loss),
            'daily_profit': [{'date': day, 'profit_or_loss': float(profit)} for day, profit in sorted(daily_profit.items())]
        }

        return Response(response_data, status=status.HTTP_200_OK)

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


    @action(detail=True, methods=['put'], url_path='respond')
    def respond_to_friend_request(self, request, pk=None):
        friend_request = get_object_or_404(self.get_queryset(), id=pk)

        response_status = request.data.get('status')
        if response_status not in ['accepted', 'rejected']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        if hasattr(request.user, 'wholesalerprofile'):
            # Check if the friend request is for this wholesaler
            if friend_request.recipient_wholesaler != request.user.wholesalerprofile:
                return Response({'error': 'You can only respond to requests sent to you'}, status=status.HTTP_403_FORBIDDEN)
        elif hasattr(request.user, 'dealerprofile'):
            # Check if the friend request is related to the dealer's dealership
            if friend_request.dealership not in request.user.dealerprofile.dealerships.all():
                return Response({'error': 'Dealer does not belong to the specified dealership.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

        # Update friend request status
        friend_request.status = response_status
        friend_request.save()

        # Handle acceptance logic
        if response_status == 'accepted':
            if hasattr(request.user, 'wholesalerprofile'):
                pass
            elif hasattr(request.user, 'dealerprofile'):
                # For dealers, update the dealership's wholesalers list
                dealership = friend_request.dealership
                wholesaler_profile = friend_request.sender
                dealership.wholesalers.add(wholesaler_profile.user)
                dealership.save()

        serializer = self.get_serializer(friend_request)
        return Response(serializer.data)



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


class OfferViewSet(viewsets.GenericViewSet, viewsets.mixins.RetrieveModelMixin):
    serializer_class = OfferSerializer
    permission_classes = [IsWholesaler | IsManagement]


    def get_queryset(self):
        user = self.request.user

        if hasattr(user, 'wholesalerprofile'):
            wholesalerprofile = user.wholesalerprofile
            # If the user has a wholesaler profile, filter offers by the user's instance
            return Offer.objects.filter(user=wholesalerprofile.id)

        if hasattr(user, 'dealerprofile'):
            # If the user has a dealer profile, filter offers by dealerships related to appraisals created
            dealerships = user.dealerprofile.dealerships.all()
            return Offer.objects.filter(appraisal__dealership__in=dealerships)

        # Default: return no offers if the user does not match any role
        return Offer.objects.none()

    def filter_queryset(self, queryset):
        user = self.request.user

        if hasattr(user, 'wholesalerprofile'):
            # Filter offers by the wholesaler's user instance
            wholesalerprofile = user.wholesalerprofile
            return queryset.filter(user=wholesalerprofile)

        if hasattr(user, 'dealerprofile'):
            # Filter offers by appraisals created by the management dealer's dealerships
            dealerships = user.dealerprofile.dealerships.all()
            return queryset.filter(appraisal__dealership__in=dealerships)

        # Default: return no offers if the user does not match any role
        return queryset.none()
    
    @action(detail=True, methods=['POST'], url_path='make-winner', permission_classes=[IsManagement])
    def make_winner(self, request, pk=None):
        offer = self.get_object()
        appraisal = offer.appraisal

        user = request.user
        if hasattr(user, 'dealerprofile'):
            dealerships = user.dealerprofile.dealerships.all()
            if appraisal.dealership not in dealerships:
                return Response({"detail": "You do not have permission to select a winner for this appraisal."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"detail": "You do not have permission to select a winner for this appraisal."}, status=status.HTTP_403_FORBIDDEN)

        appraisal.winner = offer
        appraisal.save()

        return Response({"message": "Winning offer selected successfully"}, status=status.HTTP_200_OK)