from sqlalchemy.orm import Session

from app.db.models import Student
from app.services.passwords import hash_password

TEST_ACCOUNTS: list[dict[str, str]] = [
    {
        "email": "student@jobboard.test",
        "password": "Student123!",
        "name": "Test Student",
        "role": "student",
    },
    {
        "email": "demo@jobboard.test",
        "password": "Demo123!",
        "name": "Demo User",
        "role": "student",
    },
    {
        "email": "priya@jobboard.test",
        "password": "Priya123!",
        "name": "Priya Sharma",
        "role": "student",
    },
]


def seed_test_students(db: Session) -> int:
    created = 0
    for account in TEST_ACCOUNTS:
        student = db.query(Student).filter(Student.email == account["email"]).first()
        password_hash = hash_password(account["password"])
        if student:
            student.name = account["name"]
            student.password_hash = password_hash
            continue
        db.add(
            Student(
                email=account["email"],
                name=account["name"],
                password_hash=password_hash,
            )
        )
        created += 1
    db.flush()
    return created
