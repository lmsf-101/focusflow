from dataclasses import FrozenInstanceError

import pytest

from focusflow_api.domain.pomodoro.engine import (
    PomodoroPlan,
    plan_classic,
    plan_incremental,
)
from focusflow_api.domain.pomodoro.errors import (
    PomodoroPlanError,
    PomodoroValidationError,
)


@pytest.mark.parametrize(
    "work_times, break_times",
    [
        ((10, 15, 20, 25), (5, 10, 15)),
        ((5, 10, 12), (1, 2)),
        ((5, 10), (1,)),
        ((25,), ()),
        ((5, 10, 15, 20, 25, 30), (1, 2, 3, 4, 5)),
    ],
)
def test_pomodoro_plan_is_valid_with_the_correct_number_of_times(
    work_times: tuple[int, ...], break_times: tuple[int, ...]
):

    pomodoro_plan = PomodoroPlan(work_times, break_times)

    assert isinstance(pomodoro_plan, PomodoroPlan)

    assert pomodoro_plan.work_times == work_times
    assert pomodoro_plan.break_times == break_times


@pytest.mark.parametrize(
    "work_times, break_times",
    [
        ((10, 15, 20, 25), (5, 10, 15, 20)),
        ((5, 10, 12), (1, 2, 3)),
        ((5, 10), ()),
        ((5, 10, 25, 30), (1, 2, 3, 4, 5)),
    ],
)
def test_pomodoro_plan_fails_when_number_of_breaks_is_not_the_number_of_work_timers_minus_one(
    work_times: tuple[int, ...], break_times: tuple[int, ...]
):

    with pytest.raises(PomodoroPlanError, match="must be one less than"):
        _ = PomodoroPlan(work_times, break_times)


def test_pomodoro_plan_is_inmutable():

    with pytest.raises(FrozenInstanceError):
        pomodoro_plan = PomodoroPlan((5, 10, 15, 20), (1, 2, 3))
        pomodoro_plan.work_times = (10, 15, 20)


def test_empty_pomodoro_plan_is_rejected():
    with pytest.raises(PomodoroPlanError, match="tuple must not be empty"):
        _ = PomodoroPlan((), ())


@pytest.mark.parametrize(
    "start_minutes, break_minutes, num_of_rounds, expected_work_times, expected_break_times",
    [
        (25, 5, 4, (25, 25, 25, 25), (5, 5, 5)),
        (10, 2, 3, (10, 10, 10), (2, 2)),
        (80, 15, 2, (80, 80), (15,)),
        (70, 5, 1, (70,), ()),
    ],
)
def test_plan_classic_returns_fixed_work_times_and_break_times(
    start_minutes: int,
    break_minutes: int,
    num_of_rounds: int,
    expected_work_times: tuple[int, ...],
    expected_break_times: tuple[int, ...],
):

    pomodoro_plan = plan_classic(start_minutes, break_minutes, num_of_rounds)

    assert pomodoro_plan.work_times == expected_work_times
    assert pomodoro_plan.break_times == expected_break_times


@pytest.mark.parametrize(
    "start_minutes, break_minutes, num_of_rounds, expected_field",
    [
        (0, 5, 4, "start_minutes"),
        (-5, 1, 2, "start_minutes"),
        (10, -5, 2, "break_minutes"),
        (12, 0, 5, "break_minutes"),
        (20, 5, 0, "num_of_rounds"),
        (20, 2, -5, "num_of_rounds"),
        (90, 5, 3, "start_minutes"),
    ],
)
def test_plan_classic_fails_when_invalid_arguments_are_passed(
    start_minutes: int, break_minutes: int, num_of_rounds: int, expected_field: str
):

    with pytest.raises(PomodoroValidationError) as exc_info:
        _ = plan_classic(start_minutes, break_minutes, num_of_rounds)

    assert exc_info.value.field == expected_field


@pytest.mark.parametrize(
    "start_minutes, growth, cap_minutes, num_of_rounds, expected_work_times, expected_break_times",
    [
        (25, 2, 30, 4, (25, 27, 29, 30), (5, 5, 6)),
        (10, 3, 15, 5, (10, 13, 15, 15, 15), (2, 3, 3, 3)),
        (2, 5, 20, 7, (2, 7, 12, 17, 20, 20, 20), (1, 1, 2, 3, 4, 4)),
        (50, 5, 55, 1, (50,), ()),
    ],
)
def test_plan_incremental_returns_incremental_work_times_and_adaptive_break_times(
    start_minutes: int,
    growth: int,
    cap_minutes: int,
    num_of_rounds: int,
    expected_work_times: tuple[int, ...],
    expected_break_times: tuple[int, ...],
):

    pomodoro_plan = plan_incremental(start_minutes, growth, cap_minutes, num_of_rounds)

    assert pomodoro_plan.work_times == expected_work_times
    assert pomodoro_plan.break_times == expected_break_times


@pytest.mark.parametrize(
    "start_minutes, growth, cap_minutes, num_of_rounds, expected_field",
    [
        (0, 5, 10, 4, "start_minutes"),
        (-5, 1, 5, 2, "start_minutes"),
        (10, -5, 12, 2, "growth"),
        (5, 0, 15, 3, "growth"),
        (12, 2, 10, 5, "cap_minutes"),
        (10, 5, -5, 3, "cap_minutes"),
        (20, 5, 25, 0, "num_of_rounds"),
        (15, 3, 25, -3, "num_of_rounds"),
    ],
)
def test_plan_incremental_fails_when_invalid_arguments_are_passed(
    start_minutes: int,
    growth: int,
    cap_minutes: int,
    num_of_rounds: int,
    expected_field: str,
):

    with pytest.raises(PomodoroValidationError) as exec_info:
        _ = plan_incremental(start_minutes, growth, cap_minutes, num_of_rounds)

    assert exec_info.value.field == expected_field
