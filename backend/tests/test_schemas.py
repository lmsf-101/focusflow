import pydantic
import pytest

from focusflow_api.models import User
from focusflow_api.schemas import UserCreate, UserRead


# Validar que correo con formato invalido en UserCreate es rechazado
def test_invalid_email_in_UserCreate_is_rejected():
    with pytest.raises(pydantic.ValidationError):
        _ = UserCreate(email="test123", password="password")


# Validar que usuario sin contraseña en UserCreate es rechazado
def test_user_with_no_password_is_rejected():
    with pytest.raises(pydantic.ValidationError):
        _ = UserCreate(email="test123@gmail.com", password=None)


# Verificar que UserRead (lectura de un usuario) no regresa credenciales confidenciales (password)
def test_UserRead_does_not_expose_secrets():
    user = User(id=1, email="test123@gmail.com", hashed_password="secret")

    user_data = UserRead.model_validate(user).model_dump()

    assert "hashed_password" not in user_data
