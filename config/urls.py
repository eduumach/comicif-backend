"""
URL configuration for comicif_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def api_root(request):
    """Root API endpoint"""
    return JsonResponse({
        "message": "Comicif Backend API",
        "version": "1.0.0",
        "endpoints": {
            "backgrounds": "/api/backgrounds/",
            "poses": "/api/poses/",
            "process_photo": "/api/process-photo/",
            "process_photo_base64": "/api/process-photo-base64/",
            "health": "/api/health/"
        }
    })


def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        "status": "healthy",
        "service": "comicif-backend"
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root, name='api_root'),
    path('api/', include('apps.backgrounds.urls')),
    path('api/', include('apps.poses.urls')),
    path('api/', include('apps.photo_processing.urls')),
    path('api/health/', health_check, name='health_check'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)