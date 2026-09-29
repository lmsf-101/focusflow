from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

from focusflow_api.config import get_settings

pass_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return pass_hash.hash(password)


def verify_password(text: str, hash_password: str) -> bool:
    return pass_hash.verify(text, hash_password)


def create_access_token(
    data: dict[str, Any], expiration_delta: timedelta | None = None
) -> str:

    settings = get_settings()

    expiration = datetime.now(tz=UTC)

    if expiration_delta:
        expiration = expiration + expiration_delta
    else:
        expiration = expiration + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    payload_data = {"sub": str(data["id"]), "exp": expiration}

    return jwt.encode(
        payload=payload_data, key=settings.secret_key, algorithm=settings.algorithm
    )
