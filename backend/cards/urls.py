"""
URL configuration for the cards app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UserRegistrationView,
    CurrentUserView,
    VirtualCardViewSet,
    TransactionViewSet,
    process_transaction,
    AccountSummaryView,
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'cards', VirtualCardViewSet, basename='card')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', CurrentUserView.as_view(), name='current_user'),

    # Transaction processing
    path('transactions/process/', process_transaction, name='process_transaction'),

    # Account summary
    path('account/summary/', AccountSummaryView.as_view(), name='account_summary'),

    # Include router URLs
    path('', include(router.urls)),
]
