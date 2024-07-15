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


class DealershipViewSet(viewsets.ModelViewSet):
    queryset = Dealership.objects.all()
    serializer_class = DealershipSerializer

    permission_classes_by_action = {
        'list': [permissions.AllowAny],
        'create': [permissions.AllowAny],
        'update': [IsManagementDealerFromSameDealership],  # Adding 'update'
        'partial_update': [IsManagementDealerFromSameDealership],
        'default': [permissions.IsAuthenticated],
        'dealers': [IsManagementDealerFromSameDealership],
    }

    def get_permissions(self):
        print(f"Action: {self.action}")  # Debug: print the action name
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes_by_action['default']]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        dealership_id = request.query_params.get('dealership_id')
        if dealership_id:
            queryset = queryset.filter(id=dealership_id)

        role = request.query_params.get('role')
        if role and role in ['M', 'S']:
            queryset = queryset.filter(dealer_profiles__role=role)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        return Response(data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsManagementDealerFromSameDealership])
    def dealers(self, request, pk=None):
        dealership = self.get_object()
        
        try:
            dealer_profile = DealerProfile.objects.get(user=request.user)
            if dealer_profile.role != 'M' or dealership not in dealer_profile.dealerships.all():
                return Response({'detail': 'Not authorized to view dealers of this dealership.'}, status=403)
        except DealerProfile.DoesNotExist:
            return Response({'detail': 'Not authorized to view dealers of this dealership.'}, status=403)

        dealers = DealerProfile.objects.filter(dealerships=dealership)
        serializer = DealerProfileSerializer(dealers, many=True)
        return Response(serializer.data)
    
    

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

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance:
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

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

    permission_classes_by_action = {
        'create': [permissions.IsAuthenticated, IsManagementDealerOrReadOnly],
        'default': [permissions.IsAuthenticatedOrReadOnly],
        'promote': [permissions.IsAuthenticated, IsDealerFromSameDealership],
    }

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes_by_action['default']]
    
    def list(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        if user_id:
            queryset = DealerProfile.objects.filter(user__id=user_id)
        else:
            queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def current_user_profile(self, request):
        """
        Retrieve the profile of the current authenticated user.
        """
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'User ID parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            dealer_profile = DealerProfile.objects.get(user_id=user_id)
            serializer = self.get_serializer(dealer_profile)
            return Response(serializer.data)
        except DealerProfile.DoesNotExist:
            return Response({'error': 'Dealer Profile not found for the given user ID'}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=False, methods=['POST'], url_path='(?P<user_id>[^/.]+)/promote')
    def promote_dealer(self, request, user_id=None):
        try:
            # Fetch the management dealer (requesting user)
            management_dealer = self.request.user.dealerprofile  # Assuming 'dealerprofile' is the related name

            # Fetch the dealer to promote
            dealer_to_promote = DealerProfile.objects.get(user_id=user_id, dealerships=management_dealer.dealerships.first(), role='S')
        except DealerProfile.DoesNotExist:
            return Response({'error': 'Dealer not found or not promotable'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the requesting user is a management dealer
        if management_dealer.role != 'M':
            return Response({'error': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
        
        # Perform promotion action here
        dealer_to_promote.role = 'M'
        dealer_to_promote.save()

        serializer = self.get_serializer(dealer_to_promote)
        return Response(serializer.data)

class WholesalerProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing wholesaler profiles.
    """
    queryset = WholesalerProfile.objects.all()
    serializer_class = WholesalerProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsWholesalerOwnerOrReadOnly]

    def perform_create(self, serializer):
        # Automatically set the current user as the owner of the profile
        serializer.save(user=self.request.user)

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

class AppraisalViewSet(viewsets.ModelViewSet):
    queryset = Appraisal.objects.all()
    serializer_class = AppraisalSerializer
    # permission_classes = [permissions.IsAuthenticated, IsDealerFromSameDealership]

    permission_classes_by_action = {
        'create': [permissions.IsAuthenticated, IsDealerFromSameDealership],
        'update': [permissions.IsAuthenticated, IsDealerFromSameDealership, IsManagementDealerOrReadOnly],
        'partial_update': [permissions.IsAuthenticated, IsDealerFromSameDealership, IsManagementDealerOrReadOnly],
        'retrieve': [permissions.IsAuthenticated, IsDealerFromSameDealership],
        'list': [permissions.IsAuthenticated],
        'list_offers': [permissions.IsAuthenticated, CanViewOffers],
        'make_offer': [permissions.IsAuthenticated, CanMakeOffer],
    }

    def get_serializer_class(self):
        if self.action == 'list_offers' and self.request.user.dealerprofile.role == 'S':
            return SalesSerializer
        return AppraisalSerializer

    def get_queryset(self):
        # Check if the user is a wholesaler
        if hasattr(self.request.user, 'wholesalerprofile'):
            return Appraisal.objects.all()

        # If the user is a dealer, filter by dealerships
        if hasattr(self.request.user, 'dealerprofile'):
            user_dealership_ids = self.request.user.dealerprofile.dealerships.values_list('id', flat=True)
            # Debug statement
            print(f"User {self.request.user.username} belongs to dealerships: {list(user_dealership_ids)}")
            queryset = Appraisal.objects.filter(dealership_id__in=user_dealership_ids)
            # Debug statement
            print(f"Initial queryset for user {self.request.user.username}: {queryset}")
            # Additional filters based on query params
            dealership_id = self.request.query_params.get('dealership_id')
            if dealership_id:
                queryset = queryset.filter(dealership_id=dealership_id)
            user_id = self.request.query_params.get('user_id')
            if user_id:
                queryset = queryset.filter(Q(initiating_dealer__user__id=user_id) | Q(last_updating_dealer__user__id=user_id))
            # Debug statement
            print(f"Filtered queryset for user {self.request.user.username}: {queryset}")
            return queryset
        
        return Appraisal.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        dealer_profile = DealerProfile.objects.get(user=user)
        if not dealer_profile.dealerships.exists():
            return Response({"detail": "You are not associated with any dealership."}, status=status.HTTP_400_BAD_REQUEST)
        
        dealership = dealer_profile.dealerships.first()
        validated_data = serializer.validated_data
        validated_data['initiating_dealer'] = dealer_profile
        validated_data['dealership'] = dealership
        validated_data['last_updating_dealer'] = dealer_profile

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        keyword = request.query_params.get('filter')
        if keyword:
            queryset = self.filter_queryset_by_keyword(queryset, keyword)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        appraisal = self.get_object()  # Get the object from the queryset
        dealership_id = appraisal.dealership.id  # Get the ID of the dealership associated with the object

        # Check permissions for management dealers
        self.check_object_permissions(request, appraisal) 

        # Debug statement
        print(f"Retrieving appraisal for user {request.user.username}") 

        serializer = self.get_serializer(appraisal)  # Serialize 
        return Response(serializer.data) 

    def update(self, request, *args, **kwargs):
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

    def partial_update(self, request, *args, **kwargs):
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
    
    @action(detail=True, methods=['POST'])
    def add_private_comment(self, request, pk=None):
        appraisal = self.get_object()
        user = request.user
        data = request.data

        if 'comment' not in data:
            return Response({"error": "Comment data not provided"}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(user=user, comment=data['comment'])
        appraisal.private_comments.add(comment)

        return Response({"message": "Private comment added successfully."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST'])
    def add_general_comment(self, request, pk=None):
        appraisal = self.get_object()
        user = request.user
        data = request.data

        if 'comment' not in data:
            return Response({"error": "Comment data not provided"}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(user=user, comment=data['comment'])
        appraisal.general_comments.add(comment)

        return Response({"message": "General comment added successfully."}, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], url_path='csv')
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
    
    @action(detail=True, methods=['POST'], url_path='make_offer')
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
        
    @action(detail=True, methods=['get'], url_path='offers', permission_classes=[permissions.IsAuthenticated, CanViewOffers])
    def list_offers(self, request, pk=None):
        appraisal = self.get_object()
        offers = Offer.objects.filter(appraisal=appraisal)
        serializer = OfferSerializer(offers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
