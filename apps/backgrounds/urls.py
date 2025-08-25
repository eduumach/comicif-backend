from django.urls import path
from . import views

app_name = 'backgrounds'

urlpatterns = [
    path('backgrounds/', views.get_backgrounds, name='backgrounds_list'),
]