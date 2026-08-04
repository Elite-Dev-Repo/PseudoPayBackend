from django.db import models
from django.contrib.auth import get_user_model
from core.models import MerchantProfile
# Create your models here.

User = get_user_model()

class Wallet(models.Model):
    CURRENCY_TYPE= [
        ('NGN', 'Naira'),
        ('USD', 'Dollar'),
        ('EUR', 'Euro'),
    ]

    WALLET_STATUS = [
        ('ACTIVE', 'Active'),
        ('LOCKED', 'Locked'),
        ('FROZEN', 'Frozen'),
    ]

    profile = models.ForeignKey(MerchantProfile, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=500000.00)
    currency = models.CharField(max_length=3, choices=CURRENCY_TYPE, default='NGN')
    status = models.CharField(max_length=10, choices=WALLET_STATUS, default='ACTIVE')
    request_origin = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wallet - {self.profile.merchant_email}"




class Transaction(models.Model):
    TRANSACTION_TYPE = [
        ('DEBIT', 'Debit'),
        ('CREDIT', 'Credit'),
    ]
    TRANSACTION_STATUS = [
        ('INITIATED', 'Initiated'),
        ('PENDING', 'Pending'),
        ('SUCCESSFUL', 'Successful'),
        ('FAILED', 'Failed'),
    ]
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transaction')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    transaction_status = models.CharField(max_length=10, choices=TRANSACTION_STATUS, default='INITIATED')
    transaction_reference = models.CharField(max_length=100, unique=True)
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=100)
    currency = models.CharField(max_length=3, default='NGN')
    transaction_metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction - {self.wallet.profile.merchant_email}"