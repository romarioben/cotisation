from django.db import models
from django.contrib.auth.models  import AbstractUser
from django_softdelete.models import SoftDeleteModel
import datetime
from django.utils.timezone import now
from auth_app.models import User
from .models0 import Groupe, SousGroupe


# Create your models here.


class Membre(SoftDeleteModel):
    sexe_choices = (
        ('M', 'Masculin'),
        ('F', 'Féminin')
    )
    nom = models.CharField(max_length=60)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(max_length=2, choices=sexe_choices, default='sexe', null=True, blank=True)
    code = models.CharField(verbose_name="Code",max_length=70, blank=True, null=True, unique=True)
    email = models.EmailField(verbose_name="Email", null=True, blank=True)
    #annee_naissance = models.PositiveSmallIntegerField(default=0, verbose_name="Année de naissance ou Age")
    date_naissance = models.DateField(verbose_name="Date de naissance", null=True, blank=True)
    nationalite = models.CharField(max_length=70, null=True, blank=True, verbose_name="Nationalité")
    numero = models.CharField(max_length=21, verbose_name='Numéro de téléphone', null=True, blank=True)
    profession = models.CharField(max_length=100)
    sous_groupe = models.ForeignKey(SousGroupe, on_delete=models.SET_NULL, verbose_name='Sous groupe', null=True, blank=True, related_name='sousgroupe')
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, verbose_name='Groupe', null=True)
    date_enregistrement = models.DateTimeField("Date d'enregistrement", default=now)
    cree_par = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name='Créé par', null=True, blank=True, related_name="membre_cree_par")
    modifie_par = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name='Modifié par', null=True, blank=True, related_name="membre_modifie_par")
    supprime_par = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name='Supprimé par', null=True, blank=True, related_name="membre_supprime_par")

    def __str__(self):
        return f"{self.nom} {self.prenom}"
    
        
    
class ListPresence(SoftDeleteModel):
    date_presence = models.DateTimeField("Date de la présence", default=now)
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, )
    
    def __str__(self):
        return f'La liste de présence du {self.date_presence}'
    
class Presence(SoftDeleteModel):
    presencechoices = (
        ('présent', 'Présent'),
        ('absent', 'Absent'),
        ('permissionnaire', 'Permissionnaire'),
        ('retard', 'Retard'),
    )
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, verbose_name="Membre")
    date_presence = models.DateTimeField("Date de la présence", default=now)
    presence = models.CharField(max_length=30, choices=presencechoices)
    liste_presence = models.ForeignKey(ListPresence, on_delete=models.CASCADE, verbose_name='Liste de présence')
    cree_par = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name='Créé par', null=True, blank=True, related_name="presence_cree_par")
    
class Cotisation(SoftDeleteModel):
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100, verbose_name='Nom de la cotisation')
    date_creation = models.DateTimeField(default=now)
    cree_par = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name='Créé par', null=True, blank=True, related_name="cotisation_cree_par")
    ouverte = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nom
    
    def get_membre_total(self, membre:Membre):
        cotisation_items = self.cotisationitem_set.filter(membre=membre)
        somme_total = sum([item.montant for item in cotisation_items])
        return somme_total
    
class CotisationItem(SoftDeleteModel):
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, verbose_name="Membre")
    date_cotisation = models.DateTimeField("Date de la cotisation", default=now)
    cotisation = models.ForeignKey(Cotisation, on_delete=models.CASCADE)
    montant = models.PositiveIntegerField(verbose_name='Montant payé')
    cree_par = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name='Créé par', null=True, blank=True, related_name="cotisation_item_cree_par")
    
    
class Depense(SoftDeleteModel):
    date_depense = models.DateTimeField(verbose_name="Date", default=now)
    montant = models.PositiveIntegerField(verbose_name="Montant")
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)
    sous_groupe = models.ForeignKey(SousGroupe, on_delete=models.SET_NULL, verbose_name='Sous groupe', null=True, blank=True, related_name='depensesousgroupe')
    motif = models.TextField()
    cree_par = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name='Créé par', null=True, blank=True)
    
class Promesse(SoftDeleteModel):
    types_choices = (
        ("Espèce" , "Espèce"),
        ("Nature" , "Nature")
    )
    date_promesse = models.DateTimeField(verbose_name="Date", default=now)
    date_echeance = models.DateTimeField(verbose_name="Date d'échéance", default=now)
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, verbose_name="Membre")
    cotisation = models.ForeignKey(Cotisation, on_delete=models.CASCADE)
    type_promesse = models.CharField(max_length=20, choices=types_choices, default='Espèce', null=True, blank=True)
    unite =  models.CharField(max_length=100,  default='Francs CFA', null=True, blank=True)
    quantite = models.PositiveIntegerField(verbose_name='Quantité')
    cree_par = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name='Créé par', null=True, blank=True, related_name="promesse_cree_par")
    
    def get_status(self):
        """Une fonction pour avoir le status cotisation, est-ce que c'est soldé ou pas et le reste du montant"""
        if self.type_promesse == "Nature":
            return "Promesse en nature non gérable"
        cotisation_items = CotisationItem.objects.filter(membre=self.membre, cotisation=self.cotisation)
        montant_total = 0
        for item in cotisation_items:
            montant_total += item.montant
        if montant_total - self.quantite >= 0:
            return f'Soldée  surplus {montant_total - self.quantite}'
        else:
            return f'Non soldée  restant { -montant_total + self.quantite}'
    
def getMembres(user:User):
    "Une fonction qui permet de récupérer des membres selon l'utilisateur"
    if user.role == "admin" or user.role =="responsable":
        return user.groupe.membre_set.all().order_by('nom', 'prenom')
    elif user.role == "sous_responsable":
        return user.groupe.membre_set.filter(sous_groupe=user.sous_groupe).order_by('nom', 'prenom')
    else:
        return []
    
def getCotisationItem(user:User):
    "Une fonction qui permet de recupérer les cotisations items des membres selon l'utilisteur"
    if user.role == "admin" or user.role =="responsable":
        return CotisationItem.objects.filter(cotisation__groupe=user.groupe).order_by("-date_cotisation")
    elif user.role == "sous_responsable":
        return CotisationItem.objects.filter(cotisation__groupe=user.groupe, membre__sous_groupe=user.sous_groupe).order_by("-date_cotisation")
    else:
        return []
    
def getPresence(user:User):
    "Une fonction qui retourne la liste de présence selon l'utilisateur"
    if user.role == "admin" or user.role =="responsable":
        return Presence.objects.filter(liste_presence__groupe=user.groupe)
    elif user.role == "sous_responsable":
        return Presence.objects.filter(liste_presence__groupe=user.groupe, membre__sous_groupe=user.sous_groupe)
    else:
        return []
    
def getSousGroupe(user:User):
    if user.role == "admin" or user.role =="responsable":
        return SousGroupe.objects.filter(groupe=user.groupe).order_by('nom')
    elif user.role == "sous_responsable":
        return SousGroupe.objects.filter(groupe=user.groupe, id=user.sous_groupe.id).order_by('nom')
    else:
        return []