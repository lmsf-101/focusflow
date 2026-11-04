from enum import Enum

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy import Enum as sqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from focusflow_api.db import Base

MAX_TASK_TITLE_LENGTH = 100

task_tag = Table(
    "task_tag",
    Base.metadata,
    Column("task_id", ForeignKey("task.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True),
)


def enum_values(enum_cls: type[Enum]) -> list[str]:
    return [e.value for e in enum_cls]


class TaskPriority(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class PomodoroMode(str, Enum):
    CLASSIC = "classic"
    INCREMENTAL = "incremental"
    FLEXIBLE = "flexible"


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    projects: Mapped[list["Project"]] = relationship(back_populates="owner")
    tasks: Mapped[list["Task"]] = relationship(back_populates="owner")
    categories: Mapped[list["Category"]] = relationship(back_populates="owner")
    tags: Mapped[list["Tag"]] = relationship(back_populates="owner")


class Project(Base):
    __tablename__ = "project"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    owner: Mapped["User"] = relationship(back_populates="projects")

    tasks: Mapped[list["Task"]] = relationship(back_populates="project")


class Category(Base):
    __tablename__ = "category"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    owner: Mapped["User"] = relationship(back_populates="categories")

    tasks: Mapped[list["Task"]] = relationship(back_populates="category")


class Tag(Base):
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    owner: Mapped["User"] = relationship(back_populates="tags")
    tasks: Mapped[list["Task"]] = relationship(
        secondary=task_tag, back_populates="tags"
    )
    __table_args__ = (
        UniqueConstraint("owner_id", "name", name="uq_tag_owner_id_name"),
        CheckConstraint("name = lower(name)", name="ck_tag_name_lowercase"),
    )


class Task(Base):
    __tablename__ = "task"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(MAX_TASK_TITLE_LENGTH))

    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    owner: Mapped["User"] = relationship(back_populates="tasks")

    project_id: Mapped[int | None] = mapped_column(ForeignKey("project.id"))
    project: Mapped["Project | None"] = relationship(back_populates="tasks")

    category_id: Mapped[int | None] = mapped_column(ForeignKey("category.id"))
    category: Mapped["Category | None"] = relationship(back_populates="tasks")

    tags: Mapped[list["Tag"]] = relationship(secondary=task_tag, back_populates="tasks")

    priority: Mapped["TaskPriority"] = mapped_column(
        sqlEnum(TaskPriority, values_callable=enum_values)
    )

    status: Mapped["TaskStatus"] = mapped_column(
        sqlEnum(TaskStatus, values_callable=enum_values)
    )


class PomodoroPreference(Base):
    __tablename__ = "pomodoro_preference"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("project.id", ondelete="CASCADE")
    )
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("category.id", ondelete="CASCADE")
    )
    mode: Mapped["PomodoroMode"] = mapped_column(
        sqlEnum(PomodoroMode, values_callable=enum_values)
    )
    start_minutes: Mapped[int] = mapped_column()
    num_of_rounds: Mapped[int] = mapped_column()
    break_minutes: Mapped[int | None] = mapped_column()
    growth: Mapped[int | None] = mapped_column()
    cap_minutes: Mapped[int | None] = mapped_column()
    rate: Mapped[float | None] = mapped_column()

    __table_args__ = (
        CheckConstraint(
            "num_nonnulls(project_id, category_id) <= 1",
            name="ck_pomodoro_preference_single_scope",
        ),
        CheckConstraint(
            "mode <> 'classic' OR (break_minutes IS NOT NULL AND growth IS NULL AND cap_minutes IS NULL AND rate IS NULL)",
            name="ck_pomodoro_preference_classic_parameters",
        ),
        CheckConstraint(
            "mode <> 'incremental' OR (break_minutes IS NULL AND growth IS NOT NULL AND cap_minutes IS NOT NULL AND rate IS NULL)",
            name="ck_pomodoro_preference_incremental_parameters",
        ),
        CheckConstraint(
            "mode <> 'flexible' OR (break_minutes IS NULL AND growth IS NULL AND cap_minutes IS NOT NULL AND rate IS NOT NULL)",
            name="ck_pomodoro_preference_flexible_parameters",
        ),
    )
