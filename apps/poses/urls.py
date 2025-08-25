from django.urls import path
from . import views

app_name = 'poses'

urlpatterns = [
    path('poses/', views.get_poses, name='poses_list'),
]