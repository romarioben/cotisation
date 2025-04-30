from django import forms
from .models0 import Groupe
from . import models


class GroupeForm(forms.ModelForm):
    
    class Meta:
        model = Groupe
        fields = ["nom"]
        widgets = {
            'nom' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Nom du groupe'}),
        }
        

class MembreForm(forms.ModelForm):
    
    class Meta:
        model = models.Membre
        fields = ["nom", "prenom", "sexe", "profession", "numero", "email", "nationalite", "date_naissance"]
        widgets = {
            'nom' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Nom'}),
            'prenom' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Prénom'}),
            'sexe' : forms.RadioSelect(),
            'profession' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'profession'}),
            'numero' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Numéro'}),
            'email' : forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Email'}),
            'nationalite' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Nationalité'}),
            'date_naissance' : forms.DateInput(attrs={'class':'form-select', 'type':'date'}),
        }
        
        
class PresenceForm(forms.ModelForm):
    
    class Meta:
        model = models.Presence
        fields = ["presence", ]
        widgets = {
            'presence' : forms.Select(attrs={'class':'form-select'}),
        }
        
        
class CotisationForm(forms.ModelForm):
    
    class Meta:
        model = models.Cotisation
        fields = ["nom",]
        widgets = {
            'nom' : forms.TextInput(attrs={'class':'form-control'}),
        }
        
class PromesseForm(forms.ModelForm):
    
    class Meta:
        model = models.Promesse
        fields = ["date_echeance", "type_promesse", "unite", "quantite"]
        widgets = {
            'date_echeance' : forms.DateInput(attrs={'class':'form-control', 'type': "date"}),
            'type_promesse' : forms.Select(attrs={'class':'form-select', 'type': "date"}),
            'unite' : forms.TextInput(attrs={'class':'form-control'}),
            'quantite' : forms.NumberInput(attrs={'class':'form-select'}),
        }
        
class SousGroupeForm(forms.ModelForm):
    
    class Meta:
        model = models.SousGroupe
        fields = ["nom"]
        widgets = {
            'nom' : forms.TextInput(attrs={'class':'form-control'}),
        }