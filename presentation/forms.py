from django import forms
from . import models


class ContactForm(forms.ModelForm):
    
    class Meta:
        model = models.Contact
        fields = ["nom", "email", "objet", "message"]
        widgets = {
            'nom' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Votre nom et prénoms'}),
            'email' : forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Votre email'}),
            'objet' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'objet'}),
            'message' : forms.Textarea(attrs={'class':'form-control', 'placeholder':'Votre message'}),
        }
        
