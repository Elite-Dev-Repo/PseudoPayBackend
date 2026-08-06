from core.models import MerchantProfile
from django.shortcuts import render
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
# Create your views here.

class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Transaction.objects.all()
        user_profile = MerchantProfile.objects.get(user=user)
        return Transaction.objects.filter(wallet=user_profile.wallet)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        with transaction.atomic():
            user_profile = MerchantProfile.objects.get(user=request.user)
            data= request.data
            wallet = Wallet.objects.get(profile=user_profile, id=data['wallet'])
            if wallet.status != 'ACTIVE':
                return Response({"error": "Wallet is not active"}, status=status.HTTP_400_BAD_REQUEST)
            if data['transaction_type'] == 'DEBIT':
                if wallet.balance < int(data['amount']):
                    return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)
                wallet.balance -= int(data['amount'])
            elif data['transaction_type'] == 'CREDIT':
                wallet.balance += int(data['amount'])

            # import sys
            # sys.exit()

            wallet.save()
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)