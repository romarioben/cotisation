from django.db import models
from django.contrib.auth.models import AbstractUser
from django_softdelete.models import SoftDeleteModel
from app.models0 import Groupe, SousGroupe

# Create your models here.


class User(AbstractUser, SoftDeleteModel):
    
    def nom_photo_profil(self, filename):
        #Pour avoir l'extension du fichier chargé
        extension  = filename.split('.')
        return self.laboratoire + '/' + 'PROFIL' + '/' + '.' + extension[-1]
    
    RESPONSABLE = 'responsable'
    SOUS_RESPONSABLE = 'sous_responsable'
    ADMIN = 'admin'
    choices_role = (
        (RESPONSABLE, RESPONSABLE),
        (SOUS_RESPONSABLE, SOUS_RESPONSABLE),
        (ADMIN, ADMIN)
    )
    role = models.CharField(max_length=30, choices=choices_role, verbose_name='Rôle', default='reponsable')
    numero = models.PositiveSmallIntegerField(verbose_name="Numéro de téléphone", null=True, blank=True)
    poste = models.CharField(max_length=100, null=True, blank=True, verbose_name="Poste")
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, related_name="user_groupe", null=True)
    sous_groupe = models.ForeignKey(SousGroupe, on_delete=models.CASCADE, verbose_name="Sous groupe", related_name="user_sous_groupe", null=True, blank=True)
    email = models.EmailField(verbose_name='Email', null=True, blank=True, unique=True)
    is_email_verified = models.BooleanField(default=False)
    photo_profl = models.ImageField(verbose_name="Photo de profil", null=True, blank=True, upload_to=nom_photo_profil)
    