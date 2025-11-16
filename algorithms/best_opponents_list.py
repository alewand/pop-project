from dataclasses import dataclass
import pandas as pd
from typing import List, Tuple


@dataclass
class Opponent:
    team: pd.DataFrame
    average_remaining_hp: float
    percentage_remaining_hp: float
    stats_sum: float


class BestOpponentsList:
    def __init__(self, limit: int = 1):
        if (limit < 1):
            raise ValueError("Limit must be at least 1.")
        self._limit = limit
        self._opponents: List[Opponent] = []

    @property
    def opponents(self) -> Tuple[Opponent, ...]:
        return tuple(self._opponents)

    @property
    def is_full(self) -> bool:
        return len(self._opponents) >= self._limit

    @staticmethod
    def _opponent_sort_key(opponent: Opponent) -> Tuple[float, float]:
        return (opponent.percentage_remaining_hp, -opponent.stats_sum)

    def append(self, opponent: Opponent) -> None:
        if not self.is_full:
            self._opponents.append(opponent)
            self._opponents.sort(key=self._opponent_sort_key)
            return

        worst_opponent = self._opponents[-1]

        if (self._opponent_sort_key(opponent) <
                self._opponent_sort_key(worst_opponent)):
            self._opponents[-1] = opponent
            self._opponents.sort(key=self._opponent_sort_key)
