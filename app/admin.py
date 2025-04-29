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
