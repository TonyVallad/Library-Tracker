from __future__ import annotations

from typing import Iterable

from ..extensions import db
from ..models.books import Livre


def find_potential_duplicates(titre: str) -> list[Livre]:
	if not titre:
		return []
	q = db.session.query(Livre).filter(Livre.titre.ilike(f"%{titre.strip()}%"))
	return list(q.limit(10))
