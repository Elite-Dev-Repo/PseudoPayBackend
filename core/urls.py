from core.views import ResendTokenView
from django.urls import path
from .views import UserRegistrationView, MerchantProfileUpdateView, getUserProfileView, UpdateUserProfileView, ResendEmailVerificationTokenView, VerifyEmailView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('update-merchant-profile/', MerchantProfileUpdateView.as_view(), name='update-merchant-profile'),
    path('profile/', getUserProfileView.as_view(), name='profile'),
    path('update-profile/', UpdateUserProfileView.as_view(), name='update-profile'),
    path('resend-code/', ResendEmailVerificationTokenView.as_view(), name='resend-email-verification'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-token/', ResendTokenView.as_view(), name='resend-token'),
]