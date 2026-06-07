from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_student
from app.db.models import Student
from app.db.session import get_db
from app.schemas.auth import LoginRequest, LoginResponse, StudentOut, TestAccountOut
from app.seed.test_users import TEST_ACCOUNTS
from app.services.auth_tokens import create_access_token
from app.services.passwords import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/test-accounts", response_model=list[TestAccountOut])
def list_test_accounts():
    """Public list of seeded test logins (for QA / demos)."""
    return [
        TestAccountOut(
            email=a["email"],
            password=a["password"],
            name=a["name"],
            role=a["role"],
        )
        for a in TEST_ACCOUNTS
    ]


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.email == body.email.lower()).first()
    if not student or not student.password_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not verify_password(body.password, student.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(student.id)
    return LoginResponse(
        access_token=token,
        student=StudentOut(id=student.id, email=student.email, name=student.name),
    )


@router.get("/me", response_model=StudentOut)
def me(student: Student = Depends(get_current_student)):
    return StudentOut(id=student.id, email=student.email, name=student.name)


@router.post("/logout")
def logout():
    return {"message": "Logged out (discard token on client)"}
