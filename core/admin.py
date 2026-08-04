from django.contrib import admin
from .models import User, MerchantProfile, EmailVerificationToken

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

@admin.register(MerchantProfile)
class MerchantProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'merchant_email', 'merchant_phone', 'merchant_category')
    list_filter = ('merchant_category',)
    search_fields = ('user__email', 'merchant_email', 'merchant_phone')
    ordering = ('user',)

@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expires_at')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('user__email', 'token')
    ordering = ('-created_at',)


