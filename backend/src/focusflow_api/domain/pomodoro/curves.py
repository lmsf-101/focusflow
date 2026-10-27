from focusflow_api.domain.pomodoro.errors import PomodoroCurveError

MAX_POMODORO_LIMIT = 80
MAX_NUMBER_ROUNDS = 8


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
