from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import *


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
    dealerships = DealershipSerializer(many=True, read_only=True)  # Use the DealershipSerializer to serialize dealerships

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
        return list(instance.dealerships.values_list('id', flat=True))

    # def get_dealerships(self, instance):
    #     user = instance.user
    #     role = instance.role
        
    #     # Fetch associated dealerships based on user's role
    #     if role == 'S':  # Sales dealer
    #         dealerships = user.sales_dealerships.values_list('id', flat=True)
    #     elif role == 'M':  # Management dealer
    #         dealerships = user.managed_dealerships.values_list('id', flat=True)
    #     else:
    #         dealerships = []

    #     return list(dealerships)

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
