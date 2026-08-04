from django.urls import path
from .views import ApiKeyListView, ApiKeyCreateView, ApiKeyDeleteView

urlpatterns = [
    path('api-keys/', ApiKeyListView.as_view(), name='api-key-list'),
    path('api-keys/create/', ApiKeyCreateView.as_view(), name='api-key-create'),
    path('api-keys/<int:pk>/', ApiKeyDeleteView.as_view(), name='api-key-delete'),
]