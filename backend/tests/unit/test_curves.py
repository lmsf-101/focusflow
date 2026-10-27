import pytest

from focusflow_api.domain.pomodoro.curves import (
    MAX_NUMBER_ROUNDS,
    MAX_POMODORO_LIMIT,
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
