from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from focusflow_api.db import get_db
from focusflow_api.dependencies import get_current_user, get_owned_project
from focusflow_api.models import Project, User
from focusflow_api.schemas import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(tags=["projects"], prefix="/projects")


@router.post("", response_model=ProjectRead, status_code=201)
def create_project(
    body: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Project:

    new_project = Project(owner_id=user.id, name=body.name)

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


@router.get("", response_model=list[ProjectRead])
def get_projects(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list:

    stmt = select(Project).where(Project.owner_id == user.id)

    projects = db.execute(stmt).scalars().all()

    return projects


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project: Project = Depends(get_owned_project)) -> Project:
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    body: ProjectUpdate,
    project: Project = Depends(get_owned_project),
    db: Session = Depends(get_db),
) -> Project:

    data = body.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(project, key, value)

    db.commit()

    db.refresh(project)

    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project: Project = Depends(get_owned_project), db: Session = Depends(get_db)
):
    db.delete(project)
    db.commit()
