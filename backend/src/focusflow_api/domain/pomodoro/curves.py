import math

from focusflow_api.domain.pomodoro.errors import PomodoroCurveError

MAX_POMODORO_LIMIT = 80
MAX_NUMBER_ROUNDS = 8
MIN_RATE = 0.2
MAX_RATE = 0.6


def curve(
    start_minutes: int, growth: int, cap_minutes: int, num_of_rounds: int
) -> list[int]:
    """
    Generates Pomodoro curve with specific default start (minutes) and growth (add X minutes)

    Args:
        start_minutes (integer): The amount of minutes for the first round. Must be at least 1 minute, cannot be 0 or negative.
        growth (integer): Specify how much should the timer grow every round, in minutes. Can be zero (fixed pomodoros) or a positive value (add X minutes in every round)
        cap_minutes (integer): The max amount of time a single round can have. Must be a value equal or greater than start_minutes, but limited to the MAX_POMODORO_LIMIT
        num_of_rounds (integer): The number of Pomodoros to do in a single session. Must be at least 1 round, and limited to the MAX_NUMBER_ROUNDS

    Returns:
        Array of values representing the pomodoro times for each round

    Examples:
        curve(20, 2, 30, 4) => [20, 22, 24, 26]
        curve(25, 5, 50, 4) => [25, 30, 35, 40]
        curve(5, 5, 12, 4) => [5, 10, 12, 12]
    """
    # Revisar si los argumentos son valores validos:

    # Revisar que start_minutes sea mayor que 0
    if start_minutes <= 0:
        raise PomodoroCurveError(
            "start_minutes must be at least 1 minute", "start_minutes"
        )

    # Revisar que el numero de rounds sea mayor que 0:
    if num_of_rounds <= 0:
        raise PomodoroCurveError(
            "num_of_rounds must be at least 1 round", "num_of_rounds"
        )

    # Revisar que growth no sea negativo
    if growth < 0:
        raise PomodoroCurveError("growth must not be a negative value", "growth")

    # Revisar que el limite máximo no sea menor que el valor inicial
    if cap_minutes < start_minutes:
        raise PomodoroCurveError(
            "cap_minutes must be greater than or equal to start_minutes", "cap_minutes"
        )

    # Revisar que el limite máximo no sobrepase MAX_POMODORO_LIMIT
    if cap_minutes > MAX_POMODORO_LIMIT:
        raise PomodoroCurveError(
            f"cap_minutes must not be bigger than MAX_POMODORO_LIMIT ({MAX_POMODORO_LIMIT})",
            "cap_minutes",
        )

    # Revisar que la maxima cantidad de rondas no sobrepase MAX_NUMBER_ROUNDS
    if num_of_rounds > MAX_NUMBER_ROUNDS:
        raise PomodoroCurveError(
            f"num_of_rounds must not be bigger than MAX_NUMBER_ROUNDS ({MAX_NUMBER_ROUNDS})",
            "num_of_rounds",
        )

    pomodoro_times: list[int] = []

    for i in range(num_of_rounds):
        calculated_time = start_minutes + (growth * i)

        next_timer = min(calculated_time, cap_minutes)

        pomodoro_times.append(next_timer)

    return pomodoro_times


def _asymptotic_formula(start: int, cap: int, rate: float, n: int) -> int:
    """
    Auxiliary asymptotic formula for calculating the asymptotic's work times

    Args:
        start (integer): initial start value
        cap (integer): top limit for the asymptotic curve
        rate (float): rhythm of how fast / slow will the timers reach the capped limit within each round
        n (integer): The round number
    """
    return math.floor((cap - (cap - start) * (1 - rate) ** n) + 0.5)


def asymptotic_curve(
    start_minutes: int, cap_minutes: int, rate: float, num_of_rounds: int
) -> list[int]:
    """
    Generates an asymptotic Pomodoro curve: every round covers a fraction (rate) of the minutes that are still missing to reach the cap

    Each round is calculated by the auxiliary asymptotic formula function

    Every value is rounded to the nearest whole number (a .5 goes up). A value never goes over cap_minutes, but it can reach it
    in the last rounds, and from then on it repeats (the tail of the curve is flat).

    Raises PomodoroCurveError when an argument is invalid; its field is the name of that argument.

    Args:
        start_minutes (integer): The amount of minutes for the first round. Must be at least 1 minute, and limited to the MAX_POMODORO_LIMIT
        cap_minutes (integer): The value the curve gets closer to. Must be bigger than start_minutes, and limited to the MAX_POMODORO_LIMIT
        rate (float): The fraction of the missing minutes that is covered in every round. Must be between MIN_RATE and MAX_RATE, both included
        num_of_rounds (integer): The number of Pomodoros to do in a single session. Must be at least 1 round, and limited to the MAX_NUMBER_ROUNDS

    Returns:
        Array of values representing the pomodoro times for each round

    Examples:
        asymptotic_curve(5, 30, 0.5, 4) => [5, 18, 24, 27]
        asymptotic_curve(20, 30, 0.3, 4) => [20, 23, 25, 27]
        asymptotic_curve(5, 30, 0.6, 6) => [5, 20, 26, 28, 29, 30]
    """

    if start_minutes <= 0:
        raise PomodoroCurveError(
            "The initial value must be at least 1 minute", "start_minutes"
        )
    elif start_minutes > MAX_POMODORO_LIMIT:
        raise PomodoroCurveError(
            f"The initial value must not be larger than the maximum value ({MAX_POMODORO_LIMIT})",
            "start_minutes",
        )

    if cap_minutes <= start_minutes:
        raise PomodoroCurveError(
            "The limit must be greater than the initial value", "cap_minutes"
        )
    elif cap_minutes > MAX_POMODORO_LIMIT:
        raise PomodoroCurveError(
            f"The limit must not be larger than the maximum value ({MAX_POMODORO_LIMIT})",
            "cap_minutes",
        )

    if rate < MIN_RATE or rate > MAX_RATE:
        raise PomodoroCurveError(
            f"The rate must be a value between {MIN_RATE} and {MAX_RATE}", "rate"
        )

    if num_of_rounds <= 0 or num_of_rounds > MAX_NUMBER_ROUNDS:
        raise PomodoroCurveError(
            f"Number of rounds invalid: Must be a minimum of 1, and maximum of {MAX_NUMBER_ROUNDS}",
            "num_of_rounds",
        )

    return [
        _asymptotic_formula(start_minutes, cap_minutes, rate, i)
        for i in range(num_of_rounds)
    ]
