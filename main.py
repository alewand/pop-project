from battle.battle_formulas import (
    damage_attack_minus_defense,
    multiply_type_multiplier)
from data.data import get_pokemons_data
from data.generators import generate_start_team
from battle.battle import simulate_battle
from constants.constants import (
    NAME_COL,
    FIRST_TYPE_COL,
    SECOND_TYPE_COL,
)


if __name__ == "__main__":
    pokemons = get_pokemons_data()
    current_team = generate_start_team(pokemons)
    print("Current Team:")
    print(current_team[[NAME_COL, FIRST_TYPE_COL, SECOND_TYPE_COL]])
    opponent_team = generate_start_team(pokemons)
    print("Opponent Team:")
    print(opponent_team[[NAME_COL, FIRST_TYPE_COL, SECOND_TYPE_COL]])
    result, _, _ = simulate_battle(
        current_team, opponent_team,
        multiply_type_multiplier, damage_attack_minus_defense)
    print("Battle Result:")
    print(result)
