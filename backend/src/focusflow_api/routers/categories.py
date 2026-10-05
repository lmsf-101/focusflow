from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from focusflow_api.db import get_db
from focusflow_api.dependencies import get_current_user, get_owned_category
from focusflow_api.models import Category, User
from focusflow_api.schemas import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(tags=["categories"], prefix="/categories")


@router.get("", response_model=list[CategoryRead])
def get_categories(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list:

    stmt = select(Category).where(Category.owner_id == user.id)

    categories = db.execute(stmt).scalars().all()

    return categories


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category: Category = Depends(get_owned_category)) -> Category:
    return category


@router.post("", response_model=CategoryRead, status_code=201)
def create_category(
    body: CategoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Category:

    new_category = Category(name=body.name, owner_id=user.id)

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(
    body: CategoryUpdate,
    category: Category = Depends(get_owned_category),
    db: Session = Depends(get_db),
) -> Category:

    data = body.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)

    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category: Category = Depends(get_owned_category), db: Session = Depends(get_db)
):
    db.delete(category)
    db.commit()
