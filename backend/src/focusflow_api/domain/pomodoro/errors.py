class PomodoroError(Exception):
    pass


class PomodoroCurveError(PomodoroError):
    def __init__(self, message: str, field: str) -> None:
        self.field: str = field
        super().__init__(message)
