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
        fields = ["nom", "prenom", "sexe", "profession", "numero", "email", "nationalite", "sous_groupe", "date_naissance"]
        widgets = {
            'nom' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Nom'}),
            'prenom' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Prénom'}),
            'sexe' : forms.RadioSelect(),
            'profession' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'profession'}),
            'numero' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Numéro'}),
            'email' : forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Email'}),
            'nationalite' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Nationalité'}),
            'sous_groupe' : forms.Select(attrs={'class':'form-select'}),
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
        
