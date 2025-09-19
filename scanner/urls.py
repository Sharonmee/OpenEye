from django.urls import path
from . import views
from .cognito_auth import cognito_login, cognito_callback, cognito_logout

app_name = 'scanner'

urlpatterns = [
    path("", views.scan, name="scan"),  # This will handle /scan/
    path("<int:scan_id>/", views.scan_results, name="scan_results"),  # This will handle /scan/123/
    path("history/", views.scan_history, name="scan_history"),
    
    # API endpoints
    path("api/start-scan/", views.start_scan_api, name="start_scan_api"),
    path("api/scan/<int:scan_id>/status/", views.get_scan_status, name="get_scan_status"),
    path("api/scan/<int:scan_id>/results/", views.get_scan_results, name="get_scan_results"),
    path("api/scan/<int:scan_id>/cancel/", views.cancel_scan, name="cancel_scan"),
    path("api/zap-status/", views.check_zap_status, name="check_zap_status"),
]