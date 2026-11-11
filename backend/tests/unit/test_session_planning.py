import pytest
from pydantic import BaseModel

from focusflow_api.domain.pomodoro.errors import (
    PomodoroPlanError,
    PomodoroValidationError,
)
from focusflow_api.schemas import (
    ClassicPlanRequest,
    FlexiblePlanRequest,
    IncrementalPlanRequest,
)
from focusflow_api.services.session_planning import create_plan_from_request


def test_classic_request_to_plan():

    user_input = {
        "mode": "classic",
        "start_minutes": 25,
        "break_minutes": 5,
        "num_of_rounds": 4,
    }

    plan_request = ClassicPlanRequest(**user_input)

    pomodoro_plan = create_plan_from_request(plan_request)

    assert pomodoro_plan.work_times == (25, 25, 25, 25)
    assert pomodoro_plan.break_times == (5, 5, 5)


def test_incremental_request_to_plan():

    user_input = {
        "mode": "incremental",
        "start_minutes": 25,
        "cap_minutes": 35,
        "growth": 2,
        "num_of_rounds": 4,
    }

    plan_request = IncrementalPlanRequest(**user_input)

    pomodoro_plan = create_plan_from_request(plan_request)

    assert pomodoro_plan.work_times == (25, 27, 29, 31)
    assert pomodoro_plan.break_times == (5, 5, 6)


def test_flexible_request_to_plan():

    user_input = {
        "mode": "flexible",
        "start_minutes": 25,
        "cap_minutes": 35,
        "rate": 0.4,
        "num_of_rounds": 4,
        "break_ratio": 0.3,
    }

    plan_request = FlexiblePlanRequest(**user_input)

    pomodoro_plan = create_plan_from_request(plan_request)

    assert pomodoro_plan.work_times == (25, 29, 31, 33)
    assert pomodoro_plan.break_times == (8, 9, 9)


def test_request_with_broken_constraints_returns_validation_error():

    bad_input = {
        "mode": "incremental",
        "start_minutes": 25,
        "cap_minutes": 15,
        "growth": 2,
        "num_of_rounds": 4,
    }

    plan_request = IncrementalPlanRequest(**bad_input)

    with pytest.raises(PomodoroValidationError):
        create_plan_from_request(plan_request)


def test_create_plan_service_rejects_unknown_plan_request():

    class UnknownPlanRequest(BaseModel):
        mode: str
        start_minutes: int
        num_of_rounds: int

    unknown_request = UnknownPlanRequest(mode="test", start_minutes=25, num_of_rounds=4)

    with pytest.raises(PomodoroPlanError):
        _ = create_plan_from_request(unknown_request)  # pyright: ignore[reportArgumentType]
