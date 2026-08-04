"""
URL configuration for PseudoPayBackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from django.urls import path
from core.views import GoogleLogin

urlpatterns = [
    path('admin/', admin.site.urls),
    
    ## App URLs
    path('api/', include('ApiKeys.urls')),
    path('api/', include('core.urls')),  
    path('api/', include('Wallet.urls')),  

    ## Auth URLs
    path('api/auth/', include('rest_framework.urls')),  
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += [
    path('api/auth/google/', GoogleLogin.as_view(), name='google_login'),
]

