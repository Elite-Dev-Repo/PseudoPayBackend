import pathlib
from django.urls import path
from .views import WalletViewSet,ViewUserTransactionsAPIView, InitializeTransaction, checkout, payment_success

urlpatterns = [
    path('wallet/', WalletViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('wallet/<int:pk>/', WalletViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('transaction/', ViewUserTransactionsAPIView.as_view()),
    path('transaction/initialize/', InitializeTransaction.as_view()),
    path('checkout/<str:transaction_reference>/', checkout, name='checkout'),
    path('payment/success/<str:transaction_reference>/', payment_success, name='payment_success'),
]