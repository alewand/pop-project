import pandas as pd
import numpy as np
from typing import Callable, Tuple

from structures.best_opponents_list import (
    BestOpponentsList,
    Opponent,
    PokemonTeam
)
from battle.battle import simulate_battle
from constants.constants import (
    TEAM_SIZE
)


def find_best_opponent_team_from_random(
        pokemons: pd.DataFrame,
        current_team: PokemonTeam,
        type_multiplier_formula: Callable[[float, float], float],
        damage_formula: Callable[[int, int, float], int],
        unique_types: bool = True,
        opponents_limit: int | None = None,
        results_amount: int = 1,
) -> Tuple[Opponent, ...]:
    rng = np.random.default_rng()

    opponents = current_team.generate_opponents(
        pokemons,
        current_team,
        unique_types,
        opponents_limit
    )

    best_opponents = BestOpponentsList(results_amount)

    chosen_opponents_indexes = rng.choice(
        len(opponents),
        size=min(results_amount, len(opponents)),
        replace=False
    )

    chosen_opponents = [
        opponents[i] for i in chosen_opponents_indexes
    ]

    for opponent in chosen_opponents:
        original_opponent_team_setup, remaining_hp = (
            simulate_battle(
                current_team,
                opponent,
                type_multiplier_formula,
                damage_formula,
                TEAM_SIZE
            )
        )

        remaining_hp_percentage = (
            remaining_hp / sum(current_team.hps)
            if sum(current_team.hps) > 0 else 0.0
        )

        opponent_data = Opponent(
            team=original_opponent_team_setup,
            average_remaining_hp=remaining_hp,
            percentage_remaining_hp=remaining_hp_percentage,
            stats_sum=original_opponent_team_setup.stats,
        )

        best_opponents.append(opponent_data)

    return best_opponents.opponents, len(opponents)


def find_the_best_opponent_team(
        pokemons: pd.DataFrame,
        current_team: PokemonTeam,
        type_multiplier_formula: Callable[[float, float], float],
        damage_formula: Callable[[int, int, float], int],
        unique_types: bool = True,
        opponents_limit: int | None = None,
        results_amount: int = 1,
) -> Tuple[Opponent, ...]:
    opponents = current_team.generate_opponents(
        pokemons,
        current_team,
        unique_types,
        opponents_limit
    )

    best_opponents = BestOpponentsList(results_amount)

    for opponent in opponents:
        original_opponent_team_setup, remaining_hp = (
            simulate_battle(
                current_team,
                opponent,
                type_multiplier_formula,
                damage_formula,
                TEAM_SIZE
            )
        )

        remaining_hp_percentage = (
            remaining_hp / sum(current_team.hps)
            if sum(current_team.hps) > 0 else 0.0
        )

        opponent_data = Opponent(
            original_opponent_team_setup,
            remaining_hp_percentage,
        )

        best_opponents.append(opponent_data)

    return best_opponents.opponents, len(opponents)


def evaluate_team(opponent: Opponent) -> int:
    return 0 if opponent.remaining_hp_percentage > 0 else opponent.team.stats
