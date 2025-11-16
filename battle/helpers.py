import pandas as pd
from typing import Literal, Tuple, List

from constants.constants import CURRENT, OPPONENT, SPEED_COL

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
        team: pd.DataFrame,
        team_hp: List[Tuple[int, int]],
        current_index: int
        ) -> Tuple[bool, pd.DataFrame, List[Tuple[int, int]]]:

    team_size = len(team)

    for i in range(current_index + 1, team_size):
        if team_hp[i][0] > 0:
            (team_hp[current_index],
                team_hp[i]) = (team_hp[i], team_hp[current_index])
            current_pokemon = team.iloc[current_index].copy()
            pokemon_to_swap = team.iloc[i].copy()
            team.iloc[current_index] = pokemon_to_swap
            team.iloc[i] = current_pokemon

            return True, team, team_hp

    return False, team, team_hp


def recover_hp_order(team_hp: List[Tuple[int, int]]) -> List[int]:
    team_hp_in_order: List[int] = [0] * len(team_hp)

    for hp, oryginal_index in team_hp:
        team_hp_in_order[oryginal_index] = hp

    return team_hp_in_order
