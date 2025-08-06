from django.urls import path
from . import views
from .cognito_auth import cognito_login, cognito_callback, cognito_logout

app_name = 'scanner'

urlpatterns = [
    path("", views.index, name="index"),
    path("scan/", views.scan, name="scan"),
    path("home/", views.index, name="home"),

]