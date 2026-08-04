# pyrefly: ignore [missing-import]
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User, MerchantProfile, EmailVerificationToken
from .serializers import UserSerializer, MerchantProfileSerializer, EmailVerificationTokenSerializer,ResendEmailVerificationTokenSerializer
from rest_framework.exceptions import PermissionDenied
from django.db import transaction
from rest_framework.views import APIView
from django.utils import timezone
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client



# Create your views here.


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    # client_class is only needed if you are using specific OAuth2 flows
    client_class = OAuth2Client



class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class MerchantProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset = MerchantProfile.objects.all()
    serializer_class = MerchantProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.merchant_profile

    def perform_update(self, serializer):
        user = self.request.user
        owner = self.get_object().user
        if user != owner:
            raise PermissionDenied("You are not authorized to update this profile")
        serializer.save(user=self.request.user)


class getUserProfileView(generics.RetrieveAPIView):
    queryset = User.objects.prefetch_related('merchant_profile')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ResendEmailVerificationTokenView(APIView):
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationTokenSerializer

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
        