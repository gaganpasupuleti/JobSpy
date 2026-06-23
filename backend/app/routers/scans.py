from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import EmailNotification, JobPost, JobScanRun
from app.lab_schemas import EmailNotificationOut, ScanResultOut, ScanRunOut
from app.services.scan_service import run_demo_scan

router = APIRouter()


@router.post("/scans/run-demo", response_model=ScanResultOut)
def run_demo(db: Session = Depends(get_db)):
    scan = run_demo_scan(db)
    return ScanResultOut(
        scan_run=ScanRunOut.model_validate(scan),
        emails_generated=scan.matched_alerts_count,
    )


@router.get("/email-notifications", response_model=list[EmailNotificationOut])
def list_email_notifications(db: Session = Depends(get_db)):
    rows = (
        db.query(EmailNotification)
        .order_by(EmailNotification.created_at.desc())
        .all()
    )
    result = []
    for row in rows:
        out = EmailNotificationOut.model_validate(row)
        if row.job_post:
            out.job_title = row.job_post.title
            out.company = row.job_post.company
        result.append(out)
    return result


@router.get("/scan-runs", response_model=list[ScanRunOut])
def list_scan_runs(db: Session = Depends(get_db)):
    return (
        db.query(JobScanRun)
        .order_by(JobScanRun.created_at.desc())
        .all()
    )
