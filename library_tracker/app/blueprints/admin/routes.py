from __future__ import annotations

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from ...extensions import db
from ...models.auth import User, Role
from ...services.authz import require_roles

bp = Blueprint("admin", __name__, template_folder="../../templates/admin")


@bp.get("/")
@login_required
@require_roles("admin")
def home():
	users = db.session.query(User).all()
	roles = db.session.query(Role).all()
	return render_template("admin/users.html", users=users, roles=roles)


@bp.post("/users")
@login_required
@require_roles("admin")
def create_user():
	username = (request.form.get("username") or "").strip()
	password = request.form.get("password") or ""
	if not username or not password:
		flash("Nom d'utilisateur et mot de passe requis.", "error")
		return redirect(url_for("admin.home"))
	user = User(username=username)
	user.set_password(password)
	db.session.add(user)
	db.session.commit()
	flash("Utilisateur créé.", "success")
	return redirect(url_for("admin.home"))


@bp.post("/users/<int:user_id>/roles")
@login_required
@require_roles("admin")
def set_roles(user_id: int):
	user = db.session.get(User, user_id)
	if not user:
		flash("Utilisateur introuvable.", "error")
		return redirect(url_for("admin.home"))
	role_names = request.form.getlist("roles[]")
	roles = db.session.query(Role).filter(Role.name.in_(role_names)).all()
	user.roles = roles
	db.session.commit()
	flash("Rôles mis à jour.", "success")
	return redirect(url_for("admin.home"))


@bp.post("/users/<int:user_id>/reset_password")
@login_required
@require_roles("admin")
def reset_password(user_id: int):
	user = db.session.get(User, user_id)
	if not user:
		flash("Utilisateur introuvable.", "error")
		return redirect(url_for("admin.home"))
	new_password = request.form.get("password") or ""
	if not new_password:
		flash("Mot de passe requis.", "error")
		return redirect(url_for("admin.home"))
	user.set_password(new_password)
	db.session.commit()
	flash("Mot de passe réinitialisé.", "success")
	return redirect(url_for("admin.home"))
