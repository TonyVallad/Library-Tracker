from __future__ import annotations

from typing import Optional

from flask_login import UserMixin
from passlib.hash import bcrypt

from ..extensions import db, login_manager


user_role = db.Table(
	"user_role",
	db.Column("user_id", db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
	db.Column("role_id", db.Integer, db.ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
)


class Role(db.Model):
	__tablename__ = "role"
	id: int = db.Column(db.Integer, primary_key=True)
	name: str = db.Column(db.String(64), nullable=False)
	description: Optional[str] = db.Column(db.String(255), nullable=True)

	def __repr__(self) -> str:
		return f"<Role {self.name}>"


class User(UserMixin, db.Model):
	__tablename__ = "user"
	id: int = db.Column(db.Integer, primary_key=True)
	username: str = db.Column(db.String(128), nullable=False)
	email: Optional[str] = db.Column(db.String(255), nullable=True)
	password_hash: str = db.Column(db.String(255), nullable=False)
	is_active_flag: bool = db.Column(db.Boolean, default=True, nullable=False)

	roles = db.relationship(
		"Role",
		secondary=user_role,
		backref=db.backref("users", lazy="dynamic"),
		lazy="joined",
	)

	@property
	def is_active(self) -> bool:  # Flask-Login compatibility
		return self.is_active_flag

	def get_id(self) -> str:
		return str(self.id)

	def set_password(self, password: str) -> None:
		self.password_hash = bcrypt.hash(password)

	def check_password(self, password: str) -> bool:
		try:
			return bcrypt.verify(password, self.password_hash)
		except Exception:
			return False

	def has_role(self, name: str) -> bool:
		return any(r.name == name for r in self.roles or [])

	def __repr__(self) -> str:
		return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
	return db.session.get(User, int(user_id))
