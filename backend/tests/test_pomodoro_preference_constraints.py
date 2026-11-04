import pytest
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import select

from focusflow_api.models import (
    Category,
    PomodoroMode,
    PomodoroPreference,
    Project,
    User,
)
from focusflow_api.security import hash_password

VALID_CLASSIC = {
    "mode": PomodoroMode.CLASSIC,
    "start_minutes": 25,
    "num_of_rounds": 4,
    "break_minutes": 5,
}

VALID_INCREMENTAL = {
    "mode": PomodoroMode.INCREMENTAL,
    "start_minutes": 20,
    "num_of_rounds": 4,
    "growth": 2,
    "cap_minutes": 30,
}

VALID_FLEXIBLE = {
    "mode": PomodoroMode.FLEXIBLE,
    "start_minutes": 20,
    "num_of_rounds": 4,
    "cap_minutes": 30,
    "rate": 0.4,
}


@pytest.fixture(scope="function")
def get_user_id(db_session):
    test_user = User(
        email="test12@example.com", hashed_password=hash_password("test12")
    )

    db_session.add(test_user)
    db_session.flush()

    yield test_user.id


@pytest.mark.integration
@pytest.mark.parametrize(
    "valid_pomodoro_mode",
    [
        pytest.param(VALID_CLASSIC, id="Valid Classic Pomodoro Preference"),
        pytest.param(VALID_INCREMENTAL, id="Valid Incremental Pomodoro Preference"),
        pytest.param(VALID_FLEXIBLE, id="Valid Flexible Pomodoro Preference"),
    ],
)
def test_working_pomodoro_preference_with_valid_arguments(
    db_session, get_user_id, valid_pomodoro_mode
):

    valid_pomodoro_preference = PomodoroPreference(
        owner_id=get_user_id, **valid_pomodoro_mode
    )

    db_session.add(valid_pomodoro_preference)

    db_session.flush()

    assert valid_pomodoro_preference.id is not None


@pytest.mark.integration
@pytest.mark.parametrize(
    "overrides",
    [
        pytest.param({"break_minutes": None}, id="classic-without-break"),
        pytest.param({"growth": 2}, id="classic-with-growth"),
        pytest.param({"cap_minutes": 5}, id="classic-with-cap-minutes"),
        pytest.param({"rate": 0.4}, id="classic-with-rate"),
    ],
)
def test_classic_pomodoro_preference_fail_when_using_invalid_arguments(
    db_session, get_user_id, overrides
):

    with pytest.raises(IntegrityError) as exc_info:
        classic_pomodoro_preference = PomodoroPreference(
            owner_id=get_user_id, **{**VALID_CLASSIC, **overrides}
        )

        db_session.add(classic_pomodoro_preference)

        db_session.flush()

    assert (
        exc_info.value.orig.diag.constraint_name
        == "ck_pomodoro_preference_classic_parameters"
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "overrides",
    [
        pytest.param({"break_minutes": 5}, id="incremental-with-break"),
        pytest.param({"growth": None}, id="incremental-without-growth"),
        pytest.param({"cap_minutes": None}, id="incremental-without-cap-minutes"),
        pytest.param({"rate": 0.2}, id="incremental-with-rate"),
    ],
)
def test_incremental_pomodoro_preference_fail_when_using_invalid_arguments(
    db_session, get_user_id, overrides
):

    with pytest.raises(IntegrityError) as exc_info:
        incremental_pomodoro_preference = PomodoroPreference(
            owner_id=get_user_id, **{**VALID_INCREMENTAL, **overrides}
        )

        db_session.add(incremental_pomodoro_preference)

        db_session.flush()

    assert (
        exc_info.value.orig.diag.constraint_name
        == "ck_pomodoro_preference_incremental_parameters"
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "overrides",
    [
        pytest.param({"break_minutes": 5}, id="flexible-with-break"),
        pytest.param({"growth": 2}, id="flexible-with-growth"),
        pytest.param({"cap_minutes": None}, id="flexible-without-cap-minutes"),
        pytest.param({"rate": None}, id="flexible-without-rate"),
    ],
)
def test_flexible_pomodoro_preference_fail_when_using_invalid_arguments(
    db_session, get_user_id, overrides
):

    with pytest.raises(IntegrityError) as exc_info:
        flexible_pomodoro_preference = PomodoroPreference(
            owner_id=get_user_id, **{**VALID_FLEXIBLE, **overrides}
        )

        db_session.add(flexible_pomodoro_preference)

        db_session.flush()

    assert (
        exc_info.value.orig.diag.constraint_name
        == "ck_pomodoro_preference_flexible_parameters"
    )


@pytest.mark.integration
def test_pomodoro_preference_get_deleted_when_associated_project_is_deleted(
    db_session, get_user_id
):

    new_project = Project(name="test_project", owner_id=get_user_id)

    db_session.add(new_project)

    db_session.flush()

    pomodoro_preference = PomodoroPreference(
        owner_id=get_user_id, project_id=new_project.id, **VALID_CLASSIC
    )

    db_session.add(pomodoro_preference)

    db_session.flush()

    db_session.execute(delete(Project).where(Project.id == new_project.id))

    db_session.flush()

    preference_exists = select(PomodoroPreference).where(
        PomodoroPreference.id == pomodoro_preference.id
    )

    assert not db_session.scalar(preference_exists)


@pytest.mark.integration
def test_pomodoro_preference_get_deleted_when_associated_category_is_deleted(
    db_session, get_user_id
):

    new_category = Category(name="test_category", owner_id=get_user_id)

    db_session.add(new_category)

    db_session.flush()

    pomodoro_preference = PomodoroPreference(
        owner_id=get_user_id, category_id=new_category.id, **VALID_CLASSIC
    )

    db_session.add(pomodoro_preference)

    db_session.flush()

    db_session.execute(delete(Category).where(Category.id == new_category.id))

    db_session.flush()

    preference_exists = select(PomodoroPreference).where(
        PomodoroPreference.id == pomodoro_preference.id
    )

    assert not db_session.scalar(preference_exists)


@pytest.mark.integration
def test_pomodoro_preference_get_deleted_when_associated_user_is_deleted(
    db_session, get_user_id
):
    pomodoro_preference = PomodoroPreference(owner_id=get_user_id, **VALID_CLASSIC)

    db_session.add(pomodoro_preference)

    db_session.flush()

    db_session.execute(delete(User).where(User.id == pomodoro_preference.owner_id))

    db_session.flush()

    preference_exists = select(PomodoroPreference).where(
        PomodoroPreference.id == pomodoro_preference.id
    )

    assert not db_session.scalar(preference_exists)
