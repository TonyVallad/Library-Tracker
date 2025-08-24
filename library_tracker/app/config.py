from __future__ import annotations

import os
from pathlib import Path


class Config:
	SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

	BASE_DIR = Path(__file__).resolve().parent.parent.parent
	INSTANCE_PATH = BASE_DIR / "instance"
	DB_PATH = INSTANCE_PATH / "library.db"
	SQLALCHEMY_DATABASE_URI = os.getenv(
		"DATABASE_URL", f"sqlite:///{DB_PATH.as_posix()}"
	)
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	# Uploads
	STATIC_DIR = BASE_DIR / "library_tracker" / "app" / "static"
	UPLOAD_FOLDER = (STATIC_DIR / "uploads" / "covers").as_posix()
	THUMB_FOLDER = (STATIC_DIR / "thumbs" / "256").as_posix()
	MAX_CONTENT_LENGTH = 15 * 1024 * 1024  # 15 MB
	ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

	# i18n
	BABEL_DEFAULT_LOCALE = os.getenv("BABEL_DEFAULT_LOCALE", "fr")
	BABEL_DEFAULT_TIMEZONE = os.getenv("BABEL_DEFAULT_TIMEZONE", "Europe/Paris")

	# Auth
	SESSION_COOKIE_SECURE = False
	REMEMBER_COOKIE_SECURE = False

	def __call__(self) -> "Config":
		# ensure folders exist
		for path in [self.INSTANCE_PATH, Path(self.UPLOAD_FOLDER), Path(self.THUMB_FOLDER)]:
			path.mkdir(parents=True, exist_ok=True)
		return self
