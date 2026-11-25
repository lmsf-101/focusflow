from focusflow_api.domain.pomodoro.session_enums import SessionEvent, SessionStatus


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


class PomodoroPlanError(PomodoroError):
    pass


class InvalidTransitionError(PomodoroError):
    def __init__(
        self, session_status: SessionStatus, session_event: SessionEvent
    ) -> None:
        super().__init__(
            f"Event '{session_event.value}' is not allowed "
            f"in state '{session_status.value}'"
        )

        self.session_status = session_status
        self.session_event = session_event
