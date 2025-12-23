from dataclasses import dataclass

from .pokemon_team import PokemonTeam


@dataclass
class Opponent:
    team: PokemonTeam
    remaining_hp_percentage: float


class BestOpponentsList:
    def __init__(self, limit: int = 1):
        if limit <= 0:
            raise ValueError("Limit must be positive.")

        self._limit = limit
        self._opponents: list[Opponent] = []

    def get_opponents(self) -> tuple[Opponent, ...]:
        return tuple(self._opponents)

    def get_the_best_opponent(self) -> Opponent | None:
        if not self._opponents:
            return None
        return self._opponents[0]

    def append(self, opponent: Opponent) -> None:
        if not self._is_full():
            self._opponents.append(opponent)
            self._opponents.sort(key=self._opponent_sort_key)
            return

        worst_opponent = self._opponents[-1]

        if self._opponent_sort_key(opponent) < self._opponent_sort_key(worst_opponent):
            self._opponents[-1] = opponent
            self._opponents.sort(key=self._opponent_sort_key)

    def _is_full(self) -> bool:
        return len(self._opponents) >= self._limit

    @staticmethod
    def _opponent_sort_key(opponent: Opponent) -> tuple[float, float]:
        return (opponent.remaining_hp_percentage, -opponent.team.get_stats())
