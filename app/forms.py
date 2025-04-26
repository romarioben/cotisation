from django import forms
from .models0 import Groupe


class GroupeForm(forms.ModelForm):
    
    class Meta:
        model = Groupe
        fields = ["nom"]
        widgets = {
            'nom' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Nom du groupe'}),
        }