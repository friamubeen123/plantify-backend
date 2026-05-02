from django.urls import path
from .views import login_view, register, save_scan, get_scans, delete_scan

urlpatterns = [
    path('login/', login_view),
    path('register/', register),
    path('save-scan/', save_scan),
    path('scans/', get_scans),
    path('delete-scan/<int:id>/', delete_scan),
]