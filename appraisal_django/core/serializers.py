from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import *
from datetime import timezone, datetime


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
    management_dealers = UserSerializer(many=True, read_only=True)
    sales_dealers = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Dealership
        fields = ['id', 'dealership_name', 'street_address', 'suburb', 'state', 'postcode', 'email', 'phone', 'wholesalers', 'management_dealers', 'sales_dealers']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Fetch management dealers and sales dealers for the dealership
        management_dealers = instance.management_dealers.filter(dealerprofile__role='M')
        sales_dealers = instance.sales_dealers.filter(dealerprofile__role='S')

        # Serialize management dealers and sales dealers
        representation['management_dealers'] = UserSerializer(management_dealers, many=True).data
        representation['sales_dealers'] = UserSerializer(sales_dealers, many=True).data
        
        return representation

class DealerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    dealerships = serializers.PrimaryKeyRelatedField(queryset=Dealership.objects.all(), many=True, required=False)  # Change to PrimaryKeyRelatedField

    class Meta:
        model = DealerProfile
        fields = ['user', 'phone', 'role', 'dealerships']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        dealership_data = validated_data.pop('dealerships', [])

        user = UserSerializer().create(user_data)
        dealer_profile = DealerProfile.objects.create(user=user, **validated_data)
        dealer_profile.dealerships.set(dealership_data)

        return dealer_profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        dealerships_data = validated_data.pop('dealerships', instance.user.managed_dealerships.all())

        user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()

        instance.phone = validated_data.get('phone', instance.phone)
        instance.role = validated_data.get('role', instance.role)
        instance.save()

        # Update the associated dealerships for the user
        instance.user.managed_dealerships.set(dealerships_data)
        
        return instance
    
    def get_dealerships(self, instance):
        user = instance.user
        role = instance.role
        
        # Fetch associated dealerships based on user's role
        if role == 'S':  # Sales dealer
            dealerships = instance.dealerships.values_list('id', flat=True)
        elif role == 'M':  # Management dealer
            dealerships = user.managed_dealerships.values_list('id', flat=True)
        else:
            dealerships = []
        
        return list(dealerships)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['dealerships'] = self.get_dealerships(instance)
        return representation
    

class WholesalerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = WholesalerProfile
        fields = ['user', 'wholesaler_name', 'street_address', 'suburb', 'state', 'postcode', 'email', 'phone']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        wholesaler_profile = WholesalerProfile.objects.create(user=user, **validated_data)
        return wholesaler_profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()

        instance.wholesaler_name = validated_data.get('wholesaler_name', instance.wholesaler_name)
        instance.street_address = validated_data.get('street_address', instance.street_address)
        instance.suburb = validated_data.get('suburb', instance.suburb)
        instance.state = validated_data.get('state', instance.state)
        instance.postcode = validated_data.get('postcode', instance.postcode)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.save()
        return instance
    

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'appraisal', 'photo', 'description']

    def create(self, validated_data):
        return Photo.objects.create(**validated_data)
    

class AppraisalSerializer(serializers.ModelSerializer):
    damage_photos = PhotoSerializer(many=True, read_only=True, source='damage_photos_set')
    vehicle_photos = PhotoSerializer(many=True, read_only=True, source='vehicle_photos_set')
    sent_to_management = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = Appraisal
        fields = [
            'id', 'start_date', 'last_updated', 'is_active',
            'dealership', 'initiating_dealer', 'last_updating_dealer',
            'customer_first_name', 'customer_last_name', 'customer_email', 'customer_phone',
            'vehicle_make', 'vehicle_model', 'vehicle_year', 'vehicle_vin', 'vehicle_registration',
            'color', 'odometer_reading', 'engine_type', 'transmission', 'body_type', 'fuel_type',
            'damage_description', 'damage_location', 'repair_cost_estimate',
            'damage_photos', 'vehicle_photos',
            'reserve_price',
            'sent_to_management',
        ]
        read_only_fields = ['initiating_dealer', 'dealership', 'last_updating_dealer']


    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        dealer_profile = DealerProfile.objects.get(user=user)

        if not dealer_profile.dealerships.exists():
            raise serializers.ValidationError("You are not associated with any dealership.")

        dealership = dealer_profile.dealerships.first()
        validated_data['initiating_dealer'] = dealer_profile
        validated_data['dealership'] = dealership
        validated_data['last_updating_dealer'] = dealer_profile

        sent_to_management_ids = validated_data.pop('sent_to_management', [])
        damage_photos_data = request.FILES.getlist('damage_photos', [])
        vehicle_photos_data = request.FILES.getlist('vehicle_photos', [])

        appraisal = Appraisal.objects.create(**validated_data)

        for damage_photo_data in damage_photos_data:
            Photo.objects.create(appraisal=appraisal, image=damage_photo_data, location='damage')

        for vehicle_photo_data in vehicle_photos_data:
            Photo.objects.create(appraisal=appraisal, image=vehicle_photo_data, location='vehicle')

        appraisal.sent_to_management.set(sent_to_management_ids)

        return appraisal