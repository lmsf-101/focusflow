from datetime import UTC, datetime

from focusflow_api.domain.pomodoro.session_enums import SessionEvent
from focusflow_api.domain.pomodoro.session_state import transition
from focusflow_api.models import PomodoroSession


def abandon_session(session: PomodoroSession) -> None:
    new_session_state = transition(session.status, SessionEvent.QUIT_SESSION)

    abandoned_at = datetime.now(UTC)

    session.ended_at = abandoned_at
    session.status = new_session_state
