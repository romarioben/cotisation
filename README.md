# Gestionnaire de Cotisations

## Vue d'ensemble
Le **Gestionnaire de Cotisations** est une application web Django dédiée à la gestion des adhérents, des listes de présence, des cotisations et des dépenses au sein d’une association ou d’un club. Le projet est structuré en trois apps Django principales :

- **auth_app** – modèle utilisateur personnalisé et flux d’authentification.
- **app** – logique métier : membres (`Membre`), groupes (`Groupe`, `SousGroupe`), listes de présence (`ListPresence` / `Presence`), cotisations (`Cotisation` / `CotisationItem`) et dépenses (`Depense`).
- **presentation** – vues front‑end qui affichent l’interface utilisateur.

L’application sert les fichiers statiques via **WhiteNoise**, ce qui facilite le déploiement en production.

## Fonctionnalités

- **Gestion des membres** – ajouter, modifier, supprimer des membres avec la possibilité de télécharger une photo de profil.
- **Suivi des présences** – créer une liste de présence et enregistrer le statut de chaque membre.
- **Suivi financier** – cotisations, paiements, et dépenses par groupe.
- **Contrôle d’accès basé sur les rôles** – admin, responsable et sous‑responsable qui disposent de permissions différentes.
- **Internationalisation** – l’application est en français (`LANGUAGE_CODE = "fr-fr"`).
- **Docker ready** – un conteneur Docker est fourni pour un déploiement rapide.

## Prérequis

| Élément               | Version minimale | Remarques |
|-----------------------|------------------|-----------|
| Python                | 3.11             | L'image Docker utilise Python 3.12 mais le projet fonctionne en 3.11 et plus.
| Docker/docker‑compose  | 19+              | Optionnel, voir la section Docker.
| PostgreSQL           | —                | Optionnel, SQLite est la valeur par défaut.
| Linux / macOS / Windows | —              | `manage.py` fonctionne sur tous les systèmes d’exploitation.

## Développement local

Suivez ces étapes pour exécuter l’application en local à l’aide d’un environnement virtuel.

### 1. Cloner le dépôt

```bash
git clone https://github.com/romarioben/cotisation-manager.git
cd cotisation-manager
```

### 2. Créer un environnement virtuel (recommandé)

```bash
python -m venv .venv
source .venv/bin/activate   # Sur Windows: .venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d’environnement

L’application utilise `django-environ`. Copiez le modèle et ajustez les valeurs :

```bash
cp .env.example .env
# Éditez .env
#   SECRET_KEY        : une chaîne aléatoire (ex. https://djecrety.ir/)
#   DEBUG             : True en développement
#   ALLOWED_HOSTS      : localhost,127.0.0.1
#   STATIC_URL         : /static/ (défaut)
#   STATIC_ROOT       : staticfiles/
#   MEDIA_ROOT        : media/
#   DATABASE_URL       : sqlite:///db.sqlite3 (défaut) ou URL PostgreSQL
```

Pour une configuration SQLite rapide, laissez les valeurs par défaut.

### 5. Appliquer les migrations

```bash
python manage.py migrate
```

### 6. Collecter les fichiers statiques

`collectstatic` est exécuté automatiquement par `entrypoint.sh` dans Docker. En local, vous pouvez l’exécuter manuellement :

```bash
python manage.py collectstatic --noinput
```

> **Astuce** : lorsque vous lancez `runserver`, assurez‑vous que la variable `DJANGO_STATIC_ROOT` n’est pas définie ; Django servira alors les fichiers directement.

### 7. Créer un super‑utilisateur (recommandé)

```bash
python manage.py createsuperuser
```

### 8. Lancer le serveur de développement

```bash
python manage.py runserver
```

Ouvrez <http://127.0.0.1:8000/> dans votre navigateur.  Les routes ci‑dessous sont disponibles.

## Docker – Production

Un Dockerfile minimal est fourni.

### 1. Construire l’image

```bash
docker build -t cotisation-manager .
```

### 2. Lancer le conteneur

```bash
docker run -d -p 8000:8000 \
   -e SECRET_KEY=VOTRE_SECRET \
   -e DEBUG=False \
   -e DATABASE_URL=sqlite:///db.sqlite3 \
   cotisation-manager
```

L’entrée du conteneur exécute `collectstatic` et `migrate` à chaque démarrage.

> **Important** : en production, il est typique de concevoir la persistance des bases de données et des fichiers médias sur un volume distinct.

## Configuration de la base de données

La valeur par défaut est SQLite, mais vous pouvez configurer PostgreSQL en définissant `DATABASE_URL` :

```env
DATABASE_URL=postgres://user:pass@localhost:5432/yourdb
```

Le survol de `SECURE_PROXY_SSL_HEADER` garantit que le protocole HTTPS est correctement détecté.

## Fichiers statiques & médias

* **Static** : collectés dans `staticfiles/` au démarrage; servis par WhiteNoise.
* **Media** : uploads (photos, etc.) dans le répertoire `media/`. Ce dossier doit exister et être accessible en écriture.

## Tests

```bash
python manage.py test
```

Les tests fournis valident principalement la logique des modèles.  Ajoutez d’autres tests dans `tests.py` ou créez un répertoire `tests/`.

## Structure du projet

```
cotisation/            # Projet Django (settings, wsgi, urls)
├─ app/                  # Logique métier
│  ├─ migrations/        # Migrations SQLite/PostgreSQL
│  ├─ templates/         # Templates Django
│  └─ …                  # Modèles, vues, URLs
├─ auth_app/             # Modèle utilisateur personnalisé
├─ presentation/         # Vues front‑end
├─ static/               # Ressources statiques (JS/CSS)
├─ media/                # Fichiers uploadés
├─ Dockerfile
├─ entrypoint.sh
├─ manage.py
└─ requirements.txt
```

## Routes principales (extraits)

| URL              | Vue | Description |
|------------------|------|------------|
| `/auth/`         | login, logout, register | Authentification |
| `/app/`          | dashboard | Tableau de bord des membres |
| `/app/users/`   | users_list | Liste et édition des utilisateurs |
| `/app/cotisations/` | cotisations | CRUD des cotisations |
| `/app/expenses/`   | dépenses | CRUD des dépenses |
| `/app/presence/`     | présence | Gestion des listes de présence |

Consultez `cotisation/urls.py` pour la liste complète.

## Contribution

Les pull‑requests sont les bienvenus !  Quelques points à garder en tête :

* Le code est en **français** ; n’écrivez pas d’erreurs public sans français.
* Utilisez `django-environ` pour toute nouvelle variable d’environnement.
* Le modèle `SoftDeleteModel` est utilisé ; évitez de supprimer physiquement les objets.
* Testez vos modifications avec `python manage.py test`.

### Qualité de code

```bash
pip install flake8
flake8 ./
```

Vous pouvez également lancer `pytest` si vous avez la dépendance.

## Licence

MIT © 2026 Romario.  Le code est disponible en open source et peut être utilisé à titre personnel ou commercial.

---