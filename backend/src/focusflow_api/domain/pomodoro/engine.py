from dataclasses import dataclass
from enum import Enum

from focusflow_api.domain.pomodoro.breaks import generate_flexible_break_time
from focusflow_api.domain.pomodoro.curves import curve
from focusflow_api.domain.pomodoro.errors import (
    PomodoroBreakError,
    PomodoroCurveError,
    PomodoroPlanError,
    PomodoroValidationError,
)

INCREMENTAL_BREAK_RATIO = 0.2


class PomodoroModes(Enum):
    CLASSIC = "classic"
    INCREMENTAL = "incremental"


@dataclass(frozen=True)
class PomodoroPlan:
    work_times: tuple[int, ...]
    break_times: tuple[int, ...]

    def __post_init__(self):
        if not self.work_times:
            raise PomodoroPlanError("work_times tuple must not be empty")
        elif len(self.break_times) != len(self.work_times) - 1:
            raise PomodoroPlanError(
                f"Num of break times ({len(self.break_times)}) must be one less than the Num. of work times ({len(self.work_times)})"
            )


def plan_classic(
    start_minutes: int, break_minutes: int, num_of_rounds: int
) -> PomodoroPlan:
    """
    Generates a Classic Pomodoro Plan: Fixed working timers, with fixed times for breaks, for N rounds
    Args:
        start_minutes (integer): The initial timer for the first round. Must be at least 1 minute, cannot be 0 or negative
        break_minutes (integer): The fixed amount of minutes for each break. Must be a positive value, and more than 0.
        num_of_rounds (integer): Number of rounds for the session. Must be at least 1 round.
    Returns:
        PomodoroPlan with fixed sessions

    Examples:
        plan_classic(10, 2, 4) => PomodoroPlan((10, 10, 10, 10), (2, 2, 2))
        plan_classic(25, 5, 3) => PomodoroPlan((25, 25, 25), (5, 5))

    """
    try:
        work_times = tuple(curve(start_minutes, 0, start_minutes, num_of_rounds))

        break_times = (generate_flexible_break_time(break_minutes, 1),) * (
            num_of_rounds - 1
        )

        return PomodoroPlan(work_times, break_times)

    except PomodoroCurveError as curve_error:
        if curve_error.field == "start_minutes" or curve_error.field == "cap_minutes":
            raise PomodoroCurveError(
                f"Classic plan failed to generate due to work times: {curve_error}",
                "start_minutes",
            )
        elif curve_error.field == "num_of_rounds":
            raise PomodoroCurveError(
                f"Classic plan failed to generate due to work times: {curve_error}",
                "num_of_rounds",
            )
        else:
            raise

    except PomodoroBreakError as break_error:
        raise PomodoroBreakError(
            f"Classic plan failed to generate due to break times: {break_error}",
            "break_minutes",
        )


def plan_incremental(
    start_minutes: int, growth: int, cap_minutes: int, num_of_rounds: int
) -> PomodoroPlan:
    """
    Generates an Incremental Pomodoro Plan: The working timer increments by X minutes (until it is capped by Y minutes), by N rounds.

    Breaks are calculated by a constant ratio (INCREMENTAL_BREAK_RATIO)

    Args:
        start_minutes (integer): The initial timer for the first round. Must be at least 1 minute, cannot be 0 or negative
        growth (integer): Amount of minutes to add to the next working timer. Must be at least 1 minute, and must be a positive value.
        cap_minutes (integer): The maximum limit for any working timer. Must be bigger than the initial timer, and cannot be negative.
        num_of_rounds (integer): Number of rounds for the session. Must be at least 1 round.
    Returns:
        PomodoroPlan with incremental sessions for each round

    Examples:
        plan_incremental(25, 2, 35, 4) => PomodoroPlan((25, 27, 29, 31), (5, 5, 6))
        plan_incremental(15, 3, 25, 5) => PomodoroPlan((15, 18, 21, 24, 25), (3, 4, 4, 5))
    """

    if growth <= 0:
        raise PomodoroValidationError("Growth must be bigger than 0", "growth")

    work_times = tuple(curve(start_minutes, growth, cap_minutes, num_of_rounds))

    break_times = tuple(
        generate_flexible_break_time(work_time, INCREMENTAL_BREAK_RATIO)
        for work_time in work_times[:-1]
    )

    return PomodoroPlan(work_times, break_times)
