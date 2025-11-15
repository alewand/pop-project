import pandas as pd
from typing import Callable
from constants.constants import (
    AGAINST_COL,
    ATTACK_COL,
    DEFENSE_COL,
    FIRST_TYPE_COL,
    HP_COL,
    SECOND_TYPE_COL,
    SPECIAL_ATTACK_COL,
    SPECIAL_DEFENSE_COL,
    SPEED_COL,
    TEAM_SIZE,
    CURRENT,
    OPPONENT,
)


def get_first_attacker(
    current_team: pd.DataFrame,
    opponent_team: pd.DataFrame
) -> str:
    first_current_pokemon_speed = current_team.iloc[0][SPEED_COL]
    first_opponent_pokemon_speed = opponent_team.iloc[0][SPEED_COL]

    return (
        CURRENT if first_current_pokemon_speed > first_opponent_pokemon_speed
        else OPPONENT
    )


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
    current_team: pd.DataFrame,
    opponent_team: pd.DataFrame,
    type_multiplier_formula: Callable[[float, float], float],
    damage_formula: Callable[[int, int, float], int],
    team_size: int = TEAM_SIZE
):
    if len(current_team) != team_size or len(opponent_team) != team_size:
        raise ValueError("Both teams must have equal, specified team size.")

    current_team_hp = current_team[HP_COL].astype(int).to_list()
    opponent_team_hp = opponent_team[HP_COL].astype(int).to_list()

    current_pokemon_index = 0
    opponent_pokemon_index = 0

    turn = get_first_attacker(current_team, opponent_team)

    while (current_pokemon_index < team_size and
           opponent_pokemon_index < team_size):

        if turn == CURRENT:
            attacker = current_team.iloc[current_pokemon_index]
            defender = opponent_team.iloc[opponent_pokemon_index]

            damage = calculate_damage(attacker, defender,
                                      type_multiplier_formula,
                                      damage_formula)
            if (opponent_team_hp[opponent_pokemon_index] - damage) <= 0:
                opponent_team_hp[opponent_pokemon_index] = 0
                opponent_pokemon_index += 1
            else:
                opponent_team_hp[opponent_pokemon_index] -= damage

            if opponent_pokemon_index >= team_size:
                break

            turn = OPPONENT

        else:
            attacker = opponent_team.iloc[opponent_pokemon_index]
            defender = current_team.iloc[current_pokemon_index]

            damage = calculate_damage(attacker, defender,
                                      type_multiplier_formula,
                                      damage_formula)
            if (current_team_hp[current_pokemon_index] - damage) <= 0:
                current_team_hp[current_pokemon_index] = 0
                current_pokemon_index += 1
            else:
                current_team_hp[current_pokemon_index] -= damage

            if current_pokemon_index >= team_size:
                break

            turn = CURRENT

    return (turn,
            sum(current_team_hp),
            sum(opponent_team_hp),
            current_pokemon_index,
            opponent_pokemon_index)
