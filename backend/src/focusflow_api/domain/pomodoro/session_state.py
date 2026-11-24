from focusflow_api.domain.pomodoro.errors import InvalidTransitionError
from focusflow_api.domain.pomodoro.session_enums import SessionEvent, SessionStatus

TRANSITIONS: dict[tuple[SessionStatus, SessionEvent], SessionStatus] = {
    (SessionStatus.ACTIVE, SessionEvent.REGISTER_INTERVAL): SessionStatus.ACTIVE,
    (SessionStatus.ACTIVE, SessionEvent.COMPLETE_SESSION): SessionStatus.COMPLETED,
    (SessionStatus.ACTIVE, SessionEvent.QUIT_SESSION): SessionStatus.ABANDONED,
    (SessionStatus.ACTIVE, SessionEvent.EXPIRE_SESSION): SessionStatus.ABANDONED,
}


def transition(current_status: SessionStatus, event: SessionEvent) -> SessionStatus:

    valid_transition = TRANSITIONS.get((current_status, event))

    if valid_transition is None:
        raise InvalidTransitionError(current_status, event)

    return valid_transition
