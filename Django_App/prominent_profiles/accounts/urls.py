from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import get_user_data, register_user, toggle_sub, get_sub_status, get_sub_list



urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api/register/', register_user, name='register_user'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/get_user_data/', get_user_data, name='get_user_data'),
    path('api/toggle_sub/<int:entity_id>/', toggle_sub, name='toggle_sub'),
    path('api/get_sub_status/<int:entity_id>/', get_sub_status, name='get_sub_status'),
    path('api/get_sub_list/', get_sub_list, name='get_sub_list'),
]
    # TODO: Need to add forgot password still!