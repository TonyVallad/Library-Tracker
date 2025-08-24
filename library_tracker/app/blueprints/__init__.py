from __future__ import annotations

from flask import Flask


def register_all_blueprints(app: Flask) -> None:
	from .catalog.routes import bp as catalog_bp
	from .refs.routes import bp as refs_bp
	from .auth.routes import bp as auth_bp
	from .files.routes import bp as files_bp
	from .admin.routes import bp as admin_bp

	app.register_blueprint(catalog_bp)
	app.register_blueprint(refs_bp, url_prefix="/refs")
	app.register_blueprint(auth_bp, url_prefix="/auth")
	app.register_blueprint(files_bp, url_prefix="/files")
	app.register_blueprint(admin_bp, url_prefix="/admin")
