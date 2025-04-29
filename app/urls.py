from django.urls import path
from . import views

urlpatterns = [
    path("", views.app_home, name='dashboard'),
    path("registration", views.registration, name='registration'),
    
    path("membre", views.membre, name='membre'),
    path("membre/update/<int:id>/", views.UpdateMembre.as_view(), name='update-membre'),
    
    path("presence/faire/", views.presence_faire, name='presence-faire'),
    path("presence/", views.presence_liste, name='presence-liste'),
    path("presence/gerer/<int:id>/", views.presence_gerer, name='presence-gerer'),
    
    path("cotisation/", views.cotisation, name='cotisation'),
    path("cotisation/update/<int:id>/", views.UpdateCotisation.as_view(), name='cotisation-update'),
    path("cotisation/fermer-ouvrir/<int:id>/", views.cotisation_fermer_ouvrir, name='cotisation-fermer-ouvrir'),
    
    
]
