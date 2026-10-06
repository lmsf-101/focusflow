from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from focusflow_api.db import get_db
from focusflow_api.dependencies import get_current_user, get_owned_tag
from focusflow_api.models import Tag, User
from focusflow_api.schemas import TagCreate, TagRead

router = APIRouter(tags=["tags"], prefix="/tags")


@router.get("", response_model=list[TagRead])
def get_tags(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list:

    stmt = select(Tag).where(Tag.owner_id == user.id)

    tags = db.execute(stmt).scalars().all()

    return tags


@router.get("/{tag_id}", response_model=TagRead)
def get_tag(tag: Tag = Depends(get_owned_tag)) -> Tag:
    return tag


@router.post("", response_model=TagRead, status_code=201)
def create_tag(
    body: TagCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Tag:

    new_tag = Tag(name=body.name, owner_id=user.id)

    try:
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)
    except IntegrityError as integrity_err:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot create tag (Possible duplicate or invalid value)",
        ) from integrity_err
    else:
        return new_tag


@router.delete("/{tag_id}", status_code=204)
def delete_tag(tag: Tag = Depends(get_owned_tag), db: Session = Depends(get_db)):
    db.delete(tag)
    db.commit()
