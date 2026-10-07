import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from focusflow_api.config import get_settings
from focusflow_api.db import get_db
from focusflow_api.models import Category, Project, Tag, Task, User

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
        raise HTTPException(status_code=401, detail="Unauthorized", headers=headers)
    else:
        sub = data.get("sub")

        if not (sub):
            raise HTTPException(status_code=401, detail="Unauthorized", headers=headers)

        user = db.get(User, int(sub))

        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized", headers=headers)

        return user


def get_owned_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Project:

    stmt = select(Project).where(Project.id == project_id, Project.owner_id == user.id)

    project = db.execute(stmt).scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


def get_owned_category(
    category_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Category:

    stmt = select(Category).where(
        Category.id == category_id, Category.owner_id == user.id
    )

    category = db.execute(stmt).scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category


def get_owned_task(
    task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Task:

    stmt = select(Task).where(Task.id == task_id, Task.owner_id == user.id)

    task = db.execute(stmt).scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def get_owned_tag(
    tag_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Tag:
    return get_owned_model_or_404(db, Tag, tag_id, user.id)


def get_owned_model_or_404[T](
    db: Session, model: type[T], obj_id: int, user_id: int
) -> T:

    stmt = select(model).where(model.id == obj_id, model.owner_id == user_id)

    result = db.execute(stmt).scalar_one_or_none()

    if not result:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return result


def get_owned_tags_or_404(db: Session, tag_ids: list[int], user_id: int) -> list[Tag]:

    if not tag_ids:
        return []

    user_tags_stmt = select(Tag).where(Tag.owner_id == user_id, Tag.id.in_(tag_ids))
    user_tags_list = db.execute(user_tags_stmt).scalars().all()

    if set(tag_ids) != {tag.id for tag in user_tags_list}:
        raise HTTPException(status_code=404, detail="One or more tags was not found.")

    return user_tags_list
