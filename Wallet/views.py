from django.shortcuts import render
from .models import Wallet
from .serializers import WalletSerializer
from rest_framework import viewsets
# Create your views here.

class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
