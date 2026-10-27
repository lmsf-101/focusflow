import pytest

from focusflow_api.domain.pomodoro.breaks import generate_flexible_break_time
from focusflow_api.domain.pomodoro.errors import PomodoroBreakError


@pytest.mark.parametrize(
    "accumulated_time, ratio, expected_break_time",
    [
        (20, 0.2, 4),
        (40, 0.5, 20),
        (50, 0.25, 13),
        (10, 0.25, 3),
        (2, 0.25, 1),
        (3, 0.1, 1),
        (10, 1, 10),
    ],
)
def test_valid_breaks_with_correct_arguments(
    accumulated_time: int, ratio: float, expected_break_time: int
):
    assert generate_flexible_break_time(accumulated_time, ratio) == expected_break_time


@pytest.mark.parametrize(
    "accumulated_time, ratio, expected_failed_field",
    [
        (0, 0.2, "accumulated_time"),
        (-4, 0.5, "accumulated_time"),
        (10, 0, "ratio"),
        (12, -0.2, "ratio"),
        (40, 1.01, "ratio"),
    ],
)
def test_break_fail_when_invalid_arguments_are_used(
    accumulated_time: int, ratio: float, expected_failed_field: str
):
    with pytest.raises(PomodoroBreakError) as exc_info:
        _ = generate_flexible_break_time(accumulated_time, ratio)

    assert exc_info.value.field == expected_failed_field
