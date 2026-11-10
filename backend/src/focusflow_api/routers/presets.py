from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from focusflow_api.db import get_db
from focusflow_api.dependencies import get_current_user, get_owned_model_or_404
from focusflow_api.models import Category, PomodoroPreset, Project, User
from focusflow_api.schemas import PomodoroPresetCreate, PomodoroPresetRead

router = APIRouter(tags=["presets"], prefix="/presets")


@router.post("", response_model=PomodoroPresetRead, status_code=201)
def create_preset(
    body: PomodoroPresetCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PomodoroPreset:

    if body.project_id is not None:
        get_owned_model_or_404(
            db, model=Project, obj_id=body.project_id, user_id=user.id
        )

    if body.category_id is not None:
        get_owned_model_or_404(
            db, model=Category, obj_id=body.category_id, user_id=user.id
        )

    new_preset = PomodoroPreset(
        name=body.name,
        owner_id=user.id,
        project_id=body.project_id,
        category_id=body.category_id,
        mode=body.mode,
        start_minutes=body.start_minutes,
        num_of_rounds=body.num_of_rounds,
        break_minutes=body.break_minutes,
        growth=body.growth,
        cap_minutes=body.cap_minutes,
        rate=body.rate,
    )

    try:
        db.add(new_preset)
        db.commit()
        db.refresh(new_preset)

    except IntegrityError as integrity_err:
        db.rollback()
        # Recuperar la restricción para averiguar que regla se rompio
        constraint_name = integrity_err.orig.diag.constraint_name

        if constraint_name == "uq_pomodoro_preset_owner_id_name":
            raise HTTPException(
                status_code=409,
                detail="Cannot have duplicated presets (presets with the same name)",
            ) from integrity_err

        else:
            raise
    else:
        return new_preset


@router.get("", response_model=list[PomodoroPresetRead])
def get_presets(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[PomodoroPreset]:

    stmt = select(PomodoroPreset).where(PomodoroPreset.owner_id == user.id)

    user_presets = db.execute(stmt).scalars().all()

    return user_presets
