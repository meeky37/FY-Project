"""
Key Module Functionality:
 - Defines URL patterns for basic authentication views like login and logout.
 - JWT token endpoints for obtaining, refreshing, and verifying authentication tokens.
 - Custom views for user registration, subscription management, and user data retrieval.
 - Uses Django's built-in views for password reset functionality.
 - Includes a custom password reset view (https://pypi.org/project/django-rest-passwordreset/) for Vue app.
 - Integrates Django Rest Password Reset URLs for API-based password reset operations.

Further comments for each view are in accounts/views.py.
"""

from django.urls import path, include
from django.contrib.auth.views import (LoginView, LogoutView, PasswordResetView,
                                       PasswordResetDoneView, PasswordResetConfirmView,
                                       PasswordResetCompleteView)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import get_user_data, register_user, toggle_sub, get_sub_status, get_sub_list, \
    CustomPasswordResetView, CustomTokenObtainPairView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api/register/', register_user, name='register_user'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/get_user_data/', get_user_data, name='get_user_data'),
    path('api/toggle_sub/<int:entity_id>/', toggle_sub, name='toggle_sub'),
    path('api/get_sub_status/<int:entity_id>/', get_sub_status, name='get_sub_status'),
    path('api/get_sub_list/', get_sub_list, name='get_sub_list'),

    # Django Password Reset Views
    path('password_reset/', CustomPasswordResetView.as_view(),
         name='password_reset_request'),
    path('password_reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Django Rest Password Reset
    path('api/password_reset/',
         include('django_rest_passwordreset.urls', namespace='password_reset')),

]
