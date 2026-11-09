from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass

from focusflow_api.domain.pomodoro.engine import (
    FLEXIBLE_BREAK_RATIO,
    PomodoroPlan,
    plan_classic,
    plan_flexible,
    plan_incremental,
)
from focusflow_api.domain.pomodoro.errors import PomodoroPlanError


@dataclass(frozen=True)
class ClassicSuggestion:
    start_minutes: int
    break_minutes: int
    num_of_rounds: int


@dataclass(frozen=True)
class IncrementalSuggestion:
    start_minutes: int
    growth: int
    cap_minutes: int
    num_of_rounds: int


@dataclass(frozen=True)
class FlexibleSuggestion:
    start_minutes: int
    cap_minutes: int
    rate: float
    num_of_rounds: int
    break_ratio: float = FLEXIBLE_BREAK_RATIO


type PomodoroSuggestion = ClassicSuggestion | IncrementalSuggestion | FlexibleSuggestion


class RecommendationStrategy(ABC):
    @abstractmethod
    def recommend(self, history: Sequence[int]) -> PomodoroSuggestion:
        """
        Generates the adequate Pomodoro suggestion for the session / task, based on historical data (list of working minutes, based on a specific task / category)

        NOTE: RecommendationStrategy does not validate the domain rules

        Args:
            # TODO: Provisional, después cambiar para reflejar mejor los datos de las sesiones
            # TODO: Revisar cómo manejar un historial vacío
            history (Sequence[int]): list of historical work times done for the specific task / job / category

        Returns:
            A PomodoroSuggestion that returns the best Pomodoro mode for the session (Classic, Incremental, ...) and its corresponding parameters.
        """
        raise NotImplementedError


def convert_to_plan(
    strategy: RecommendationStrategy, history: Sequence[int]
) -> PomodoroPlan:
    """
    Transforms the strategy's suggestion into a validated Pomodoro Plan.

    The function takes the strategy suggested mode and parameters, and runs the appropriate domain function to validate them.

    Args:
        strategy (RecommendationStrategy): strategy that produces the suggested mode and parameters

        history (Sequence[int]): historical work times done by the user, passed as arguments to the strategy recommendation function

    Returns:
        PomodoroPlan built from the suggested mode and parameters

    Raises:
        PomodoroValidationError: if the suggested parameters do not meet domain rule(s)

        PomodoroPlanError: if the suggestion itself isn't a valid mode (Classic, Incremental, Flexible)
    """

    suggested_plan = strategy.recommend(history)

    if isinstance(suggested_plan, ClassicSuggestion):
        return plan_classic(
            suggested_plan.start_minutes,
            suggested_plan.break_minutes,
            suggested_plan.num_of_rounds,
        )

    elif isinstance(suggested_plan, IncrementalSuggestion):
        return plan_incremental(
            suggested_plan.start_minutes,
            suggested_plan.growth,
            suggested_plan.cap_minutes,
            suggested_plan.num_of_rounds,
        )

    elif isinstance(suggested_plan, FlexibleSuggestion):
        return plan_flexible(
            suggested_plan.start_minutes,
            suggested_plan.cap_minutes,
            suggested_plan.rate,
            suggested_plan.num_of_rounds,
            suggested_plan.break_ratio,
        )

    else:
        raise PomodoroPlanError(
            "An error occurred when converting the recommended strategy to a plan"
        )
