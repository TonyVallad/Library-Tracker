from __future__ import annotations

from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required

from ...extensions import db
from ...models.auth import User

bp = Blueprint("auth", __name__, template_folder="../../templates/auth")


@bp.get("/login")
@bp.post("/login")
def login():
	if request.method == "POST":
		username = request.form.get("username", "").strip()
		password = request.form.get("password", "")
		user = db.session.query(User).filter(User.username == username).first()
		if user and user.check_password(password):
			login_user(user)
			flash("Connecté.", "success")
			return redirect(url_for("catalog.home"))
		flash("Identifiants invalides.", "error")
	return render_template("auth/login.html")


@bp.get("/logout")
@login_required

def logout():
	logout_user()
	flash("Déconnecté.", "info")
	return redirect(url_for("auth.login"))
