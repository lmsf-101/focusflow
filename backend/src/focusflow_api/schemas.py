from pydantic import BaseModel, ConfigDict, EmailStr, Field

from focusflow_api.models import MAX_TASK_TITLE_LENGTH, TaskPriority, TaskStatus


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


class TaskCreate(BaseModel):
    title: str = Field(max_length=MAX_TASK_TITLE_LENGTH, min_length=1)
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    project_id: int | None = None
    category_id: int | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    priority: TaskPriority
    status: TaskStatus
    project_id: int | None
    category_id: int | None


class TaskUpdate(BaseModel):
    title: str = Field(default="", min_length=1, max_length=MAX_TASK_TITLE_LENGTH)

    # Valor None es usado como centinela para hacer priority,
    # status como opciónal, pero tambien imponer los valores de los Enums si se incluye en el cuerpo de la solicitud
    priority: TaskPriority = None
    status: TaskStatus = None

    project_id: int | None = None
    category_id: int | None = None
