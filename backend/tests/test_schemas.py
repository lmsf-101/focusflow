import pydantic
import pytest

from focusflow_api.models import PomodoroPreset, User
from focusflow_api.schemas import (
    PomodoroMode,
    PomodoroPresetCreate,
    PomodoroPresetRead,
    UserCreate,
    UserRead,
)


# Validar que correo con formato invalido en UserCreate es rechazado
def test_invalid_email_in_UserCreate_is_rejected():
    with pytest.raises(pydantic.ValidationError):
        _ = UserCreate(email="test123", password="password")


# Validar que usuario sin contraseña en UserCreate es rechazado
def test_user_with_no_password_is_rejected():
    with pytest.raises(pydantic.ValidationError):
        _ = UserCreate(email="test123@gmail.com", password=None)


# Verificar que UserRead (lectura de un usuario) no regresa credenciales confidenciales (password)
def test_UserRead_does_not_expose_secrets():
    user = User(id=1, email="test123@gmail.com", hashed_password="secret")

    user_data = UserRead.model_validate(user).model_dump()

    assert "hashed_password" not in user_data


# Verificar que PomodoroPresetCreate se crea con argumentos validos para el modo clasico
@pytest.mark.parametrize(
    "name, mode, start_minutes, num_of_rounds, break_minutes, project_id, category_id",
    [
        pytest.param(
            "classic_preset",
            "classic",
            25,
            4,
            5,
            None,
            None,
            id="classic_without_scope",
        ),
        pytest.param(
            "classic_preset",
            "classic",
            25,
            4,
            5,
            2,
            None,
            id="classic_with_project_scope",
        ),
        pytest.param(
            "classic_preset",
            "classic",
            25,
            4,
            5,
            None,
            2,
            id="classic_with_category_scope",
        ),
    ],
)
def test_PomodoroPresetCreate_for_classic_mode(
    name, mode, start_minutes, num_of_rounds, break_minutes, project_id, category_id
):
    preset_input = PomodoroPresetCreate(
        name=name,
        mode=mode,
        project_id=project_id,
        category_id=category_id,
        start_minutes=start_minutes,
        num_of_rounds=num_of_rounds,
        break_minutes=break_minutes,
    )

    assert preset_input.project_id == project_id
    assert preset_input.category_id == category_id


# Verificar que PomodoroPresetCreate se crea con argumentos validos para el modo incremental
@pytest.mark.parametrize(
    "name, mode, start_minutes, num_of_rounds, growth, cap_minutes, project_id, category_id",
    [
        pytest.param(
            "incremental_preset",
            "incremental",
            20,
            4,
            2,
            30,
            None,
            None,
            id="incremental_without_scope",
        ),
        pytest.param(
            "incremental_preset",
            "incremental",
            20,
            4,
            2,
            30,
            2,
            None,
            id="incremental_with_project_scope",
        ),
        pytest.param(
            "incremental_preset",
            "incremental",
            20,
            4,
            2,
            30,
            None,
            2,
            id="incremental_with_category_scope",
        ),
    ],
)
def test_PomodoroPresetCreate_for_incremental_mode(
    name,
    mode,
    start_minutes,
    num_of_rounds,
    growth,
    cap_minutes,
    project_id,
    category_id,
):
    preset_input = PomodoroPresetCreate(
        name=name,
        mode=mode,
        project_id=project_id,
        category_id=category_id,
        start_minutes=start_minutes,
        num_of_rounds=num_of_rounds,
        growth=growth,
        cap_minutes=cap_minutes,
    )

    assert preset_input.project_id == project_id
    assert preset_input.category_id == category_id


# Verificar que PomodoroPresetCreate se crea con argumentos validos para el modo flexible
@pytest.mark.parametrize(
    "name, mode, start_minutes, num_of_rounds, rate, cap_minutes, project_id, category_id",
    [
        pytest.param(
            "flexible_preset",
            "flexible",
            20,
            4,
            0.4,
            30,
            None,
            None,
            id="flexible_without_scope",
        ),
        pytest.param(
            "flexible_preset",
            "flexible",
            20,
            4,
            0.5,
            30,
            2,
            None,
            id="flexible_with_project_scope",
        ),
        pytest.param(
            "flexible_preset",
            "flexible",
            20,
            4,
            0.6,
            30,
            None,
            2,
            id="flexible_with_category_scope",
        ),
    ],
)
def test_PomodoroPresetCreate_for_flexible_mode(
    name, mode, start_minutes, num_of_rounds, rate, cap_minutes, project_id, category_id
):
    preset_input = PomodoroPresetCreate(
        name=name,
        mode=mode,
        project_id=project_id,
        category_id=category_id,
        start_minutes=start_minutes,
        num_of_rounds=num_of_rounds,
        rate=rate,
        cap_minutes=cap_minutes,
    )

    assert preset_input.project_id == project_id
    assert preset_input.category_id == category_id


# Verificar que argumentos invalidos para modo clasico arrojan un error de validación
@pytest.mark.parametrize(
    "invalid_arguments, error_message",
    [
        pytest.param({"break_minutes": None}, "break_minutes must be defined"),
        pytest.param(
            {"growth": 2},
            "Input must not contain arguments invalid for the classic mode",
        ),
        pytest.param(
            {"rate": 0.2},
            "Input must not contain arguments invalid for the classic mode",
        ),
        pytest.param(
            {"cap_minutes": 30},
            "Input must not contain arguments invalid for the classic mode",
        ),
    ],
)
def test_PomodoroPresetCreate_fails_if_input_contains_invalid_arguments_for_classic_mode(
    invalid_arguments, error_message
):

    classic_preset_args = {
        "name": "classic_preset_test",
        "mode": "classic",
        "start_minutes": 25,
        "num_of_rounds": 4,
        "break_minutes": 5,
    }

    with pytest.raises(pydantic.ValidationError, match=error_message):
        _ = PomodoroPresetCreate(**{**classic_preset_args, **invalid_arguments})


# Verificar que argumentos invalidos para modo incremental arrojan un error de validación
@pytest.mark.parametrize(
    "invalid_arguments, error_message",
    [
        pytest.param({"growth": None}, "must be defined"),
        pytest.param({"cap_minutes": None}, "must be defined"),
        pytest.param(
            {"break_minutes": 5},
            "Input must not contain arguments invalid for the incremental mode",
        ),
        pytest.param(
            {"rate": 0.2},
            "Input must not contain arguments invalid for the incremental mode",
        ),
    ],
)
def test_PomodoroPresetCreate_fails_if_input_contains_invalid_arguments_for_incremental_mode(
    invalid_arguments, error_message
):

    incremental_preset_args = {
        "name": "incremental_preset_test",
        "mode": "incremental",
        "start_minutes": 20,
        "num_of_rounds": 4,
        "growth": 2,
        "cap_minutes": 30,
    }

    with pytest.raises(pydantic.ValidationError, match=error_message):
        _ = PomodoroPresetCreate(**{**incremental_preset_args, **invalid_arguments})


# Verificar que argumentos invalidos para modo flexible arrojan un error de validación
@pytest.mark.parametrize(
    "invalid_arguments, error_message",
    [
        pytest.param({"rate": None}, "must be defined"),
        pytest.param({"cap_minutes": None}, "must be defined"),
        pytest.param(
            {"growth": 2},
            "Input must not contain arguments invalid for the flexible mode",
        ),
        pytest.param(
            {"break_minutes": 5},
            "Input must not contain arguments invalid for the flexible mode",
        ),
    ],
)
def test_PomodoroPresetCreate_fails_if_input_contains_invalid_arguments_for_flexible_mode(
    invalid_arguments, error_message
):

    flexible_preset_args = {
        "name": "flexible_preset_test",
        "mode": "flexible",
        "start_minutes": 20,
        "num_of_rounds": 4,
        "rate": 0.4,
        "cap_minutes": 30,
    }

    with pytest.raises(pydantic.ValidationError, match=error_message):
        _ = PomodoroPresetCreate(**{**flexible_preset_args, **invalid_arguments})


# Revisar si PomodoroPresetCreate falla si se trata de asignar tanto un proyecto como una categoria
# al preset / configuración
def test_PomodoroPresetCreate_fails_if_more_than_one_scope_is_defined():

    preset_args = {
        "name": "preset_test",
        "mode": "classic",
        "start_minutes": 20,
        "num_of_rounds": 4,
        "break_minutes": 5,
    }

    with pytest.raises(pydantic.ValidationError, match="Only one scope is allowed"):
        _ = PomodoroPresetCreate(**{**preset_args, "project_id": 1, "category_id": 2})


# Revisar si PomodoroPresetCreate falla si el modo no es uno de los valores válidos según PomodoroMode
def test_PomodoroPresetCreate_fails_if_mode_is_invalid():

    preset_args = {
        "name": "preset_test",
        "mode": "turbo",
        "start_minutes": 20,
        "num_of_rounds": 4,
        "break_minutes": 5,
    }

    with pytest.raises(
        pydantic.ValidationError,
        match="Input should be 'classic', 'incremental' or 'flexible'",
    ):
        _ = PomodoroPresetCreate(**preset_args)


# Revisar si PomodoroPresetCreate falla si no se entrega el campo obligatorio que es name
def test_PomodoroPresetCreate_fails_if_name_is_empty_string():

    preset_args = {
        "name": "",
        "mode": "classic",
        "start_minutes": 20,
        "num_of_rounds": 4,
        "break_minutes": 5,
    }

    with pytest.raises(
        pydantic.ValidationError, match="String should have at least 1 character"
    ):
        _ = PomodoroPresetCreate(**preset_args)


# Revisar que PomodoroPresetCreate falla si se omite el campo de name
def test_PomodoroPresetCreate_fails_if_name_is_omitted():

    preset_args = {
        "mode": "classic",
        "start_minutes": 20,
        "num_of_rounds": 4,
        "break_minutes": 5,
    }

    with pytest.raises(pydantic.ValidationError, match="Field required"):
        _ = PomodoroPresetCreate(**preset_args)


# Verificar que PomodoroPresetRead puede leer un objeto ORM (PomodoroPreset) y no solo diccionarios
def test_PomodoroPresetRead_can_be_built_from_a_PomodoroPreset_object():
    preset = PomodoroPreset(
        id=1,
        owner_id=1,
        name="classic_preset",
        mode=PomodoroMode.CLASSIC,
        start_minutes=25,
        num_of_rounds=4,
        break_minutes=5,
    )

    preset_data = PomodoroPresetRead.model_validate(preset)

    assert preset_data.mode == PomodoroMode.CLASSIC
    assert preset_data.break_minutes == 5
    assert preset_data.growth is None


# Verificar que PomodoroPresetCreate rechaza valores fuera de rango
@pytest.mark.parametrize(
    "mode, start_minutes, num_of_rounds, break_minutes, growth, rate, cap_minutes, error_match",
    [
        pytest.param(
            "classic",
            0,
            4,
            5,
            None,
            None,
            None,
            r"start_minutes\s+Input should be greater than or equal to 1",
            id="start_below_minimum",
        ),
        pytest.param(
            "classic",
            81,
            4,
            5,
            None,
            None,
            None,
            r"start_minutes\s+Input should be less than or equal to 80",
            id="start_above_maximum",
        ),
        pytest.param(
            "classic",
            25,
            0,
            5,
            None,
            None,
            None,
            r"num_of_rounds\s+Input should be greater than or equal to 1",
            id="rounds_below_minimum",
        ),
        pytest.param(
            "classic",
            25,
            9,
            5,
            None,
            None,
            None,
            r"num_of_rounds\s+Input should be less than or equal to 8",
            id="rounds_above_maximum",
        ),
        pytest.param(
            "classic",
            25,
            4,
            0,
            None,
            None,
            None,
            r"break_minutes\s+Input should be greater than 0",
            id="break_not_positive",
        ),
        pytest.param(
            "incremental",
            25,
            4,
            None,
            -1,
            None,
            50,
            r"growth\s+Input should be greater than or equal to 0",
            id="growth_negative",
        ),
        pytest.param(
            "incremental",
            25,
            4,
            None,
            5,
            None,
            81,
            r"cap_minutes\s+Input should be less than or equal to 80",
            id="incremental_cap_above_maximum",
        ),
        pytest.param(
            "incremental",
            25,
            4,
            None,
            5,
            None,
            24,
            r"Cap minutes \(24\) must be a value equal or greater",
            id="incremental_cap_below_start",
        ),
        pytest.param(
            "flexible",
            25,
            4,
            None,
            None,
            0.19,
            50,
            r"rate\s+Input should be greater than or equal to 0\.2",
            id="rate_below_minimum",
        ),
        pytest.param(
            "flexible",
            25,
            4,
            None,
            None,
            0.61,
            50,
            r"rate\s+Input should be less than or equal to 0\.6",
            id="rate_above_maximum",
        ),
        pytest.param(
            "flexible",
            25,
            4,
            None,
            None,
            0.4,
            81,
            r"cap_minutes\s+Input should be less than or equal to 80",
            id="flexible_cap_above_maximum",
        ),
        pytest.param(
            "flexible",
            25,
            4,
            None,
            None,
            0.4,
            25,
            r"Cap minutes \(25\) must be a value greater than",
            id="flexible_cap_equal_to_start",
        ),
        pytest.param(
            "flexible",
            25,
            4,
            None,
            None,
            0.4,
            24,
            r"Cap minutes \(24\) must be a value greater than",
            id="flexible_cap_below_start",
        ),
    ],
)
def test_PomodoroPresetCreate_fails_if_values_are_out_of_range(
    mode,
    start_minutes,
    num_of_rounds,
    break_minutes,
    growth,
    rate,
    cap_minutes,
    error_match,
):

    with pytest.raises(pydantic.ValidationError, match=error_match):
        _ = PomodoroPresetCreate(
            name="preset-error",
            mode=mode,
            start_minutes=start_minutes,
            break_minutes=break_minutes,
            growth=growth,
            num_of_rounds=num_of_rounds,
            rate=rate,
            cap_minutes=cap_minutes,
        )


# Verificar que PomodoroPresetCreate acepta los valores justo en el borde de cada rango
@pytest.mark.parametrize(
    "mode, start_minutes, num_of_rounds, break_minutes, growth, rate, cap_minutes",
    [
        pytest.param("classic", 1, 1, 1, None, None, None, id="classic_minimum_values"),
        pytest.param(
            "classic", 80, 8, 5, None, None, None, id="classic_maximum_values"
        ),
        pytest.param(
            "incremental", 25, 4, None, 0, None, 50, id="incremental_growth_zero"
        ),
        pytest.param(
            "incremental", 25, 4, None, 5, None, 25, id="incremental_cap_equal_to_start"
        ),
        pytest.param(
            "incremental", 25, 4, None, 5, None, 80, id="incremental_cap_at_limit"
        ),
        pytest.param(
            "flexible", 25, 4, None, None, 0.2, 50, id="flexible_rate_at_minimum"
        ),
        pytest.param(
            "flexible", 25, 4, None, None, 0.6, 50, id="flexible_rate_at_maximum"
        ),
        pytest.param(
            "flexible", 25, 4, None, None, 0.4, 26, id="flexible_cap_just_above_start"
        ),
        pytest.param(
            "flexible", 25, 4, None, None, 0.4, 80, id="flexible_cap_at_limit"
        ),
    ],
)
def test_PomodoroPresetCreate_accepts_values_at_range_borders(
    mode, start_minutes, num_of_rounds, break_minutes, growth, rate, cap_minutes
):

    preset_input = PomodoroPresetCreate(
        name="preset-test",
        mode=mode,
        start_minutes=start_minutes,
        num_of_rounds=num_of_rounds,
        break_minutes=break_minutes,
        growth=growth,
        rate=rate,
        cap_minutes=cap_minutes,
    )

    assert preset_input.start_minutes == start_minutes
    assert preset_input.mode == mode
    assert preset_input.break_minutes == break_minutes
    assert preset_input.growth == growth
    assert preset_input.rate == rate
    assert preset_input.cap_minutes == cap_minutes
