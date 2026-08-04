from rest_framework import serializers
from .models import User, MerchantProfile, EmailVerificationToken



class MerchantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantProfile
        fields = ['id', 'user', 'user_type', 'merchant_address', 'merchant_phone', 'merchant_email', 'merchant_description']
        read_only_fields = ['id', 'user', 'merchant_email', 'created_at']


class EmailVerificationTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailVerificationToken
        fields = ['id', 'user', 'token', 'created_at', 'expires_at']
        read_only_fields = ['id', 'created_at', 'expires_at']


class ResendEmailVerificationTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    


class UserSerializer(serializers.ModelSerializer):
    profile = MerchantProfileSerializer(source='merchant_profile', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'password', 'date_of_birth', 'gender', 'email', 'profile']
        read_only_fields = ['id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
