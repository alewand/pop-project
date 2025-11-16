from algorithms.evaluation import find_the_best_opponent_team
from battle.battle_formulas import (
    damage_attack_minus_defense,
    multiply_type_multiplier)
from data.data import get_pokemons_data
from data.generators import (
    generate_start_team,
)

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
    best_opponents = find_the_best_opponent_team(
        pokemons,
        current_team,
        multiply_type_multiplier,
        damage_attack_minus_defense,
        True,
        2,
    )
    print("Best Opponent Team:")
    print(best_opponents[0].team[[NAME_COL, FIRST_TYPE_COL, SECOND_TYPE_COL]])
    print(
        f"Average Remaining HP: {best_opponents[0].average_remaining_hp} "
        f"({best_opponents[0].percentage_remaining_hp*100:.2f}%)"
    )
