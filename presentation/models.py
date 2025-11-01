from django.db import models
from django_softdelete.models import SoftDeleteModel
# Create your models here.

class Contact(SoftDeleteModel):
    nom = models.CharField(max_length=250, verbose_name="Nom")
    prenom = models.CharField(max_length=250, verbose_name="Prénom")
    telephone = models.CharField(max_length=22, verbose_name="Numéro de téléphone", null=True, blank=True)
    email = models.EmailField(verbose_name="Email")
    objet = models.CharField(max_length=150, verbose_name="Objet")
    message = models.TextField(verbose_name='Message')