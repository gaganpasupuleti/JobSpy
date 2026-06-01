from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db.models import Keyword, RoleCategory

MIN_ROLE_SCORE = 2
MISMATCH_FLAG_SCORE = 3


@dataclass
class RoleClassification:
    role_category_id: int | None
    role_slug: str | None
    score: int
    profile_mismatch: bool


def classify_role(
    db: Session,
    *,
    title: str | None,
    description: str | None,
    profile_role_category_id: int | None,
) -> RoleClassification:
    haystack = f"{title or ''} {description or ''}".lower()
    roles = db.query(RoleCategory).all()
    keywords_by_role: dict[int, list[Keyword]] = {}
    for role in roles:
        keywords_by_role[role.id] = (
            db.query(Keyword).filter(Keyword.role_category_id == role.id).all()
        )

    best_id: int | None = None
    best_slug: str | None = None
    best_score = 0

    for role in roles:
        score = _score_role(haystack, keywords_by_role.get(role.id, []))
        if score > best_score:
            best_score = score
            best_id = role.id
            best_slug = role.slug

    if best_score < MIN_ROLE_SCORE:
        return RoleClassification(
            role_category_id=None,
            role_slug=None,
            score=best_score,
            profile_mismatch=False,
        )

    mismatch = (
        profile_role_category_id is not None
        and best_id != profile_role_category_id
        and best_score >= MISMATCH_FLAG_SCORE
    )
    return RoleClassification(
        role_category_id=best_id,
        role_slug=best_slug,
        score=best_score,
        profile_mismatch=mismatch,
    )


def _score_role(haystack: str, keywords: list[Keyword]) -> int:
    score = 0
    for kw in keywords:
        term = kw.term.lower()
        if term and term in haystack:
            score += 3 if kw.is_primary else 1
    return score
