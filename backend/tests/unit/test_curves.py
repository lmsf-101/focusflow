import pytest

from focusflow_api.domain.pomodoro.curves import (
    MAX_NUMBER_ROUNDS,
    MAX_POMODORO_LIMIT,
    MAX_RATE,
    MIN_RATE,
    asymptotic_curve,
    curve,
)
from focusflow_api.domain.pomodoro.errors import PomodoroCurveError


@pytest.mark.parametrize(
    "start_minutes, growth, cap_minutes, num_of_rounds, expected_list",
    [
        (20, 2, 30, 4, [20, 22, 24, 26]),
        (25, 5, 50, 4, [25, 30, 35, 40]),
        (5, 5, 12, 4, [5, 10, 12, 12]),
        (1, 2, 4, 3, [1, 3, 4]),
        (10, 3, 10, 3, [10, 10, 10]),
        (15, 0, 30, 3, [15, 15, 15]),
        (20, 5, 60, 1, [20]),
        (
            MAX_POMODORO_LIMIT,
            1,
            MAX_POMODORO_LIMIT,
            2,
            [MAX_POMODORO_LIMIT, MAX_POMODORO_LIMIT],
        ),
        (10, 0, 10, MAX_NUMBER_ROUNDS, [10] * MAX_NUMBER_ROUNDS),
    ],
)
def test_pomodoro_curves_are_calculated_correctly_based_on_appropiate_arguments(
    start_minutes, growth, cap_minutes, num_of_rounds, expected_list
):
    assert curve(start_minutes, growth, cap_minutes, num_of_rounds) == expected_list


@pytest.mark.parametrize(
    "arguments, expected_invalid_field",
    [
        ([-5, 2, 5, 2], "start_minutes"),
        ([0, 2, 5, 2], "start_minutes"),
        ([1, 2, 5, -5], "num_of_rounds"),
        ([1, 2, 5, 0], "num_of_rounds"),
        ([5, 2, 2, 4], "cap_minutes"),
        ([10, -5, 20, 3], "growth"),
        ([10, 10, MAX_POMODORO_LIMIT + 1, 4], "cap_minutes"),
        ([20, 5, 30, MAX_NUMBER_ROUNDS + 1], "num_of_rounds"),
    ],
)
def test_pomodoro_curves_fail_with_invalid_arguments(arguments, expected_invalid_field):
    with pytest.raises(PomodoroCurveError) as exc_info:
        curve(*arguments)
    assert exc_info.value.field == expected_invalid_field


@pytest.mark.parametrize(
    "start_minutes, cap_minutes, rate, num_of_rounds, expected_work_times",
    [
        (5, 30, 0.5, 4, [5, 18, 24, 27]),
        (20, 30, 0.3, 4, [20, 23, 25, 27]),
        (5, 30, 0.6, 6, [5, 20, 26, 28, 29, 30]),
        (10, 50, 0.4, 4, [10, 26, 36, 41]),
        (1, 15, 0.2, 1, [1]),
        (1, 80, 0.2, 8, [1, 17, 29, 40, 48, 54, 59, 63]),
        (79, 80, 0.6, 8, [79, 80, 80, 80, 80, 80, 80, 80]),
        (5, 30, 0.6, 3, [5, 20, 26]),
        (20, 60, 0.3, 5, [20, 32, 40, 46, 50]),
    ],
)
def test_asymptotic_curve_returns_expected_timers(
    start_minutes: int,
    cap_minutes: int,
    rate: float,
    num_of_rounds: int,
    expected_work_times: list[int],
):

    work_times = asymptotic_curve(start_minutes, cap_minutes, rate, num_of_rounds)

    assert work_times == expected_work_times


@pytest.mark.parametrize(
    "start_minutes, cap_minutes, rate, num_of_rounds, expected_field",
    [
        (0, 10, 0.4, 2, "start_minutes"),
        (-5, 12, 0.2, 4, "start_minutes"),
        (MAX_POMODORO_LIMIT + 1, MAX_POMODORO_LIMIT + 2, 0.3, 1, "start_minutes"),
        (5, 5, 0.5, 3, "cap_minutes"),
        (5, 2, 0.4, 3, "cap_minutes"),
        (10, MAX_POMODORO_LIMIT + 1, 0.2, 4, "cap_minutes"),
        (10, 30, MIN_RATE - 0.1, 4, "rate"),
        (10, 25, MAX_RATE + 0.1, 3, "rate"),
        (5, 15, 0.4, 0, "num_of_rounds"),
        (5, 10, 0.2, -5, "num_of_rounds"),
        (5, 10, 0.2, MAX_NUMBER_ROUNDS + 1, "num_of_rounds"),
    ],
)
def test_asymptotic_curve_raises_error_when_arguments_are_invalid(
    start_minutes: int,
    cap_minutes: int,
    rate: float,
    num_of_rounds: int,
    expected_field: str,
):

    with pytest.raises(PomodoroCurveError) as exc_info:
        _ = asymptotic_curve(start_minutes, cap_minutes, rate, num_of_rounds)

    assert exc_info.value.field == expected_field
