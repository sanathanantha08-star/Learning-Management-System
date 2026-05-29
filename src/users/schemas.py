import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


# ── Register ──────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "student"

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v.lower() not in {"student", "teacher"}:
            raise ValueError("role must be 'student' or 'teacher'")
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters")
        return v


class RegisterResponse(BaseModel):
    message: str
    user: "UserOut"


# ── Login ─────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ── Logout  ─────────────────────────────────────────────────────────────────────
class LogoutRequest(BaseModel):
    refresh_token: str

class LogoutResponse(BaseModel):
    message: str


# ── User out ──────────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

    # ── Refresh Tokens ──────────────────────────────────────────────────────────────────
class RefreshTokenOutRequest(BaseModel):
        refresh_token: str

class RefreshTokenResponse(BaseModel):
        access_token: str
        token_type: str = "bearer"


class UpdateUserRequest(BaseModel):
    full_name: str | None = None
    avatar_url: str | None = None

class UpdateUserResponse(BaseModel):
    message: str
    user: UserOut