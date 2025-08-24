from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

from ..extensions import db
from ..models.core import Auteur, Editeur, Langue, Genre, Serie, Emplacement
from ..models.books import Livre, LivreAuteur
from ..models.anthologies import Oeuvre, LivreOeuvre


@dataclass
class ImportResult:
	created: int = 0
	updated: int = 0
	skipped: int = 0
	errors: list[str] = None

	def __post_init__(self) -> None:
		if self.errors is None:
			self.errors = []


def _get_or_create(model, defaults=None, **kwargs):
	obj = db.session.query(model).filter_by(**kwargs).first()
	if obj:
		return obj, False
	obj = model(**{**kwargs, **(defaults or {})})
	db.session.add(obj)
	return obj, True


def import_books_from_csv(rows: Iterable[dict]) -> ImportResult:
	"""Import books from dictionaries, creating missing reference data.

	Columns expected similar to export: id, titre, editeur, langue, serie, numero_serie, emplacement,
	"auteurs" ("Nom Prenom (role); ..."), "genres" ("Genre1, Genre2"), "oeuvres" ("1 Title (pages); ...").
	"""
	res = ImportResult()
	for row in rows:
		try:
			title = (row.get("titre") or "").strip()
			if not title:
				res.skipped += 1
				continue

			editeur_name = (row.get("editeur") or "").strip() or None
			langue_name = (row.get("langue") or "").strip() or None
			serie_name = (row.get("serie") or "").strip() or None
			numero_serie = row.get("numero_serie") or None
			numero_serie = int(numero_serie) if str(numero_serie).isdigit() else None
			emp = (row.get("emplacement") or "").strip() or None

			editeur = None
			if editeur_name:
				editeur, _ = _get_or_create(Editeur, nom=editeur_name)
			langue = None
			if langue_name:
				langue, _ = _get_or_create(Langue, nom=langue_name)
			serie = None
			if serie_name:
				serie, _ = _get_or_create(Serie, nom=serie_name)
			emplacement = None
			if emp:
				# expected format: "zone C{colonne} E{etage}" or "C{colonne} E{etage}"
				zone = None
				col = None
				etg = None
				parts = emp.split()
				for p in parts:
					if p.startswith("C") and p[1:].isdigit():
						col = int(p[1:])
					elif p.startswith("E"):
						etg = p[1:]
					else:
						zone = (zone + " " + p).strip() if zone else p
				if col is not None and etg is not None:
					emplacement, _ = _get_or_create(Emplacement, colonne=col, etage=etg, zone=zone)

			livre = db.session.query(Livre).filter(Livre.titre == title).first()
			created = False
			if not livre:
				livre = Livre(titre=title)
				db.session.add(livre)
				created = True

			livre.editeur = editeur
			livre.langue = langue
			livre.serie = serie
			livre.numero_serie = numero_serie
			livre.emplacement = emplacement

			# genres
			genres_list = [g.strip() for g in (row.get("genres") or "").split(",") if g.strip()]
			livre.genres = []
			for gname in genres_list:
				g, _ = _get_or_create(Genre, nom=gname)
				livre.genres.append(g)

			# auteurs: "Prenom Nom (role); ..." or "Nom (role)"
			auteurs_val = row.get("auteurs") or ""
			livre.livre_auteurs.clear()
			for part in [p.strip() for p in auteurs_val.split(";") if p.strip()]:
				role = None
				if part.endswith(")") and "(" in part:
					name, role = part.rsplit("(", 1)
					part = name.strip()
					role = role[:-1].strip()
				names = part.split()
				nom = names[-1]
				prenom = " ".join(names[:-1]) if len(names) > 1 else None
				auteur, _ = _get_or_create(Auteur, nom=nom, prenom=prenom)
				livre.livre_auteurs.append(LivreAuteur(auteur=auteur, role=role))

			# oeuvres: "1 Title (pages); ..."
			livre.livre_oeuvres.clear()
			for o in [p.strip() for p in (row.get("oeuvres") or "").split(";") if p.strip()]:
				ordre = None
				pages = None
				if ")" in o and "(" in o:
					t, pages = o.rsplit("(", 1)
					pages = pages[:-1].strip()
					o = t.strip()
				if o and o[0].isdigit():
					first, _, rest = o.partition(" ")
					if first.isdigit():
						ordre = int(first)
						o = rest
					oeuvre, _ = _get_or_create(Oeuvre, titre=o)
					livre.livre_oeuvres.append(LivreOeuvre(livre=livre, oeuvre=oeuvre, ordre=ordre, pages=pages))

			if created:
				res.created += 1
			else:
				res.updated += 1
		except Exception as exc:
			res.errors.append(str(exc))
			res.skipped += 1
		db.session.flush()

	db.session.commit()
	return res
