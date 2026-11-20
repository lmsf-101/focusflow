from typing import Any

from focusflow_api.domain.pomodoro.engine import (
    PomodoroPlan,
    plan_classic,
    plan_flexible,
    plan_incremental,
)
from focusflow_api.domain.pomodoro.errors import PomodoroPlanError
from focusflow_api.schemas import (
    ClassicPlanRequest,
    FlexiblePlanRequest,
    IncrementalPlanRequest,
    PlannedConfig,
    PlanRequest,
    PlanResponse,
)

PLANNED_CONFIG_SCHEMA_VERSION = 1


def create_plan_from_request(plan: PlanRequest) -> PomodoroPlan:

    if isinstance(plan, ClassicPlanRequest):
        return plan_classic(
            start_minutes=plan.start_minutes,
            break_minutes=plan.break_minutes,
            num_of_rounds=plan.num_of_rounds,
        )

    elif isinstance(plan, IncrementalPlanRequest):
        return plan_incremental(
            start_minutes=plan.start_minutes,
            growth=plan.growth,
            cap_minutes=plan.cap_minutes,
            num_of_rounds=plan.num_of_rounds,
        )

    elif isinstance(plan, FlexiblePlanRequest):
        return plan_flexible(
            start_minutes=plan.start_minutes,
            cap_minutes=plan.cap_minutes,
            rate=plan.rate,
            num_of_rounds=plan.num_of_rounds,
            break_ratio=plan.break_ratio,
        )
    else:
        raise PomodoroPlanError(
            "An error occurred trying to setup the Pomodoro Session"
        )


def build_planned_config(params: PlanRequest) -> dict[str, Any]:
    pomodoro_plan = create_plan_from_request(params)

    config_plan = PlannedConfig(
        schema_version=PLANNED_CONFIG_SCHEMA_VERSION,
        params=params,
        plan=PlanResponse.model_validate(pomodoro_plan),
    )

    return config_plan.model_dump(mode="json")
