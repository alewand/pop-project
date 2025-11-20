import pandas as pd
from typing import Callable, Tuple
from battle.helpers import (
    who_is_first,
    swap_to_next_alive,
)
from constants.constants import (
    AGAINST_COL,
    ATTACK_COL,
    DEFENSE_COL,
    FIRST_TYPE_COL,
    SECOND_TYPE_COL,
    SPECIAL_ATTACK_COL,
    SPECIAL_DEFENSE_COL,
    TEAM_SIZE,
    CURRENT,
    OPPONENT,
)
from structures.team import PokemonTeam


def calculate_damage(
        attacker: pd.Series,
        defender: pd.Series,
        type_multiplier_formula: Callable[[float, float], float],
        damage_formula: Callable[[int, int, float], int]) -> int:
    combined_attack: int = attacker[ATTACK_COL] + attacker[SPECIAL_ATTACK_COL]
    combined_defense: int = (
        defender[DEFENSE_COL] + defender[SPECIAL_DEFENSE_COL]
    )

    firstEffectivness: float = (
        defender[f"{AGAINST_COL}{attacker[FIRST_TYPE_COL]}"]
    )

    secondEffectivness: float = (
        defender[f"{AGAINST_COL}{attacker[SECOND_TYPE_COL]}"]
        if pd.notna(attacker[SECOND_TYPE_COL]) else 1.0
    )

    type_multiplier = type_multiplier_formula(
        firstEffectivness, secondEffectivness
    )

    if type_multiplier == 0:
        return 0

    damage = damage_formula(
        combined_attack, combined_defense, type_multiplier
    )

    return max(damage, 1)


def simulate_battle(
    current_team: PokemonTeam,
    opponent_team: PokemonTeam,
    type_multiplier_formula: Callable[[float, float], float],
    damage_formula: Callable[[int, int, float], int],
    team_size: int = TEAM_SIZE
) -> Tuple[PokemonTeam, int]:
    if current_team.size != team_size or opponent_team.size != team_size:
        raise ValueError("Both teams must have equal, specified team size.")

    original_opponent_team_setup = opponent_team.copy()

    current_team_hp = current_team.hps
    opponent_team_hp = opponent_team.hps
    current_pokemon_index = 0
    opponent_pokemon_index = 0

    turn = who_is_first(
        current_team.iloc[current_pokemon_index],
        opponent_team.iloc[opponent_pokemon_index]
    )

    while (sum(current_team_hp) > 0 and
            sum(opponent_team_hp) > 0):

        if turn == CURRENT:
            attacker = current_team.iloc[current_pokemon_index]
            defender = opponent_team.iloc[opponent_pokemon_index]

            damage = calculate_damage(attacker, defender,
                                      type_multiplier_formula,
                                      damage_formula)
            if damage == 0:
                swapped, current_team, current_team_hp = swap_to_next_alive(
                    current_team,
                    current_team_hp,
                    current_pokemon_index
                )

                turn = OPPONENT

                if not swapped:
                    break

                continue

            if (opponent_team_hp[opponent_pokemon_index] - damage > 0):
                opponent_team_hp[opponent_pokemon_index] -= damage
                turn = OPPONENT
                continue

            opponent_team_hp[opponent_pokemon_index] = 0
            if opponent_pokemon_index + 1 < team_size:
                opponent_pokemon_index += 1
                turn = who_is_first(
                    current_team.iloc[current_pokemon_index],
                    opponent_team.iloc[opponent_pokemon_index]
                )

        else:
            attacker = opponent_team.iloc[opponent_pokemon_index]
            defender = current_team.iloc[current_pokemon_index]

            damage = calculate_damage(attacker, defender,
                                      type_multiplier_formula,
                                      damage_formula)
            if damage == 0:
                swapped, opponent_team, opponent_team_hp = swap_to_next_alive(
                    opponent_team,
                    opponent_team_hp,
                    opponent_pokemon_index
                )

                turn = CURRENT

                if not swapped:
                    break

                continue

            if (current_team_hp[current_pokemon_index] - damage > 0):
                current_team_hp[current_pokemon_index] -= damage
                turn = CURRENT
                continue

            current_team_hp[current_pokemon_index] = 0
            if current_pokemon_index + 1 < team_size:
                current_pokemon_index += 1
                turn = who_is_first(
                    current_team.iloc[current_pokemon_index],
                    opponent_team.iloc[opponent_pokemon_index]
                )

    return original_opponent_team_setup, sum(current_team_hp)
