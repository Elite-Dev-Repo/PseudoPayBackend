import secrets
from rest_framework import serializers
from .models import Wallet, Transaction

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'profile', 'balance', 'currency', 'status', 'request_origin', 'created_at']
        extra_kwargs = {
            'profile': {'read_only': True},
            'balance': {'read_only': True},
            'created_at': {'read_only': True},
        }


    def create(self, validated_data):
        user = self.context['request'].user
        profile = user.merchant_profile
        if Wallet.objects.filter(profile=profile).count() >= 3:
            raise serializers.ValidationError("You can only have 3 wallets")
        validated_data['profile'] = profile
        return super().create(validated_data)


    def validate_balance(self, value):
        if value < 0:
            raise serializers.ValidationError("Balance cannot be negative")
        return value



class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='wallet.profile.user.email', read_only=True)
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'wallet', 'amount', 'transaction_type', 'transaction_status', 'transaction_reference', 'customer_email', 'customer_name', 'transaction_metadata', 'created_at']
        read_only_fields = ['id', 'user', 'transaction_status', 'transaction_reference', 'created_at']


    def validate_amount(self, value):
        if value < 500:
            raise serializers.ValidationError("Amount cannot be less than 500")
        return value
