from django.urls import path
from . import views

app_name = 'photo_processing'

urlpatterns = [
    path('process-photo/', views.process_photo, name='process_photo'),
    path('process-photo-base64/', views.process_photo_base64, name='process_photo_base64'),
    path('available-options/', views.get_available_options, name='get_available_options'),
]