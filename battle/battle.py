import pandas as pd
from typing import Callable, Tuple
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


def who_is_first(
    current_pokemon: pd.Series,
    opponent_pokemon: pd.Series
) -> str:
    return (
        CURRENT if current_pokemon[SPEED_COL] > opponent_pokemon[SPEED_COL]
        else OPPONENT
    )


def swap_to_next_alive(
        team: pd.DataFrame,
        team_hp: list[int],
        current_index: int) -> Tuple[bool, pd.DataFrame, list[int]]:

    team_size = len(team)

    for i in range(current_index + 1, team_size):
        if team_hp[i] > 0:
            (team_hp[current_index],
                team_hp[i]) = (team_hp[i], team_hp[current_index])
            current_pokemon = team.iloc[current_index].copy()
            pokemon_to_swap = team.iloc[i].copy()
            team.iloc[current_index] = pokemon_to_swap
            team.iloc[i] = current_pokemon
            # print(f"{current_pokemon['name']} is swapped out for {pokemon_to_swap['name']}!")

            return True, team, team_hp

    return False, team, team_hp


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

    original_current_team_setup = current_team.copy()
    original_opponent_team_setup = opponent_team.copy()

    current_team_hp = current_team[HP_COL].astype(int).to_list()
    opponent_team_hp = opponent_team[HP_COL].astype(int).to_list()

    current_pokemon_index = 0
    opponent_pokemon_index = 0

    turn = who_is_first(current_team.iloc[current_pokemon_index],
                        opponent_team.iloc[opponent_pokemon_index])

    while (sum(current_team_hp) > 0 and sum(opponent_team_hp) > 0):

        if turn == CURRENT:
            attacker = current_team.iloc[current_pokemon_index]
            defender = opponent_team.iloc[opponent_pokemon_index]

            damage = calculate_damage(attacker, defender,
                                      type_multiplier_formula,
                                      damage_formula)
            if damage == 0:
                # print(f"{defender['name']} is immune to {attacker['name']}'s attacks!")
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
                # print(f"{attacker['name']} deals {damage} damage to {defender['name']}!")
                opponent_team_hp[opponent_pokemon_index] -= damage
                turn = OPPONENT
                continue

            opponent_team_hp[opponent_pokemon_index] = 0

            if opponent_pokemon_index + 1 < team_size:
                # print(f"{defender['name']} has fainted!")
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
                # print(f"{defender['name']} is immune to {attacker['name']}'s attacks!")
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
                # print(f"{attacker['name']} deals {damage} damage to {defender['name']}!")
                current_team_hp[current_pokemon_index] -= damage
                turn = CURRENT
                continue

            current_team_hp[current_pokemon_index] = 0

            if current_pokemon_index + 1 < team_size:
                # print(f"{defender['name']} has fainted!")
                current_pokemon_index += 1
                turn = who_is_first(
                    current_team.iloc[current_pokemon_index],
                    opponent_team.iloc[opponent_pokemon_index]
                )

    return (turn,
            original_current_team_setup,
            original_opponent_team_setup)
