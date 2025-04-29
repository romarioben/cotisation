from django.shortcuts import render, get_object_or_404, redirect, HttpResponse

from django.http import JsonResponse, FileResponse, HttpResponseForbidden
from . import models#, forms, autresfonctions, report
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import  Q
# import html
# from bs4 import BeautifulSoup
import unidecode
from django.utils.timezone import now
import pandas as pd
import numpy as np
from django.core.paginator import Paginator
from auth_app.forms import SignupForm
from . import forms
# Create your views here.

@login_required
def app_home(request):
    page_name = "Dashboard"
    return render(request, "app/home.html", locals())

def registration(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        form1 = forms.GroupeForm(request.POST)
        if form.is_valid() and form1.is_valid():
            user = form.save()
            groupe = form1.save()
        else:
            return render(request, 'app/registration.html', locals())
        user.groupe = groupe
        user.role = "admin"
        user.save()
        return redirect('login')
    else:
        form = SignupForm()
        form1 = forms.GroupeForm()
        return render(request, 'app/registration.html', locals())

@login_required
def membre(request):
    user = request.user
    groupe = user.groupe
    page_name = "Membres"
    form = forms.MembreForm()
    membres = models.getMembres(user)
    if request.method == "POST":
        form = forms.MembreForm(request.POST)
        if form.is_valid():
            membre = form.save()
            membre.groupe = groupe
            membre.cree_par = user
            membre.save()
            messages.success(request, "Un membre ajouté avec succès")
            form = forms.MembreForm()
            return redirect('membre')
    return render(request, "app/membre/membre.html", locals())

class UpdateMembre(View, LoginRequiredMixin):
    def get(self, request, id):
        membre = get_object_or_404(models.Membre, id=id)
        form = forms.MembreForm(instance=membre)
        return render(request, "app/membre/update_membre.html", locals())
    
    def post(self, request,id):
        page_name = "Membres"
        membre = get_object_or_404(models.Membre, id=id)
        form = forms.MembreForm(request.POST)
        if form.is_valid():
            membre.nom = form.cleaned_data["nom"]
            membre.prenom = form.cleaned_data["prenom"]
            membre.nationalite = form.cleaned_data["nationalite"]
            membre.numero = form.cleaned_data["numero"]
            # membre.code = form.cleaned_data["code"]
            membre.date_naissance = form.cleaned_data["date_naissance"]
            membre.sexe = form.cleaned_data["sexe"]
            membre.email = form.cleaned_data["email"]
            membre.profession = form.cleaned_data["profession"]
            membre.sous_groupe = form.cleaned_data["sous_groupe"]
            membre.modifie_par = request.user
            membre.save()
        return redirect('membre')
            
@login_required
def presence_ajouter(request):
    user = request.user
    models.ListPresence.objects.create(groupe=user.groupe)
    return redirect('presence-liste')

@login_required  
def presence_faire(request):
    page_name = "Présence"
    groupe = request.user.groupe
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    membres = models.getMembres(request.user)
    presence_membres = []
    
    #Avoir la dernière liste de présence
    liste_presence = models.ListPresence.objects.filter(date_presence__date=today, groupe=groupe).order_by('-id')[0]
    
    for membre in membres:
        if models.Presence.objects.filter(date_presence__date=today, membre=membre, liste_presence=liste_presence):
            presence = models.Presence.objects.filter(date_presence__date=today, membre=membre, liste_presence__groupe=groupe).order_by('-id')[0]
        else:
            presence = None
        presence_membres.append((membre, presence))
    form = forms.PresenceForm()
    return render(request, 'app/presence/presence_faire.html', locals())


@login_required
def presence_liste(request):
    page_name = "Liste de Présences"
    user = request.user
    groupe = user.groupe
    listes_presences = models.ListPresence.objects.filter(groupe=groupe).order_by('-date_presence')
    liste_presence = models.ListPresence.objects.filter(groupe=groupe).order_by('-date_presence')[0]
    presences = models.Presence.objects.filter(liste_presence=liste_presence).order_by('membre__nom', 'membre__prenom')
    return render(request, 'app/presence/listes_presence.html', locals())

def presence_details(request):
    id = int(request.POST.get('liste_presence'))
    liste_presence = get_object_or_404(models.ListPresence, id=id)
    presences = models.Presence.objects.filter(liste_presence=liste_presence).order_by('membre__nom', 'membre__prenom')
    return render(request, 'app/presence/presence_details.html', locals())

@login_required
def presence_gerer(request, id):
    page_name = "Présence"
    user = request.user
    groupe = user.groupe
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    if models.ListPresence.objects.filter(date_presence__date=today, groupe = groupe):
        liste_presence = models.ListPresence.objects.filter(date_presence__date=today, groupe = groupe).order_by('-id')[0]
    else:
        liste_presence = models.ListPresence.objects.create(groupe=groupe)
    membre = models.Membre.objects.get(id=id)
    presence = models.Presence(presence=request.POST.get('presence', 'Absent'))
    presence.membre = membre
    presence.cree_par = request.user
    presence.liste_presence = liste_presence
    presence.save()
    return render(request, 'app/presence/presence.html', locals())


@login_required
def cotisation(request):
    user = request.user
    groupe = user.groupe
    page_name = "Cotisations"
    form = forms.CotisationForm()
    cotisations = models.Cotisation.objects.filter(groupe=groupe)
    if request.method == "POST":
        form = forms.CotisationForm(request.POST)
        if form.is_valid():
            cotisation = models.Cotisation(nom=request.POST.get("nom"))
            cotisation.groupe = groupe
            cotisation.cree_par = user
            cotisation.save()
            messages.success(request, "Une cotisation ajouté avec succès")
            form = forms.CotisationForm()
            return redirect('cotisation')
    return render(request, "app/cotisation/cotisation.html", locals())

class UpdateCotisation(LoginRequiredMixin, View):
    def get(self, request, id):
        cotisation = get_object_or_404(models.Cotisation, id=id)
        form = forms.CotisationForm(instance=cotisation)
        return render(request, "app/cotisation/update_cotisation.html", locals())
    def post(self, request, id):
        page_name = "Cotisations"
        cotisation = get_object_or_404(models.Cotisation, id=id)
        form = forms.CotisationForm(request.POST)
        if form.is_valid():
            cotisation.nom = form.cleaned_data["nom"]
            cotisation.save()
        return redirect('cotisation')
    
    
def cotisation_fermer_ouvrir(request, id):
    cotisation = get_object_or_404(models.Cotisation, id=id)
    cotisation.ouverte = not cotisation.ouverte
    cotisation.save()
    if cotisation.ouverte:
        response = f"""<span id="fermer-ouvrir-{id}" class="text-success">ouverte</span>"""
    else:
        response = f"""<span id="fermer-ouvrir-{id}" class="text-danger">Fermée</span>"""
    return HttpResponse(response)

@login_required
def ajouter_cotisation_form(request, membre_id):
    user = request.user
    groupe = user.groupe
    page_name = "Cotisations"
    cotisations = models.Cotisation.objects.filter(groupe=groupe, ouverte=True)
    membre = get_object_or_404(models.Membre, id=membre_id)
    return render(request, "app/forms/cotisation_item.html", locals())
    
@login_required  
def cotisation_item_gerer(request, membre_id):
    user = request.user
    groupe = user.groupe
    if request.method == "POST" and request.POST['cotisation_id'] and request.POST['montant']:
        membre = get_object_or_404(models.Membre, id=membre_id)
        cotisation=int(request.POST['cotisation_id'])
        cotisation = models.Cotisation.objects.get(id=cotisation)
        montant = int(request.POST['montant'])
        cotisation_item = models.CotisationItem(membre=membre, cree_par=user, cotisation=cotisation, montant=montant)
        cotisation_item.save()
        return render(request, "app/cotisation/cotisation_item.html", locals())
    else:
        return render(request, "app/cotisation/cotisation_item.html", locals())
    
@login_required
def cotisation_evolution(request, cotisation_id):
    cotisation = get_object_or_404(models.Cotisation, id=cotisation_id)
    page_name = f"Cotisation/Evolution {cotisation}"
    user = request.user
    today = datetime.datetime.today()
    groupe = user.groupe
    membres = models.getMembres(user=user)
    donnees_membres  = []
    for membre in membres:
        montant_total = 0
        cotisation_items = models.CotisationItem.objects.filter(membre=membre, cotisation=cotisation)
        for cotisation_item in cotisation_items:
            montant_total += cotisation_item.montant
        donnees_membres.append((membre, montant_total))
    return render(request, "app/cotisation/cotisation_evolution.html", locals())

def cotisation_details(request, membre_id, cotisation_id):
    membre = get_object_or_404(models.Membre, id=membre_id)
    cotisation = get_object_or_404(models.Cotisation, id=cotisation_id)
    cotisation_items = models.CotisationItem.objects.filter(cotisation=cotisation, membre=membre).order_by('-date_cotisation')
    montant_total = sum([item.montant for item in cotisation_items])
    return render(request, "app/cotisation/cotisation_details.html", locals())



@login_required  
def promesse_faire(request):
    
    groupe = request.user.groupe
    membres = models.getMembres(request.user)
    promesse_membres = []
    
    cotisation_id = int(request.GET.get('cotisation_id', 1))
    #Avoir la dernière liste de présence
    cotisation = models.Cotisation.objects.get(id=cotisation_id)
    page_name = f"Promesse de Cotisation {cotisation}"
    
    for membre in membres:
        if models.Promesse.objects.filter(cotisation=cotisation, membre=membre):
            promesse = models.Promesse.objects.filter(membre=membre, cotisation=cotisation).order_by('-id')[0]
        else:
            promesse = None
        promesse_membres.append((membre, promesse))
    form = forms.PromesseForm()
    return render(request, 'app/promesse/promesse_faire.html', locals())


@login_required
def promesse_liste(request):
    page_name = "Liste des Promesses"
    user = request.user
    groupe = user.groupe
    cotisations = models.Cotisation.objects.filter(groupe=groupe).order_by('-date_creation')
    cotisation = models.Cotisation.objects.filter(groupe=groupe, ouverte=True).order_by('-date_creation')[0]
    promesses = models.Promesse.objects.filter(cotisation=cotisation).order_by('membre__nom', 'membre__prenom')
    return render(request, 'app/promesse/listes_promesse.html', locals())

def promesse_details(request):
    cotisation_id = int(request.POST.get('cotisation_id'))
    cotisation = get_object_or_404(models.Cotisation, id=cotisation_id)
    promesses = models.Promesse.objects.filter(cotisation=cotisation).order_by('membre__nom', 'membre__prenom')
    return render(request, 'app/promesse/promesse_details.html', locals())

@login_required
def promesse_gerer(request, membre_id, cotisation_id):
    user = request.user
    groupe = user.groupe
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    cotisation = models.Cotisation.objects.get(id=cotisation_id)
    membre = models.Membre.objects.get(id=membre_id)
    promesse = models.Promesse(date_echeance=request.POST.get('date_echeance'))
    promesse.membre = membre
    promesse.unite = request.POST.get('unite')
    promesse.quantite = request.POST.get('quantite')
    promesse.type_promesse = request.POST.get('type_promesse')
    promesse.cotisation = cotisation
    promesse.cree_par = request.user
    promesse.save()
    return render(request, 'app/promesse/promesse.html', locals())
