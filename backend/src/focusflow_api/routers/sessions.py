from fastapi import APIRouter, Depends

from focusflow_api.dependencies import get_current_user
from focusflow_api.domain.pomodoro.engine import PomodoroPlan
from focusflow_api.models import User
from focusflow_api.schemas import PlanRequest, PlanResponse
from focusflow_api.services.session_planning import create_plan_from_request

router = APIRouter(tags=["sessions"], prefix="/sessions")


@router.post("/plan", response_model=PlanResponse)
def plan_session(
    body: PlanRequest,
    user: User = Depends(get_current_user),
) -> PomodoroPlan:

    return create_plan_from_request(body)
