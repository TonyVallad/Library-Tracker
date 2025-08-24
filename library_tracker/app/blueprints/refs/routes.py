from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ...extensions import db
from ...models.core import Auteur, Editeur, Langue, Genre, Serie, Emplacement
from ...services.authz import require_roles

bp = Blueprint("refs", __name__, template_folder="../../templates/refs")


@bp.get("/")
@login_required
def refs_home():
	return render_template("refs/home.html")


# AUTEURS
@bp.get("/auteurs")
@login_required
def auteurs_list():
	items = db.session.query(Auteur).order_by(Auteur.nom, Auteur.prenom).all()
	return render_template("refs/auteurs.html", items=items)


@bp.post("/auteurs")
@require_roles("admin", "editeur")
def auteurs_create():
	nom = request.form.get("nom", "").strip()
	prenom = request.form.get("prenom", "").strip() or None
	alias = request.form.get("alias", "").strip() or None
	if not nom:
		flash("Le nom est requis.", "error")
		return redirect(url_for("refs.auteurs_list"))
	item = Auteur(nom=nom, prenom=prenom, alias=alias)
	db.session.add(item)
	db.session.commit()
	flash("Auteur créé.", "success")
	return redirect(url_for("refs.auteurs_list"))


@bp.post("/auteurs/<int:item_id>/delete")
@require_roles("admin", "editeur")
def auteurs_delete(item_id: int):
	item = db.session.get(Auteur, item_id)
	if item:
		db.session.delete(item)
		db.session.commit()
		flash("Auteur supprimé.", "info")
	return redirect(url_for("refs.auteurs_list"))


# EDITEURS
@bp.get("/editeurs")
@login_required
def editeurs_list():
	items = db.session.query(Editeur).order_by(Editeur.nom).all()
	return render_template("refs/editeurs.html", items=items)


@bp.post("/editeurs")
@require_roles("admin", "editeur")
def editeurs_create():
	nom = request.form.get("nom", "").strip()
	if not nom:
		flash("Le nom est requis.", "error")
		return redirect(url_for("refs.editeurs_list"))
	item = Editeur(nom=nom)
	db.session.add(item)
	db.session.commit()
	flash("Éditeur créé.", "success")
	return redirect(url_for("refs.editeurs_list"))


@bp.post("/editeurs/<int:item_id>/delete")
@require_roles("admin", "editeur")
def editeurs_delete(item_id: int):
	item = db.session.get(Editeur, item_id)
	if item:
		db.session.delete(item)
		db.session.commit()
		flash("Éditeur supprimé.", "info")
	return redirect(url_for("refs.editeurs_list"))


# LANGUES
@bp.get("/langues")
@login_required
def langues_list():
	items = db.session.query(Langue).order_by(Langue.nom).all()
	return render_template("refs/langues.html", items=items)


@bp.post("/langues")
@require_roles("admin", "editeur")
def langues_create():
	nom = request.form.get("nom", "").strip()
	if not nom:
		flash("Le nom est requis.", "error")
		return redirect(url_for("refs.langues_list"))
	item = Langue(nom=nom)
	db.session.add(item)
	db.session.commit()
	flash("Langue créée.", "success")
	return redirect(url_for("refs.langues_list"))


@bp.post("/langues/<int:item_id>/delete")
@require_roles("admin", "editeur")
def langues_delete(item_id: int):
	item = db.session.get(Langue, item_id)
	if item:
		db.session.delete(item)
		db.session.commit()
		flash("Langue supprimée.", "info")
	return redirect(url_for("refs.langues_list"))


# GENRES
@bp.get("/genres")
@login_required
def genres_list():
	items = db.session.query(Genre).order_by(Genre.nom).all()
	return render_template("refs/genres.html", items=items)


@bp.post("/genres")
@require_roles("admin", "editeur")
def genres_create():
	nom = request.form.get("nom", "").strip()
	if not nom:
		flash("Le nom est requis.", "error")
		return redirect(url_for("refs.genres_list"))
	item = Genre(nom=nom)
	db.session.add(item)
	db.session.commit()
	flash("Genre créé.", "success")
	return redirect(url_for("refs.genres_list"))


@bp.post("/genres/<int:item_id>/delete")
@require_roles("admin", "editeur")
def genres_delete(item_id: int):
	item = db.session.get(Genre, item_id)
	if item:
		db.session.delete(item)
		db.session.commit()
		flash("Genre supprimé.", "info")
	return redirect(url_for("refs.genres_list"))


# SERIES
@bp.get("/series")
@login_required
def series_list():
	items = db.session.query(Serie).order_by(Serie.nom).all()
	return render_template("refs/series.html", items=items)


@bp.post("/series")
@require_roles("admin", "editeur")
def series_create():
	nom = request.form.get("nom", "").strip()
	if not nom:
		flash("Le nom est requis.", "error")
		return redirect(url_for("refs.series_list"))
	item = Serie(nom=nom)
	db.session.add(item)
	db.session.commit()
	flash("Série créée.", "success")
	return redirect(url_for("refs.series_list"))


@bp.post("/series/<int:item_id>/delete")
@require_roles("admin", "editeur")
def series_delete(item_id: int):
	item = db.session.get(Serie, item_id)
	if item:
		db.session.delete(item)
		db.session.commit()
		flash("Série supprimée.", "info")
	return redirect(url_for("refs.series_list"))


# EMPLACEMENTS
@bp.get("/emplacements")
@login_required
def emplacements_list():
	items = db.session.query(Emplacement).order_by(Emplacement.zone, Emplacement.colonne, Emplacement.etage).all()
	return render_template("refs/emplacements.html", items=items)


@bp.post("/emplacements")
@require_roles("admin", "editeur")
def emplacements_create():
	zone = request.form.get("zone", "").strip() or None
	colonne = request.form.get("colonne", "").strip()
	etage = request.form.get("etage", "").strip()
	description = request.form.get("description", "").strip() or None
	if not colonne or not etage:
		flash("Colonne et étage sont requis.", "error")
		return redirect(url_for("refs.emplacements_list"))
	item = Emplacement(zone=zone, colonne=int(colonne), etage=etage, description=description)
	db.session.add(item)
	db.session.commit()
	flash("Emplacement créé.", "success")
	return redirect(url_for("refs.emplacements_list"))


@bp.post("/emplacements/<int:item_id>/delete")
@require_roles("admin", "editeur")
def emplacements_delete(item_id: int):
	item = db.session.get(Emplacement, item_id)
	if item:
		db.session.delete(item)
		db.session.commit()
		flash("Emplacement supprimé.", "info")
	return redirect(url_for("refs.emplacements_list"))
