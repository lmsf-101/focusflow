from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    model_validator,
)

from focusflow_api.domain.pomodoro.curves import (
    MAX_NUMBER_ROUNDS,
    MAX_POMODORO_LIMIT,
    MAX_RATE,
    MIN_RATE,
)
from focusflow_api.domain.pomodoro.engine import FLEXIBLE_BREAK_RATIO
from focusflow_api.models import (
    MAX_POMODORO_PRESET_NAME_LENGTH,
    MAX_TASK_TITLE_LENGTH,
    PomodoroMode,
    TaskPriority,
    TaskStatus,
)


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1)


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ProjectUpdate(BaseModel):
    name: str = Field(default="", min_length=1)


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1)


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CategoryUpdate(BaseModel):
    name: str = Field(default="", min_length=1)


class TagCreate(BaseModel):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, to_lower=True, min_length=1),
    ]


class TagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class TaskCreate(BaseModel):
    title: str = Field(max_length=MAX_TASK_TITLE_LENGTH, min_length=1)
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    project_id: int | None = None
    category_id: int | None = None
    tag_ids: list[int] = []


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    priority: TaskPriority
    status: TaskStatus
    project_id: int | None
    category_id: int | None
    tags: list[TagRead]


class TaskUpdate(BaseModel):
    title: str = Field(default="", min_length=1, max_length=MAX_TASK_TITLE_LENGTH)

    # Valor None es usado como centinela para hacer priority,
    # status como opciónal, pero tambien imponer los valores de los Enums si se incluye en el cuerpo de la solicitud
    priority: TaskPriority = None
    status: TaskStatus = None

    project_id: int | None = None
    category_id: int | None = None
    tag_ids: list[int] = []


class PomodoroPresetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=MAX_POMODORO_PRESET_NAME_LENGTH)
    mode: PomodoroMode
    project_id: int | None = None
    category_id: int | None = None
    start_minutes: int = Field(ge=1, le=MAX_POMODORO_LIMIT)
    num_of_rounds: int = Field(ge=1, le=MAX_NUMBER_ROUNDS)

    # Atributos que corresponden a
    # Modo clasico
    break_minutes: int | None = Field(default=None, gt=0)

    # Modo incremental
    growth: int | None = Field(default=None, ge=0)

    # Modo flexible
    rate: float | None = Field(default=None, ge=MIN_RATE, le=MAX_RATE)

    # Modo incremental | flexible
    cap_minutes: int | None = Field(default=None, le=MAX_POMODORO_LIMIT)

    # Validadores para revisar si se cumple con las reglas de los modos
    @model_validator(mode="after")
    def classic_mode_validator(self) -> Self:

        if self.mode != PomodoroMode.CLASSIC:
            return self

        if self.break_minutes is None:
            raise ValueError(
                f"break_minutes must be defined if the Pomodoro mode is {PomodoroMode.CLASSIC.value}"
            )

        elif (
            self.growth is not None
            or self.rate is not None
            or self.cap_minutes is not None
        ):
            raise ValueError(
                f"Input must not contain arguments invalid for the {PomodoroMode.CLASSIC.value} mode (growth, rate, cap_minutes)"
            )

        else:
            return self

    @model_validator(mode="after")
    def incremental_mode_validator(self) -> Self:

        if self.mode != PomodoroMode.INCREMENTAL:
            return self

        if self.growth is None or self.cap_minutes is None:
            raise ValueError(
                f"growth and cap_minutes must be defined if the Pomodoro mode is {PomodoroMode.INCREMENTAL.value}"
            )

        elif self.rate is not None or self.break_minutes is not None:
            raise ValueError(
                f"Input must not contain arguments invalid for the {PomodoroMode.INCREMENTAL.value} mode (rate, break_minutes)"
            )

        elif self.cap_minutes < self.start_minutes:
            raise ValueError(
                f"Cap minutes ({self.cap_minutes}) must be a value equal or greater than the initial minutes value ({self.start_minutes})"
            )

        else:
            return self

    @model_validator(mode="after")
    def flexible_mode_validator(self) -> Self:

        if self.mode != PomodoroMode.FLEXIBLE:
            return self

        if self.rate is None or self.cap_minutes is None:
            raise ValueError(
                f"rate and cap_minutes must be defined if the Pomodoro mode is {PomodoroMode.FLEXIBLE.value}"
            )

        elif self.growth is not None or self.break_minutes is not None:
            raise ValueError(
                f"Input must not contain arguments invalid for the {PomodoroMode.FLEXIBLE.value} mode (growth, break_minutes)"
            )

        elif self.cap_minutes <= self.start_minutes:
            raise ValueError(
                f"Cap minutes ({self.cap_minutes}) must be a value greater than the initial minutes value ({self.start_minutes})"
            )

        else:
            return self

    @model_validator(mode="after")
    def check_for_single_scope_definition(self) -> Self:

        if self.project_id is not None and self.category_id is not None:
            raise ValueError(
                "Only one scope is allowed. project_id and category_id cannot be defined at the same time"
            )

        return self


class PomodoroPresetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    mode: PomodoroMode
    start_minutes: int
    num_of_rounds: int
    project_id: int | None
    category_id: int | None

    # Atributos que corresponden a
    # Modo clasico
    break_minutes: int | None = None

    # Modo incremental
    growth: int | None = None

    # Modo flexible
    rate: float | None = None

    # Modo incremental | flexible
    cap_minutes: int | None = None


class _PlanRequestBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    start_minutes: int
    num_of_rounds: int


class ClassicPlanRequest(_PlanRequestBase):
    mode: Literal[PomodoroMode.CLASSIC]
    break_minutes: int


class IncrementalPlanRequest(_PlanRequestBase):
    mode: Literal[PomodoroMode.INCREMENTAL]
    cap_minutes: int
    growth: int


class FlexiblePlanRequest(_PlanRequestBase):
    mode: Literal[PomodoroMode.FLEXIBLE]
    cap_minutes: int
    rate: float
    break_ratio: float = FLEXIBLE_BREAK_RATIO


type PlanRequest = Annotated[
    ClassicPlanRequest | IncrementalPlanRequest | FlexiblePlanRequest,
    Field(discriminator="mode"),
]


class PlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    work_times: tuple[int, ...]
    break_times: tuple[int, ...]
