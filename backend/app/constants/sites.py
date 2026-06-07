"""Job board source labels and display order."""

SITE_LABELS: dict[str, str] = {
    "indeed": "Indeed",
    "linkedin": "LinkedIn",
    "naukri": "Naukri",
    "foundit": "Foundit",
    "glassdoor": "Glassdoor",
    "google": "Google Jobs",
    "zip_recruiter": "ZipRecruiter",
    "bayt": "Bayt",
    "bdjobs": "BDJobs",
}

SITE_ORDER: tuple[str, ...] = (
    "indeed",
    "linkedin",
    "naukri",
    "foundit",
    "glassdoor",
    "google",
    "zip_recruiter",
    "bayt",
    "bdjobs",
)


def site_label(slug: str) -> str:
    return SITE_LABELS.get(slug.lower(), slug.replace("_", " ").title())
