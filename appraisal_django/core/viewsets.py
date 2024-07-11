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



class DealershipViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing dealerships.
    """
    queryset = Dealership.objects.all()
    serializer_class = DealershipSerializer

    permission_classes_by_action = {
        'list': [permissions.AllowAny],
        'create': [permissions.AllowAny],
        'default': [permissions.IsAuthenticated],
    }

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes_by_action['default']]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Filter the queryset based on dealership_id
        dealership_id = request.query_params.get('dealership_id')
        if dealership_id:
            queryset = queryset.filter(id=dealership_id)

        # Filter the queryset based on role (if provided)
        role = request.query_params.get('role')
        if role and role in ['M', 'S']:
            queryset = queryset.filter(dealer_profiles__role=role)  # Use 'dealer_profiles__role' here

        # Serialize the queryset
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        return Response(data)


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


class WholesalerProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing wholesaler profiles.
    """
    queryset = WholesalerProfile.objects.all()
    serializer_class = WholesalerProfileSerializer
    permission_classes = [permissions.AllowAny] 


class AppraisalViewSet(viewsets.ModelViewSet):
    queryset = Appraisal.objects.all()
    serializer_class = AppraisalSerializer
    permission_classes = [permissions.IsAuthenticated, IsDealerFromSameDealership]

    def get_queryset(self):
        user_dealership_ids = self.request.user.dealerprofile.dealerships.values_list('id', flat=True)
        queryset = Appraisal.objects.filter(dealership_id__in=user_dealership_ids)

        # Debug statement
        print(f"Initial queryset for user {self.request.user.username}: {queryset}")

        dealership_id = self.request.query_params.get('dealership_id')
        if dealership_id:
            queryset = queryset.filter(dealership_id=dealership_id)
        
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(Q(initiating_dealer__user__id=user_id) | Q(last_updating_dealer__user__id=user_id))
        
        # Debug statement
        print(f"Filtered queryset for user {self.request.user.username}: {queryset}")
        
        return queryset

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
        appraisal = self.get_object() # Get the object from the queryset
        dealership_id = appraisal.dealership.id # Get the ID of the dealership associated with the object

        # Check permissions for management dealers
        self.check_object_permissions(request, appraisal) 

        print(f"Retrieving appraisal for user {request.user.username}") 

        serializer = self.get_serializer(appraisal) # Serialize 
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