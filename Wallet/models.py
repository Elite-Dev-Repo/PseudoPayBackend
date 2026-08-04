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


