"""Pure domain services — stateless logic with no side effects."""

from __future__ import annotations

import math


class RewardCalculator:
    """Calculates credits earned for a typing attempt.

    The reward is proportional to how close the user's WPM is to the goal.
    Exceeding the goal always yields the full level cost.
    Repeating a level yields nothing — checked before calling this class.
    """

    def calculate(self, user_wpm: int, goal_wpm: int, level_cost: int) -> int:
        """Computes the reward for a single typing attempt.

        Args:
            user_wpm: Words per minute the user achieved.
            goal_wpm: The level's target words per minute.
            level_cost: Maximum credits this level can award.

        Returns:
            Integer credits between 0 and level_cost (inclusive).
        """
        ratio = min(1.0, user_wpm / goal_wpm)
        return math.floor(ratio * level_cost)
