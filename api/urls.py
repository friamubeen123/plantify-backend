from django.urls import path
from .views import predict, login_view, register, save_scan, get_scans, delete_scan
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import get_scans

urlpatterns = [
    path('predict/', predict),
    path('login/', login_view),
    path('register/', register),
    path('save-scan/', save_scan),
    path('scans/', get_scans),
    path('delete-scan/<int:id>/', delete_scan),
]