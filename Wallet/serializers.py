import secrets
from rest_framework import serializers
from .models import Wallet, Transaction

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



class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='wallet.profile.user.email', read_only=True)
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'wallet', 'amount', 'transaction_type', 'transaction_status', 'transaction_reference', 'customer_email', 'customer_name', 'transaction_metadata', 'created_at']
        read_only_fields = ['id', 'user', 'transaction_status', 'transaction_reference', 'created_at']


    def create(self):
        transaction_reference = f"TRX-{secrets.token_hex(4) + str(self.created_at).replace(' ', '').replace('-', '').replace(':', '').replace('.', '')}"
        transaction = Transaction.objects.create(transaction_reference=transaction_reference, **self.validated_data)
        return transaction


    def validate_amount(self, value):
        if value < 500:
            raise serializers.ValidationError("Amount cannot be less than 500")
        return value
