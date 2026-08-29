from core.views import ResendTokenView
from django.urls import path
from .views import UserRegistrationView, MerchantProfileUpdateView, getUserProfileView, UpdateUserProfileView, ResendEmailVerificationTokenView, VerifyEmailView, ResetPasswordEmailLinkAPIView, ResetPasswordLinkVerifyAPIView, ResetPasswordConfirmAPIView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('update-merchant-profile/', MerchantProfileUpdateView.as_view(), name='update-merchant-profile'),
    path('profile/', getUserProfileView.as_view(), name='profile'),
    path('update-profile/', UpdateUserProfileView.as_view(), name='update-profile'),
    path('resend-code/', ResendEmailVerificationTokenView.as_view(), name='resend-email-verification'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-token/', ResendTokenView.as_view(), name='resend-token'),
    path('reset-password/', ResetPasswordEmailLinkAPIView.as_view(), name='reset-password'),
    path('reset-password/verify/<str:uidb64>/<str:token>/', ResetPasswordLinkVerifyAPIView.as_view(), name='reset-password-verify'),
    path('reset-password/confirm/', ResetPasswordConfirmAPIView.as_view(), name='reset-password-confirm'),
    path('reset-password/confirm/<str:uidb64>/<str:token>/', ResetPasswordConfirmAPIView.as_view(), name='reset-password-confirm-with-params'),
]