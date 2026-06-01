import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import ExperienceBand, Keyword, Location, RoleCategory, SearchProfile
from app.seed.search_terms import build_profile_search_term

SEED_DIR = Path(__file__).parent


def seed_database(db: Session) -> dict:
    roles_data = json.loads((SEED_DIR / "roles_keywords.json").read_text(encoding="utf-8"))
    locations_data = json.loads((SEED_DIR / "locations_india.json").read_text(encoding="utf-8"))

    bands_created = _seed_experience_bands(db, roles_data["experience_bands"])
    roles_created = _seed_role_categories(db, roles_data["role_categories"])
    locations_created = _seed_locations(db, locations_data["locations"])
    profiles_created = _seed_search_profiles(db, roles_data["role_categories"])
    legacy_deactivated = _deactivate_legacy_profiles(db)

    db.commit()
    return {
        "experience_bands": bands_created,
        "role_categories": roles_created,
        "locations": locations_created,
        "search_profiles": profiles_created,
        "legacy_profiles_deactivated": legacy_deactivated,
    }


def _deactivate_legacy_profiles(db: Session) -> int:
    """Deactivate old role×city profiles without experience band (pre-1080 grid)."""
    legacy = (
        db.query(SearchProfile)
        .filter(
            SearchProfile.experience_band_id.is_(None),
            SearchProfile.is_active.is_(True),
        )
        .all()
    )
    for profile in legacy:
        profile.is_active = False
    db.flush()
    return len(legacy)


def _seed_experience_bands(db: Session, bands: list[dict]) -> int:
    created = 0
    for item in bands:
        existing = db.query(ExperienceBand).filter(ExperienceBand.slug == item["slug"]).first()
        if existing:
            continue
        db.add(
            ExperienceBand(
                slug=item["slug"],
                label=item["label"],
                sort_order=item.get("sort_order", 0),
            )
        )
        created += 1
    db.flush()
    return created


def _seed_role_categories(db: Session, categories: list[dict]) -> int:
    created = 0
    for item in categories:
        role = db.query(RoleCategory).filter(RoleCategory.slug == item["slug"]).first()
        if not role:
            role = RoleCategory(
                slug=item["slug"],
                name=item["name"],
                description=item.get("description"),
                sort_order=item.get("sort_order", 0),
            )
            db.add(role)
            db.flush()
            created += 1

        for kw in item.get("keywords", []):
            exists = (
                db.query(Keyword)
                .filter(Keyword.role_category_id == role.id, Keyword.term == kw["term"])
                .first()
            )
            if not exists:
                db.add(
                    Keyword(
                        role_category_id=role.id,
                        term=kw["term"],
                        is_primary=kw.get("is_primary", False),
                    )
                )
    db.flush()
    return created


def _seed_locations(db: Session, locations: list[dict]) -> int:
    created = 0
    for item in locations:
        existing = (
            db.query(Location)
            .filter(
                Location.city == item["city"],
                Location.state == item["state"],
                Location.country == "India",
            )
            .first()
        )
        if existing:
            continue
        db.add(
            Location(
                city=item["city"],
                state=item["state"],
                country="India",
                display_name=item["display_name"],
                indeed_location_string=item["indeed_location_string"],
                is_active=True,
            )
        )
        created += 1
    db.flush()
    return created


def _seed_search_profiles(db: Session, role_categories: list[dict]) -> int:
    created = 0
    roles = db.query(RoleCategory).all()
    locations = db.query(Location).filter(Location.is_active.is_(True)).all()
    bands = db.query(ExperienceBand).order_by(ExperienceBand.sort_order).all()
    search_terms = {r["slug"]: r["search_term"] for r in role_categories}

    for role in roles:
        base_term = search_terms.get(role.slug, role.name)
        for location in locations:
            for band in bands:
                existing = (
                    db.query(SearchProfile)
                    .filter(
                        SearchProfile.role_category_id == role.id,
                        SearchProfile.location_id == location.id,
                        SearchProfile.experience_band_id == band.id,
                    )
                    .first()
                )
                if existing:
                    existing.search_term = build_profile_search_term(base_term, band.slug)
                    existing.sites = settings.site_list
                    existing.is_active = True
                    continue
                db.add(
                    SearchProfile(
                        role_category_id=role.id,
                        location_id=location.id,
                        experience_band_id=band.id,
                        search_term=build_profile_search_term(base_term, band.slug),
                        sites=settings.site_list,
                        results_wanted=settings.default_results_wanted,
                        hours_old=settings.default_hours_old,
                        is_remote=location.city.lower() == "remote",
                        is_active=True,
                    )
                )
                created += 1
    db.flush()
    return created
