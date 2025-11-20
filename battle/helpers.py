import pandas as pd
from typing import Literal, Tuple, List

from constants.constants import CURRENT, OPPONENT, SPEED_COL
from structures.team import PokemonTeam

Turn = Literal["current", "opponent"]


def who_is_first(
    current_pokemon: pd.Series,
    opponent_pokemon: pd.Series
) -> Turn:
    return (
        CURRENT if current_pokemon[SPEED_COL] > opponent_pokemon[SPEED_COL]
        else OPPONENT
    )


def swap_to_next_alive(
        team: PokemonTeam,
        team_hp: List[int],
        current_index: int
        ) -> Tuple[bool, PokemonTeam, List[int]]:

    for i in range(current_index + 1, team.size):
        if team_hp[i] > 0:
            (team_hp[current_index],
                team_hp[i]) = (team_hp[i], team_hp[current_index])

            team.swap_members(current_index, i)

            return True, team, team_hp

    return False, team, team_hp
