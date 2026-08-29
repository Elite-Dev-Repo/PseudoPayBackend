# pyrefly: ignore [missing-import]
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User, MerchantProfile, EmailVerificationToken
from .serializers import UserSerializer, MerchantProfileSerializer, EmailVerificationTokenSerializer,ResendEmailVerificationTokenSerializer, UserProfileUpdateSerializer,ResetPasswordEmailLinkSerializer, ResetPasswordConfirmSerializer
from rest_framework.exceptions import PermissionDenied
from django.db import transaction
from rest_framework.views import APIView
from django.utils import timezone
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, force_bytes, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from Wallet.services import send_reset_link_email



# Create your views here.


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    # client_class is only needed if you are using specific OAuth2 flows
    client_class = OAuth2Client
    throttle_scope = 'google_login'



class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    throttle_scope = 'register'

class ResetPasswordEmailLinkAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordEmailLinkSerializer
    throttle_scope = 'password_reset'

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get("email")

        try:
            user = User.objects.filter(email=email).first()
            if user:
                token = PasswordResetTokenGenerator().make_token(user)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

                # Build frontend reset URL - use FRONTEND_URL setting
                frontend_base = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
                # Allow override via Origin/Referer header if needed for preview deployments
                # but always prefer settings.FRONTEND_URL for security
                reset_url = f"{frontend_base}/reset-password/{uidb64}/{token}/"

                data = {"link": reset_url, "user_email": email}
                print(f"[password-reset] reset_url: {reset_url} for {email}")
                try:
                    send_reset_link_email(reset_url, email)
                except Exception as mail_err:
                    print(f"[password-reset] email send failed: {mail_err}")
                    return Response(
                        {"error": "Failed to send email. Please try again later."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                return Response(
                    {"success": "If an account exists for that email, a reset link has been sent. Please check your inbox."},
                    status=status.HTTP_200_OK,
                )
            else:
                # Security: don't reveal whether email exists - return generic success
                # Log for debugging but return same message as success case
                print(f"[password-reset] attempted for non-existent email: {email}")
                return Response(
                    {"success": "If an account exists for that email, a reset link has been sent. Please check your inbox."},
                    status=status.HTTP_200_OK,
                )

        except Exception as e:
            print(f"error - {e}")
            return Response(
                {"error": "An internal server error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ResetPasswordLinkVerifyAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = 'password_reset'

    def get(self, request, uidb64, token):
        try:
            uid = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {"valid": False, "error": "Invalid or expired token. Please request a new reset link."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"valid": True, "message": "Token is valid", "email": user.email},
                status=status.HTTP_200_OK,
            )
        except (DjangoUnicodeDecodeError, ValueError, TypeError, User.DoesNotExist) as e:
            return Response(
                {'valid': False, 'error': 'Token is not valid, please request a new one'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            print(f"[verify-token] error: {e}")
            return Response(
                {'valid': False, 'error': 'Token is not valid, please request a new one'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResetPasswordConfirmAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordConfirmSerializer
    throttle_scope = 'password_reset_confirm'

    def post(self, request, uidb64=None, token=None):
        # Accept both URL params and body params for flexibility
        data = request.data.copy()
        if uidb64 and not data.get('uidb64'):
            data['uidb64'] = uidb64
        if token and not data.get('token'):
            data['token'] = token

        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uidb64_val = serializer.validated_data.get('uidb64')
        token_val = serializer.validated_data.get('token')
        new_password = serializer.validated_data.get('new_password')

        try:
            uid = smart_str(urlsafe_base64_decode(uidb64_val))
            user = User.objects.get(id=uid)
        except (DjangoUnicodeDecodeError, ValueError, TypeError, User.DoesNotExist):
            return Response(
                {'error': 'Invalid reset link. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not PasswordResetTokenGenerator().check_token(user, token_val):
            return Response(
                {'error': 'Invalid or expired token. Please request a new reset link.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Set new password
        user.set_password(new_password)
        user.save()

        return Response(
            {"success": "Password has been reset successfully. You can now log in with your new password."},
            status=status.HTTP_200_OK,
        )



class MerchantProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset = MerchantProfile.objects.all()
    serializer_class = MerchantProfileSerializer
    permission_classes = [IsAuthenticated]
    throttle_scope = 'profile'

    def get_object(self):
        return self.request.user.merchant_profile

    def perform_update(self, serializer):
        user = self.request.user
        owner = self.get_object().user
        if user != owner    :
            raise PermissionDenied("You are not authorized to update this profile")
        serializer.save(user=self.request.user)

class getUserProfileView(generics.RetrieveAPIView):
    queryset = User.objects.prefetch_related('merchant_profile')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    throttle_scope = 'profile'

    def get_object(self):
        return self.request.user


class UpdateUserProfileView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ResendEmailVerificationTokenView(APIView):
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationTokenSerializer
    throttle_scope = 'resend_email'

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        if user.is_active:
            return Response({"message": "User is already verified"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response({"message": "Email verification token resent successfully"}, status=status.HTTP_200_OK)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationTokenSerializer
    throttle_scope = 'verify_email'

    def post(self, request):
        with transaction.atomic():
            token = request.data.get('token')
            if not token:
                return Response({"message": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)
            


            token = EmailVerificationToken.objects.filter(token=token).first()
            if not token:
                return Response({"message": "Token is invalid"}, status=status.HTTP_400_BAD_REQUEST)
            


            if token.expires_at < timezone.now():
                return Response({"message": "Token has expired"}, status=status.HTTP_400_BAD_REQUEST)
            user = token.user
            user.is_active = True
            user.save()
            token.delete()
            return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)



class ResendTokenView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ResendEmailVerificationTokenSerializer
    throttle_scope = 'resend_email'

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
        else:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        if user.is_active:
            return Response({"message": "User is already verified"}, status=status.HTTP_400_BAD_REQUEST)
        EmailVerificationToken.objects.create(user=user)
        return Response({"message": "Email verification token sent successfully", "url": "/verify-email/"}, status=status.HTTP_200_OK)
        