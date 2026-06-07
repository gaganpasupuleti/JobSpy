from __future__ import annotations

import base64
import hashlib
import hmac
import time
from uuid import UUID

from app.config import settings

_TOKEN_TTL_SECONDS = 60 * 60 * 24 * 14  # 14 days


def create_access_token(student_id: UUID) -> str:
    payload = f"{student_id}:{int(time.time())}"
    sig = hmac.new(
        settings.auth_secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    raw = f"{payload}:{sig}".encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8")


def verify_access_token(token: str) -> UUID | None:
    try:
        raw = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        student_id, issued_at, sig = raw.rsplit(":", 2)
        payload = f"{student_id}:{issued_at}"
        expected = hmac.new(
            settings.auth_secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        if int(time.time()) - int(issued_at) > _TOKEN_TTL_SECONDS:
            return None
        return UUID(student_id)
    except (ValueError, TypeError):
        return None
