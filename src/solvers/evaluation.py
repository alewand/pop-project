from collections.abc import Callable

import numpy as np
from pandera.typing import DataFrame

from classes import BestOpponentsList, Opponent, PokemonTeam
from schemas import PokemonSchema
from simulation import DamageFormula, TypeMultiplierFormula, simulate_battle


def find_the_best_opponent_team(
    pokemons: DataFrame[PokemonSchema],
    current_team: PokemonTeam,
    type_multiplier_formula: TypeMultiplierFormula,
    damage_formula: DamageFormula,
    unique_types: bool = True,
    opponents_limit: int | None = None,
    results_amount: int = 1,
) -> tuple[Opponent, ...]:
    opponents = current_team.generate_opponents(pokemons, unique_types, opponents_limit)

    best_opponents = BestOpponentsList(results_amount)

    for opponent in opponents:
        original_opponent_team_setup, remaining_hp = simulate_battle(
            current_team, opponent, type_multiplier_formula, damage_formula
        )

        remaining_hp_percentage = (
            remaining_hp / sum(current_team.get_hps())
            if sum(current_team.get_hps()) > 0
            else 0.0
        )

        opponent_data = Opponent(
            original_opponent_team_setup,
            remaining_hp_percentage,
        )

        best_opponents.append(opponent_data)

    return best_opponents.get_opponents()


def find_best_opponent_team_from_random(
    pokemons: DataFrame[PokemonSchema],
    current_team: PokemonTeam,
    type_multiplier_formula: Callable[[float, float], float],
    damage_formula: Callable[[int, int, float], int],
    unique_types: bool = True,
    opponents_limit: int | None = None,
    results_amount: int = 1,
) -> tuple[Opponent, ...]:
    rng = np.random.default_rng()

    opponents = current_team.generate_opponents(pokemons, unique_types, opponents_limit)

    best_opponents = BestOpponentsList(results_amount)

    chosen_opponents_indexes = rng.choice(
        len(opponents), size=min(results_amount, len(opponents)), replace=False
    )

    chosen_opponents = [opponents[i] for i in chosen_opponents_indexes]

    for opponent in chosen_opponents:
        original_opponent_team_setup, remaining_hp = simulate_battle(
            current_team,
            opponent,
            type_multiplier_formula,
            damage_formula,
        )

        remaining_hp_percentage = (
            remaining_hp / sum(current_team.get_hps())
            if sum(current_team.get_hps()) > 0
            else 0.0
        )

        opponent_data = Opponent(
            original_opponent_team_setup,
            remaining_hp_percentage,
        )

        best_opponents.append(opponent_data)

    return best_opponents.get_opponents()


def evaluate_team(opponent: Opponent) -> int:
    return 0 if opponent.remaining_hp_percentage > 0 else opponent.team.get_stats()
