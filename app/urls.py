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
    path("presence/details/", views.presence_details, name='presence-details'),
    path("presence/ajouter/", views.presence_ajouter, name='presence-ajouter'),
    
    
    path("cotisation/", views.cotisation, name='cotisation'),
    path("cotisation/update/<int:id>/", views.UpdateCotisation.as_view(), name='cotisation-update'),
    path("cotisation/fermer-ouvrir/<int:id>/", views.cotisation_fermer_ouvrir, name='cotisation-fermer-ouvrir'),
    path("cotisation/item/<int:membre_id>/ajouter-form", views.ajouter_cotisation_form, name='cotisation-ajouter-form'),
    path("cotisation/item/<int:membre_id>/gerer", views.cotisation_item_gerer, name='cotisation-item-gerer'),
    path("cotisation/evolution/<int:cotisation_id>/", views.cotisation_evolution, name='cotisation-evolution'),
    path("cotisation/details/<int:cotisation_id>/<int:membre_id>", views.cotisation_details, name='cotisation-details'),
    
    
    path("promesse/prendre/", views.promesse_faire, name='promesse-prendre'),
    path("promesse/", views.promesse_liste, name='promesse-liste'),
    path("promesse/gerer/<int:membre_id>/<int:cotisation_id>", views.promesse_gerer, name='promesse-gerer'),
    path("promesse/details/", views.promesse_details, name='promesse-details'),
    
    
    path("sous-groupe/", views.sous_groupe, name='sous-groupe'),
    path("sous-groupe/update/<int:id>/", views.UpdateSousGroupe.as_view(), name='update-sous-groupe'),
]
