from __future__ import annotations

import math
import random
import time
from datetime import datetime
from typing import Optional

from jobspy.exception import FounditException
from jobspy.foundit.constant import headers as foundit_headers
from jobspy.model import (
    Compensation,
    CompensationInterval,
    Country,
    DescriptionFormat,
    JobPost,
    JobResponse,
    Location,
    Scraper,
    ScraperInput,
    Site,
)
from jobspy.util import create_logger, create_session, markdown_converter

log = create_logger("Foundit")


class Foundit(Scraper):
    search_url = "https://www.foundit.in/middleware/jobsearch"
    jobs_per_page = 20

    def __init__(
        self, proxies: list[str] | str | None = None, ca_cert: str | None = None, user_agent: str | None = None
    ):
        super().__init__(Site.FOUNDIT, proxies=proxies, ca_cert=ca_cert)
        self.session = create_session(
            proxies=self.proxies,
            ca_cert=ca_cert,
            is_tls=False,
            has_retry=True,
            delay=3,
        )
        self.session.headers.update(foundit_headers)
        if user_agent:
            self.session.headers["user-agent"] = user_agent
        self.scraper_input = None

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        self.scraper_input = scraper_input
        if not scraper_input.search_term:
            return JobResponse(jobs=[])

        job_list: list[JobPost] = []
        seen_ids: set[str] = set()
        start = scraper_input.offset or 0
        page = 0
        max_pages = math.ceil(scraper_input.results_wanted / self.jobs_per_page) + 2

        location = self._normalize_location(scraper_input.location)

        while len(job_list) < scraper_input.results_wanted and page < max_pages:
            params = {
                "query": scraper_input.search_term,
                "start": start,
                "limit": self.jobs_per_page,
            }
            if location:
                params["locations"] = location

            log.info(
                f"search page: {page + 1} / {math.ceil(scraper_input.results_wanted / self.jobs_per_page)}"
            )
            try:
                response = self.session.get(self.search_url, params=params, timeout=20)
                if response.status_code not in range(200, 400):
                    log.error(
                        f"Foundit API response status code {response.status_code} - {response.text[:300]}"
                    )
                    break
                payload = response.json()
                jobs_data = payload.get("jobSearchResponse", {}).get("data", [])
            except Exception as exc:
                log.error(f"Foundit API request failed: {exc}")
                raise FounditException(str(exc)) from exc

            if not jobs_data:
                break

            for job in jobs_data:
                if job.get("type"):
                    continue
                job_id = str(job.get("jobId") or job.get("id") or "")
                if not job_id or job_id in seen_ids:
                    continue
                seen_ids.add(job_id)
                job_post = self._process_job(job, job_id)
                if job_post:
                    job_list.append(job_post)
                if len(job_list) >= scraper_input.results_wanted:
                    break

            if len(jobs_data) < self.jobs_per_page:
                break

            start += self.jobs_per_page
            page += 1
            time.sleep(random.uniform(1.5, 3.0))

        return JobResponse(jobs=job_list[: scraper_input.results_wanted])

    def _normalize_location(self, location: str | None) -> str | None:
        if not location:
            return None
        if location.lower() in ("india", "remote india", "remote"):
            return None
        return location.split(",")[0].strip()

    def _process_job(self, job: dict, job_id: str) -> Optional[JobPost]:
        title = job.get("title") or "Untitled"
        company = job.get("companyName")
        skills_raw = job.get("skills") or ""
        skills = [s.strip() for s in skills_raw.split(",") if s.strip()] if skills_raw else None

        job_url = job.get("applyUrl") or job.get("redirectUrl")
        if not job_url:
            seo_path = job.get("seoJdUrl") or job.get("jdUrl")
            if seo_path:
                job_url = seo_path if seo_path.startswith("http") else f"https://www.foundit.in{seo_path}"
        if not job_url:
            kiwi_id = job.get("kiwiJobId")
            job_url = f"https://www.foundit.in/job/{kiwi_id}" if kiwi_id else None
        if not job_url:
            return None

        location_str = job.get("locations") or ""
        parts = [p.strip() for p in location_str.split(",") if p.strip()]
        city = parts[0] if parts else location_str or None
        state = parts[1] if len(parts) > 1 else None

        compensation = self._parse_compensation(job)
        date_posted = self._parse_date(job.get("createdAt"))

        description_parts = []
        if skills_raw:
            description_parts.append(f"Key skills: {skills_raw}")
        if job.get("functions"):
            description_parts.append(f"Function: {', '.join(job['functions'])}")
        if job.get("roles"):
            description_parts.append(f"Role: {', '.join(job['roles'])}")
        exp = job.get("exp")
        if exp:
            description_parts.append(f"Experience: {exp}")
        salary_text = job.get("salary")
        if salary_text:
            description_parts.append(f"Salary: {salary_text}")

        description = "\n".join(description_parts) if description_parts else None
        if description and self.scraper_input.description_format == DescriptionFormat.MARKDOWN:
            description = markdown_converter(f"<p>{description.replace(chr(10), '</p><p>')}</p>")

        return JobPost(
            id=f"fd-{job_id}",
            title=title,
            company_name=company,
            company_url=job.get("seoCompanyUrl"),
            company_logo=job.get("companyLogoUrl") or job.get("companyLogo"),
            job_url=job_url,
            job_url_direct=job.get("applyUrl"),
            location=Location(city=city, state=state, country=Country.INDIA),
            is_remote="remote" in (title + location_str).lower(),
            date_posted=date_posted,
            compensation=compensation,
            description=description,
            company_industry=", ".join(job.get("industries", []) or []) or None,
            skills=skills,
            experience_range=job.get("exp"),
        )

    def _parse_compensation(self, job: dict) -> Optional[Compensation]:
        min_salary = job.get("minimumSalary") or {}
        max_salary = job.get("maximumSalary") or {}
        min_val = min_salary.get("absoluteValue")
        max_val = max_salary.get("absoluteValue")
        if not min_val and not max_val:
            return None
        currency = min_salary.get("currency") or max_salary.get("currency") or "INR"
        return Compensation(
            interval=CompensationInterval.YEARLY,
            min_amount=float(min_val) if min_val else None,
            max_amount=float(max_val) if max_val else None,
            currency=currency,
        )

    def _parse_date(self, created_at) -> Optional[datetime.date]:
        if not created_at:
            return None
        try:
            ts = int(created_at)
            if ts > 1_000_000_000_000:
                ts = ts / 1000
            return datetime.fromtimestamp(ts).date()
        except (TypeError, ValueError, OSError):
            return None
