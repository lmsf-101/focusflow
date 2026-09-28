import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from focusflow_api.config import get_settings
from focusflow_api.db import get_db
from focusflow_api.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:

    settings = get_settings()
    headers = {"WWW-Authenticate": "Bearer"}

    try:
        # Decodificación de token
        data = jwt.decode(
            token, key=settings.secret_key, algorithms=[settings.algorithm]
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Not permitted", headers=headers)
    else:
        sub = data.get("sub")

        if not (sub):
            raise HTTPException(
                status_code=401, detail="Sub not found", headers=headers
            )

        user = db.get(User, int(sub))

        if not user:
            raise HTTPException(
                status_code=401, detail="User does not exist", headers=headers
            )

        return user
