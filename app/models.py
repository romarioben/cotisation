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
    numero = models.PositiveIntegerField(verbose_name='Numéro de téléphone', null=True, blank=True)
    profession = models.CharField(max_length=100)
    sous_groupe = models.ForeignKey(SousGroupe, on_delete=models.CASCADE, verbose_name='Sous groupe', null=True, blank=True, related_name='sousgroupe')
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
    
class CotisationItem(SoftDeleteModel):
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, verbose_name="Membre")
    date_cotisation = models.DateTimeField("Date de la cotisation", default=now)
    cotisation = models.ForeignKey(Cotisation, on_delete=models.CASCADE)
    montant = models.PositiveIntegerField(verbose_name='Montant payé')
    cree_par = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name='Créé par', null=True, blank=True, related_name="cotisation_item_cree_par")
    
    
class Depense(SoftDeleteModel):
    date_depense = models.DateTimeField(verbose_name="Date", default=now)
    montant = models.PositiveIntegerField(verbose_name="Montant")
    motif = models.TextField()
    
def getMembres(user:User):
    "Une fonction qui permet de récupérer des membres selon l'utilisateur"
    if user.role == "admin" or user.role =="responsable":
        return user.groupe.membre_set.all().order_by('nom', 'prenom')
    elif user.role == "sous_responsable":
        return user.sous_groupe.membre_set.all().order_by('nom', 'prenom')
    else:
        return []