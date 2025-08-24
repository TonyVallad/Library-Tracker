from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app, Response
from flask_login import login_required

from ...extensions import db
from ...models.books import Livre, LivreAuteur
from ...models.core import Editeur, Langue, Serie, Emplacement, Auteur, Genre
from ...models.anthologies import Oeuvre, LivreOeuvre
from ...services.duplicate_check import find_potential_duplicates
from ...services.images import save_image_and_thumbnail, is_allowed_image, delete_cover_files
from ...services.import_export import import_books_from_csv

bp = Blueprint("catalog", __name__, template_folder="../../templates/catalog")


@bp.get("/")
@login_required
def home():
	q = db.session.query(Livre)
	search = request.args.get("q", "").strip()
	genre_id = request.args.get("genre_id")
	editeur_id = request.args.get("editeur_id")
	serie_id = request.args.get("serie_id")
	author_q = request.args.get("author", "").strip()
	zone = request.args.get("zone", "").strip()
	colonne = request.args.get("colonne", "").strip()
	etage = request.args.get("etage", "").strip()
	sort = request.args.get("sort", "created_desc")
	page = max(int(request.args.get("page", 1)), 1)
	per_page = 20

	if search:
		q = q.filter(Livre.titre.ilike(f"%{search}%"))
	if genre_id:
		q = q.join(Livre.genres).filter(Genre.id == int(genre_id))
	if editeur_id:
		q = q.filter(Livre.editeur_id == int(editeur_id))
	if serie_id:
		q = q.filter(Livre.serie_id == int(serie_id))
	if author_q:
		q = q.join(Livre.livre_auteurs).join(Auteur).filter((Auteur.nom.ilike(f"%{author_q}%")) | (Auteur.prenom.ilike(f"%{author_q}%")))
	if zone:
		q = q.join(Emplacement).filter(Emplacement.zone.ilike(f"%{zone}%"))
	if colonne and colonne.isdigit():
		q = q.join(Emplacement).filter(Emplacement.colonne == int(colonne))
	if etage:
		q = q.join(Emplacement).filter(Emplacement.etage == etage)

	# sorting
	if sort == "title_asc":
		q = q.order_by(Livre.titre.asc())
	elif sort == "title_desc":
		q = q.order_by(Livre.titre.desc())
	elif sort == "created_asc":
		q = q.order_by(Livre.created_at.asc())
	else:
		q = q.order_by(Livre.created_at.desc())

	# count total (distinct if joins)
	total = q.distinct(Livre.id).count()
	livres = q.offset((page - 1) * per_page).limit(per_page).all()
	pages = (total + per_page - 1) // per_page

	# pagination urls
	params = request.args.to_dict(flat=True)
	params.pop("page", None)
	prev_url = url_for("catalog.home", **params, page=page - 1) if page > 1 else None
	next_url = url_for("catalog.home", **params, page=page + 1) if page < pages else None

	genres = db.session.query(Genre).order_by(Genre.nom).all()
	editeurs = db.session.query(Editeur).order_by(Editeur.nom).all()
	series = db.session.query(Serie).order_by(Serie.nom).all()
	return render_template(
		"catalog/home.html",
		livres=livres,
		search=search,
		genres=genres,
		editeurs=editeurs,
		series=series,
		selected_genre=genre_id,
		selected_editeur=editeur_id,
		selected_serie=serie_id,
		author_q=author_q,
		zone=zone,
		colonne=colonne,
		etage=etage,
		sort=sort,
		page=page,
		pages=pages,
		total=total,
		prev_url=prev_url,
		next_url=next_url,
	)


@bp.get("/import")
@login_required
def import_form():
	return render_template("catalog/import.html")


@bp.post("/import")
@login_required
def import_upload():
	file = request.files.get("file")
	if not file or not file.filename:
		flash("Veuillez sélectionner un fichier CSV.", "error")
		return redirect(url_for("catalog.import_form"))
	# read CSV
	import csv
	from io import TextIOWrapper

	stream = TextIOWrapper(file.stream, encoding="utf-8")
	reader = csv.DictReader(stream)
	res = import_books_from_csv(reader)
	return render_template("catalog/import_result.html", result=res)


@bp.get("/livres/nouveau")
@login_required
def livre_new():
	editeurs = db.session.query(Editeur).order_by(Editeur.nom).all()
	langues = db.session.query(Langue).order_by(Langue.nom).all()
	series = db.session.query(Serie).order_by(Serie.nom).all()
	emplacements = db.session.query(Emplacement).order_by(Emplacement.zone, Emplacement.colonne, Emplacement.etage).all()
	genres = db.session.query(Genre).order_by(Genre.nom).all()
	auteurs = db.session.query(Auteur).order_by(Auteur.nom, Auteur.prenom).all()
	return render_template("catalog/livre_form.html", editeurs=editeurs, langues=langues, series=series, emplacements=emplacements, genres=genres, auteurs=auteurs)


def _apply_relations_from_form(livre: Livre) -> None:
	# genres
	genre_ids = request.form.getlist("genres[]")
	genres = []
	for gid in genre_ids:
		g = db.session.get(Genre, int(gid))
		if g:
			genres.append(g)
	livre.genres = genres

	# auteurs with roles
	author_ids = request.form.getlist("author_id[]")
	author_roles = request.form.getlist("author_role[]")
	livre.livre_auteurs.clear()
	for idx, aid in enumerate(author_ids):
		if not aid:
			continue
		a = db.session.get(Auteur, int(aid))
		if a:
			role = author_roles[idx] if idx < len(author_roles) else None
			la = LivreAuteur(auteur=a, role=(role or None))
			livre.livre_auteurs.append(la)

	# oeuvres
	oeuvre_ids = request.form.getlist("oeuvre_id[]")
	oeuvre_titles = request.form.getlist("oeuvre_title[]")
	oeuvre_ordres = request.form.getlist("oeuvre_ordre[]")
	oeuvre_pages_list = request.form.getlist("oeuvre_pages[]")
	# clear and re-add
	livre.livre_oeuvres.clear()
	for i in range(max(len(oeuvre_ids), len(oeuvre_titles))):
		oid = oeuvre_ids[i] if i < len(oeuvre_ids) else ""
		title = (oeuvre_titles[i] if i < len(oeuvre_titles) else "").strip()
		ordre = oeuvre_ordres[i] if i < len(oeuvre_ordres) else None
		pages = oeuvre_pages_list[i] if i < len(oeuvre_pages_list) else None
		if oid:
			oeuvre = db.session.get(Oeuvre, int(oid))
		elif title:
			# reuse existing by exact title or create
			oeuvre = db.session.query(Oeuvre).filter(Oeuvre.titre == title).first()
			if not oeuvre:
				oeuvre = Oeuvre(titre=title)
				db.session.add(oeuvre)
		else:
			continue
		le = LivreOeuvre(livre=livre, oeuvre=oeuvre, ordre=int(ordre) if ordre else None, pages=pages or None)
		livre.livre_oeuvres.append(le)


@bp.post("/livres")
@login_required
def livre_create():
	titre = request.form.get("titre", "").strip()
	editeur_id = request.form.get("editeur_id") or None
	langue_id = request.form.get("langue_id") or None
	serie_id = request.form.get("serie_id") or None
	numero_serie = request.form.get("numero_serie") or None
	emplacement_id = request.form.get("emplacement_id") or None
	file = request.files.get("cover")

	if not titre:
		flash("Le titre est requis.", "error")
		return redirect(url_for("catalog.livre_new"))

	dups = find_potential_duplicates(titre)
	if dups:
		flash("Attention: des livres similaires existent déjà.", "warning")

	lien_couverture = None
	if file and file.filename:
		if not is_allowed_image(file.filename, set(current_app.config["ALLOWED_IMAGE_EXTENSIONS"])):
			flash("Format d'image non autorisé.", "error")
			return redirect(url_for("catalog.livre_new"))
		name, _thumb = save_image_and_thumbnail(
			file_storage=file,
			upload_dir=current_app.config["UPLOAD_FOLDER"],
			thumb_dir=current_app.config["THUMB_FOLDER"],
			allowed_ext=set(current_app.config["ALLOWED_IMAGE_EXTENSIONS"]),
		)
		lien_couverture = name

	livre = Livre(
		titre=titre,
		editeur_id=int(editeur_id) if editeur_id else None,
		langue_id=int(langue_id) if langue_id else None,
		serie_id=int(serie_id) if serie_id else None,
		numero_serie=int(numero_serie) if numero_serie else None,
		emplacement_id=int(emplacement_id) if emplacement_id else None,
		lien_couverture=lien_couverture,
	)

	# relations
	_apply_relations_from_form(livre)

	db.session.add(livre)
	db.session.commit()
	flash("Livre créé.", "success")
	return redirect(url_for("catalog.detail", livre_id=livre.id))


@bp.get("/livres/<int:livre_id>")
@login_required
def detail(livre_id: int):
	livre = db.session.get(Livre, livre_id)
	if not livre:
		flash("Livre introuvable.", "error")
		return redirect(url_for("catalog.home"))
	auteurs = db.session.query(Auteur).order_by(Auteur.nom, Auteur.prenom).all()
	return render_template("catalog/livre_detail.html", livre=livre, auteurs=auteurs)


@bp.post("/livres/<int:livre_id>/authors")
@login_required
def update_authors(livre_id: int):
	livre = db.session.get(Livre, livre_id)
	if not livre:
		flash("Livre introuvable.", "error")
		return redirect(url_for("catalog.home"))
	author_ids = request.form.getlist("author_id[]")
	author_roles = request.form.getlist("author_role[]")
	livre.livre_auteurs.clear()
	for idx, aid in enumerate(author_ids):
		if not aid:
			continue
		a = db.session.get(Auteur, int(aid))
		if a:
			role = author_roles[idx] if idx < len(author_roles) else None
			livre.livre_auteurs.append(LivreAuteur(auteur=a, role=(role or None)))
	db.session.commit()
	flash("Auteurs mis à jour.", "success")
	return redirect(url_for("catalog.detail", livre_id=livre.id))


@bp.get("/livres/<int:livre_id>/edit")
@login_required
def edit(livre_id: int):
	livre = db.session.get(Livre, livre_id)
	if not livre:
		flash("Livre introuvable.", "error")
		return redirect(url_for("catalog.home"))
	editeurs = db.session.query(Editeur).order_by(Editeur.nom).all()
	langues = db.session.query(Langue).order_by(Langue.nom).all()
	series = db.session.query(Serie).order_by(Serie.nom).all()
	emplacements = db.session.query(Emplacement).order_by(Emplacement.zone, Emplacement.colonne, Emplacement.etage).all()
	genres = db.session.query(Genre).order_by(Genre.nom).all()
	auteurs = db.session.query(Auteur).order_by(Auteur.nom, Auteur.prenom).all()
	return render_template("catalog/livre_edit.html", livre=livre, editeurs=editeurs, langues=langues, series=series, emplacements=emplacements, genres=genres, auteurs=auteurs)


@bp.post("/livres/<int:livre_id>")
@login_required
def update(livre_id: int):
	livre = db.session.get(Livre, livre_id)
	if not livre:
		flash("Livre introuvable.", "error")
		return redirect(url_for("catalog.home"))

	titre = request.form.get("titre", "").strip()
	if not titre:
		flash("Le titre est requis.", "error")
		return redirect(url_for("catalog.edit", livre_id=livre.id))
	if titre != livre.titre:
		dups = [d for d in find_potential_duplicates(titre) if d.id != livre.id]
		if dups:
			flash("Attention: des livres similaires existent déjà.", "warning")

	livre.titre = titre
	livre.editeur_id = int(request.form.get("editeur_id")) if request.form.get("editeur_id") else None
	livre.langue_id = int(request.form.get("langue_id")) if request.form.get("langue_id") else None
	livre.serie_id = int(request.form.get("serie_id")) if request.form.get("serie_id") else None
	numero_serie = request.form.get("numero_serie")
	livre.numero_serie = int(numero_serie) if numero_serie else None
	livre.emplacement_id = int(request.form.get("emplacement_id")) if request.form.get("emplacement_id") else None

	# cover replace optionally
	file = request.files.get("cover")
	if file and file.filename:
		if not is_allowed_image(file.filename, set(current_app.config["ALLOWED_IMAGE_EXTENSIONS"])):
			flash("Format d'image non autorisé.", "error")
			return redirect(url_for("catalog.edit", livre_id=livre.id))
		name, _thumb = save_image_and_thumbnail(
			file_storage=file,
			upload_dir=current_app.config["UPLOAD_FOLDER"],
			thumb_dir=current_app.config["THUMB_FOLDER"],
			allowed_ext=set(current_app.config["ALLOWED_IMAGE_EXTENSIONS"]),
		)
		# delete old files
		delete_cover_files(livre.lien_couverture, current_app.config["UPLOAD_FOLDER"], current_app.config["THUMB_FOLDER"])
		livre.lien_couverture = name

	_apply_relations_from_form(livre)

	db.session.commit()
	flash("Livre mis à jour.", "success")
	return redirect(url_for("catalog.detail", livre_id=livre.id))


@bp.post("/livres/<int:livre_id>/delete")
@login_required
def delete(livre_id: int):
	livre = db.session.get(Livre, livre_id)
	if livre:
		# delete files first
		delete_cover_files(livre.lien_couverture, current_app.config["UPLOAD_FOLDER"], current_app.config["THUMB_FOLDER"])
		db.session.delete(livre)
		db.session.commit()
		flash("Livre supprimé.", "info")
	return redirect(url_for("catalog.home"))


@bp.get("/export.csv")
@login_required
def export_csv() -> Response:
	import csv
	from io import StringIO

	output = StringIO()
	writer = csv.writer(output)
	writer.writerow([
		"id", "titre", "editeur", "langue", "serie", "numero_serie", "emplacement",
		"auteurs", "genres", "oeuvres",
	])
	for l in db.session.query(Livre).order_by(Livre.id):
		auteurs = "; ".join([f"{la.auteur.prenom or ''} {la.auteur.nom}{f' ({la.role})' if la.role else ''}".strip() for la in l.livre_auteurs])
		genres = ", ".join([g.nom for g in l.genres])
		oeuvres = "; ".join([f"{lo.ordre or ''} {lo.oeuvre.titre}{f' ({lo.pages})' if lo.pages else ''}".strip() for lo in sorted(l.livre_oeuvres, key=lambda x: (x.ordre or 0))])
		editeur = l.editeur.nom if l.editeur else ""
		langue = l.langue.nom if l.langue else ""
		serie = l.serie.nom if l.serie else ""
		emplacement = f"{l.emplacement.zone or ''} C{l.emplacement.colonne} E{l.emplacement.etage}" if l.emplacement else ""
		writer.writerow([l.id, l.titre, editeur, langue, serie, l.numero_serie or "", emplacement, auteurs, genres, oeuvres])

	output.seek(0)
	return Response(output.read(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=livres.csv"})
