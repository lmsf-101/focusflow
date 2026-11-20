from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from focusflow_api.db import get_db
from focusflow_api.dependencies import get_current_user, get_owned_tasks_or_404
from focusflow_api.domain.pomodoro.engine import PomodoroPlan
from focusflow_api.models import (
    PomodoroSession,
    PomodoroSessionTask,
    SessionStatus,
    User,
)
from focusflow_api.schemas import (
    PlanRequest,
    PlanResponse,
    PomodoroSessionCreate,
    PomodoroSessionRead,
)
from focusflow_api.services.session_planning import (
    build_planned_config,
    create_plan_from_request,
)

router = APIRouter(tags=["sessions"], prefix="/sessions")


@router.post("", response_model=PomodoroSessionRead, status_code=201)
def create_session(
    body: PomodoroSessionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PomodoroSession:

    planned_config = build_planned_config(body.params)

    tasks = get_owned_tasks_or_404(
        db=db, task_ids=[task.task_id for task in body.tasks], user_id=user.id
    )

    tasks_dict = {t.id: t for t in tasks}

    pomodoro_session = PomodoroSession(
        owner_id=user.id,
        mode=body.params.mode,
        status=SessionStatus.ACTIVE,
        planned_config=planned_config,
    )

    db.add(pomodoro_session)
    for t in body.tasks:
        db.add(
            PomodoroSessionTask(
                task_id=t.task_id,
                task_title=tasks_dict[t.task_id].title,
                category_id=tasks_dict[t.task_id].category_id,
                estimate_minutes=t.estimate_minutes,
                pomodoro_session=pomodoro_session,
            )
        )

    db.commit()

    db.refresh(pomodoro_session, ["session_tasks"])

    return pomodoro_session


@router.post("/plan", response_model=PlanResponse)
def plan_session(
    body: PlanRequest,
    user: User = Depends(get_current_user),
) -> PomodoroPlan:

    return create_plan_from_request(body)
