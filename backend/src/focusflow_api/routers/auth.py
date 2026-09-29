from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from focusflow_api.db import get_db
from focusflow_api.dependencies import get_current_user
from focusflow_api.models import User
from focusflow_api.schemas import Token, UserCreate, UserRead
from focusflow_api.security import create_access_token, hash_password, verify_password

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=UserRead)
def register_user(body: UserCreate, db: Session = Depends(get_db)) -> User:
    # Revisar si hay un usuario existente con el email ingresado
    stmt = select(User).where(User.email == body.email)

    # Si existe, avisar que ya se registro con el email particular:
    if db.execute(stmt).scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="The email has been registered previously. Try recovering the account.",
        )

    # Crear nuevo usuario con ID, y agregarlo a la base de datos
    new_user = User(email=body.email, hashed_password=hash_password(body.password))

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/token", response_model=Token)
def generate_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:

    # Buscar si existe usuario
    stmt = select(User).where(User.email == form_data.username)

    user = db.execute(stmt).scalar_one_or_none()

    # Si no existe el usuario, o no cumple con la contraseña, denegar creacion de token
    if not (user and verify_password(form_data.password, user.hashed_password)):
        raise HTTPException(
            status_code=401,
            detail="Incorrect credentials. Try again",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear token de acceso
    token = create_access_token(data={"id": user.id})

    return Token(access_token=token, token_type="bearer")


@router.get("/users/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user
