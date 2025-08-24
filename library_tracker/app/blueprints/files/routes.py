from __future__ import annotations

from flask import Blueprint

bp = Blueprint("files", __name__)


@bp.get("/")
def files_home():
	return "Files"
