from django.urls import path
from .views import WalletViewSet, TransactionViewSet

urlpatterns = [
    path('wallet/', WalletViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('wallet/<int:pk>/', WalletViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('transaction/', TransactionViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('transaction/<int:pk>/', TransactionViewSet.as_view({'get': 'retrieve'})),
]