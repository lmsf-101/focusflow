import math

from focusflow_api.domain.pomodoro.errors import PomodoroBreakError

MAXIMUM_RATIO = 1
MINIMUM_BREAK_MINUTES = 1


def generate_flexible_break_time(accumulated_time: int, ratio: float) -> int:
    """
    Generates an flexible break timer, based on the accumulated work time done and an specific ratio

    If the calculated break time has a decimal, the value is rounded to the nearest whole number.

    A break is at least a minute long

    Args:
        accumulated_time (integer): Work time done as of now, in minutes. Must be a positive value
        ratio (float): The fraction of the accumulated time for the break. Must be a positive value and greater than 0, and less than or equal to MAXIMUM_RATIO

    Returns:
        Amount of break time, in minutes

    Examples:
        generate_flexible_break_time(20, 0.2) => 4
        generate_flexible_break_time(40, 0.5) => 20
        generate_flexible_break_time(50, 0.25) => 13
    """

    # Revisar si el tiempo acumulado sea mayor que 0
    if accumulated_time <= 0:
        raise PomodoroBreakError(
            "accumulated_time must be a positive value, and larger than 0",
            "accumulated_time",
        )

    # Revisar que el ratio sea mayor de 0, y menor que el MAXIMUM_RATIO
    if ratio <= 0 or ratio > MAXIMUM_RATIO:
        raise PomodoroBreakError(
            f"ratio must be bigger than 0, and less than or equal to the MAXIMUM_RATIO ({MAXIMUM_RATIO})",
            "ratio",
        )
    break_timer = math.floor((accumulated_time * ratio) + 0.5)

    return max(break_timer, MINIMUM_BREAK_MINUTES)
