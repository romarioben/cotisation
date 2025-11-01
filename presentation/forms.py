from django import forms
from . import models


class ContactForm(forms.ModelForm):
    
    class Meta:
        model = models.Contact
        fields = ["nom","prenom", "telephone", "email", "objet", "message"]
        widgets = {
            'nom' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Votre nom'}),
            'prenom' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Votre prénom'}),
            'telephone' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Votre numéo de téléphone'}),
            'email' : forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Votre email'}),
            'objet' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Objet'}),
            'message' : forms.Textarea(attrs={'class':'form-control', 'placeholder':'Votre message', 'rows':'4'}),
        }
        
