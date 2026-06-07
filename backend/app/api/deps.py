from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import Student
from app.db.session import get_db
from app.services.auth_tokens import verify_access_token


def verify_admin_key(x_admin_key: str = Header(..., alias="X-Admin-Key")) -> None:
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin API key")


def _student_from_authorization(
    authorization: str | None,
    db: Session,
) -> Student | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    student_id: UUID | None = verify_access_token(token)
    if not student_id:
        return None
    return db.query(Student).filter(Student.id == student_id).first()


def get_optional_student(
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
) -> Student | None:
    return _student_from_authorization(authorization, db)


def get_current_student(
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
) -> Student:
    student = _student_from_authorization(authorization, db)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return student
