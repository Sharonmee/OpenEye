"""
URL configuration for OpenEye project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from scanner.views import home
from scanner.cognito_auth import cognito_login, cognito_callback, cognito_logout

urlpatterns = [
    path('scanner/', include('scanner.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', home, name='home'),
    path('login/', cognito_login, name='cognito_login'),
    path('authorize/', cognito_callback, name='cognito_callback'),
    path('logout/', cognito_logout, name='cognito_logout'),
]
