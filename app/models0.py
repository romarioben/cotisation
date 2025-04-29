from django.db import models
from django.contrib.auth.models  import AbstractUser
from django_softdelete.models import SoftDeleteModel
import datetime
from django.utils.timezone import now



class Groupe(SoftDeleteModel):
    nom = models.CharField(max_length=200, verbose_name="Nom du groupe", unique=True)
    date_inscription = models.DateTimeField(default=now)
    def __str__(self):
        return f"Groupe {self.nom}"

class SousGroupe(Groupe, SoftDeleteModel):
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, related_name="groupe_sous_groupe")
    def __str__(self):
        return f'Sous groupe {self.nom}'
