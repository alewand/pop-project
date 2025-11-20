from dataclasses import dataclass
from typing import List, Tuple

from structures.team import PokemonTeam


@dataclass
class Opponent:
    team: PokemonTeam
    remaining_hp_percentage: float


class BestOpponentsList:
    def __init__(self, limit: int = 1):
        if limit < 1:
            raise ValueError("Limit must be at least 1.")
        self._limit = limit
        self._opponents: List[Opponent] = []

    @property
    def opponents(self) -> Tuple[Opponent, ...]:
        return tuple(self._opponents)

    @property
    def _is_full(self) -> bool:
        return len(self._opponents) >= self._limit

    def append(self, opponent: Opponent) -> None:
        if not self._is_full:
            self._opponents.append(opponent)
            self._opponents.sort(key=self._opponent_sort_key)
            return

        worst_opponent = self._opponents[-1]

        if (self._opponent_sort_key(opponent) <
                self._opponent_sort_key(worst_opponent)):
            self._opponents[-1] = opponent
            self._opponents.sort(key=self._opponent_sort_key)

    @staticmethod
    def _opponent_sort_key(opponent: Opponent) -> Tuple[float, float]:
        return (opponent.remaining_hp_percentage, -opponent.team.stats)
