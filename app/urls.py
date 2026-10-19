from django.urls import path
from . import views


urlpatterns = [
    path("", views.app_home, name='dashboard'),
    path("registration", views.registration, name='registration'),
    path("users", views.users, name='users'),
    path("user-update/<int:id>", views.UpdateUser.as_view(), name='user-update'),

    path('changer-mot-de-passe/', views.PassWordChangeView.as_view(), name='changePass'),
    path('profile/', views.profile, name='profile'),
    path('user-change/', views.user_change, name='user-change'),


    path("membre", views.membre, name='membre'),
    path("membre/update/<int:id>/", views.UpdateMembre.as_view(), name='update-membre'),
    path("membre/supprime/<int:id>/", views.supprime_membre, name='supprime-membre'),

    path("presence/faire/", views.presence_faire, name='presence-faire'),
    path("presence/", views.presence_liste, name='presence-liste'),
    path("presence/gerer/<int:id>/", views.presence_gerer, name='presence-gerer'),
    path("presence/details/", views.presence_details, name='presence-details'),
    path("presence/ajouter-liste/", views.presence_ajouter, name='presence-ajouter'),
    path("presence/modifier/<int:presence_id>/", views.presence_modifier, name='presence-modifier'),


    path("cotisation/", views.cotisation, name='cotisation'),
    path("cotisation/update/<int:id>/", views.UpdateCotisation.as_view(), name='cotisation-update'),
    # path("cotisation/supprime/<int:id>/", views.supprime_cotisation, name='cotisation-supprime'),
    path("cotisation/fermer-ouvrir/<int:id>/", views.cotisation_fermer_ouvrir, name='cotisation-fermer-ouvrir'),
    path("cotisation/item/<int:membre_id>/ajouter-form", views.ajouter_cotisation_form, name='cotisation-ajouter-form'),
    path("cotisation/item/<int:membre_id>/gerer", views.cotisation_item_gerer, name='cotisation-item-gerer'),
    path("cotisation/item/<int:id>/modifier", views.cotisation_item_modifier, name='cotisation-item-modifier'),
    path("cotisation/evolution/<int:cotisation_id>/", views.cotisation_evolution, name='cotisation-evolution'),
    path("cotisation/details/<int:cotisation_id>/", views.cotisation_details, name='cotisation-details'),
    path("cotisation/details-membre/<int:cotisation_id>/<int:membre_id>", views.cotisation_details_membre, name='cotisation-details-membre'),
    path("cotisation/evolution-sous/<int:cotisation_id>/", views.cotisation_evolution_sous, name='cotisation-evolution-sous'),


    path("carte/", views.carte, name="carte"),
    path("carte/<int:pk>/semaine/", views.carte_semaine, name="carte-semaine"),
    path("carte/<int:pk>/supprimer/", views.carte_supprimer, name="carte-supprimer"),
    path("carte/<int:pk>/annee/", views.carte_annee, name="carte-annee"),
    path("carte/<int:pk>/pdf/", views.carte_pdf, name="carte-pdf"),
    path("carte/vierge/pdf/", views.carte_vierge_pdf, name="carte-vierge-pdf"),

    path("promesse/prendre/", views.promesse_faire, name='promesse-prendre'),
    path("promesse/", views.promesse_liste, name='promesse-liste'),
    path("promesse/gerer/<int:membre_id>/<int:cotisation_id>", views.promesse_gerer, name='promesse-gerer'),
    path("promesse/details/", views.promesse_details, name='promesse-details'),
    path("promesse/modifier/<int:promesse_id>", views.promesse_modifier, name='promesse-modifier'),

    # Fiches de promesse (tableau enregistré, indépendant des cotisations)
    path("promesse/fiches/", views.fiche_promesse, name='fiche-promesse'),
    path("promesse/fiches/creer/", views.fiche_promesse_creer, name='fiche-promesse-creer'),
    path("promesse/fiches/<int:fiche_id>/", views.fiche_promesse_detail, name='fiche-promesse-detail'),
    path("promesse/fiches/<int:fiche_id>/enregistrer/", views.fiche_promesse_enregistrer, name='fiche-promesse-enregistrer'),
    path("promesse/fiches/<int:fiche_id>/sync/", views.fiche_promesse_sync, name='fiche-promesse-sync'),
    path("promesse/fiches/<int:fiche_id>/supprimer/", views.fiche_promesse_supprimer, name='fiche-promesse-supprimer'),
    path("promesse/fiches/<int:fiche_id>/export/", views.fiche_promesse_export, name='fiche-promesse-export'),
    path("promesse/ligne/<int:ligne_id>/payer/", views.fiche_promesse_payer, name='fiche-promesse-payer'),
    path("promesse/ligne/<int:ligne_id>/solder/", views.fiche_promesse_solder, name='fiche-promesse-solder'),
    path("promesse/paiement/<int:paiement_id>/supprimer/", views.fiche_promesse_paiement_supprimer, name='fiche-promesse-paiement-supprimer'),

    path("promesse/fiches/<int:fiche_id>/ajouter-ligne/", views.fiche_promesse_ajouter_ligne, name='fiche-promesse-ajouter-ligne'),
    path("promesse/fiches/<int:fiche_id>/pdf/", views.fiche_promesse_pdf, name='fiche-promesse-pdf'),
    path("promesse/ligne/<int:ligne_id>/supprimer/", views.fiche_promesse_ligne_supprimer, name='fiche-promesse-ligne-supprimer'),

    path("sous-groupe/", views.sous_groupe, name='sous-groupe'),
    path("sous-groupe/update/<int:id>/", views.UpdateSousGroupe.as_view(), name='update-sous-groupe'),
    path("sous-groupe/supprime/<int:id>/", views.supprime_sous_groupe, name='supprime-sous-groupe'),

    path("depense", views.depense, name='depense'),
    path("depense/update/<int:id>/", views.UpdateDepense.as_view(), name='depense-update'),


    path("point/", views.point, name='point'),
]