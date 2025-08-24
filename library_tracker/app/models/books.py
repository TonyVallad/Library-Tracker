from __future__ import annotations

from datetime import datetime
from typing import Optional

from ..extensions import db


class LivreAuteur(db.Model):
	__tablename__ = "livre_auteur"
	livre_id: int = db.Column(db.Integer, db.ForeignKey("livres.id", ondelete="CASCADE"), primary_key=True)
	auteur_id: int = db.Column(db.Integer, db.ForeignKey("auteur.id", ondelete="CASCADE"), primary_key=True)
	role: Optional[str] = db.Column(db.String(64), nullable=True)

	auteur = db.relationship("Auteur", backref=db.backref("livre_auteurs", cascade="all, delete-orphan"))


livre_genre = db.Table(
	"livre_genre",
	db.Column("livre_id", db.Integer, db.ForeignKey("livres.id", ondelete="CASCADE"), primary_key=True),
	db.Column("genre_id", db.Integer, db.ForeignKey("genre.id", ondelete="CASCADE"), primary_key=True),
)


class Livre(db.Model):
	__tablename__ = "livres"
	id: int = db.Column(db.Integer, primary_key=True)
	titre: str = db.Column(db.String(512), nullable=False)

	editeur_id: Optional[int] = db.Column(db.Integer, db.ForeignKey("editeur.id"))
	langue_id: Optional[int] = db.Column(db.Integer, db.ForeignKey("langue.id"))
	serie_id: Optional[int] = db.Column(db.Integer, db.ForeignKey("serie.id"))
	numero_serie: Optional[int] = db.Column(db.Integer)

	emplacement_id: Optional[int] = db.Column(db.Integer, db.ForeignKey("emplacement.id"))

	lien_couverture: Optional[str] = db.Column(db.String(1024))

	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	editeur = db.relationship("Editeur", backref="livres")
	langue = db.relationship("Langue", backref="livres")
	serie = db.relationship("Serie", backref="livres")
	emplacement = db.relationship("Emplacement", backref="livres")

	livre_auteurs = db.relationship(
		"LivreAuteur",
		cascade="all, delete-orphan",
		backref="livre",
		lazy="joined",
	)
	genres = db.relationship(
		"Genre",
		secondary=livre_genre,
		backref=db.backref("livres", lazy="dynamic"),
		lazy="joined",
	)

	def __repr__(self) -> str:
		return f"<Livre {self.titre}>"
