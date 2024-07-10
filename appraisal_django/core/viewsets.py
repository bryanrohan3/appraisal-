from rest_framework import viewsets, permissions, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from .models import *
from .serializers import *
from .permissions import IsManagementDealerOrReadOnly, CanManageDealerships, SalesDealerPermission


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
        """
        Retrieve a list of dealerships.
        """
        queryset = self.get_queryset()

        # Filter the queryset to include only the requested dealership_id
        dealership_id = request.query_params.get('dealership_id')
        if dealership_id:
            queryset = queryset.filter(id=dealership_id)

        # Serialize the queryset
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        # Add sales_dealers to the response if dealership_id is provided
        if dealership_id:
            dealership = queryset.first()  # Assuming only one dealership will match the ID
            sales_dealers = DealerProfile.objects.filter(dealerships=dealership_id, role='S')
            data[0]['sales_dealers'] = DealerProfileSerializer(sales_dealers, many=True).data

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
        'create': [IsManagementDealerOrReadOnly],
        'default': [permissions.IsAuthenticatedOrReadOnly],
    }

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes_by_action['default']]

    def create(self, request, *args, **kwargs):
        role = request.data.get('role')
        if role == 'M':
            # Allow creation of Management Dealer without authentication
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif role == 'S':
            # Ensure that only Management Dealers can create Sales Dealers
            user = request.user
            dealership_ids = [int(id) for id in request.data.get('dealerships', [])]
            managed_dealerships = user.managed_dealerships.values_list('id', flat=True)
            
            for dealership_id in dealership_ids:
                if dealership_id not in managed_dealerships:
                    return Response({"error": "You do not have permission to associate sales dealers with this dealership."},
                                    status=status.HTTP_403_FORBIDDEN)
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Require authentication for other roles
            if not request.user.is_authenticated:
                return Response({"error": "Authentication required to create this user."}, status=status.HTTP_403_FORBIDDEN)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


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
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Ensure that only management dealers of the associated dealership can be in sent_to_management
        sent_to_management_ids = request.data.get('sent_to_management', [])

        # Perform any validation if needed

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    # list appraisals by dealership id
    def list(self, request, *args, **kwargs):
        dealership_id = request.query_params.get('dealership_id')
        if not dealership_id:
            return Response({'error': 'Dealership ID parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            dealership = Dealership.objects.get(id=dealership_id)
            appraisals = Appraisal.objects.filter(dealership=dealership)
            serializer = self.get_serializer(appraisals, many=True)
            return Response(serializer.data)
        except Dealership.DoesNotExist:
            return Response({'error': 'Dealership not found'}, status=status.HTTP_404_NOT_FOUND)
        
    def retrieve(self, request, *args, **kwargs):
        try:
            appraisal = self.get_object()
            serializer = self.get_serializer(appraisal)
            return Response(serializer.data)
        except Appraisal.DoesNotExist:
            return Response({'error': 'Appraisal not found'}, status=status.HTTP_404_NOT_FOUND)