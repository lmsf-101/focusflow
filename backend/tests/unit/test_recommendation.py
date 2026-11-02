from collections.abc import Sequence
from typing import override

import pytest

from focusflow_api.domain.pomodoro.engine import PomodoroPlan
from focusflow_api.domain.pomodoro.errors import PomodoroPlanError
from focusflow_api.domain.pomodoro.recommendation import (
    ClassicSuggestion,
    IncrementalSuggestion,
    PomodoroSuggestion,
    RecommendationStrategy,
    convert_to_plan,
)


class FakeStrategy(RecommendationStrategy):
    @override
    def recommend(self, history: Sequence[int]) -> PomodoroSuggestion:
        return ClassicSuggestion(start_minutes=25, break_minutes=5, num_of_rounds=4)


class FakeIncrementalStrategy(RecommendationStrategy):
    @override
    def recommend(self, history: Sequence[int]) -> PomodoroSuggestion:
        return IncrementalSuggestion(
            start_minutes=25, growth=2, cap_minutes=35, num_of_rounds=4
        )


def test_recommendation_strategy_instance_is_not_allowed():
    with pytest.raises(TypeError):
        _ = RecommendationStrategy()


def test_strategy_without_recommend_function_returns_an_error_when_instancing():
    class BadStrategy(RecommendationStrategy):
        pass

    with pytest.raises(TypeError):
        _ = BadStrategy()


def test_strategy_is_converted_to_plan_successfully():

    expected_work_times = (25, 25, 25, 25)
    expected_break_times = (5, 5, 5)

    classic_plan = convert_to_plan(strategy=FakeStrategy(), history=[20, 21, 25, 25])

    assert isinstance(classic_plan, PomodoroPlan)

    assert classic_plan.work_times == expected_work_times
    assert classic_plan.break_times == expected_break_times


def test_incremental_strategy_is_converted_to_plan():

    expected_work_times = (25, 27, 29, 31)

    expected_break_times = (5, 5, 6)

    incremental_plan = convert_to_plan(
        strategy=FakeIncrementalStrategy(), history=[25, 28, 29, 32]
    )

    assert isinstance(incremental_plan, PomodoroPlan)

    assert incremental_plan.work_times == expected_work_times
    assert incremental_plan.break_times == expected_break_times


def test_invalid_strategy_raises_pomodoro_plan_error():

    class InvalidStrategy(RecommendationStrategy):
        @override
        def recommend(self, history: Sequence[int]) -> PomodoroSuggestion:
            return "This is an invalid suggestion"

    with pytest.raises(PomodoroPlanError, match="An error occurred when converting"):
        _ = convert_to_plan(strategy=InvalidStrategy(), history=[1, 2, 3])
