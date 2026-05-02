from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static


def home(request):
    return HttpResponse("Plantify Backend Running ✅")


urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

# ✅ ALWAYS serve media (important for Railway)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

