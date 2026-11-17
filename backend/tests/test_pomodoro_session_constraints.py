from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql import delete, select

from focusflow_api.models import (
    PomodoroMode,
    PomodoroSession,
    PomodoroSessionTask,
    SessionStatus,
    Task,
    TaskPriority,
    TaskStatus,
    User,
)
from focusflow_api.security import hash_password

PLANNED_CONFIG = {
    "mode": "incremental",
    "params": {"start_minutes": 20, "growth": 2, "cap_minutes": 30, "num_of_rounds": 3},
    "intervals": [
        {"kind": "work", "minutes": 20},
        {"kind": "break", "minutes": 5},
        {"kind": "work", "minutes": 22},
        {"kind": "break", "minutes": 6},
        {"kind": "work", "minutes": 24},
    ],
}


@pytest.fixture(scope="function")
def get_user_id(db_session: Session):
    test_user = User(
        email="user_test@test.com", hashed_password=hash_password("test-123")
    )

    db_session.add(test_user)
    db_session.flush()

    return test_user.id


@pytest.fixture(scope="function")
def get_session_id(db_session: Session, get_user_id):
    USER_CONFIG = {
        "mode": "classic",
        "params": {"start_minutes": 25, "break_minutes": 5, "num_of_rounds": 3},
        "intervals": [
            {"kind": "work", "minutes": 25},
            {"kind": "break", "minutes": 5},
            {"kind": "work", "minutes": 25},
            {"kind": "break", "minutes": 5},
            {"kind": "work", "minutes": 25},
        ],
    }

    test_pomodoro_session = PomodoroSession(
        owner_id=get_user_id,
        mode=PomodoroMode.CLASSIC,
        status=SessionStatus.ACTIVE,
        planned_config=USER_CONFIG,
    )

    db_session.add(test_pomodoro_session)
    db_session.flush()

    return test_pomodoro_session.id


# Pruebas de casos válidos (sesiones con dos tareas)


@pytest.mark.integration
def test_working_session_with_two_tasks(db_session, get_user_id):
    pomodoro_session = PomodoroSession(
        owner_id=get_user_id,
        mode=PomodoroMode.INCREMENTAL,
        status=SessionStatus.ACTIVE,
        planned_config=PLANNED_CONFIG,
    )

    session_task_1 = PomodoroSessionTask(
        task_title="Test title 1", pomodoro_session=pomodoro_session
    )
    session_task_2 = PomodoroSessionTask(
        task_title="Test title 2", pomodoro_session=pomodoro_session
    )

    db_session.add(pomodoro_session)
    db_session.add(session_task_1)
    db_session.add(session_task_2)

    db_session.flush()

    db_session.refresh(pomodoro_session, ["session_tasks"])

    assert session_task_1.id is not None
    assert session_task_2.id is not None

    assert session_task_1.pomodoro_session_id == pomodoro_session.id
    assert session_task_2.pomodoro_session_id == pomodoro_session.id

    assert {session_task_1, session_task_2} == set(pomodoro_session.session_tasks)


# Prueba de CHECK para status y ended_at
@pytest.mark.integration
@pytest.mark.parametrize(
    "status, ended_at",
    [
        (SessionStatus.ACTIVE, None),
        (SessionStatus.COMPLETED, datetime.now(UTC) + timedelta(minutes=10)),
        (SessionStatus.ABANDONED, datetime.now(UTC) + timedelta(minutes=5)),
    ],
)
def test_session_status_and_ended_at_valid_combinations(
    db_session: Session, get_user_id, status, ended_at
):
    pomodoro_session = PomodoroSession(
        owner_id=get_user_id,
        mode=PomodoroMode.INCREMENTAL,
        planned_config=PLANNED_CONFIG,
        status=status,
        ended_at=ended_at,
    )

    db_session.add(pomodoro_session)

    db_session.flush()

    db_session.refresh(pomodoro_session, ["status", "ended_at"])

    assert pomodoro_session.status == status
    assert pomodoro_session.ended_at == ended_at


@pytest.mark.integration
@pytest.mark.parametrize(
    "status, ended_at",
    [
        pytest.param(
            SessionStatus.ACTIVE, datetime.now(UTC), id="active-with-ended-at"
        ),
        pytest.param(SessionStatus.COMPLETED, None, id="completed-without-ended-at"),
        pytest.param(SessionStatus.ABANDONED, None, id="abandoned-without-ended-at"),
    ],
)
def test_session_status_and_ended_at_invalid_combinations(
    db_session, get_user_id, status, ended_at
):
    with pytest.raises(IntegrityError) as exc_info:
        pomodoro_session = PomodoroSession(
            owner_id=get_user_id,
            mode=PomodoroMode.INCREMENTAL,
            planned_config=PLANNED_CONFIG,
            status=status,
            ended_at=ended_at,
        )

        db_session.add(pomodoro_session)

        db_session.flush()

    assert (
        exc_info.value.orig.diag.constraint_name
        == "ck_pomodoro_session_status_ended_at"
    )


# Pruebas de CHECK para estimación de minutos (cero, negativo)


@pytest.mark.integration
@pytest.mark.parametrize(
    "estimate_minutes",
    [
        pytest.param(0, id="estimate_minutes_zero"),
        pytest.param(-2, id="negative_estimate_minutes"),
    ],
)
def test_estimate_minutes_must_be_positive(
    db_session, get_session_id, estimate_minutes
):
    with pytest.raises(IntegrityError) as exc_info:
        bad_session_task = PomodoroSessionTask(
            pomodoro_session_id=get_session_id,
            task_title="Bad session task",
            estimate_minutes=estimate_minutes,
        )

        db_session.add(bad_session_task)

        db_session.flush()

    assert (
        exc_info.value.orig.diag.constraint_name
        == "ck_pomodoro_session_task_estimate_positive"
    )


@pytest.mark.integration
def test_estimate_minutes_can_be_null(db_session, get_session_id):
    session_task = PomodoroSessionTask(
        pomodoro_session_id=get_session_id,
        task_title="Test session task without estimate minutes",
    )

    db_session.add(session_task)

    db_session.flush()
    db_session.refresh(session_task)

    assert session_task.id is not None
    assert session_task.estimate_minutes is None


# Pruebas de restricción única (tareas)


@pytest.mark.integration
def test_same_task_twice_in_one_session_fails(db_session, get_user_id, get_session_id):
    # Creacion de tarea
    new_task = Task(
        title="New task",
        owner_id=get_user_id,
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.PENDING,
    )

    db_session.add(new_task)
    db_session.flush()

    first_session_task = PomodoroSessionTask(
        pomodoro_session_id=get_session_id,
        task_id=new_task.id,
        task_title=new_task.title,
    )

    db_session.add(first_session_task)
    db_session.flush()

    with pytest.raises(IntegrityError) as exc_info:
        duplicate_session_task = PomodoroSessionTask(
            pomodoro_session_id=get_session_id,
            task_id=new_task.id,
            task_title=new_task.title,
        )

        db_session.add(duplicate_session_task)
        db_session.flush()

    assert (
        exc_info.value.orig.diag.constraint_name
        == "uq_pomodoro_session_task_pomodoro_session_id_task_id"
    )


@pytest.mark.integration
def test_several_null_task_ids_in_one_session_are_allowed(db_session, get_session_id):
    first_session_task = PomodoroSessionTask(
        pomodoro_session_id=get_session_id,
        task_id=None,
        task_title="First task",
    )
    second_session_task = PomodoroSessionTask(
        pomodoro_session_id=get_session_id,
        task_id=None,
        task_title="Second task",
    )
    db_session.add(first_session_task)
    db_session.add(second_session_task)
    db_session.flush()

    assert first_session_task.id is not None
    assert second_session_task.id is not None


# Pruebas de valores por defecto


@pytest.mark.integration
def test_session_task_defaults(db_session, get_session_id):
    session_task = PomodoroSessionTask(
        pomodoro_session_id=get_session_id,
        task_title="Test task",
    )

    db_session.add(session_task)

    db_session.flush()
    # db_session.refresh(session_task)

    assert session_task.actual_minutes == 0
    assert session_task.completed == False


# prueba de elementos ON DELETE
@pytest.mark.integration
def test_deleting_task_sets_task_id_to_null_and_keeps_the_row(
    db_session, get_user_id, get_session_id
):

    TASK_TITLE = "New task"

    # Creación de tarea
    new_task = Task(
        title=TASK_TITLE,
        owner_id=get_user_id,
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.PENDING,
    )

    db_session.add(new_task)
    db_session.flush()

    session_task = PomodoroSessionTask(
        pomodoro_session_id=get_session_id,
        task_id=new_task.id,
        task_title=new_task.title,
    )

    db_session.add(session_task)
    db_session.flush()

    db_session.execute(delete(Task).where(Task.id == new_task.id))

    db_session.flush()
    db_session.expire(session_task)

    session_task_query = select(PomodoroSessionTask).where(
        PomodoroSessionTask.id == session_task.id
    )

    session_task_query_result = db_session.scalar(session_task_query)

    assert isinstance(session_task_query_result, PomodoroSessionTask)
    assert session_task_query_result.task_id is None
    assert session_task_query_result.task_title == TASK_TITLE


@pytest.mark.integration
def test_deleting_session_deletes_its_session_tasks(db_session, get_session_id):
    session_task = PomodoroSessionTask(
        pomodoro_session_id=get_session_id,
        task_title="Test task for session",
    )

    db_session.add(session_task)
    db_session.flush()

    session_task_id = session_task.id
    assert session_task_id is not None

    db_session.execute(
        delete(PomodoroSession).where(PomodoroSession.id == get_session_id)
    )

    db_session.flush()

    session_task_exists = select(PomodoroSessionTask).where(
        PomodoroSessionTask.id == session_task_id
    )

    assert not db_session.scalar(session_task_exists)


# Prueba de anidación de JSONB


@pytest.mark.integration
def test_planned_config_roundtrip(db_session, get_user_id):
    pomodoro_session = PomodoroSession(
        owner_id=get_user_id,
        mode=PomodoroMode.INCREMENTAL,
        status=SessionStatus.ACTIVE,
        planned_config=PLANNED_CONFIG,
    )

    db_session.add(pomodoro_session)
    db_session.flush()

    db_session.expire(pomodoro_session)

    assert pomodoro_session.planned_config == PLANNED_CONFIG
