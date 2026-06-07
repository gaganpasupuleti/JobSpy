from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class StudentOut(BaseModel):
    id: UUID
    email: str
    name: str | None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    student: StudentOut


class TestAccountOut(BaseModel):
    email: str
    password: str
    name: str
    role: str
