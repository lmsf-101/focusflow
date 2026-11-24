import pytest

from focusflow_api.domain.pomodoro.errors import InvalidTransitionError
from focusflow_api.domain.pomodoro.session_enums import SessionEvent, SessionStatus
from focusflow_api.domain.pomodoro.session_state import transition


@pytest.mark.parametrize(
    "status, event, expected_status",
    [
        pytest.param(
            SessionStatus.ACTIVE,
            SessionEvent.REGISTER_INTERVAL,
            SessionStatus.ACTIVE,
            id="Active + Register Interval == Active",
        ),
        pytest.param(
            SessionStatus.ACTIVE,
            SessionEvent.COMPLETE_SESSION,
            SessionStatus.COMPLETED,
            id="Active + Complete Session == Completed",
        ),
        pytest.param(
            SessionStatus.ACTIVE,
            SessionEvent.QUIT_SESSION,
            SessionStatus.ABANDONED,
            id="Active + Quit Session == Abandoned",
        ),
        pytest.param(
            SessionStatus.ACTIVE,
            SessionEvent.EXPIRE_SESSION,
            SessionStatus.ABANDONED,
            id="Active + Expire Session == Abandoned",
        ),
    ],
)
def test_valid_session_transition(
    status: SessionStatus, event: SessionEvent, expected_status: SessionStatus
):

    new_status = transition(status, event)

    assert new_status == expected_status


@pytest.mark.parametrize(
    "status, event",
    [
        pytest.param(
            SessionStatus.COMPLETED,
            SessionEvent.REGISTER_INTERVAL,
            id="Completed + Register Interval",
        ),
        pytest.param(
            SessionStatus.COMPLETED,
            SessionEvent.COMPLETE_SESSION,
            id="Completed + Complete Session",
        ),
        pytest.param(
            SessionStatus.COMPLETED,
            SessionEvent.QUIT_SESSION,
            id="Completed + Quit Session",
        ),
        pytest.param(
            SessionStatus.COMPLETED,
            SessionEvent.EXPIRE_SESSION,
            id="Completed + Expire Session",
        ),
        pytest.param(
            SessionStatus.ABANDONED,
            SessionEvent.REGISTER_INTERVAL,
            id="Abandoned + Register Interval",
        ),
        pytest.param(
            SessionStatus.ABANDONED,
            SessionEvent.COMPLETE_SESSION,
            id="Abandoned + Complete Session",
        ),
        pytest.param(
            SessionStatus.ABANDONED,
            SessionEvent.QUIT_SESSION,
            id="Abandoned + Quit Session",
        ),
        pytest.param(
            SessionStatus.ABANDONED,
            SessionEvent.EXPIRE_SESSION,
            id="Abandoned + Expire Session",
        ),
    ],
)
def test_invalid_session_transition_is_not_allowed(
    status: SessionStatus, event: SessionEvent
):

    with pytest.raises(InvalidTransitionError) as exc_info:
        _ = transition(status, event)

    assert exc_info.value.session_status == status
    assert exc_info.value.session_event == event
