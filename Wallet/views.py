from core.models import MerchantProfile
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction as db_transaction
from functools import partial
from .services import send_transaction_email
# Create your views here.

class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer

class ViewUserTransactionsAPIView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Transaction.objects.all()
        user_profile = MerchantProfile.objects.get(user=user)
        return Transaction.objects.filter(wallet=user_profile.wallet)



class InitializeTransaction(generics.CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def create(self, request):
        with db_transaction.atomic():
            user_profile = MerchantProfile.objects.get(user=request.user)
            data= request.data
            wallet = Wallet.objects.get(profile=user_profile, id=data['wallet'])
            if wallet.status != 'ACTIVE':
                return Response({"error": "Wallet is not active"}, status=status.HTTP_400_BAD_REQUEST)
            # import sys
            # sys.exit()
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                response_data = serializer.data
                response_data['checkout_url'] = "http://127.0.0.1:8000/api/checkout/" + serializer.data['transaction_reference']
                return Response(response_data , status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




def payment_success(request, transaction_reference):
    payment_transaction = Transaction.objects.get(transaction_reference=transaction_reference)
    return render(request, 'payment_success.html', {'transaction': payment_transaction})


def checkout(request, transaction_reference):
    if request.method == 'GET':
        payment_transaction = Transaction.objects.get(transaction_reference=transaction_reference)
        wallet = payment_transaction.wallet
        if payment_transaction.transaction_status == 'SUCCESSFUL':
            return redirect('payment_success', transaction_reference=payment_transaction.transaction_reference)
        return render(request, 'checkout.html', {'transaction': payment_transaction})
    elif request.method == 'POST':
        with db_transaction.atomic():
            payment_transaction = Transaction.objects.get(transaction_reference=transaction_reference)
            wallet = payment_transaction.wallet
            if payment_transaction.transaction_type == 'DEBIT':
                if wallet.balance < payment_transaction.amount:
                    return JsonResponse({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)
                wallet.balance -= payment_transaction.amount
            elif payment_transaction.transaction_type == 'CREDIT':
                wallet.balance += payment_transaction.amount

            payment_transaction.transaction_status = 'SUCCESSFUL'
            payment_transaction.save()
            wallet.save()
            db_transaction.on_commit(
                partial(send_transaction_email, payment_transaction.customer_name, payment_transaction)
            )
            return redirect('payment_success', transaction_reference=payment_transaction.transaction_reference)

# class TransactionViewSet(viewsets.ModelViewSet):
#     queryset = Transaction.objects.all()
#     serializer_class = TransactionSerializer

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_superuser:
#             return Transaction.objects.all()
#         user_profile = MerchantProfile.objects.get(user=user)
#         return Transaction.objects.filter(wallet=user_profile.wallet)

#     def list(self, request):
#         queryset = self.get_queryset()
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def create(self, request):
#         with transaction.atomic():
#             user_profile = MerchantProfile.objects.get(user=request.user)
#             data= request.data
#             wallet = Wallet.objects.get(profile=user_profile, id=data['wallet'])
#             if wallet.status != 'ACTIVE':
#                 return Response({"error": "Wallet is not active"}, status=status.HTTP_400_BAD_REQUEST)
#             if data['transaction_type'] == 'DEBIT':
#                 if wallet.balance < int(data['amount']):
#                     return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)
#                 wallet.balance -= int(data['amount'])
#             elif data['transaction_type'] == 'CREDIT':
#                 wallet.balance += int(data['amount'])

#             # import sys
#             # sys.exit()

#             wallet.save()
#             serializer = self.get_serializer(data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)