from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import *
from datetime import timezone, datetime
from django.db import transaction
from django.db.models import Q


class UserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'token', 'is_active', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        # Token.objects.create(user=user)
        return user
    
    def get_role(self, user):
        if hasattr(user, 'dealerprofile'):
            return 'dealer'
        elif hasattr(user, 'wholesalerprofile'):
            return 'wholesaler'
        return 'unknown'

    def get_token(self, obj):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key
    
    def get_dealer_profile(self, user):
        try:
            return DealerProfileSerializer(user.dealerprofile).data
        except DealerProfile.DoesNotExist:
            return None
    
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class DealershipSerializer(serializers.ModelSerializer):
    dealers = serializers.SerializerMethodField()

    class Meta:
        model = Dealership
        fields = ['id', 'dealership_name', 'street_address', 'suburb', 'state', 'postcode', 'email', 'phone', 'wholesalers', 'is_active' ,'dealers']

    def get_dealers(self, obj):
        # TODO: Querying should be done in the viewset
        # Only pass the filtered queryset to the serializer
        role = self.context['request'].query_params.get('role')
        
        if role and role in ['M', 'S']:
            dealers = DealerProfile.objects.filter(dealerships=obj, role=role)
        else:
            dealers = DealerProfile.objects.filter(dealerships=obj)
        
        return DealerProfileSerializer(dealers, many=True).data
    

class DealershipBasicSerializer(serializers.ModelSerializer):
    '''
    Basic serializer for Dealership. Used for Searching for Dealerships.
    '''
    class Meta:
        model = Dealership
        fields = ['id', 'dealership_name', 'phone', 'email']


class DealershipSearchSerializer(serializers.Serializer):
    dealership_name = serializers.CharField(required=False, allow_blank=True)

class DealershipNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dealership
        fields = ['id', 'dealership_name']


class DealershipCurrentUserFKSerializer(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        user = request.user
        return user.dealerprofile.dealerships.all()
    
    def to_internal_value(self, data):
        queryset = self.get_queryset()
        if not queryset.filter(id=data).exists():
            raise serializers.ValidationError("You are not associated with this dealership.")
        return super().to_internal_value(data)

class DealerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for DealerProfile model.
    """
    user = UserSerializer()
    dealerships = DealershipCurrentUserFKSerializer(many=True, required=False)
    dealership_names = serializers.SerializerMethodField()  # Use SerializerMethodField here
    received_requests = serializers.SerializerMethodField()
    sent_requests = serializers.SerializerMethodField()

    class Meta:
        model = DealerProfile
        fields = ['id', 'user', 'phone', 'role', 'dealerships', 'dealership_names', 'received_requests', 'sent_requests']

    def get_dealership_names(self, instance):
        # Retrieve the dealerships associated with the profile
        return DealershipNestedSerializer(instance.dealerships.all(), many=True).data

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication credentials were not provided.")

        # Ensure the creator is a Management Dealer
        creator_profile = DealerProfile.objects.get(user=request.user)
        if creator_profile.role != 'M':
            raise serializers.ValidationError("Only Management Dealers can create new users.")

        # Extract user and dealership data
        user_data = validated_data.pop('user')
        dealership_data = validated_data.pop('dealerships', [])

        user = UserSerializer().create(user_data)
        dealer_profile = DealerProfile.objects.create(user=user, **validated_data)
        dealer_profile.dealerships.set(dealership_data)
        
        return dealer_profile
        

    # TODO: I would seperate this serializer into "DealerUpdateSerializer"
    # Consists of UserUpdateSerializer -> UserSerialzer
    # And DealerUpdateSerializer
    # DealerSerializer -> Model Serializer -> Phone + Role fields
    def update(self, instance, validated_data):
        # Check if 'user' is in the validated data
        user_data = validated_data.pop('user', None)
        dealerships_data = validated_data.pop('dealerships', instance.dealerships.all())

        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()

        # Update other fields
        instance.phone = validated_data.get('phone', instance.phone)
        instance.role = validated_data.get('role', instance.role)
        instance.save()

        instance.dealerships.set(dealerships_data)
        
        return instance

    def get_received_requests(self, instance):
        # Adjusted logic to get received requests for the dealer's dealerships
        received_requests = FriendRequest.objects.filter(dealership__in=instance.dealerships.all())
        return FriendRequestSerializer(received_requests, many=True).data

    def get_sent_requests(self, instance):
        # Check if the user has a wholesaler profile before accessing it
        if hasattr(instance.user, 'wholesalerprofile'):
            sent_requests = FriendRequest.objects.filter(sender=instance.user.wholesalerprofile)
            return FriendRequestSerializer(sent_requests, many=True).data
        return []

class DealerProfileSmallSerializer(serializers.ModelSerializer):
    """
    Serializer for a simplified version of DealerProfile model with selected fields.
    """
    user = UserSerializer()
    dealerships = DealershipCurrentUserFKSerializer(many=True, required=False)
    dealership_names = serializers.SerializerMethodField()

    class Meta:
        model = DealerProfile
        fields = ['user', 'phone', 'role', 'dealerships', 'dealership_names']

    def get_dealership_names(self, instance):
        # Retrieve and serialize the names of the associated dealerships
        return [dealership.dealership_name for dealership in instance.dealerships.all()]

class DealerProfileNestedSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = DealerProfile
        fields = ['id', 'first_name', 'last_name']


class UserProfileNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username']


class WholesalerInviteSerializer(serializers.Serializer):
    wholesalers = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True
    )

    def validate_wholesalers(self, value):
        if not value:
            raise serializers.ValidationError("No wholesalers provided")
        return value

    def validate(self, data):
        dealership = self.context['dealership']
        wholesaler_ids = data['wholesalers']

        # Check if all provided wholesaler IDs are associated with the dealership
        dealership_wholesaler_ids = dealership.wholesalers.values_list('id', flat=True)
        for wholesaler_id in wholesaler_ids:
            if wholesaler_id not in dealership_wholesaler_ids:
                raise serializers.ValidationError(f"Wholesaler {wholesaler_id} is not associated with the dealership")
        return data

    def create_invites(self):
        data = self.validated_data
        dealership = self.context['dealership']
        wholesaler_ids = data['wholesalers']

        invited_wholesalers = []
        for wholesaler_id in wholesaler_ids:
            try:
                wholesaler = WholesalerProfile.objects.get(id=wholesaler_id)
                # Create or get the invite
                offer, created = Offer.objects.get_or_create(
                    appraisal=self.context['appraisal'],
                    user=wholesaler,
                    defaults={'passed': False, 'amount': None}
                )
                invited_wholesalers.append(wholesaler_id)
            except WholesalerProfile.DoesNotExist:
                continue  # Skip wholesaler ID if it does not exist
        
        return invited_wholesalers


class WholesalerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    friends = serializers.SerializerMethodField()

    class Meta:
        model = WholesalerProfile
        fields = ['user', 'wholesaler_name', 'street_address', 'suburb', 'state', 'postcode', 'email', 'phone', 'friends', 'is_active']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        wholesaler_profile = WholesalerProfile.objects.create(user=user, **validated_data)
        return wholesaler_profile
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
            # Just use is_valid(raise_exception=True)
            if user_serializer.is_valid():
                user_serializer.save()
            else:
                raise serializers.ValidationError(user_serializer.errors)

        # Update the wholesaler profile fields
        return super().update(instance, validated_data)
    
    def get_friends(self, obj):
        # Get accepted friend requests where the wholesaler is either the sender or the recipient
        accepted_friend_requests = FriendRequest.objects.filter(
            (Q(sender=obj) | Q(recipient_wholesaler=obj)) &
            Q(status='accepted')
        ).select_related('sender', 'recipient_wholesaler')

        # Extract the IDs of the accepted friends
        friend_ids = set()
        for request in accepted_friend_requests:
            if request.sender and request.sender != obj:
                friend_ids.add(request.sender.id)
            if request.recipient_wholesaler and request.recipient_wholesaler != obj:
                friend_ids.add(request.recipient_wholesaler.id)

        # Convert set to list
        friend_ids = list(friend_ids)
        
        return friend_ids
    

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'image', 'appraisal'] 
    
class CommentSerializer(serializers.ModelSerializer):
    user = UserProfileNestedSerializer(read_only=True)  # Ensure user is read-only
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'appraisal', 'comment', 'comment_date_time', 'is_private']
        extra_kwargs = {
            'user': {'read_only': True},  # Mark user as read-only
            'appraisal': {'write_only': True}  # Include appraisal in input but exclude from output
        }


class OfferSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = ['id', 'user', 'amount', 'adjusted_amount', 'passed', 'created_at', 'offer_made_at']
        read_only_fields = ['user', 'adjusted_amount', 'offer_created_at']

    def get_user(self, obj):
        user = obj.user
        return {
            'username': user.user.username,  # Assuming `user` is related to a `User` model with `username`
            'first_name': user.user.first_name,
            'last_name': user.user.last_name
        }


    def get_winner(self, obj):
        return obj.appraisal.winner == obj

    # TODO: This can be done in the viewset
    def validate(self, attrs):
        user = self.context['request'].user
        if not hasattr(user, 'wholesalerprofile'):
            raise serializers.ValidationError("Only wholesalers can make an offer.")
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
    

class InviteSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    
    class Meta:
        model = Offer
        fields = ['id', 'appraisal', 'username', 'created_at']
        
    def get_username(self, obj):
        return obj.user.user.username  

class AdjustedAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ['adjusted_amount']


class DamageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Damage
        fields = ('id', 'location', 'appraisal', 'description', 'repair_cost_estimate', 'image')
        extra_kwargs = {
            'appraisal': {'read_only': True}  # Ensure 'appraisal' is read-only during creation
        }

    

class AppraisalSerializer(serializers.ModelSerializer):
    initiating_dealer = DealerProfileNestedSerializer(read_only=True)
    last_updating_dealer = DealerProfileNestedSerializer(read_only=True)
    dealership = DealershipCurrentUserFKSerializer()  
    damages = DamageSerializer(many=True)
    vehicle_photos = PhotoSerializer(many=True, read_only=True, source='vehicle_photos_set')
    general_comments = serializers.SerializerMethodField()
    private_comments = serializers.SerializerMethodField()
    winner = serializers.SerializerMethodField()
    offers = serializers.SerializerMethodField()
    invites = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField() 

    class Meta:
        model = Appraisal
        fields = [
            'id', 'start_date', 'last_updated', 'is_active', 'ready_for_management', 'dealership', 
            'initiating_dealer', 'last_updating_dealer', 'customer_first_name', 'customer_last_name', 
            'customer_email', 'customer_phone', 'vehicle_make', 'vehicle_model', 'vehicle_year', 
            'vehicle_vin', 'vehicle_registration', 'color', 'odometer_reading', 'engine_type', 
            'transmission', 'body_type', 'fuel_type', 'reserve_price', 'damages', 'vehicle_photos',
            'private_comments', 'general_comments', 'winner', 'status', 'offers', 'invites',
        ]

    def get_winner(self, obj):
        # Check if the winner field is not None
        if obj.winner:
            winner_offer = obj.winner  # Directly access the Offer instance
            return {
                'amount': winner_offer.amount,
                'offer_id': winner_offer.id,
                'username': winner_offer.user.user.username,
                'id': winner_offer.user.id
            }
        return None
    
    def get_general_comments(self, obj):
        comments = obj.comments.filter(is_private=False)
        return CommentSerializer(comments, many=True).data

    def get_private_comments(self, obj):
        comments = obj.comments.filter(is_private=True)
        return CommentSerializer(comments, many=True).data

    def get_status(self, obj):
        request = self.context.get('request')
        user = request.user if request else None

        if hasattr(user, 'dealerprofile'):
            return obj.get_dealer_status()
        elif hasattr(user, 'wholesalerprofile'):
            return obj.get_wholesaler_status(user.wholesalerprofile)
        return "Not authorized"
    
    def get_offers(self, obj):
        offers = obj.offers.filter(
            Q(amount__isnull=False) | Q(passed=True)
        )
        return OfferSerializer(offers, many=True).data
    
    def get_invites(self, obj):
        invites = obj.offers.filter(amount__isnull=True, passed=False)
        return InviteSerializer(invites, many=True).data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        user = request.user

        # Include detailed dealership information
        dealership = instance.dealership
        if dealership:
            dealership_serializer = DealershipNestedSerializer(dealership)
            representation['dealership'] = dealership_serializer.data

        # Exclude fields based on user role
        if hasattr(user, 'dealerprofile') and user.dealerprofile.role == 'S':
            # Exclude fields for Sales Dealers
            representation.pop('offers', None)
            representation.pop('invites', None)

        if hasattr(user, 'wholesalerprofile'):
            representation.pop('offers', None)
            representation.pop('invites', None)
            representation.pop('private_comments', None)
            representation.pop('reserve_price', None)
            representation.pop('winner', None)

        return representation
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        dealer_profile = user.dealerprofile
        
        # Validate if the dealer works for the given dealership
        dealership = validated_data.get('dealership')
        if dealership and not dealer_profile.dealerships.filter(id=dealership.id).exists():
            raise serializers.ValidationError("You are not associated with this dealership.")
        
        validated_data['initiating_dealer'] = dealer_profile
        validated_data['last_updating_dealer'] = dealer_profile
        damages_data = validated_data.pop('damages', [])

        # Create the Appraisal
        appraisal = Appraisal.objects.create(**validated_data)

        if damages_data:
            for damage_data in damages_data:
                Damage.objects.create(appraisal=appraisal, **damage_data)

        return appraisal

    def update(self, instance, validated_data):
        # Handle updating of nested fields
        damages_data = validated_data.pop('damages', [])
        instance = super().update(instance, validated_data)

        # Update damages
        for damage_data in damages_data:
            damage_id = damage_data.get('id', None)
            if damage_id:
                # Update existing damage
                Damage.objects.filter(id=damage_id).update(**damage_data)
            else:
                # Create new damage
                Damage.objects.create(appraisal=instance, **damage_data)

        return instance

class SimpleAppraisalSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Appraisal
        fields = [
            'id', 'customer_first_name', 'customer_last_name', 'start_date',
            'vehicle_make', 'vehicle_model', 'status', 
            'vehicle_vin', 'vehicle_registration'
        ]

    def get_status(self, obj):
        request = self.context.get('request')
        user = request.user if request else None

        if hasattr(user, 'dealerprofile'):
            return obj.get_dealer_status()
        elif hasattr(user, 'wholesalerprofile'):
            return obj.get_wholesaler_status(user.wholesalerprofile)
        return "Not authorized"
    

class AppraisalStatusSerializer(serializers.Serializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Appraisal
        fields = ['status', 'start_date']

    def get_status(self, obj):
        request = self.context.get('request')
        user = request.user if request else None

        if hasattr(user, 'dealerprofile'):
            return obj.get_dealer_status()
        elif hasattr(user, 'wholesalerprofile'):
            return obj.get_wholesaler_status(user.wholesalerprofile)
        return "Not authorized"


class SelectWinnerSerializer(serializers.Serializer):
    offer_id = serializers.IntegerField()


class FriendRequestSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.user.username')
    dealership = serializers.PrimaryKeyRelatedField(queryset=Dealership.objects.all(), required=False)
    recipient_wholesaler = serializers.PrimaryKeyRelatedField(queryset=WholesalerProfile.objects.all(), required=False)

    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'dealership', 'recipient_wholesaler', 'status', 'created_at']
        read_only_fields = ['sender', 'status', 'created_at']

    def validate(self, data):
        # Ensure either recipient wholesaler or dealership is specified
        if not data.get('recipient_wholesaler') and not data.get('dealership'):
            raise serializers.ValidationError("Either recipient wholesaler or dealership must be specified.")

        # Ensure both fields are not specified simultaneously
        if data.get('recipient_wholesaler') and data.get('dealership'):
            raise serializers.ValidationError("Cannot specify both recipient wholesaler and dealership.")
        
        user = self.context.get('request').user
        try:
            wholesaler_profile = user.wholesalerprofile
        except WholesalerProfile.DoesNotExist:
            raise serializers.ValidationError("Only wholesalers can send friend requests.")
        
        # Check for existing pending friend requests
        if FriendRequest.objects.filter(
            sender=wholesaler_profile,
            dealership=data.get('dealership'),
            recipient_wholesaler=data.get('recipient_wholesaler'),
            status='pending'
        ).exists():
            raise serializers.ValidationError("A pending friend request already exists.")

        return data
    
    def create(self, validated_data):
        user = self.context.get('request').user
        wholesaler_profile = user.wholesalerprofile

        validated_data['sender'] = wholesaler_profile

        return FriendRequest.objects.create(**validated_data)
    