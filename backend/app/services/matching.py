def job_matches_alert(job, alert) -> bool:
    keywords = (alert.keywords or "").strip().lower()
    if not keywords:
        return False

    title = (job.title or "").lower()
    description = (job.description or "").lower()
    if keywords not in title and keywords not in description:
        return False

    alert_location = (alert.location or "").strip().lower()
    job_location = (job.location or "").strip().lower()
    if alert_location:
        if alert_location != job_location and job_location != "remote":
            return False

    alert_exp = (alert.experience_level or "").strip()
    if alert_exp:
        job_exp = (job.experience_level or "").strip()
        if alert_exp.lower() != job_exp.lower():
            return False

    return True
