from collections.abc import Callable
from typing import Literal

import pandas as pd

from classes import PokemonTeam
from constants import (
    AGAINST,
    ATTACK,
    DEFENSE,
    FIRST_TYPE,
    MAX_STEPS_PER_BATTLE,
    SECOND_TYPE,
    SPECIAL_ATTACK,
    SPECIAL_DEFENSE,
    SPEED,
)

from .formulas import DamageFormula, TypeMultiplierFormula

type Turn = Literal["current", "opponent"]


def simulate_battle(
    current_team: PokemonTeam,
    opponent_team: PokemonTeam,
    type_multiplier_formula: TypeMultiplierFormula,
    damage_formula: DamageFormula,
    max_steps: int = MAX_STEPS_PER_BATTLE,
) -> int:
    current_team_battle = current_team.copy()
    opponent_team_battle = opponent_team.copy()

    current_team_hp = current_team_battle.get_hps()
    opponent_team_hp = opponent_team_battle.get_hps()
    current_pokemon_index = 0
    opponent_pokemon_index = 0

    turn = get_first_attacker(
        current_team_battle,
        opponent_team_battle,
        current_pokemon_index,
        opponent_pokemon_index,
    )

    steps = 0

    while sum(current_team_hp) > 0 and sum(opponent_team_hp) > 0 and steps < max_steps:
        steps += 1

        if turn == "current":
            attacker = current_team_battle.members.iloc[current_pokemon_index]
            defender = opponent_team_battle.members.iloc[opponent_pokemon_index]

            damage = calculate_damage(
                attacker,
                defender,
                type_multiplier_formula,
                damage_formula,
            )

            if damage == 0:
                swapped, current_team_battle, current_team_hp = swap_to_next_alive(
                    current_team_battle, current_team_hp, current_pokemon_index
                )

                turn = "opponent"

                if not swapped:
                    break

                continue

            if opponent_team_hp[opponent_pokemon_index] - damage > 0:
                opponent_team_hp[opponent_pokemon_index] -= damage
                turn = "opponent"
                continue

            opponent_team_hp[opponent_pokemon_index] = 0
            if opponent_pokemon_index + 1 < opponent_team_battle.get_size():
                opponent_pokemon_index += 1
                turn = get_first_attacker(
                    current_team_battle,
                    opponent_team_battle,
                    current_pokemon_index,
                    opponent_pokemon_index,
                )

        else:
            attacker = opponent_team_battle.members.iloc[opponent_pokemon_index]
            defender = current_team_battle.members.iloc[current_pokemon_index]

            damage = calculate_damage(
                attacker,
                defender,
                type_multiplier_formula,
                damage_formula,
            )

            if damage == 0:
                swapped, opponent_team_battle, opponent_team_hp = swap_to_next_alive(
                    opponent_team_battle, opponent_team_hp, opponent_pokemon_index
                )

                turn = "current"

                if not swapped:
                    break

                continue

            if current_team_hp[current_pokemon_index] - damage > 0:
                current_team_hp[current_pokemon_index] -= damage
                turn = "current"
                continue

            current_team_hp[current_pokemon_index] = 0
            if current_pokemon_index + 1 < current_team_battle.get_size():
                current_pokemon_index += 1
                turn = get_first_attacker(
                    current_team_battle,
                    opponent_team_battle,
                    current_pokemon_index,
                    opponent_pokemon_index,
                )

    final_current_team_hp = sum(current_team_hp)

    if final_current_team_hp > 0 and turn == "opponent":
        final_current_team_hp = 0

    if final_current_team_hp <= sum(opponent_team_hp) and steps >= max_steps:
        final_current_team_hp = 0

    return final_current_team_hp


def calculate_damage(
    attacker: pd.Series,
    defender: pd.Series,
    type_multiplier_formula: Callable[[float, float], float],
    damage_formula: Callable[[int, int, float], int],
) -> int:
    combined_attack: int = attacker[ATTACK] + attacker[SPECIAL_ATTACK]
    combined_defense: int = defender[DEFENSE] + defender[SPECIAL_DEFENSE]

    firstEffectivness: float = attacker[f"{AGAINST}{defender[FIRST_TYPE]}"]

    secondEffectivness: float = (
        attacker[f"{AGAINST}{defender[SECOND_TYPE]}"]
        if pd.notna(defender[SECOND_TYPE])
        else 1.0
    )

    type_multiplier = type_multiplier_formula(firstEffectivness, secondEffectivness)

    if type_multiplier == 0:
        return 0

    damage = damage_formula(combined_attack, combined_defense, type_multiplier)

    return max(damage, 1)


def get_first_attacker(
    current_team: PokemonTeam,
    opponent_team: PokemonTeam,
    current_pokemon_index: int,
    opponent_pokemon_index: int,
) -> Turn:
    current_speed = int(current_team.members.iloc[current_pokemon_index][SPEED])
    opponent_speed = int(opponent_team.members.iloc[opponent_pokemon_index][SPEED])

    return "current" if current_speed > opponent_speed else "opponent"


def swap_to_next_alive(
    team: PokemonTeam, team_hp: list[int], current_index: int
) -> tuple[bool, PokemonTeam, list[int]]:
    for i in range(current_index + 1, team.get_size()):
        if team_hp[i] > 0:
            (team_hp[current_index], team_hp[i]) = (team_hp[i], team_hp[current_index])

            team.swap_members(current_index, i)

            return True, team, team_hp

    return False, team, team_hp
