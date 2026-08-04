from rest_framework import serializers
from .models import Wallet

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'user', 'balance', 'currency', 'status', 'request_origin', 'created_at']
        extra_kwargs = {
            'balance': {'read_only': True},
            'created_at': {'read_only': True},
        }

    def validate_balance(self, value):
        if value < 0:
            raise serializers.ValidationError("Balance cannot be negative")
        return value