from __future__ import annotations

from pathlib import Path

from flask import Flask

from .config import Config
from .extensions import db, migrate, login_manager, babel


def register_extensions(app: Flask) -> None:
	db.init_app(app)
	migrate.init_app(app, db)
	login_manager.init_app(app)
	login_manager.login_view = "auth.login"
	login_manager.login_message_category = "info"
	babel.init_app(app)


def register_blueprints(app: Flask) -> None:
	from .blueprints import register_all_blueprints
	register_all_blueprints(app)


def register_cli(app: Flask) -> None:
	from .models.auth import Role, User
	from .models.core import Auteur, Editeur, Langue, Genre, Serie, Emplacement
	from .models.books import Livre, LivreAuteur
	from .models.anthologies import Oeuvre, LivreOeuvre

	@app.cli.command("seed")
	def seed() -> None:
		"""Create initial roles and an admin user (admin/admin)."""
		admin_role = db.session.query(Role).filter_by(name="admin").one_or_none() or Role(name="admin")
		editor_role = db.session.query(Role).filter_by(name="editeur").one_or_none() or Role(name="editeur")
		viewer_role = db.session.query(Role).filter_by(name="lecteur").one_or_none() or Role(name="lecteur")
		db.session.add_all([admin_role, editor_role, viewer_role])
		db.session.flush()

		user = db.session.query(User).filter_by(username="admin").one_or_none()
		if not user:
			user = User(username="admin", email="admin@example.com")
			user.set_password("admin")
			user.roles = [admin_role]
			db.session.add(user)
		db.session.commit()
		print("Seed complete. Admin login: admin/admin")

	@app.cli.command("seed-demo")
	def seed_demo() -> None:
		"""Populate demo data: authors, genres, languages, series, emplacements, and books."""
		def get_or_create(model, **kwargs):
			obj = db.session.query(model).filter_by(**kwargs).first()
			if obj:
				return obj
			obj = model(**kwargs)
			db.session.add(obj)
			return obj

		lang_fr = get_or_create(Langue, nom="Français")
		lang_en = get_or_create(Langue, nom="Anglais")

		g_roman = get_or_create(Genre, nom="Roman")
		g_sf = get_or_create(Genre, nom="Science-Fiction")
		g_fantasy = get_or_create(Genre, nom="Fantasy")
		g_essai = get_or_create(Genre, nom="Essai")

		e_gallimard = get_or_create(Editeur, nom="Gallimard")
		e_leha = get_or_create(Editeur, nom="LEHA")
		e_pocket = get_or_create(Editeur, nom="Pocket")

		s_dune = get_or_create(Serie, nom="Dune")
		s_kinsman = get_or_create(Serie, nom="Kinsman")

		emp_a = get_or_create(Emplacement, zone="Salon", colonne=25, etage="B")
		emp_b = get_or_create(Emplacement, zone="Bureau", colonne=12, etage="A")

		a_herbert = get_or_create(Auteur, nom="Herbert", prenom="Frank")
		a_simmons = get_or_create(Auteur, nom="Simmons", prenom="Dan")
		a_kerr = get_or_create(Auteur, nom="Kerr", prenom="Poul")
		a_dupont = get_or_create(Auteur, nom="Dupont", prenom="Jean")

		# Books
		if not db.session.query(Livre).filter_by(titre="Dune").first():
			b1 = Livre(titre="Dune", editeur=e_pocket, langue=lang_fr, serie=s_dune, numero_serie=1, emplacement=emp_a)
			b1.genres = [g_sf]
			b1.livre_auteurs = [LivreAuteur(auteur=a_herbert, role="auteur")]
			db.session.add(b1)

		if not db.session.query(Livre).filter_by(titre="Hypérion").first():
			b2 = Livre(titre="Hypérion", editeur=e_gallimard, langue=lang_fr, emplacement=emp_b)
			b2.genres = [g_sf]
			b2.livre_auteurs = [LivreAuteur(auteur=a_simmons, role="auteur")]
			db.session.add(b2)

		if not db.session.query(Livre).filter_by(titre="Kinsman (Recueil)").first():
			b3 = Livre(titre="Kinsman (Recueil)", editeur=e_leha, langue=lang_fr, serie=s_kinsman, numero_serie=1, emplacement=emp_a)
			b3.genres = [g_sf, g_roman]
			b3.livre_auteurs = [LivreAuteur(auteur=a_kerr, role="auteur"), LivreAuteur(auteur=a_dupont, role="traducteur")]
			# Oeuvres du recueil
			o1 = get_or_create(Oeuvre, titre="La stratégie de Kinsman")
			o2 = get_or_create(Oeuvre, titre="L'héritage de Kinsman")
			b3.livre_oeuvres = [
				LivreOeuvre(oeuvre=o1, ordre=1, pages="1-120"),
				LivreOeuvre(oeuvre=o2, ordre=2, pages="121-240"),
			]
			db.session.add(b3)

		db.session.commit()
		print("Demo data inserted.")


def create_app() -> Flask:
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_object(Config())

	# Ensure directories exist (instance, uploads, thumbs)
	for p in [app.instance_path, app.config.get("UPLOAD_FOLDER"), app.config.get("THUMB_FOLDER")]:
		if p:
			Path(p).mkdir(parents=True, exist_ok=True)

	register_extensions(app)
	# Ensure models are imported so Alembic sees them
	from . import models as _models  # noqa: F401
	register_blueprints(app)
	register_cli(app)

	@app.route("/health")
	def health() -> str:
		return "ok"

	return app
