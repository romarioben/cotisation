from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.Groupe)
class GroupeModelAdmin(admin.ModelAdmin):
    list_display = ['id','nom',]
    
    
@admin.register(models.SousGroupe)
class SousGroupeModelAdmin(admin.ModelAdmin):
    list_display = ['id','nom', 'groupe']


@admin.register(models.Membre)
class MembreModelAdmin(admin.ModelAdmin):
    list_display = ['id','nom','prenom', 'sexe', 'profession', 'groupe']


@admin.register(models.Presence)
class PresenceModelAdmin(admin.ModelAdmin):
    list_display = ['id','membre','presence', 'date_presence', 'liste_presence', 'cree_par']


@admin.register(models.ListPresence)
class ListePresenceModelAdmin(admin.ModelAdmin):
    list_display = ['id','date_presence']

# @admin.register(models.Presence)
# class PresenceModelAdmin(admin.ModelAdmin):
#     list_display = ['id','date_presence', 'membre', 'cree_par']


@admin.register(models.Cotisation)
class CotisationModelAdmin(admin.ModelAdmin):
    list_display = ['id','date_creation','groupe', 'ouverte', 'cree_par']
    
@admin.register(models.CotisationItem)
class CotisationItemModelAdmin(admin.ModelAdmin):
    list_display = ['id','date_cotisation', 'membre', 'cotisation', 'cree_par']


@admin.register(models.Depense)
class DepenseModelAdmin(admin.ModelAdmin):
    list_display = ['id','date_depense', 'motif', 'montant', 'cree_par']



