from django.db import models
from django.contrib.auth.models import AbstractUser
from django_softdelete.models import SoftDeleteModel
import datetime
from django.utils.timezone import now
from auth_app.models import User
from .models0 import Groupe, SousGroupe


# Create your models here.


class Membre(SoftDeleteModel):
    def photo_upload(self, filename):
        # Pour avoir l'extension du fichier chargé
        extension = filename.split('.')
        return str(self.groupe) + '/' + 'PROFIL' + '/' + '.' + extension[-1]
    sexe_choices = (
        ('M', 'Masculin'),
        ('F', 'Féminin')
    )
    nom = models.CharField(max_length=60)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(max_length=2, choices=sexe_choices, default='sexe', null=True, blank=True)
    code = models.CharField(verbose_name="Code", max_length=70, blank=True, null=True, unique=True)
    email = models.EmailField(verbose_name="Email", null=True, blank=True)
    date_naissance = models.DateField(verbose_name="Date de naissance", null=True, blank=True)
    nationalite = models.CharField(max_length=70, null=True, blank=True, verbose_name="Nationalité")
    numero = models.CharField(max_length=21, verbose_name='Numéro de téléphone', null=True, blank=True)
    photo = models.ImageField(verbose_name="Photo", upload_to=photo_upload, null=True, blank=True)
    profession = models.CharField(max_length=100)
    sous_groupe = models.ForeignKey(SousGroupe, on_delete=models.SET_NULL, verbose_name='Sous groupe', null=True, blank=True, related_name='sousgroupe')
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, verbose_name='Groupe', null=True)
    date_enregistrement = models.DateTimeField("Date d'enregistrement", default=now)
    cree_par = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Créé par', null=True, blank=True, related_name="membre_cree_par")
    modifie_par = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Modifié par', null=True, blank=True, related_name="membre_modifie_par")
    supprime_par = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Supprimé par', null=True, blank=True, related_name="membre_supprime_par")

    def __str__(self):
        return f"{self.nom} {self.prenom}"


class ListPresence(SoftDeleteModel):
    date_presence = models.DateTimeField("Date de la présence", default=now)
    nom = models.CharField(max_length=255, verbose_name='Titre', null=True)
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, )
    sous_groupe = models.ForeignKey(SousGroupe, on_delete=models.CASCADE, related_name="liste_presence_sous_groupe", null=True, blank=True)

    def __str__(self):
        return f'La liste de présence {self.nom} du {self.date_presence}'


class Presence(SoftDeleteModel):
    presencechoices = (
        ('présent', 'Présent'),
        ('absent', 'Absent'),
        ('permissionnaire', 'Permissionnaire'),
        ('retard', 'Retard'),
    )
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, verbose_name="Membre")
    date_presence = models.DateTimeField("Date de la présence", default=now)
    presence = models.CharField(max_length=30, choices=presencechoices)
    liste_presence = models.ForeignKey(ListPresence, on_delete=models.CASCADE, verbose_name='Liste de présence')
    cree_par = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Créé par', null=True, blank=True, related_name="presence_cree_par")


class Cotisation(SoftDeleteModel):
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100, verbose_name='Nom de la cotisation')
    date_creation = models.DateTimeField(default=now)
    cree_par = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Créé par', null=True, blank=True, related_name="cotisation_cree_par")
    ouverte = models.BooleanField(default=True)

    def __str__(self):
        return self.nom

    def get_membre_total(self, membre: Membre):
        cotisation_items = self.cotisationitem_set.filter(membre=membre)
        somme_total = sum([item.montant for item in cotisation_items])
        return somme_total


class CotisationItem(SoftDeleteModel):
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, verbose_name="Membre")
    date_cotisation = models.DateTimeField("Date de la cotisation", default=now)
    cotisation = models.ForeignKey(Cotisation, on_delete=models.CASCADE)
    montant = models.PositiveIntegerField(verbose_name='Montant payé')
    cree_par = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Créé par', null=True, blank=True, related_name="cotisation_item_cree_par")


class Depense(SoftDeleteModel):
    date_depense = models.DateTimeField(verbose_name="Date", default=now)
    montant = models.PositiveIntegerField(verbose_name="Montant")
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)
    sous_groupe = models.ForeignKey(SousGroupe, on_delete=models.SET_NULL, verbose_name='Sous groupe', null=True, blank=True, related_name='depensesousgroupe')
    motif = models.TextField()
    cree_par = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Créé par', null=True, blank=True)


class Promesse(SoftDeleteModel):
    types_choices = (
        ("Espèce", "Espèce"),
        ("Nature", "Nature")
    )
    date_promesse = models.DateTimeField(verbose_name="Date", default=now)
    date_echeance = models.DateTimeField(verbose_name="Date d'échéance", default=now)
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, verbose_name="Membre")
    cotisation = models.ForeignKey(Cotisation, on_delete=models.CASCADE)
    type_promesse = models.CharField(max_length=20, choices=types_choices, default='Espèce', null=True, blank=True)
    unite = models.CharField(max_length=100, default='Francs CFA', null=True, blank=True)
    quantite = models.PositiveIntegerField(verbose_name='Quantité')
    cree_par = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Créé par', null=True, blank=True, related_name="promesse_cree_par")

    def get_status(self):
        """Une fonction pour avoir le status cotisation, est-ce que c'est soldé ou pas et le reste du montant"""
        if self.type_promesse == "Nature":
            return "Promesse en nature non gérable"
        cotisation_items = CotisationItem.objects.filter(membre=self.membre, cotisation=self.cotisation)
        montant_total = 0
        for item in cotisation_items:
            montant_total += item.montant
        if montant_total - self.quantite >= 0:
            return f'Soldée  surplus {montant_total - self.quantite}'
        else:
            return f'Non soldée  restant { -montant_total + self.quantite}'


class FichePromesse(SoftDeleteModel):
    nom = models.CharField(max_length=150, verbose_name="Titre de la fiche")
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, null=True, blank=True)
    date_creation = models.DateTimeField(default=now)
    cree_par = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="fiche_promesse_cree_par")

    def __str__(self):
        return self.nom


class LignePromesse(SoftDeleteModel):
    "Une ligne de la fiche : un membre (ou une personne ajoutée à la main), son montant promis, et son état soldé ou non"
    fiche = models.ForeignKey(FichePromesse, on_delete=models.CASCADE, related_name="lignes")
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, null=True, blank=True)
    nom = models.CharField(max_length=60, blank=True, default="")        # pour une personne hors liste
    prenom = models.CharField(max_length=100, blank=True, default="")    # pour une personne hors liste
    montant_promis = models.PositiveIntegerField(default=0)
    solde = models.BooleanField(default=False)

    @property
    def nom_affiche(self):
        if self.membre_id:
            return f"{self.membre.nom} {self.membre.prenom}"
        return f"{self.nom} {self.prenom}".strip()

    def total_paye(self):
        return sum(p.montant for p in self.paiements.all())


class PaiementPromesse(SoftDeleteModel):
    ligne = models.ForeignKey(LignePromesse, on_delete=models.CASCADE, related_name="paiements")
    montant = models.PositiveIntegerField()
    date_paiement = models.DateTimeField(default=now)
    cree_par = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="paiement_promesse_cree_par")

    class Meta:
        ordering = ['date_paiement', 'id']


# ---------------------------------------------------------------------------
# NOUVEAU : Carte de cotisation hebdomadaire (52 semaines)
# ---------------------------------------------------------------------------

def annee_courante():
    return str(now().year)


class Carte(SoftDeleteModel):
    "Carte de cotisation hebdomadaire (52 semaines) d'une personne"
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, null=True, blank=True)
    membre = models.ForeignKey(Membre, on_delete=models.SET_NULL, null=True, blank=True, related_name="cartes")
    sous_groupe = models.ForeignKey(SousGroupe, on_delete=models.SET_NULL, null=True, blank=True, related_name="cartes", verbose_name="Sous groupe")
    nom = models.CharField(max_length=160, verbose_name="Nom & Prénoms")
    contact = models.CharField(max_length=50, blank=True, default="")
    maison = models.CharField(max_length=150, blank=True, default="")
    parent = models.CharField(max_length=150, blank=True, default="")
    versement = models.PositiveIntegerField(default=100, verbose_name="Versement par semaine (Frs)")
    entete = models.CharField(max_length=150, default="URHC JEUNESSE D'ABOMEY - CALAVI")
    objet = models.CharField(max_length=150, default="Cotisation Journée Récréative")
    annee = models.CharField(max_length=10, blank=True, default=annee_courante)
    verset = models.CharField(max_length=60, blank=True, default="AGGEE 2 : 8")
    semaines_payees = models.JSONField(default=list, blank=True)   # ex : [1, 2, 5]
    date_creation = models.DateTimeField(default=now)
    cree_par = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="carte_cree_par")

    def __str__(self):
        return f"Carte de {self.nom}"

    def total_paye(self):
        return len(self.semaines_payees) * self.versement


# ---------------------------------------------------------------------------
# Fonctions d'accès aux données selon l'utilisateur
# ---------------------------------------------------------------------------

def est_super_admin(user):
    "Vrai si l'utilisateur a accès à l'espace admin Django : il voit toutes les données."
    return bool(getattr(user, "is_authenticated", False) and (user.is_staff or user.is_superuser))


def getMembres(user: User):
    "Récupère les membres selon l'utilisateur"
    if est_super_admin(user):
        return Membre.objects.all().order_by('nom', 'prenom')
    if not user.groupe_id:
        return Membre.objects.none()
    if user.role in ("admin", "responsable"):
        return Membre.objects.filter(groupe_id=user.groupe_id).order_by('nom', 'prenom')
    if user.role == "sous_responsable":
        return Membre.objects.filter(groupe_id=user.groupe_id, sous_groupe_id=user.sous_groupe_id).order_by('nom', 'prenom')
    return Membre.objects.none()


def getCotisationItem(user: User):
    "Récupère les cotisations items selon l'utilisateur"
    if est_super_admin(user):
        return CotisationItem.objects.all().order_by("-date_cotisation")
    if not user.groupe_id:
        return CotisationItem.objects.none()
    if user.role in ("admin", "responsable"):
        return CotisationItem.objects.filter(cotisation__groupe_id=user.groupe_id).order_by("-date_cotisation")
    if user.role == "sous_responsable":
        return CotisationItem.objects.filter(cotisation__groupe_id=user.groupe_id, membre__sous_groupe_id=user.sous_groupe_id).order_by("-date_cotisation")
    return CotisationItem.objects.none()


def getPresence(user: User):
    "Retourne les présences selon l'utilisateur"
    if est_super_admin(user):
        return Presence.objects.all()
    if not user.groupe_id:
        return Presence.objects.none()
    if user.role in ("admin", "responsable"):
        return Presence.objects.filter(liste_presence__groupe_id=user.groupe_id)
    if user.role == "sous_responsable":
        return Presence.objects.filter(liste_presence__groupe_id=user.groupe_id, membre__sous_groupe_id=user.sous_groupe_id)
    return Presence.objects.none()


def getSousGroupe(user: User, groupe=None):
    "Retourne les sous-groupes selon l'utilisateur (le paramètre groupe ne sert qu'aux super admins)"
    if est_super_admin(user):
        qs = SousGroupe.objects.all()
        if groupe is not None:
            qs = qs.filter(groupe=groupe)
        return qs.order_by('nom')
    if not user.groupe_id:
        return SousGroupe.objects.none()
    if user.role in ("admin", "responsable"):
        return SousGroupe.objects.filter(groupe_id=user.groupe_id).order_by('nom')
    if user.role == "sous_responsable":
        return SousGroupe.objects.filter(groupe_id=user.groupe_id, id=user.sous_groupe_id).order_by('nom')
    return SousGroupe.objects.none()


def getDepense(user: User):
    "Retourne les dépenses selon l'utilisateur"
    if est_super_admin(user):
        return Depense.objects.all().order_by('-date_depense')
    if not user.groupe_id:
        return Depense.objects.none()
    if user.role in ("admin", "responsable"):
        return Depense.objects.filter(groupe_id=user.groupe_id).order_by('-date_depense')
    if user.role == "sous_responsable":
        return Depense.objects.filter(groupe_id=user.groupe_id, sous_groupe_id=user.sous_groupe_id).order_by('-date_depense')
    return Depense.objects.none()


def getCotisations(user: User):
    if est_super_admin(user):
        return Cotisation.objects.all()
    if not user.groupe_id:
        return Cotisation.objects.none()
    return Cotisation.objects.filter(groupe_id=user.groupe_id)


def getListPresences(user: User):
    if est_super_admin(user):
        return ListPresence.objects.all()
    if not user.groupe_id:
        return ListPresence.objects.none()
    return ListPresence.objects.filter(groupe_id=user.groupe_id)


def getGroupes(user: User):
    if est_super_admin(user):
        return Groupe.objects.all().order_by('id')
    if not user.groupe_id:
        return Groupe.objects.none()
    return Groupe.objects.filter(id=user.groupe_id)


def getUsers(user: User):
    if est_super_admin(user):
        return User.objects.all().select_related('groupe').order_by('id')
    if not user.groupe_id:
        return User.objects.none()
    return User.objects.filter(groupe_id=user.groupe_id).select_related('groupe').order_by('id')


def getFiches(user: User):
    if est_super_admin(user):
        return FichePromesse.objects.all().select_related('groupe').order_by('-date_creation')
    if not user.groupe_id:
        return FichePromesse.objects.none()
    return FichePromesse.objects.filter(groupe_id=user.groupe_id).select_related('groupe').order_by('-date_creation')


def getCartes(user: User):
    "Retourne les cartes selon l'utilisateur"
    if est_super_admin(user):
        return Carte.objects.all().select_related('membre').order_by('-date_creation')
    if not user.groupe_id:
        return Carte.objects.none()
    qs = Carte.objects.filter(groupe_id=user.groupe_id)
    if user.role == "sous_responsable":
        qs = qs.filter(sous_groupe_id=user.sous_groupe_id)
    return qs.select_related('membre').order_by('-date_creation')