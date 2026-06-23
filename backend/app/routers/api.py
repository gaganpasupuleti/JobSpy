from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import JobAlertRule, JobPost
from app.lab_schemas import (
    AlertRuleCreate,
    AlertRuleOut,
    AlertRuleUpdate,
    HealthOut,
    JobPostCreate,
    JobPostOut,
)
from app.services.email_service import send_test_email
from app.services.jobs import import_demo_jobs

router = APIRouter()


@router.get("/health", response_model=HealthOut)
def health():
    return HealthOut()


@router.get("/jobs", response_model=list[JobPostOut])
def list_jobs(
    keyword: str | None = Query(None),
    location: str | None = Query(None),
    source: str | None = Query(None),
    experience_level: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(JobPost)
    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(
            JobPost.title.ilike(pattern) | JobPost.description.ilike(pattern)
        )
    if location:
        query = query.filter(JobPost.location.ilike(f"%{location}%"))
    if source:
        query = query.filter(JobPost.source.ilike(f"%{source}%"))
    if experience_level:
        query = query.filter(JobPost.experience_level.ilike(f"%{experience_level}%"))
    return query.order_by(JobPost.created_at.desc()).all()


@router.post("/jobs", response_model=JobPostOut, status_code=201)
def create_job(payload: JobPostCreate, db: Session = Depends(get_db)):
    job = JobPost(**payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.post("/jobs/import-demo")
def import_demo(db: Session = Depends(get_db)):
    inserted, skipped = import_demo_jobs(db)
    return {"inserted": inserted, "skipped": skipped}


@router.get("/alerts", response_model=list[AlertRuleOut])
def list_alerts(db: Session = Depends(get_db)):
    return db.query(JobAlertRule).order_by(JobAlertRule.created_at.desc()).all()


@router.post("/alerts", response_model=AlertRuleOut, status_code=201)
def create_alert(payload: AlertRuleCreate, db: Session = Depends(get_db)):
    alert = JobAlertRule(**payload.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.patch("/alerts/{alert_id}", response_model=AlertRuleOut)
def update_alert(alert_id: int, payload: AlertRuleUpdate, db: Session = Depends(get_db)):
    alert = db.query(JobAlertRule).filter(JobAlertRule.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(alert, key, value)
    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/alerts/{alert_id}", status_code=204)
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(JobAlertRule).filter(JobAlertRule.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    db.delete(alert)
    db.commit()


@router.post("/alerts/{alert_id}/send-test")
def send_test(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(JobAlertRule).filter(JobAlertRule.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    notification = send_test_email(db, alert)
    db.commit()
    return {
        "message": "Test email generated (console mode)",
        "email_id": notification.id,
        "status": notification.status,
    }
