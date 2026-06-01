"""Build role × experience search queries for India profiles."""

LEVEL_QUERY_FRAGMENTS: dict[str, str] = {
    "intern": '"intern" OR internship',
    "fresher": 'fresher OR "entry level" OR graduate OR trainee',
    "junior": 'junior OR "1-3 years" OR "1-2 years"',
    "mid": '"mid level" OR "3-5 years" OR "3+ years"',
    "senior": 'senior OR lead OR "5+ years" OR architect',
    "manager": 'manager OR director OR "head of" OR VP',
}


def build_profile_search_term(role_search_term: str, experience_slug: str) -> str:
    level_part = LEVEL_QUERY_FRAGMENTS.get(experience_slug, "")
    if not level_part:
        return role_search_term
    return f"({role_search_term}) AND ({level_part})"
