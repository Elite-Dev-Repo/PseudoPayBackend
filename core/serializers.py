from rest_framework import serializers
from .models import User, MerchantProfile, EmailVerificationToken



class MerchantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantProfile
        fields = ['id', 'user', 'user_type', 'merchant_address', 'merchant_phone', 'merchant_email', 'merchant_description']
        read_only_fields = ['id', 'user', 'user_type', 'merchant_email', 'created_at']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['date_of_birth', 'gender']


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



class ResetPasswordEmailLinkSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=5)


class ResetPasswordConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        # Run Django password validators
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError as DjangoValidationError
        try:
            validate_password(attrs.get('new_password'))
        except DjangoValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        return attrs