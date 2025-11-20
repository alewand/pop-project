import pandas as pd
from typing import Callable, Tuple

from structures.best_opponents_list import BestOpponentsList, Opponent
from battle.battle import simulate_battle
from constants.constants import (
    ATTACK_COL,
    DEFENSE_COL,
    SPECIAL_ATTACK_COL,
    SPECIAL_DEFENSE_COL,
    TEAM_SIZE
)
from data.generators import generate_opponent_teams


def get_sum_of_team_stats(team: pd.DataFrame) -> int:
    stat_cols = [
        ATTACK_COL,
        SPECIAL_ATTACK_COL,
        DEFENSE_COL,
        SPECIAL_DEFENSE_COL]
    return int(team[stat_cols].astype(int).to_numpy().sum())


def find_the_best_opponent_team(
        pokemons: pd.DataFrame,
        current_team: pd.DataFrame,
        type_multiplier_formula: Callable[[float, float], float],
        damage_formula: Callable[[int, int, float], int],
        unique_types: bool = True,
        opponents_limit: int | None = None,
        results_amount: int = 1,
) -> Tuple[Opponent, ...]:
    opponents = generate_opponent_teams(
        pokemons,
        current_team,
        unique_types,
        opponents_limit)

    best_opponent_teams = BestOpponentsList(results_amount)

    for opponent in opponents:
        original_opponent_team_setup, remaining_hp, original_hp = (
            simulate_battle(
                current_team,
                opponent,
                type_multiplier_formula,
                damage_formula,
                TEAM_SIZE
            )
        )

        opponent_stats_sum = get_sum_of_team_stats(
            original_opponent_team_setup)

        remaining_hp_percentage = (
            remaining_hp / original_hp
            if original_hp > 0 else 0.0
        )

        opponent_data = Opponent(
            team=original_opponent_team_setup,
            average_remaining_hp=remaining_hp,
            percentage_remaining_hp=remaining_hp_percentage,
            stats_sum=opponent_stats_sum,
        )

        best_opponent_teams.append(opponent_data)

    return best_opponent_teams.opponents, len(opponents)
