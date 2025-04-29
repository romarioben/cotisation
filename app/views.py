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
def presence_faire(request):
    page_name = "Présence"
    groupe = request.user.groupe
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    membres = models.getMembres(request.user)
    presence_membres = []
    
    for membre in membres:
        if models.Presence.objects.filter(date_presence__date=today, membre=membre, liste_presence__groupe=groupe):
            presence = models.Presence.objects.filter(date_presence__date=today, membre=membre, liste_presence__groupe=groupe)[0]
        else:
            presence = None
        presence_membres.append((membre, presence))
    form = forms.PresenceForm()
    return render(request, 'app/presence/presence_faire.html', locals())


@login_required
def presence_liste(request):
    page_name = "Présence"
    user = request.user
    listes_presences = models.ListPresence.objects.all()


@login_required
def presence_gerer(request, id):
    page_name = "Présence"
    user = request.user
    groupe = user.groupe
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    if models.ListPresence.objects.filter(date_presence__date=today, groupe = groupe):
        liste_presence = models.ListPresence.objects.filter(date_presence__date=today, groupe = groupe)[0]
    else:
        liste_presence = models.ListPresence.objects.create()
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
def ajouter_cotisation_form(request, id):
    pass