# Roadmap Library Tracker

## Phase 1 — MVP (Back + minimal UI)
- Authentification multi-utilisateur, rôles: admin/editeur/lecteur — DONE
- Schéma BD normalisé (auteur, éditeur, langue, genre, série, emplacement) — DONE
- Livres: CRUD, multi-auteurs (rôles), multi-genres — DONE
- Recueils: oeuvres + liaisons livre↔oeuvre — DONE (basique)
- Upload couverture + vignettes 256px — DONE
- Détection de doublons (avertissement) — DONE
- Référentiels CRUD — DONE
- Tailwind CSS (CLI), base layout — DONE

## Phase 2 — UX & Fonctionnel
- Styles UI avec Tailwind (listes, formulaires, modales) — IN PROGRESS (50%)
- Recherche/filtrage avancé (titre, auteurs, série, genre, emplacement) — DONE (v1)
- Pagination + tri du catalogue — DONE (v1)
- Édition inline des rôles d’auteurs — DONE (v1)
- Suppression/synchronisation des fichiers de couverture en cas de mise à jour/suppression — DONE
- Gestion d’images supplémentaires (quatrième de couverture) — OPTIONAL

## Phase 3 — Import/Export
- Import CSV des livres (relations: auteurs/genres/série/emplacement) — DONE (v1)
- Export CSV — DONE
- Rapport d’import (doublons, inconsistances) — PARTIAL (liste d’erreurs)

## Phase 4 — Administration
- Gestion des utilisateurs et des rôles (UI) — DONE (v1)
- Journal d’audit simple (création/maj/suppression) — OPTIONAL

## Phase 5 — i18n et déploiement
- i18n via Flask-Babel (FR par défaut, structure prête) — PARTIAL
- Déploiement local Gunicorn — TODO
- Préparation déploiement hébergeur (procfile/env) — TODO

## Tests & Qualité
- Pytest pour modèles, services (images, duplicates, import), routes — DONE (v1, 4 tests)
- Lint/format (ruff/black) — OPTIONAL

## Notes de progression
- Backend principal et modèles: 100%
- Auth & rôles: 85% (UI admin v1 ok)
- Livres CRUD + recueils: 90% (inline auteurs/roles ok)
- Référentiels: 100%
- UI Tailwind: 50%
- Import/Export: 85%
- Tests: 25% (base verte)

## Prochaines étapes suggérées
1) Améliorer UI (tables, modales, validations côté client).
2) Déploiement (gunicorn) + docs.
3) i18n extensible et sélection de langue.
