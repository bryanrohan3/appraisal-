from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import *
from datetime import timezone, datetime
from django.db import transaction


class UserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'token']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        # Token.objects.create(user=user)
        return user

    def get_token(self, obj):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key
    
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


class DealershipCurrentUserFKSerializer(serializers.PrimaryKeyRelatedField):
    class Meta:
        model = Dealership

    def get_queryset(self):
        request = self.context.get('request', None)
        user = request.user
        return user.dealerprofile.dealerships


class DealerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for DealerProfile model.
    """
    user = UserSerializer()
    dealerships = DealershipCurrentUserFKSerializer(many=True, required=False)
    received_requests = serializers.SerializerMethodField()
    sent_requests = serializers.SerializerMethodField()

    class Meta:
        model = DealerProfile
        fields = ['user', 'phone', 'role', 'dealerships', 'received_requests', 'sent_requests']

    # TODO: Check if validation passes on phone > 15 characters
    # If it does, the dealer profile creation can fail after user creation
    # Which means, the transaction must be atomic
    # But, we can write a override for vaidate_phone to check 
    # In the case that we pick up the 15 character thing before user is created
    # The requests dont need to be atomic
    # user didn't create when had 15+ chars for phone !TESTED!

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

        with transaction.atomic():
            user = UserSerializer().create(user_data)
            dealer_profile = DealerProfile.objects.create(user=user, **validated_data)
            dealer_profile.dealerships.set(dealership_data)
        
        return dealer_profile

    # TODO: I would seperate this serializer into "DealerUpdateSerializer"
    # Consists of UserUpdateSerializer -> UserSerialzer
    # And DealerUpdateSerializer
    # DealerSerializer -> Model Serializer -> Phone + Role fields
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        dealerships_data = validated_data.pop('dealerships', instance.dealerships.all())

        user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()

        # Here we just do what we did above with the User Serializer
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


class DealerProfileNestedSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = DealerProfile
        fields = ['id', 'first_name', 'last_name']

class DealershipNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dealership
        fields = ['id', 'dealership_name']


class WholesalerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

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
    

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'image', 'appraisal'] 
    
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'user', 'comment', 'comment_date_time']


class OfferSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = ['id', 'user', 'amount', 'adjusted_amount', 'passed', 'created_at']
        read_only_fields = ['user', 'adjusted_amount']

    def get_user(self, obj):
        user = obj.user
        # TODO: validate, but I think this can never be false
        if hasattr(user, 'user'):
            return {
                'username': user.user.username,  # Assuming `user` is related to a `User` model with `username`
                'first_name': user.user.first_name,
                'last_name': user.user.last_name
            }
        return {
            'username': 'Unknown',
            'first_name': 'Unknown',
            'last_name': 'Unknown'
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



class AppraisalInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppraisalInvite
        fields = ['id', 'appraisal', 'wholesaler', 'created_at']
    

class AppraisalSerializer(serializers.ModelSerializer):
    initiating_dealer = DealerProfileNestedSerializer(read_only=True)
    last_updating_dealer = DealerProfileNestedSerializer(read_only=True)
    dealership = DealershipNestedSerializer(read_only=True)
    damages = DamageSerializer(many=True)
    vehicle_photos = PhotoSerializer(many=True, read_only=True, source='vehicle_photos_set')
    general_comments = CommentSerializer(many=True, read_only=True)
    private_comments = CommentSerializer(many=True, read_only=True)
    winner = serializers.SerializerMethodField()
    offers = OfferSerializer(many=True, required=False)
    invites = AppraisalInviteSerializer(many=True, read_only=True)

    class Meta:
        model = Appraisal
        fields = [
            'id', 'start_date', 'last_updated', 'is_active', 'ready_for_management', 'dealership', 
            'initiating_dealer', 'last_updating_dealer', 'customer_first_name', 'customer_last_name', 
            'customer_email', 'customer_phone', 'vehicle_make', 'vehicle_model', 'vehicle_year', 
            'vehicle_vin', 'vehicle_registration', 'color', 'odometer_reading', 'engine_type', 
            'transmission', 'body_type', 'fuel_type', 'reserve_price', 'damages', 'vehicle_photos',
            'private_comments', 'general_comments', 'winner', 'offers', 'invites',
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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        user = request.user

        # What we do: in our permissions class, we have 3 arrays of strings, strings are the fields of the appraisal
        # manager_permissions = ['rego', 'colour', 'customer', 'offers']
        # sales_permissions = ['rego', 'colour', 'customer']
        # wholesale_permissions = ['rego', 'colour']
        # in this serializer we have a for loop of fields, pop if its not in the correct array
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
        # dealer_profile = DealerProfile.objects.get(user=user)
        dealer_profile = user.dealerprofile
        #TODO: Just use user.dealerprofile

        if not dealer_profile.dealerships.exists():
            raise serializers.ValidationError("You are not associated with any dealership.")

        # TODO: Pass dealership in, use the FK serializer to validate
        # Validate and get the dealership using the FK serializer
        dealership = dealer_profile.dealerships.first()
        validated_data['initiating_dealer'] = dealer_profile
        validated_data['dealership'] = dealership
        validated_data['last_updating_dealer'] = dealer_profile

        damages_data = validated_data.pop('damages', [])
        appraisal = Appraisal.objects.create(**validated_data)

        for damage_data in damages_data:
            Damage.objects.create(appraisal=appraisal, **damage_data)

        return appraisal


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

        return data
