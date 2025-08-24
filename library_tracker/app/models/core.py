from __future__ import annotations

from typing import Optional

from ..extensions import db


class Auteur(db.Model):
	__tablename__ = "auteur"
	id: int = db.Column(db.Integer, primary_key=True)
	nom: str = db.Column(db.String(255), nullable=False)
	prenom: Optional[str] = db.Column(db.String(255))
	alias: Optional[str] = db.Column(db.String(255))

	def __repr__(self) -> str:
		return f"<Auteur {self.prenom or ''} {self.nom}>".strip()


class Editeur(db.Model):
	__tablename__ = "editeur"
	id: int = db.Column(db.Integer, primary_key=True)
	nom: str = db.Column(db.String(255), nullable=False)

	def __repr__(self) -> str:
		return f"<Editeur {self.nom}>"


class Langue(db.Model):
	__tablename__ = "langue"
	id: int = db.Column(db.Integer, primary_key=True)
	nom: str = db.Column(db.String(64), nullable=False)

	def __repr__(self) -> str:
		return f"<Langue {self.nom}>"


class Genre(db.Model):
	__tablename__ = "genre"
	id: int = db.Column(db.Integer, primary_key=True)
	nom: str = db.Column(db.String(128), nullable=False)

	def __repr__(self) -> str:
		return f"<Genre {self.nom}>"


class Serie(db.Model):
	__tablename__ = "serie"
	id: int = db.Column(db.Integer, primary_key=True)
	nom: str = db.Column(db.String(255), nullable=False)

	def __repr__(self) -> str:
		return f"<Serie {self.nom}>"


class Emplacement(db.Model):
	__tablename__ = "emplacement"
	id: int = db.Column(db.Integer, primary_key=True)
	colonne: int = db.Column(db.Integer, nullable=False)
	etage: str = db.Column(db.String(16), nullable=False)
	zone: str = db.Column(db.String(64), nullable=True)
	description: Optional[str] = db.Column(db.Text, nullable=True)

	def __repr__(self) -> str:
		return f"<Emplacement {self.zone or ''} C{self.colonne} E{self.etage}>".strip()
