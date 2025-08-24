import io

import pytest

from library_tracker.app import create_app
from library_tracker.app.extensions import db
from library_tracker.app.models.core import Auteur, Genre
from library_tracker.app.models.books import Livre
from library_tracker.app.services.duplicate_check import find_potential_duplicates
from library_tracker.app.services.import_export import import_books_from_csv


@pytest.fixture()
def app():
	app = create_app()
	app.config.update({
		"TESTING": True,
		"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
	})
	with app.app_context():
		db.create_all()
		yield app
		db.session.remove()


@pytest.fixture()
def client(app):
	return app.test_client()


def test_health(client):
	rv = client.get("/health")
	assert rv.status_code == 200
	assert b"ok" in rv.data


def test_auth_protection(client):
	rv = client.get("/")
	# should redirect to login when not authenticated
	assert rv.status_code in (301, 302)


def test_duplicate_check(app):
	with app.app_context():
		l = Livre(titre="Test Book")
		db.session.add(l)
		db.session.commit()
		dups = find_potential_duplicates("Test")
		assert any(x.titre == "Test Book" for x in dups)


def test_import_books(app):
	with app.app_context():
		rows = [
			{
				"titre": "Imported Book",
				"editeur": "Edit",
				"langue": "FR",
				"serie": "Serie A",
				"numero_serie": "1",
				"emplacement": "Zone C10 EA",
				"auteurs": "Jean Dupont (auteur); Anne Martin (traducteur)",
				"genres": "Roman, Aventure",
				"oeuvres": "1 Histoire 1 (p.1-20); 2 Histoire 2",
			}
		]
		res = import_books_from_csv(rows)
		assert res.created == 1
		assert db.session.query(Livre).filter_by(titre="Imported Book").count() == 1
