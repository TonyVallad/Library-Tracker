from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import abort
from flask_login import current_user, login_required


def require_roles(*role_names: str) -> Callable:
	def decorator(view: Callable) -> Callable:
		@login_required
		@wraps(view)
		def wrapped(*args, **kwargs):
			if not current_user.is_authenticated:
				abort(401)
			user_roles = {r.name for r in getattr(current_user, 'roles', [])}
			if not set(role_names).intersection(user_roles):
				abort(403)
			return view(*args, **kwargs)
		return wrapped
	return decorator
