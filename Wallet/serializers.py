from rest_framework import serializers
from .models import Wallet

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'profile', 'balance', 'currency', 'status', 'request_origin', 'created_at']
        extra_kwargs = {
            'balance': {'read_only': True},
            'created_at': {'read_only': True},
        }


    def create(self):
        user = self.context['request'].user
        if user.profile.user_type == 'premium':
            wallet = Wallet.objects.create(user=user, **self.validated_data)
            return wallet

        if Wallet.objects.filter(user=user).count() >= 3 and user.profile.user_type == 'free':
            raise serializers.ValidationError("You can only have 3 wallets")
        wallet = Wallet.objects.create(user=user, **self.validated_data)
        return wallet


    def validate_balance(self, value):
        if value < 0:
            raise serializers.ValidationError("Balance cannot be negative")
        return value