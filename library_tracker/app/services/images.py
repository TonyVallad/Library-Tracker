from __future__ import annotations

import imghdr
import os
import uuid
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image
from werkzeug.utils import secure_filename


def is_allowed_image(filename: str, allowed_ext: set[str]) -> bool:
	return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_ext


def guess_extension(file_bytes: bytes) -> Optional[str]:
	kind = imghdr.what(None, h=file_bytes)
	if kind == "jpeg":
		return "jpg"
	return kind


def save_image_and_thumbnail(
	*,
	file_storage,
	upload_dir: str,
	thumb_dir: str,
	allowed_ext: set[str],
	max_side: int = 256,
) -> Tuple[str, str]:
	filename = secure_filename(file_storage.filename or "")
	original_bytes = file_storage.read()
	file_storage.stream.seek(0)

	ext = guess_extension(original_bytes) or (filename.rsplit(".", 1)[1].lower() if "." in filename else None)
	if not ext or ext not in allowed_ext:
		raise ValueError("Format d'image non autorisé.")

	uid = uuid.uuid4().hex
	base_name = f"{uid}.{ext}"

	upload_path = Path(upload_dir)
	upload_path.mkdir(parents=True, exist_ok=True)
	thumb_path = Path(thumb_dir)
	thumb_path.mkdir(parents=True, exist_ok=True)

	image_path = upload_path / base_name
	thumb_file_path = thumb_path / base_name

	file_storage.save(image_path.as_posix())

	# Generate thumbnail
	with Image.open(image_path.as_posix()) as img:
		img.thumbnail((max_side, max_side))
		img.save(thumb_file_path.as_posix())

	return image_path.name, thumb_file_path.name


def delete_cover_files(filename: Optional[str], upload_dir: str, thumb_dir: str) -> None:
	if not filename:
		return
	try:
		for base in [upload_dir, thumb_dir]:
			p = Path(base) / filename
			if p.exists():
				p.unlink(missing_ok=True)
	except Exception:
		# Silently ignore file deletion errors
		return
