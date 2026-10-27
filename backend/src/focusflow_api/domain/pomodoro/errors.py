class PomodoroError(Exception):
    pass


class PomodoroValidationError(PomodoroError):
    def __init__(self, message: str, field: str) -> None:
        super().__init__(message)
        self.field: str = field


class PomodoroCurveError(PomodoroValidationError):
    pass


class PomodoroBreakError(PomodoroValidationError):
    pass
