from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.http import HttpResponseForbidden, JsonResponse
from django.views import View
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import csv
import datetime
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from django.views.decorators.http import require_POST

from app.decorators import permission_role
from auth_app import models as auth_models
from auth_app.forms import SignupForm, PassWordChangeForm, UserChangeForm
from . import models, forms, models0
from io import BytesIO
from django.utils.html import escape



# ---------------------------------------------------------------------------
# Fonctions utilitaires
# ---------------------------------------------------------------------------

def offline(request):
    return render(request, 'offline.html')
def calcul_finances(user):
    "Retourne (montant_total, depense_total, montant_restant) pour l'utilisateur"
    montant_total = sum(item.montant for item in models.getCotisationItem(user))
    depense_total = sum(d.montant for d in models.getDepense(user))
    return montant_total, depense_total, montant_total - depense_total


def get_groupe(request):
    """Groupe sur lequel travailler.
    - utilisateur normal : son groupe
    - super admin : le groupe choisi (groupe_id en POST ou GET), sinon son propre groupe (peut être None)"""
    if models.est_super_admin(request.user):
        gid = request.POST.get("groupe_id") or request.GET.get("groupe_id")
        if gid:
            return models.Groupe.objects.filter(id=gid).first()
    return request.user.groupe


def get_sous_groupe_post(request, groupe):
    "Sous-groupe choisi dans le formulaire (doit appartenir au groupe), sinon None"
    sid = request.POST.get("sous_groupe_id")
    if not sid:
        return None
    return models.SousGroupe.objects.filter(id=sid, groupe=groupe).first()


MSG_PAS_DE_GROUPE = "Aucun groupe associé : sélectionnez un groupe ou liez votre compte à un groupe."


# ---------------------------------------------------------------------------
# Tableau de bord
# ---------------------------------------------------------------------------

@login_required
def app_home(request):
    page_name = "Dashboard"
    u = request.user
    membres_all = list(models.getMembres(u))
    cotisation_items_all = list(models.getCotisationItem(u))
    depenses_all = list(models.getDepense(u))

    nombre_membre = len(membres_all)
    cotisations_qs = models.getCotisations(u)
    nombre_cotisations = cotisations_qs.count()
    montant_total = sum(item.montant for item in cotisation_items_all)
    depense_total = sum(d.montant for d in depenses_all)
    montant_restant = montant_total - depense_total
    derniere_depense = depenses_all[0].montant if depenses_all else 0

    # Nouveaux compteurs (groupes / utilisateurs)
    groupes = models.getGroupes(u)
    nombre_groupes = groupes.count()
    utilisateurs_qs = models.getUsers(u)
    nombre_utilisateurs = utilisateurs_qs.count()
    derniers_utilisateurs = utilisateurs_qs.order_by('-id')[:8]

    derniere_presence = models.getListPresences(u).order_by('-date_presence').first()
    if derniere_presence:
        # cotisations collectées le même jour que la dernière présence
        derniere_collecte = sum(
            item.montant for item in cotisation_items_all
            if item.date_cotisation.date() == derniere_presence.date_presence.date()
        )
    else:
        derniere_collecte = 0

    # Les douze derniers mois
    douze_derniers_mois = [now() - relativedelta(months=i) for i in range(11, -1, -1)]

    nouveaux_membres = models.getMembres(u)[:8]

    liste_data = []
    liste_nouveau_membre = []
    for mois in douze_derniers_mois:
        collecte = sum(
            item.montant for item in cotisation_items_all
            if item.date_cotisation.year == mois.year and item.date_cotisation.month == mois.month
        )
        depense = sum(
            d.montant for d in depenses_all
            if d.date_depense.year == mois.year and d.date_depense.month == mois.month
        )
        liste_data.append((mois, collecte, depense))

        nouveau_membres = len([
            m for m in membres_all
            if m.date_enregistrement.year == mois.year and m.date_enregistrement.month == mois.month
        ])
        liste_nouveau_membre.append((mois, nouveau_membres))

    dernieres_cotisations = cotisations_qs.order_by('-date_creation')[:4]

    stats_derniere_presence = {}
    if derniere_presence:
        base = models.Presence.objects.filter(liste_presence=derniere_presence)
        stats_derniere_presence["present"] = base.filter(presence="présent").count()
        stats_derniere_presence["absent"] = base.filter(presence="absent").count()
        stats_derniere_presence["retard"] = base.filter(presence="retard").count()
        stats_derniere_presence["permission"] = base.filter(presence="permissionnaire").count()

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


# ---------------------------------------------------------------------------
# Utilisateurs
# ---------------------------------------------------------------------------

@login_required
@permission_role(["admin"])
def users(request):
    page_name = "Utilisateurs"
    groupe = get_groupe(request)
    sous_groupes = models.getSousGroupe(request.user, groupe)
    users = models.getUsers(request.user)
    groupes = models.getGroupes(request.user)
    if request.method == "POST":
        form = SignupForm(request.POST)
        role = request.POST.get("role", None)
        if groupe is None:
            messages.error(request, MSG_PAS_DE_GROUPE)
            return redirect("users")
        sous_groupe = get_sous_groupe_post(request, groupe)
        if form.is_valid():
            user = form.save()
            user.groupe = groupe
            user.sous_groupe = sous_groupe
            user.role = role
            user.save()
            messages.success(request, "Un utilisateur ajouté avec succès")
            return redirect("users")
        messages.error(request, "L'utilisateur n'a pas été ajouté, vérifier les données entrées et réessayer")
        return render(request, "app/registration_user.html", locals())

    form = SignupForm()
    return render(request, "app/registration_user.html", locals())


class UpdateUser(LoginRequiredMixin, View):
    def _charger(self, request, id):
        user0 = get_object_or_404(auth_models.User, id=id)
        if not models.est_super_admin(request.user) and user0.groupe_id != request.user.groupe_id:
            return None
        return user0

    def get(self, request, id):
        montant_total, depense_total, montant_restant = calcul_finances(request.user)
        user0 = self._charger(request, id)
        if user0 is None:
            return HttpResponseForbidden("Vous n'êtes pas autorisé(e)")
        groupe = user0.groupe
        sous_groupes = models.getSousGroupe(request.user, groupe)
        return render(request, "app/forms/user.html", locals())

    def post(self, request, id):
        user0 = self._charger(request, id)
        if user0 is None:
            return HttpResponseForbidden("Vous n'êtes pas autorisé(e)")
        sous_groupe = get_sous_groupe_post(request, user0.groupe)
        username = request.POST.get("username")
        if username:
            user0.username = username
            user0.sous_groupe = sous_groupe
            user0.save()
        return redirect("users")


@login_required
def profile(request):
    montant_total, depense_total, montant_restant = calcul_finances(request.user)
    user = request.user
    page_name = 'Profil'
    user_change_form = UserChangeForm(instance=user)
    form = PassWordChangeForm(user=user)
    return render(request, 'app/profile.html', locals())


class PassWordChangeView(LoginRequiredMixin, View):
    def get(self, request):
        montant_total, depense_total, montant_restant = calcul_finances(request.user)
        user = request.user
        form = PassWordChangeForm(user=user)
        return render(request, 'app/passwordChange.html', locals())

    def post(self, request):
        montant_total, depense_total, montant_restant = calcul_finances(request.user)
        user = request.user
        user_change_form = UserChangeForm(instance=user)
        form1 = PassWordChangeForm(user, request.POST)
        if form1.is_valid():
            form1.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Félicitation Mot de passe changé  avec succès')
            return redirect('profile')
        messages.warning(request, 'Données entrées invalides')
        form = form1
        return render(request, 'app/profile.html', locals())


@login_required
def user_change(request):
    montant_total, depense_total, montant_restant = calcul_finances(request.user)
    user = request.user
    form = PassWordChangeForm(user=user)
    if request.method == "POST":
        user_change_form = UserChangeForm(request.POST, instance=user)
        if user_change_form.is_valid():
            user.last_name = user_change_form.cleaned_data['last_name']
            user.sexe = user_change_form.cleaned_data['sexe']
            user.first_name = user_change_form.cleaned_data['first_name']
            user.email = user_change_form.cleaned_data['email']
            user.numero = user_change_form.cleaned_data['numero']
            user.poste = user_change_form.cleaned_data['poste']
            user.save()
    return render(request, 'app/profile.html', locals())


# ---------------------------------------------------------------------------
# Membres
# ---------------------------------------------------------------------------

@login_required
def membre(request):
    montant_total, depense_total, montant_restant = calcul_finances(request.user)
    user = request.user
    groupe = get_groupe(request)
    groupes = models.getGroupes(user)
    sous_groupes = models.getSousGroupe(user, groupe)
    page_name = "Membres"
    form = forms.MembreForm()
    membres = models.getMembres(user)
    if request.method == "POST":
        form = forms.MembreForm(request.POST)
        if groupe is None:
            messages.error(request, MSG_PAS_DE_GROUPE)
            return redirect('membre')
        sous_groupe = get_sous_groupe_post(request, groupe)
        if form.is_valid():
            membre = form.save()
            membre.groupe = groupe
            membre.cree_par = user
            membre.sous_groupe = sous_groupe
            membre.save()
            messages.success(request, "Un membre ajouté avec succès")
            return redirect('membre')
    return render(request, "app/membre/membre.html", locals())


class UpdateMembre(LoginRequiredMixin, View):
    def get(self, request, id):
        user = request.user
        membre = get_object_or_404(models.getMembres(user), id=id)
        groupe = membre.groupe
        sous_groupes = models.getSousGroupe(user, groupe)
        form = forms.MembreForm(instance=membre)
        return render(request, "app/membre/update_membre.html", locals())

    def post(self, request, id):
        montant_total, depense_total, montant_restant = calcul_finances(request.user)
        page_name = "Membres"
        membre = get_object_or_404(models.getMembres(request.user), id=id)
        form = forms.MembreForm(request.POST)
        sous_groupe = get_sous_groupe_post(request, membre.groupe)
        if form.is_valid():
            membre.nom = form.cleaned_data["nom"]
            membre.prenom = form.cleaned_data["prenom"]
            membre.nationalite = form.cleaned_data["nationalite"]
            membre.numero = form.cleaned_data["numero"]
            membre.date_naissance = form.cleaned_data["date_naissance"]
            membre.sexe = form.cleaned_data["sexe"]
            membre.email = form.cleaned_data["email"]
            membre.profession = form.cleaned_data["profession"]
            membre.modifie_par = request.user
            membre.sous_groupe = sous_groupe
            membre.save()
        return redirect('membre')


@login_required
def supprime_membre(request, id):
    membre = get_object_or_404(models.getMembres(request.user), id=id)
    membre.delete()
    return HttpResponse('')


# ---------------------------------------------------------------------------
# Présences
# ---------------------------------------------------------------------------

@login_required
def presence_ajouter(request):
    groupe = get_groupe(request)
    if groupe is None:
        messages.error(request, MSG_PAS_DE_GROUPE)
        return redirect('presence-liste')
    models.ListPresence.objects.create(groupe=groupe)
    return redirect('presence-liste')


@login_required
def presence_faire(request):
    montant_total, depense_total, montant_restant = calcul_finances(request.user)
    page_name = "Présence"
    groupe = get_groupe(request)
    if groupe is None:
        messages.error(request, MSG_PAS_DE_GROUPE)
        return redirect('presence-liste')
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    membres = models.getMembres(request.user)
    if models.est_super_admin(request.user):
        membres = membres.filter(groupe=groupe)
    presence_membres = []

    # Dernière liste de présence du jour, sinon on la crée
    liste_presence = (
        models.ListPresence.objects.filter(date_presence__date=today, groupe=groupe).order_by('-id').first()
        or models.ListPresence.objects.create(groupe=groupe)
    )

    for membre in membres:
        presence = models.Presence.objects.filter(
            date_presence__date=today, membre=membre, liste_presence=liste_presence
        ).order_by('-id').first()
        presence_membres.append((membre, presence))
    form = forms.PresenceForm()
    return render(request, 'app/presence/presence_faire.html', locals())


@login_required
def presence_liste(request):
    montant_total, depense_total, montant_restant = calcul_finances(request.user)
    page_name = "Liste de Présences"
    user = request.user
    groupe = get_groupe(request)
    listes_presences = models.getListPresences(user).order_by('-date_presence')
    liste_presence = listes_presences.first()
    if liste_presence:
        presences = models.getPresence(user).filter(liste_presence=liste_presence).order_by('membre__nom', 'membre__prenom')
    else:
        presences = []
    return render(request, 'app/presence/listes_presence.html', locals())


@login_required
def presence_details(request):
    user = request.user
    id = int(request.POST.get('liste_presence'))
    liste_presence = get_object_or_404(models.getListPresences(user), id=id)
    presences = models.getPresence(user).filter(liste_presence=liste_presence).order_by('membre__nom', 'membre__prenom')
    return render(request, 'app/presence/presence_details.html', locals())


@login_required
def presence_gerer(request, id):
    montant_total, depense_total, montant_restant = calcul_finances(request.user)
    page_name = "Présence"
    user = request.user
    membre = get_object_or_404(models.getMembres(user), id=id)
    groupe = membre.groupe
    today = datetime.datetime.today().strftime("%Y-%m-%d")

    # Créer d'abord une liste de présence si c'est un nouveau jour
    liste_presence = (
        models.ListPresence.objects.filter(date_presence__date=today, groupe=groupe).order_by('-id').first()
        or models.ListPresence.objects.create(groupe=groupe)
    )
    presence = models.Presence(presence=request.POST.get('presence', 'absent'))
    presence.membre = membre
    presence.cree_par = user
    presence.liste_presence = liste_presence
    presence.save()
    return render(request, 'app/presence/presence.html', locals())


@login_required
def presence_modifier(request, presence_id):
    montant_total, depense_total, montant_restant = calcul_finances(request.user)
    presence = get_object_or_404(models.getPresence(request.user), id=presence_id)
    TIME_LIMIT = 2
    if now().timestamp() - presence.date_presence.timestamp() > 3600 * TIME_LIMIT:
        return HttpResponse(f'''<div class="text-danger">Délai de modification de {TIME_LIMIT} heure(s) dépassé. Impossible de modifier cette présence</div>''')
    if request.method == "POST":
        presence.presence = request.POST.get('presence')
        presence.save()
        return render(request, 'app/presence/presence.html', locals())
    form = forms.PresenceForm(instance=presence)
    return render(request, "app/forms/presence.html", locals())


# ---------------------------------------------------------------------------
# Cotisations
# ---------------------------------------------------------------------------

@login_required
def cotisation(request):
    montant_total, depense_total, montant_restant = calcul_finances(request.user)
    user = request.user
    groupe = get_groupe(request)
    groupes = models.getGroupes(user)
    page_name = "Cotisations"
    form = forms.CotisationForm()
    cotisations = models.getCotisations(user)
    if request.method == "POST":
        form = forms.CotisationForm(request.POST)
        if groupe is None:
            messages.error(request, MSG_PAS_DE_GROUPE)
            return redirect('cotisation')
        if form.is_valid():
            cotisation = models.Cotisation(nom=form.cleaned_data["nom"])
            cotisation.groupe = groupe
            cotisation.cree_par = user
            cotisation.save()
            messages.success(request, "Une cotisation ajouté avec succès")
            return redirect('cotisation')
    return render(request, "app/cotisation/cotisation.html", locals())


class UpdateCotisation(LoginRequiredMixin, View):
    def get(self, request, id):
        cotisation = get_object_or_404(models.getCotisations(request.user), id=id)
        form = forms.CotisationForm(instance=cotisation)
        return render(request, "app/cotisation/update_cotisation.html", locals())

    def post(self, request, id):
        page_name = "Cotisations"
        cotisation = get_object_or_404(models.getCotisations(request.user), id=id)
        form = forms.CotisationForm(request.POST)
        if form.is_valid():
            cotisation.nom = form.cleaned_data["nom"]
            cotisation.save()
        return redirect('cotisation')


@permission_role(["admin", "responsable"])
def cotisation_fermer_ouvrir(request, id):
    cotisation = get_object_or_404(models.getCotisations(request.user), id=id)
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
    page_name = "Cotisations"
    membre = get_object_or_404(models.getMembres(user), id=membre_id)
    groupe = membre.groupe
    cotisations = models.getCotisations(user).filter(groupe=groupe, ouverte=True)
    return render(request, "app/forms/cotisation_item.html", locals())


@login_required
def cotisation_item_gerer(request, membre_id):
    user = request.user
    if request.method == "POST" and request.POST.get('cotisation_id') and request.POST.get('montant'):
        membre = get_object_or_404(models.getMembres(user), id=membre_id)
        cotisation = get_object_or_404(models.getCotisations(user), id=int(request.POST['cotisation_id']))
        montant = int(request.POST['montant'])
        cotisation_item = models.CotisationItem(membre=membre, cree_par=user, cotisation=cotisation, montant=montant)
        cotisation_item.save()
    return render(request, "app/cotisation/cotisation_item.html", locals())


@login_required
def cotisation_evolution(request, cotisation_id):
    montant_total, depense_total, montant_restant = calcul_finances(request.user)
    user = request.user
    cotisation = get_object_or_404(models.getCotisations(user), id=cotisation_id)
    groupe = cotisation.groupe
    membres = models.getMembres(user).filter(groupe=groupe)

    totaux = {}
    for item in models.CotisationItem.objects.filter(cotisation=cotisation):
        totaux[item.membre_id] = totaux.get(item.membre_id, 0) + item.montant

    donnees_membres = [(m, totaux.get(m.id, 0)) for m in membres]
    montant = sum(total for _, total in donnees_membres)

    page_name = f"Cotisation/Evolution {cotisation}. Montant Total = {montant}"
    return render(request, "app/cotisation/cotisation_evolution.html", locals())


@login_required
def cotisation_evolution_sous(request, cotisation_id):
    "Évolution d'une cotisation par sous groupe"
    montant_total, depense_total, montant_restant = calcul_finances(request.user)
    user = request.user
    cotisation = get_object_or_404(models.getCotisations(user), id=cotisation_id)
    groupe = cotisation.groupe
    sous_groupes = models.getSousGroupe(user, groupe)
    sous_groupes_dict = {sg: 0 for sg in sous_groupes}
    sous_groupes_dict["Sans sous groupe"] = 0
    montant_total = 0

    membres = models.getMembres(user).filter(groupe=groupe)
    for membre in membres:
        total_membre = cotisation.get_membre_total(membre)
        cle = membre.sous_groupe if membre.sous_groupe else "Sans sous groupe"
        sous_groupes_dict[cle] = sous_groupes_dict.get(cle, 0) + total_membre
        montant_total += total_membre

    page_name = f"Evolution par sous groupe {cotisation}. Montant total = {montant_total}"
    return render(request, 'app/cotisation/cotisation_evoution_sous.html', locals())


@login_required
def cotisation_details_membre(request, membre_id, cotisation_id):
    montant_total, depense_total, montant_restant = calcul_finances(request.user)
    membre = get_object_or_404(models.getMembres(request.user), id=membre_id)
    cotisation = get_object_or_404(models.getCotisations(request.user), id=cotisation_id)
    cotisation_items = models.CotisationItem.objects.filter(cotisation=cotisation, membre=membre).order_by('-date_cotisation')
    montant_total = sum(item.montant for item in cotisation_items)
    return render(request, "app/cotisation/cotisation_details_membre.html", locals())


@login_required
def cotisation_details(request, cotisation_id):
    user = request.user
    cotisation = get_object_or_404(models.getCotisations(user), id=cotisation_id)
    cotisation_items = models.getCotisationItem(user).filter(cotisation=cotisation)
    montant_total = sum(item.montant for item in cotisation_items)
    page_name = f"Détails de la cotisation {cotisation} Montant total : {montant_total} FCFA"
    return render(request, "app/cotisation/cotisation_details.html", locals())


@login_required
def cotisation_item_modifier(request, id):
    TIME_LIMIT = 1
    user = request.user
    cotisation_item = get_object_or_404(models.getCotisationItem(user), id=id)
    groupe = cotisation_item.cotisation.groupe
    if now().timestamp() - cotisation_item.date_cotisation.timestamp() > 3600 * TIME_LIMIT:
        return HttpResponse(f'''<div class="text-danger">Délai de modification de {TIME_LIMIT} heure(s) dépassé. Impossible de modifier cette entrée</div>''')

    if request.method == "POST":
        form = forms.CotisationItemForm(request.POST)
    else:
        form = forms.CotisationItemForm(instance=cotisation_item)
    form.fields['membre'].queryset = models.getMembres(user).filter(groupe=groupe)
    form.fields['cotisation'].queryset = models.getCotisations(user).filter(groupe=groupe, ouverte=True)

    if request.method == "POST" and form.is_valid():
        cotisation_item.membre = form.cleaned_data['membre']
        cotisation_item.montant = form.cleaned_data['montant']
        cotisation_item.cotisation = form.cleaned_data['cotisation']
        cotisation_item.save()
        return redirect('cotisation-details', cotisation_id=cotisation_item.cotisation.id)
    return render(request, "app/cotisation/item_modifier.html", locals())


# ---------------------------------------------------------------------------
# Promesses
# ---------------------------------------------------------------------------

@login_required
def promesse_faire(request):
    montant_total, depense_total, montant_restant = calcul_finances(request.user)
    user = request.user
    toutes_cotisations = models.getCotisations(user).order_by('-date_creation')
    cotisation_id = request.GET.get('cotisation_id')
    if cotisation_id:
        cotisation = get_object_or_404(toutes_cotisations, id=int(cotisation_id))
    else:
        cotisation = toutes_cotisations.first()
    if cotisation is None:
        messages.error(request, "Créez d'abord une cotisation.")
        return redirect('cotisation')

    groupe = cotisation.groupe
    membres = models.getMembres(user).filter(groupe=groupe)
    page_name = f"Promesse de Cotisation {cotisation}"

    promesse_membres = []
    for membre in membres:
        promesse = models.Promesse.objects.filter(membre=membre, cotisation=cotisation).order_by('-id').first()
        promesse_membres.append((membre, promesse))
    form = forms.PromesseForm()
    return render(request, 'app/promesse/promesse_faire.html', locals())


@login_required
def promesse_liste(request):
    montant_total, depense_total, montant_restant = calcul_finances(request.user)
    page_name = "Liste des Promesses"
    user = request.user
    groupe = get_groupe(request)
    cotisations = models.getCotisations(user).order_by('-date_creation')
    cotisation = cotisations.filter(ouverte=True).first()
    if cotisation:
        promesses = models.Promesse.objects.filter(cotisation=cotisation).order_by('membre__nom', 'membre__prenom')
    else:
        promesses = []
    return render(request, 'app/promesse/listes_promesse.html', locals())


@login_required
def promesse_details(request):
    montant_total, depense_total, montant_restant = calcul_finances(request.user)
    cotisation_id = int(request.POST.get('cotisation_id'))
    cotisation = get_object_or_404(models.getCotisations(request.user), id=cotisation_id)
    promesses = models.Promesse.objects.filter(cotisation=cotisation).order_by('membre__nom', 'membre__prenom')
    return render(request, 'app/promesse/promesse_details.html', locals())


@login_required
def promesse_gerer(request, membre_id, cotisation_id):
    user = request.user
    cotisation = get_object_or_404(models.getCotisations(user), id=cotisation_id)
    membre = get_object_or_404(models.getMembres(user), id=membre_id)
    promesse = models.Promesse(date_echeance=request.POST.get('date_echeance'))
    promesse.membre = membre
    promesse.unite = request.POST.get('unite')
    promesse.quantite = request.POST.get('quantite')
    promesse.type_promesse = request.POST.get('type_promesse')
    promesse.cotisation = cotisation
    promesse.cree_par = user
    promesse.save()
    return render(request, 'app/promesse/promesse.html', locals())


@login_required
def promesse_modifier(request, promesse_id):
    promesse = get_object_or_404(models.Promesse, id=promesse_id)
    if not models.getCotisations(request.user).filter(id=promesse.cotisation_id).exists():
        return HttpResponseForbidden("Vous n'êtes pas autorisé(e)")
    TIME_LIMIT = 1
    if now().timestamp() - promesse.date_promesse.timestamp() > 3600 * TIME_LIMIT:
        return HttpResponse(f'''<div class="text-danger">Délai de modification de {TIME_LIMIT} heure(s) dépassé. Impossible de modifier cette promesse</div>''')
    if request.method == "POST":
        form = forms.PromesseForm(request.POST)
        if form.is_valid():
            promesse.quantite = form.cleaned_data['quantite']
            promesse.date_echeance = form.cleaned_data['date_echeance']
            promesse.save()
            return render(request, 'app/promesse/promesse.html', locals())
        return render(request, "app/forms/promesse.html", locals())
    form = forms.PromesseForm(instance=promesse)
    return render(request, "app/forms/promesse.html", locals())


# ---------------------------------------------------------------------------
# Sous-groupes
# ---------------------------------------------------------------------------

@login_required
def sous_groupe(request):
    montant_total, depense_total, montant_restant = calcul_finances(request.user)
    groupe = get_groupe(request)
    groupes = models.getGroupes(request.user)
    page_name = "Sous groupe"
    sous_groupes = models.getSousGroupe(request.user)

    if request.method == "POST":
        form = forms.SousGroupeForm(request.POST)
        if groupe is None:
            messages.error(request, MSG_PAS_DE_GROUPE)
            return redirect('sous-groupe')
        if form.is_valid():
            sg = models.SousGroupe(nom=form.cleaned_data['nom'])
            sg.groupe = groupe
            sg.save()
            messages.success(request, "Un sous-groupe ajouté avec succès")
            return redirect('sous-groupe')
    else:
        form = forms.SousGroupeForm()
    return render(request, "app/sous_groupe/sous_groupe.html", locals())


class UpdateSousGroupe(LoginRequiredMixin, View):
    def get(self, request, id):
        sous_groupe = get_object_or_404(models.getSousGroupe(request.user), id=id)
        form = forms.SousGroupeForm(instance=sous_groupe)
        return render(request, "app/sous_groupe/update_sous_groupe.html", locals())

    def post(self, request, id):
        sous_groupe = get_object_or_404(models.getSousGroupe(request.user), id=id)
        form = forms.SousGroupeForm(request.POST)
        if form.is_valid():
            sous_groupe.nom = form.cleaned_data['nom']
            sous_groupe.save()
        return redirect("sous-groupe")


@login_required
def supprime_sous_groupe(request, id):
    sous_groupe = get_object_or_404(models.getSousGroupe(request.user), id=id)
    sous_groupe.delete()
    return HttpResponse('')


# ---------------------------------------------------------------------------
# Dépenses
# ---------------------------------------------------------------------------

@login_required
def depense(request):
    montant_total, depense_total, montant_restant = calcul_finances(request.user)
    user = request.user
    groupe = get_groupe(request)
    groupes = models.getGroupes(user)
    page_name = "Dépenses"
    sous_groupes = models.getSousGroupe(user, groupe)
    if models.est_super_admin(user):
        depenses = models.Depense.objects.all().order_by('-date_depense')
    else:
        depenses = models.Depense.objects.filter(groupe=groupe).order_by('-date_depense')

    if request.method == "POST":
        form = forms.DepenseForm(request.POST)
        if groupe is None:
            messages.error(request, MSG_PAS_DE_GROUPE)
            return redirect("depense")
        sous_groupe = get_sous_groupe_post(request, groupe)
        if user.sous_groupe:
            sous_groupe = user.sous_groupe
        if form.is_valid():
            nouvelle = models.Depense(groupe=groupe)
            nouvelle.motif = form.cleaned_data['motif']
            nouvelle.montant = form.cleaned_data['montant']
            nouvelle.sous_groupe = sous_groupe
            nouvelle.cree_par = user
            nouvelle.save()
            return redirect("depense")
    else:
        form = forms.DepenseForm()
    return render(request, "app/depense/depense.html", locals())


class UpdateDepense(LoginRequiredMixin, View):
    TIME_LIMIT = 1

    def get(self, request, id):
        depense = get_object_or_404(models.getDepense(request.user), id=id)
        if now().timestamp() - depense.date_depense.timestamp() > 3600 * self.TIME_LIMIT:
            return HttpResponse('''<div class="text-danger">Délai de modification d'une heure dépassé. Impossible de modifier cette dépense</div>''')
        form = forms.DepenseForm(instance=depense)
        return render(request, "app/depense/update_depense.html", locals())

    def post(self, request, id):
        depense = get_object_or_404(models.getDepense(request.user), id=id)
        if now().timestamp() - depense.date_depense.timestamp() > 3600 * self.TIME_LIMIT:
            return redirect("depense")
        form = forms.DepenseForm(request.POST)
        sous_groupe = get_sous_groupe_post(request, depense.groupe)
        if request.user.sous_groupe:
            sous_groupe = request.user.sous_groupe
        if form.is_valid():
            depense.montant = form.cleaned_data['montant']
            depense.motif = form.cleaned_data['motif']
            depense.sous_groupe = sous_groupe
            depense.save()
        return redirect("depense")


# ---------------------------------------------------------------------------
# Point des cotisations
# ---------------------------------------------------------------------------

@login_required
def point(request):
    montant_total, depense_total, montant_restant = calcul_finances(request.user)
    user = request.user
    groupe = get_groupe(request)
    cotisations = models.getCotisations(user)
    cotisation_items = models.getCotisationItem(user)
    cotisation = None

    if request.method == "POST":
        cotisation_id = request.POST.get('cotisation') or None
        date_debut = request.POST.get('date_debut') or None
        date_fin = request.POST.get('date_fin') or None

        if cotisation_id:
            cotisation = get_object_or_404(cotisations, id=cotisation_id)
            cotisation_items = cotisation_items.filter(cotisation=cotisation)
        if date_debut:
            cotisation_items = cotisation_items.filter(date_cotisation__date__gte=datetime.date.fromisoformat(date_debut))
        if date_fin:
            cotisation_items = cotisation_items.filter(date_cotisation__date__lte=datetime.date.fromisoformat(date_fin))
        cotisation_items = cotisation_items.order_by('-date_cotisation')

    montant_total = sum(item.montant for item in cotisation_items)
    return render(request, "app/point.html", locals())


# ---------------------------------------------------------------------------
# Fiches de promesse (tableau enregistré, indépendant des cotisations)
# ---------------------------------------------------------------------------

ROLES_FICHE = ["admin", "responsable"]   # + super admins (gérés par le décorateur)


def action_fiche(vue):
    "Décorateur : connecté, rôle autorisé, méthode POST uniquement"
    return login_required(permission_role(ROLES_FICHE)(require_POST(vue)))


def peut_gerer_fiche(user):
    return models.est_super_admin(user) or user.role in ROLES_FICHE


def _retour_fiche(fiche_id):
    return redirect('fiche-promesse-detail', fiche_id=fiche_id)


@login_required
def fiche_promesse(request):
    "Liste des fiches + formulaire de création"
    montant_total, depense_total, montant_restant = calcul_finances(request.user)
    page_name = "Fiches de promesse"
    user = request.user
    groupes = models.getGroupes(user)
    fiches = models.getFiches(user)
    peut_gerer = peut_gerer_fiche(user)
    return render(request, "app/promesse/fiche_promesse.html", locals())


@action_fiche
def fiche_promesse_creer(request):
    user = request.user
    groupe = user.groupe          # None pour un super admin sans groupe
    if groupe is None and not models.est_super_admin(user):
        messages.error(request, MSG_PAS_DE_GROUPE)
        return redirect('fiche-promesse')
    nom = request.POST.get("nom", "").strip() or f"Fiche du {now():%d/%m/%Y}"
    fiche = models.FichePromesse.objects.create(nom=nom, groupe=groupe, cree_par=user)
    membres = models.Membre.objects.all() if groupe is None else models.Membre.objects.filter(groupe=groupe)
    models.LignePromesse.objects.bulk_create(
        [models.LignePromesse(fiche=fiche, membre=m) for m in membres.order_by('nom', 'prenom')]
    )
    messages.success(request, "Fiche créée avec tous les membres")
    return _retour_fiche(fiche.id)


@login_required
def fiche_promesse_detail(request, fiche_id):
    montant_total, depense_total, montant_restant = calcul_finances(request.user)
    fiche = get_object_or_404(models.getFiches(request.user), id=fiche_id)
    page_name = f"Fiche de promesse : {fiche.nom}"
    lignes = _lignes_fiche(fiche)
    total_promis = sum(l.montant_promis for l in lignes)
    total_paye = sum(l.total_paye() for l in lignes)
    peut_gerer = peut_gerer_fiche(request.user)
    return render(request, "app/promesse/fiche_promesse_detail.html", locals())


@action_fiche
def fiche_promesse_enregistrer(request, fiche_id):
    "Enregistre les montants promis de toute la fiche"
    fiche = get_object_or_404(models.getFiches(request.user), id=fiche_id)
    for ligne in fiche.lignes.all():
        valeur = request.POST.get(f"promis_{ligne.id}")
        if valeur is None:
            continue
        try:
            valeur = max(int(valeur or 0), 0)
        except ValueError:
            continue
        if valeur != ligne.montant_promis:
            ligne.montant_promis = valeur
            ligne.save(update_fields=["montant_promis"])
    messages.success(request, "Montants promis enregistrés")
    return _retour_fiche(fiche.id)


@action_fiche
def fiche_promesse_payer(request, ligne_id):
    "Ajoute un paiement à une ligne"
    ligne = get_object_or_404(
        models.LignePromesse.objects.select_related('fiche'),
        id=ligne_id, fiche__in=models.getFiches(request.user),
    )
    try:
        montant = int(request.POST.get("montant", 0))
    except ValueError:
        montant = 0
    if montant > 0:
        models.PaiementPromesse.objects.create(ligne=ligne, montant=montant, cree_par=request.user)
    else:
        messages.error(request, "Montant invalide")
    return _retour_fiche(ligne.fiche_id)


@action_fiche
def fiche_promesse_paiement_supprimer(request, paiement_id):
    paiement = get_object_or_404(
        models.PaiementPromesse.objects.select_related('ligne'),
        id=paiement_id, ligne__fiche__in=models.getFiches(request.user),
    )
    fiche_id = paiement.ligne.fiche_id
    paiement.delete()
    return _retour_fiche(fiche_id)


@action_fiche
def fiche_promesse_solder(request, ligne_id):
    "Bascule l'état soldé / non soldé d'une ligne"
    ligne = get_object_or_404(
        models.LignePromesse.objects.select_related('fiche'),
        id=ligne_id, fiche__in=models.getFiches(request.user),
    )
    ligne.solde = not ligne.solde
    ligne.save(update_fields=["solde"])
    return _retour_fiche(ligne.fiche_id)


@action_fiche
def fiche_promesse_sync(request, fiche_id):
    "Ajoute à la fiche les membres enregistrés après sa création"
    fiche = get_object_or_404(models.getFiches(request.user), id=fiche_id)
    deja = set(fiche.lignes.exclude(membre__isnull=True).values_list('membre_id', flat=True))
    membres = models.Membre.objects.all() if fiche.groupe_id is None else models.Membre.objects.filter(groupe=fiche.groupe)
    nouveaux = list(membres.exclude(id__in=deja).order_by('nom', 'prenom'))
    models.LignePromesse.objects.bulk_create(
        [models.LignePromesse(fiche=fiche, membre=m) for m in nouveaux]
    )
    messages.success(request, f"{len(nouveaux)} membre(s) ajouté(s) à la fiche")
    return _retour_fiche(fiche.id)


@action_fiche
def fiche_promesse_supprimer(request, fiche_id):
    fiche = get_object_or_404(models.getFiches(request.user), id=fiche_id)
    fiche.delete()
    messages.success(request, "Fiche supprimée")
    return redirect('fiche-promesse')

@login_required
def fiche_promesse_export(request, fiche_id):
    "Export Excel (CSV) de la fiche"
    fiche = get_object_or_404(models.getFiches(request.user), id=fiche_id)
    lignes = _lignes_fiche(fiche)

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="fiche_promesse_{fiche.id}.csv"'
    response.write("\ufeff")   # pour qu'Excel lise bien les accents
    writer = csv.writer(response, delimiter=";")
    writer.writerow(["Nom et Prénom", "Montant Promis", "Montant Payé", "Montant Total payé"])
    total_promis = total_paye = 0
    for l in lignes:
        total = l.total_paye()
        total_promis += l.montant_promis
        total_paye += total
        total_txt = (f"{total}f" if total else "") + (" Soldé" if l.solde else "")
        writer.writerow([
            l.nom_affiche,
            l.montant_promis or "",
            "+".join(f"{p.montant}f" for p in l.paiements.all()),
            total_txt.strip(),
        ])
    writer.writerow(["TOTAL", total_promis, "", f"{total_paye}f"])
    return response

def _lignes_fiche(fiche):
    "Lignes de la fiche : d'abord les membres (ordre alphabétique), puis les personnes ajoutées à la main"
    lignes = list(fiche.lignes.select_related('membre').prefetch_related('paiements'))
    lignes.sort(key=lambda l: (l.membre_id is None, l.nom_affiche.lower() if l.membre_id else "", l.id))
    return lignes


@action_fiche
def fiche_promesse_ajouter_ligne(request, fiche_id):
    "Ajoute à la fiche une personne qui n'est pas dans la liste des membres"
    fiche = get_object_or_404(models.getFiches(request.user), id=fiche_id)
    nom = request.POST.get("nom", "").strip()
    prenom = request.POST.get("prenom", "").strip()
    if not nom and not prenom:
        messages.error(request, "Saisissez au moins le nom ou le prénom")
        return _retour_fiche(fiche.id)
    try:
        promis = max(int(request.POST.get("montant_promis") or 0), 0)
    except ValueError:
        promis = 0
    models.LignePromesse.objects.create(fiche=fiche, nom=nom, prenom=prenom, montant_promis=promis)
    messages.success(request, f"{nom} {prenom} ajouté(e) à la fiche".replace("  ", " "))
    return _retour_fiche(fiche.id)


@action_fiche
def fiche_promesse_ligne_supprimer(request, ligne_id):
    "Supprime une personne ajoutée à la main (les membres ne peuvent pas être retirés ici)"
    ligne = get_object_or_404(
        models.LignePromesse.objects.select_related('fiche'),
        id=ligne_id, membre__isnull=True, fiche__in=models.getFiches(request.user),
    )
    fiche_id = ligne.fiche_id
    ligne.delete()
    return _retour_fiche(fiche_id)


@login_required
def fiche_promesse_pdf(request, fiche_id):
    "Téléchargement de la fiche en PDF"
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

    fiche = get_object_or_404(models.getFiches(request.user), id=fiche_id)
    lignes = _lignes_fiche(fiche)

    donnees = [["Nom et Prénom", "Montant Promis", "Montant Payé", "Montant Total payé"]]
    total_promis = total_paye = 0
    for l in lignes:
        total = l.total_paye()
        total_promis += l.montant_promis
        total_paye += total
        total_txt = (f"{total}f" if total else "") + (" Soldé" if l.solde else "")
        donnees.append([
            l.nom_affiche,
            l.montant_promis or "",
            "+".join(f"{p.montant}f" for p in l.paiements.all()),
            total_txt.strip(),
        ])
    donnees.append(["TOTAL", total_promis, "", f"{total_paye}f"])

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    titre = fiche.nom + (f" ({fiche.groupe})" if fiche.groupe else "")
    table = Table(donnees, colWidths=[200, 90, 130, 100], repeatRows=1)
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    doc.build([Paragraph(escape(titre), styles["Title"]), Spacer(1, 12), table])

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="fiche_promesse_{fiche.id}.pdf"'
    return response


# ---------------------------------------------------------------------------
# NOUVEAU : Cartes de cotisation (52 semaines)
# ---------------------------------------------------------------------------

VERSEMENT_MIN = 100   # versement minimum par semaine (Frs)


@login_required
def carte(request):
    "Liste des cartes (groupées par sous-groupe) + création d'une carte"
    page_name = "Cartes"
    user = request.user
    membres = models.getMembres(user).select_related('sous_groupe')
    sous_groupes = models.getSousGroupe(user)

    if request.method == "POST":
        membre_obj = None
        membre_id = request.POST.get("membre")
        if membre_id:
            membre_obj = membres.filter(pk=membre_id).first()

        # Obligatoires : nom et prénoms + numéro
        nom = request.POST.get("nom", "").strip()
        if not nom and membre_obj:
            nom = f"{membre_obj.nom} {membre_obj.prenom}"
        contact = request.POST.get("contact", "").strip()
        if not contact and membre_obj and membre_obj.numero:
            contact = membre_obj.numero
        if not nom or not contact:
            messages.error(request, "Le nom et prénoms et le numéro sont obligatoires.")
            return redirect("carte")

        # Facultatif : versement (minimum 100 Frs, 100 par défaut)
        versement_txt = request.POST.get("versement", "").strip()
        if versement_txt:
            try:
                versement = int(versement_txt)
            except ValueError:
                versement = 0
            if versement < VERSEMENT_MIN:
                messages.error(request, f"Le versement minimum est de {VERSEMENT_MIN} Frs.")
                return redirect("carte")
        else:
            versement = VERSEMENT_MIN

        # Sous-groupe : celui choisi, sinon celui du membre
        sous_groupe_obj = None
        sg_id = request.POST.get("sous_groupe")
        if sg_id:
            sous_groupe_obj = sous_groupes.filter(pk=sg_id).first()
        if sous_groupe_obj is None and membre_obj:
            sous_groupe_obj = membre_obj.sous_groupe
        if user.role == "sous_responsable" and user.sous_groupe_id:
            sous_groupe_obj = user.sous_groupe

        if membre_obj and membre_obj.groupe_id:
            groupe_id = membre_obj.groupe_id
        else:
            groupe_id = user.groupe_id

        models.Carte.objects.create(
            groupe_id=groupe_id,
            membre=membre_obj,
            sous_groupe=sous_groupe_obj,
            nom=nom,
            contact=contact,
            maison=request.POST.get("maison", "").strip(),
            parent=request.POST.get("parent", "").strip(),
            versement=versement,
            annee=request.POST.get("annee", "").strip()[:10] or str(now().year),
            entete=request.POST.get("entete", "").strip() or "URHC JEUNESSE D'ABOMEY - CALAVI",
            objet=request.POST.get("objet", "").strip() or "Cotisation Journée Récréative",
            verset=request.POST.get("verset", "").strip(),
            cree_par=user,
        )
        messages.success(request, f"Carte créée pour {nom}.")
        return redirect("carte")

    # Recherche et filtre par sous-groupe
    q = request.GET.get("q", "").strip()
    sg = request.GET.get("sg", "").strip()
    cartes = models.getCartes(user).select_related('sous_groupe')
    if q:
        cartes = cartes.filter(nom__icontains=q)
    if sg == "none":
        cartes = cartes.filter(sous_groupe__isnull=True)
    elif sg.isdigit():
        cartes = cartes.filter(sous_groupe_id=int(sg))
    cartes = cartes.order_by('sous_groupe__nom', 'nom')   # nécessaire pour le regroupement

    semaines_haut = range(1, 45)    # 4 lignes de 11 cases
    semaines_bas = range(45, 53)    # dernière ligne : 8 cases
    return render(request, "app/carte/carte.html", locals())


@login_required
@require_POST
def carte_semaine(request, pk):
    """Enregistre les semaines cochées (appelée en JavaScript).
    Règles : dans l'ordre (1, 2, 3...) et définitif (une semaine enregistrée ne peut plus être retirée)."""
    c = get_object_or_404(models.getCartes(request.user), pk=pk)
    try:
        demandees = sorted({int(n) for n in request.POST.get("semaines", "").split(",") if n.strip()})
    except ValueError:
        return JsonResponse({"ok": False, "erreur": "Données invalides."}, status=400)
    if not demandees:
        return JsonResponse({"ok": False, "erreur": "Aucune semaine à enregistrer."}, status=400)

    deja = set(c.semaines_payees)
    libres = [n for n in range(1, 53) if n not in deja]
    if demandees != libres[:len(demandees)]:
        return JsonResponse({"ok": False, "erreur": "Les semaines doivent être marquées dans l'ordre."}, status=400)

    c.semaines_payees = sorted(deja | set(demandees))
    c.save(update_fields=["semaines_payees"])
    return JsonResponse({"ok": True, "payees": c.semaines_payees, "nb": len(c.semaines_payees), "total": c.total_paye()})


@login_required
@require_POST
def carte_annee(request, pk):
    "Modifie l'année affichée sur la carte (appelée en JavaScript)"
    c = get_object_or_404(models.getCartes(request.user), pk=pk)
    c.annee = request.POST.get("annee", "").strip()[:10]
    c.save(update_fields=["annee"])
    return JsonResponse({"ok": True, "annee": c.annee})


@login_required
@require_POST
def carte_supprimer(request, pk):
    c = get_object_or_404(models.getCartes(request.user), pk=pk)
    c.delete()   # suppression "douce" (SoftDeleteModel)
    messages.success(request, "Carte supprimée.")
    return redirect("carte")


# ---------------------------------------------------------------------------
# Téléchargement des cartes en PDF
# ---------------------------------------------------------------------------

def _pdf_carte(c=None, annee_vierge=""):
    "Dessine une carte (ou une carte vierge si c est None) et retourne le PDF en octets"
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A5
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.pdfgen import canvas as rl_canvas

    largeur, hauteur = A5
    buffer = BytesIO()
    pdf = rl_canvas.Canvas(buffer, pagesize=A5)

    marge = 20
    x0, y0 = marge, marge
    w, h = largeur - 2 * marge, hauteur - 2 * marge
    interieur = 16
    xg = x0 + interieur            # bord gauche du contenu
    xd = x0 + w - interieur        # bord droit du contenu
    vert_clair = colors.HexColor("#cfe8c9")
    vert_paye = colors.HexColor("#2e7d32")
    rose = colors.HexColor("#e91e8c")

    # Fond de la carte
    pdf.setFillColor(vert_clair)
    pdf.setStrokeColor(colors.black)
    pdf.setLineWidth(2)
    pdf.roundRect(x0, y0, w, h, 18, stroke=1, fill=1)

    def texte_centre(texte, y, police, taille):
        while stringWidth(texte, police, taille) > (xd - xg) and taille > 6:
            taille -= 0.5
        pdf.setFont(police, taille)
        pdf.drawCentredString(x0 + w / 2, y, texte)

    entete = c.entete if c else "URHC JEUNESSE D'ABOMEY - CALAVI"
    objet = c.objet if c else "Cotisation Journée Récréative"
    annee = ((c.annee if c else annee_vierge) or "").strip() or "20......"
    verset = c.verset if c else "AGGEE 2 : 8"

    # En-tête
    y = y0 + h - 38
    pdf.setFillColor(colors.black)
    texte_centre(entete, y, "Helvetica-Bold", 15)
    texte_centre(f"{objet} {annee}", y - 20, "Helvetica-Bold", 11)
    if verset:
        texte_centre(verset, y - 40, "Helvetica-Bold", 12)

    # Lignes à remplir (pointillés)
    lignes = [
        ("Nom & Prénoms :", c.nom if c else ""),
        ("Contact :", c.contact if c else ""),
        ("Maison :", c.maison if c else ""),
        ("Parent :", c.parent if c else ""),
        ("Versement par semaine :", f"{c.versement} Frs" if c else ""),
    ]
    y_ligne = y - 70
    for etiquette, valeur in lignes:
        est_versement = etiquette.startswith("Versement")
        pdf.setFillColor(colors.black)
        pdf.setFont("Helvetica-Bold", 10.5)
        pdf.drawString(xg, y_ligne, etiquette)
        decal = stringWidth(etiquette, "Helvetica-Bold", 10.5) + 5
        fin = xd - 24 if (c is None and est_versement) else xd
        taille = 10.5
        while stringWidth(valeur, "Helvetica", taille) > (fin - xg - decal) and taille > 6:
            taille -= 0.5
        pdf.setFont("Helvetica", taille)
        pdf.drawString(xg + decal, y_ligne, valeur)
        pdf.setLineWidth(0.7)
        pdf.setDash(1, 2)
        pdf.line(xg + decal, y_ligne - 3, fin, y_ligne - 3)
        pdf.setDash()
        if c is None and est_versement:
            pdf.setFont("Helvetica", 10.5)
            pdf.drawRightString(xd, y_ligne, "Frs")
        y_ligne -= 26

    # Grille des 52 semaines : 4 lignes de 11 cases, puis 8 cases
    payees = set(c.semaines_payees) if c else set()
    larg_grille = xd - xg
    cell_h = 52
    haut_grille = y_ligne + 4
    pdf.setLineWidth(1)
    for n in range(1, 53):
        if n <= 44:
            rang, col, cell_w = (n - 1) // 11, (n - 1) % 11, larg_grille / 11
        else:
            rang, col, cell_w = 4, n - 45, larg_grille / 8
        x = xg + col * cell_w
        ybas = haut_grille - (rang + 1) * cell_h
        paye = n in payees
        pdf.setStrokeColor(colors.black)
        pdf.setFillColor(vert_paye if paye else vert_clair)
        pdf.rect(x, ybas, cell_w, cell_h, stroke=1, fill=1)
        pdf.setFillColor(colors.white if paye else colors.black)
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawCentredString(x + cell_w / 2, ybas + cell_h / 2 - 4, str(n))

    # Pied de carte
    pied_y = haut_grille - 5 * cell_h - 46
    pdf.setFillColor(colors.black)
    pdf.roundRect(xg, pied_y, larg_grille, 34, 8, stroke=0, fill=1)
    pdf.setFillColor(rose)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawCentredString(x0 + w / 2, pied_y + 11, "Que Dieu vous bénisse")

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


@login_required
def carte_pdf(request, pk):
    "Télécharge une carte en PDF"
    from django.utils.text import slugify
    c = get_object_or_404(models.getCartes(request.user), pk=pk)
    reponse = HttpResponse(_pdf_carte(c), content_type="application/pdf")
    nom_fichier = f"carte_{slugify(c.nom) or c.id}.pdf"
    reponse["Content-Disposition"] = f'attachment; filename="{nom_fichier}"'
    return reponse


@login_required
def carte_vierge_pdf(request):
    "Télécharge une carte vierge en PDF (l'année peut être donnée dans l'adresse)"
    annee = request.GET.get("annee", "").strip()[:10]
    reponse = HttpResponse(_pdf_carte(None, annee), content_type="application/pdf")
    reponse["Content-Disposition"] = 'attachment; filename="carte_vierge.pdf"'
    return reponse