import pandas as pd
from typing import Callable, Tuple

from algorithms.best_opponents_list import BestOpponentsList, Opponent
from battle.battle import simulate_battle
from constants.constants import (
    ATTACK_COL,
    DEFENSE_COL,
    HP_COL,
    SPECIAL_ATTACK_COL,
    SPECIAL_DEFENSE_COL,
    TEAM_SIZE
)
from data.generators import generate_opponent_teams, generate_team_permutations


def get_sum_of_team_stats(team: pd.DataFrame) -> int:
    stat_cols = [
        ATTACK_COL,
        SPECIAL_ATTACK_COL,
        DEFENSE_COL,
        SPECIAL_DEFENSE_COL]
    return int(team[stat_cols].astype(int).to_numpy().sum())


def find_the_best_opponent_team_permutation(
        current_team: pd.DataFrame,
        opponent_team: pd.DataFrame,
        type_multiplier_formula: Callable[[float, float], float],
        damage_formula: Callable[[int, int, float], int],
        limit: int | None = 1,
        team_size: int = TEAM_SIZE
) -> Tuple[pd.DataFrame, float]:
    if len(current_team) != team_size or len(opponent_team) != team_size:
        raise ValueError("Both teams must have equal, specified team size.")

    current_team_permutations = generate_team_permutations(current_team)
    opponent_team_permutations = generate_team_permutations(opponent_team)

    best_opponent_team: pd.DataFrame | None = None
    lowest_average_remaining_hp = float('inf')

    for opponent_team_permutation in opponent_team_permutations:
        total_remaining_hp = 0

        for i, current_team_permutation in enumerate(
            current_team_permutations
        ):
            _, _, _, current_team_hp, _ = simulate_battle(
                current_team_permutation,
                opponent_team_permutation,
                type_multiplier_formula,
                damage_formula,
                team_size
            )

            total_remaining_hp += sum(hp for hp in current_team_hp)

            if limit is not None and i + 1 >= limit:
                break

        average_remaining_hp = (
            total_remaining_hp / (
                len(current_team_permutations) if limit is None else limit
                )
        )

        if average_remaining_hp < lowest_average_remaining_hp:
            lowest_average_remaining_hp = average_remaining_hp
            best_opponent_team = opponent_team_permutation

    if (best_opponent_team is None):
        return opponent_team, 0.0, 0.0

    lowest_average_remaining_hp = round(lowest_average_remaining_hp, 2)
    percentage_hp = (
        lowest_average_remaining_hp / (
            sum(current_team[HP_COL].astype(int).to_list())
        )
    )

    return best_opponent_team, lowest_average_remaining_hp, percentage_hp


def find_the_best_opponent_team(
        pokemons: pd.DataFrame,
        current_team: pd.DataFrame,
        type_multiplier_formula: Callable[[float, float], float],
        damage_formula: Callable[[int, int, float], int],
        unique_types: bool = True,
        opponents_limit: int | None = 10,
        permutations_limit: int | None = 1,
        results_amount: int = 1,
) -> Tuple[Opponent, ...]:
    opponents = generate_opponent_teams(
        pokemons,
        current_team,
        unique_types,
        opponents_limit)

    best_opponent_teams = BestOpponentsList(results_amount)

    for opponent in opponents:
        best_opponent_team, avg_remaining_hp, perc_remaining_hp = (
            find_the_best_opponent_team_permutation(
                current_team,
                opponent,
                type_multiplier_formula,
                damage_formula,
                permutations_limit,
            )
        )

        opponent_stats_sum = get_sum_of_team_stats(best_opponent_team)

        opponent_data = Opponent(
            team=best_opponent_team,
            average_remaining_hp=avg_remaining_hp,
            percentage_remaining_hp=perc_remaining_hp,
            stats_sum=opponent_stats_sum,
        )

        best_opponent_teams.append(opponent_data)

    return best_opponent_teams.opponents
