import re
from dataclasses import dataclass


@dataclass
class ExperienceInference:
    slug: str | None
    years_min: int | None = None
    years_max: int | None = None


BAND_RULES: list[tuple[str, list[str]]] = [
    ("intern", [r"\bintern\b", r"\binternship\b", r"summer intern"]),
    ("fresher", [r"\bfresher\b", r"fresh graduate", r"graduate trainee", r"\btrainee\b", r"0-1 year", r"entry level", r"\bentry\b"]),
    ("manager", [r"\bmanager\b", r"\bdirector\b", r"head of", r"\bvp\b"]),
    ("senior", [r"\bsenior\b", r"\blead\b", r"\barchitect\b", r"\bl4\b", r"\bl5\b", r"5\+?\s*years", r"5-8 years"]),
    ("mid", [r"mid.?level", r"3-5 years", r"3\+?\s*years", r"\bl3\b"]),
    ("junior", [r"\bjunior\b", r"1-3 years", r"1-2 years", r"\bl1\b", r"\bl2\b"]),
]

YEAR_RANGE_PATTERN = re.compile(
    r"(\d+)\s*[-–to]+\s*(\d+)\s*years?", re.IGNORECASE
)
SINGLE_YEAR_PATTERN = re.compile(r"(\d+)\+?\s*years?", re.IGNORECASE)


def infer_experience(title: str | None, description: str | None = None) -> ExperienceInference:
    text = f"{title or ''} {description or ''}".lower()

    for slug, patterns in BAND_RULES:
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                years = _parse_years(text)
                return ExperienceInference(slug=slug, years_min=years[0], years_max=years[1])

    years = _parse_years(text)
    if years[0] is not None:
        slug = _slug_from_years(years[0], years[1])
        return ExperienceInference(slug=slug, years_min=years[0], years_max=years[1])

    return ExperienceInference(slug=None)


def _parse_years(text: str) -> tuple[int | None, int | None]:
    match = YEAR_RANGE_PATTERN.search(text)
    if match:
        return int(match.group(1)), int(match.group(2))
    match = SINGLE_YEAR_PATTERN.search(text)
    if match:
        val = int(match.group(1))
        return val, val
    return None, None


def _slug_from_years(years_min: int, years_max: int | None) -> str:
    y = years_max if years_max is not None else years_min
    if y == 0:
        return "fresher"
    if y <= 1:
        return "fresher"
    if y <= 3:
        return "junior"
    if y <= 5:
        return "mid"
    return "senior"
