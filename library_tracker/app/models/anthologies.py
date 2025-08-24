from __future__ import annotations

from typing import Optional

from ..extensions import db


class Oeuvre(db.Model):
	__tablename__ = "oeuvre"
	id: int = db.Column(db.Integer, primary_key=True)
	titre: str = db.Column(db.String(512), nullable=False)
	resume: Optional[str] = db.Column(db.Text, nullable=True)
	notes: Optional[str] = db.Column(db.Text, nullable=True)

	def __repr__(self) -> str:
		return f"<Oeuvre {self.titre}>"


oeuvre_auteur = db.Table(
	"oeuvre_auteur",
	db.Column("oeuvre_id", db.Integer, db.ForeignKey("oeuvre.id", ondelete="CASCADE"), primary_key=True),
	db.Column("auteur_id", db.Integer, db.ForeignKey("auteur.id", ondelete="CASCADE"), primary_key=True),
	db.Column("role", db.String(64), nullable=True),
)


class LivreOeuvre(db.Model):
	__tablename__ = "livre_oeuvre"
	livre_id: int = db.Column(db.Integer, db.ForeignKey("livres.id", ondelete="CASCADE"), primary_key=True)
	oeuvre_id: int = db.Column(db.Integer, db.ForeignKey("oeuvre.id", ondelete="CASCADE"), primary_key=True)
	ordre: Optional[int] = db.Column(db.Integer, nullable=True)
	pages: Optional[str] = db.Column(db.String(64), nullable=True)

	livre = db.relationship("Livre", backref=db.backref("livre_oeuvres", cascade="all, delete-orphan"))
	oeuvre = db.relationship("Oeuvre", backref=db.backref("livre_oeuvres", cascade="all, delete-orphan"))
