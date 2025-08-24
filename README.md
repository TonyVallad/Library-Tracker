# Library Tracker

Application Flask pour suivre les livres d'une bibliothèque personnelle, avec schéma normalisé (auteurs multi‑rôles, multi‑genres), gestion des recueils (oeuvres), authentification multi‑utilisateurs/roles, uploads de couvertures et UI Tailwind.

## Prérequis
- Python 3.12.10
- pip
- SQLite (inclus avec Python)
- Node.js LTS (installé via winget dans ce repo)

## Installation

1. Cloner le dépôt puis se placer dans le dossier du projet.
2. Activer votre environnement virtuel existant (venv déjà créé par vous).
3. Installer les dépendances Python:
```bash
pip install -r requirements.txt
```
4. Initialiser la base de données (déjà effectué une fois ici, mais pour une nouvelle machine):
```bash
python -m flask --app library_tracker.app:create_app db init
python -m flask --app library_tracker.app:create_app db migrate -m "init schema"
python -m flask --app library_tracker.app:create_app db upgrade
```
5. Créer les données initiales (rôles + utilisateur admin/admin):
```bash
python -m flask --app library_tracker.app:create_app seed
```
6. Installer les dépendances Node et construire le CSS Tailwind:
```bash
npm install
npm run build
# ou en développement (watch): npm run dev
```

## Lancer l'application
```bash
python -m flask --app library_tracker.app:create_app run
# Aller sur http://127.0.0.1:5000
# Identifiants: admin / admin
```

## Structure du projet
```text
library_tracker/
  app/
    __init__.py            # App factory, CLI (seed)
    config.py              # Config (SQLite, uploads, i18n)
    extensions.py          # db, migrate, login_manager, babel
    blueprints/
      catalog/             # Livres: routes & templates
      refs/                # Référentiels CRUD (auteur, éditeur, ...)
      auth/                # Login/Logout
      files/               # Réservé uploads (évolutions)
    models/
      core.py              # Auteur, Editeur, Langue, Genre, Serie, Emplacement
      books.py             # Livre, associations auteurs/genres
      anthologies.py       # Oeuvre, LivreOeuvre (recueils)
      auth.py              # User, Role, UserRole
    services/
      images.py            # Uploads, vignettes, suppression fichiers
      duplicate_check.py   # Détection de doublons (titre)
      authz.py             # Décorateur de rôles
    templates/
      base.html
      auth/
      catalog/
      refs/
    static/
      css/                 # input.css (tailwind) => app.css (build)
      uploads/
        covers/
      thumbs/
        256/

migrations/                # Alembic (flask db ...)
package.json               # Scripts npm (dev/build)
postcss.config.js          # PostCSS config
tailwind.config.js         # Tailwind config
requirements.txt           # Dépendances Python
wsgi.py                    # Entrée WSGI
```

## Fonctionnalités
- Auth multi‑utilisateur (admin/editeur/lecteur)
- Livres: CRUD, couvertures (upload + vignettes), multi‑auteurs (rôle), multi‑genres
- Recueils: oeuvres liées au livre, ordre et pages
- Référentiels CRUD (auteur, éditeur, langue, genre, série, emplacement)
- Avertissement de doublons par titre
- UI Tailwind (CLI)

## CSV (export / import)
- Export CSV: en cours d’intégration (endpoint d’export dans le catalogue)
- Import CSV: à venir (mapping relations auteurs/genres/série/emplacement)

## Déploiement
- Local: `python -m flask --app library_tracker.app:create_app run`
- Prod: gunicorn (ex: `gunicorn -w 4 'wsgi:app'`) + serveur de fichiers statiques

## Sécurité
- Mots de passe hashés (bcrypt via passlib)
- Permissions par rôles pour les opérations d’édition/suppression des référentiels

## Développement
- Générer le CSS à la volée: `npm run dev`
- Générer le CSS minifié: `npm run build`
- Migrations DB: `flask db migrate` puis `flask db upgrade`