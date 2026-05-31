from __future__ import annotations

import re

# Common skills for India tech/analytics roles (matched case-insensitively in text)
KNOWN_SKILLS = [
    "Python", "SQL", "Excel", "Power BI", "Tableau", "R", "SAS", "SPSS",
    "Java", "JavaScript", "TypeScript", "React", "Node.js", "Angular", "Vue",
    "HTML", "CSS", "C++", "C#", ".NET", "Spring Boot", "Django", "Flask", "FastAPI",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "DevOps", "CI/CD", "Git",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "TensorFlow", "PyTorch",
    "Pandas", "NumPy", "Scikit-learn", "Spark", "Hadoop", "Kafka", "Airflow", "dbt",
    "Snowflake", "Redshift", "BigQuery", "MongoDB", "PostgreSQL", "MySQL", "Oracle",
    "Looker", "Qlik", "Alteryx", "VBA", "Macros", "Statistics", "A/B Testing",
    "Agile", "Scrum", "JIRA", "Figma", "Photoshop", "Illustrator",
    "SEO", "Google Analytics", "Meta Ads", "Salesforce", "SAP", "ERP",
    "Selenium", "Automation Testing", "Manual Testing", "API Testing",
    "Business Analysis", "Data Modeling", "ETL", "Data Warehousing", "BI",
    "Communication", "Presentation", "Stakeholder Management",
]

SKILLS_SECTION_PATTERN = re.compile(
    r"(?:key\s*skills?|required\s*skills?|skills?\s*required|technical\s*skills?|"
    r"must\s*have|good\s*to\s*have|qualifications?)[:\s]*([^\n]{10,500})",
    re.IGNORECASE,
)


def _normalize_skill_list(raw: str) -> list[str]:
    parts = re.split(r"[,;|•\n/]+", raw)
    seen: set[str] = set()
    result: list[str] = []
    for part in parts:
        skill = part.strip(" .-•*")
        if not skill or len(skill) < 2 or len(skill) > 60:
            continue
        key = skill.lower()
        if key not in seen:
            seen.add(key)
            result.append(skill)
    return result[:20]


def _match_known_skills(text: str) -> list[str]:
    if not text:
        return []
    found: list[str] = []
    seen: set[str] = set()
    lower = text.lower()
    for skill in KNOWN_SKILLS:
        if skill.lower() in lower:
            key = skill.lower()
            if key not in seen:
                seen.add(key)
                found.append(skill)
    return found[:15]


def extract_key_skills(
    description: str | None,
    raw_skills: str | None = None,
    title: str | None = None,
) -> str | None:
    """
    Returns comma-separated key skills for storage in key_skills column.
    Priority: scraper-provided skills (Naukri) → skills section in description → known skill matches.
    """
    skills: list[str] = []

    if raw_skills:
        skills.extend(_normalize_skill_list(raw_skills))

    combined = f"{title or ''} {description or ''}"

    if description:
        section_match = SKILLS_SECTION_PATTERN.search(description)
        if section_match:
            skills.extend(_normalize_skill_list(section_match.group(1)))

    if not skills:
        skills.extend(_match_known_skills(combined))

    if not skills:
        return None

    # Deduplicate preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for s in skills:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            unique.append(s)

    return ", ".join(unique[:20])
