"""prominent_profiles URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.urls import include, path


def set_csrf_token(request):
    get_token(request)
    return JsonResponse({'detail': 'CSRF cookie set'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('profiles_app/', include('profiles_app.urls')),
    path('accounts/', include('accounts.urls')),
    path('set-csrf/', set_csrf_token, name='set-csrf'),
]
