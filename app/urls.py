from django.urls import path
from . import views

urlpatterns = [
    path("", views.app_home, name='app-home'),
    path("registration", views.registration, name='registration'),
    
    path("membre", views.membre, name='membre'),
]
