from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import secrets
from django.utils import timezone


class UserModelManager(BaseUserManager):
    """Manager for email-based authentication."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', False)

        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_active') is not True:
            raise ValueError('Superuser must have is_active=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if not password:
            raise ValueError('Superuser must have a password.')

        return self.create_user(email, password, **extra_fields)



class User(AbstractUser):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    username = None
    REQUIRED_FIELDS = []
    objects = UserModelManager()

    def __str__(self):
        return f"User - {self.email}"




class MerchantProfile(models.Model):
    PROFILE_TYPE = [
        ('free', 'Free'),
        ('premium', 'Premium'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='merchant_profile')
    profile_type = models.CharField(max_length=10, choices=PROFILE_TYPE, default='free')
    merchant_address = models.CharField(max_length=255, blank=True, null=True)
    merchant_phone = models.CharField(max_length=15, blank=True, null=True)
    merchant_email = models.EmailField(unique=True)
    merchant_description = models.TextField(blank=True, null=True)
    merchant_website = models.URLField(blank=True, null=True)
    merchant_category = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)



    def save(self, *args, **kwargs):
        self.merchant_email = self.user.email
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Merchant Profile - {self.merchant_email}"



class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verification')
    token = models.CharField(max_length=16, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()


    def create_token(self):
        self.token = secrets.token_hex(4).upper()
        self.expires_at = timezone.now() + timedelta(minutes=15)

    def save(self, *args, **kwargs):
        if not self.token or not self.expires_at:
            self.create_token()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Email Verification - {self.user.email}"




