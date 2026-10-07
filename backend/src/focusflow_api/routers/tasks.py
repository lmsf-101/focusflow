from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from focusflow_api.db import get_db
from focusflow_api.dependencies import (
    get_current_user,
    get_owned_model_or_404,
    get_owned_tags_or_404,
    get_owned_task,
)
from focusflow_api.models import Category, Project, Task, User
from focusflow_api.schemas import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(tags=["tasks"], prefix="/tasks")


@router.post("", response_model=TaskRead, status_code=201)
def create_task(
    body: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Task:

    if body.project_id is not None:
        get_owned_model_or_404(db, Project, body.project_id, user.id)

    if body.category_id is not None:
        get_owned_model_or_404(db, Category, body.category_id, user.id)

    user_tags = get_owned_tags_or_404(db, body.tag_ids, user.id)

    new_task = Task(
        title=body.title,
        owner_id=user.id,
        priority=body.priority,
        status=body.status,
        project_id=body.project_id,
        category_id=body.category_id,
        tags=user_tags,
    )

    db.add(new_task)

    db.commit()

    db.refresh(new_task)

    return new_task


@router.get("", response_model=list[TaskRead])
def get_tasks(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list:

    stmt = select(Task).where(Task.owner_id == user.id)

    tasks = db.execute(stmt).scalars().all()

    return tasks


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task: Task = Depends(get_owned_task)) -> Task:
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    body: TaskUpdate,
    task: Task = Depends(get_owned_task),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Task:

    data = body.model_dump(exclude_unset=True)

    if "project_id" in data and data["project_id"] is not None:
        get_owned_model_or_404(db, Project, data["project_id"], user.id)
    if "category_id" in data and data["category_id"] is not None:
        get_owned_model_or_404(db, Category, data["category_id"], user.id)

    if "tag_ids" in data:
        user_tags = get_owned_tags_or_404(db, data["tag_ids"], user.id)
        data.pop("tag_ids")
        task.tags = user_tags

    for key, value in data.items():
        setattr(task, key, value)

    db.commit()

    db.refresh(task)

    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task: Task = Depends(get_owned_task), db: Session = Depends(get_db)):
    db.delete(task)
    db.commit()
