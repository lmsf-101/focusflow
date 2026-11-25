from fastapi.testclient import TestClient

from focusflow_api.app import create_app
from focusflow_api.domain.pomodoro.errors import InvalidTransitionError
from focusflow_api.domain.pomodoro.session_enums import SessionEvent, SessionStatus


def test_invalid_transition_exception_handler():
    app = create_app()

    @app.get("/boom")
    def provoke_invalid_transition_error():
        raise InvalidTransitionError(
            SessionStatus.ABANDONED, SessionEvent.COMPLETE_SESSION
        )

    client = TestClient(app=app)

    response = client.get("/boom")

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Event 'complete_session' is not allowed in state 'abandoned'"
    }
