from algorithms.evaluation import (
    find_the_best_opponent_team,
    get_sum_of_team_stats
)
from battle.battle import simulate_battle
from battle.battle_formulas import (
    damage_attack_minus_defense,
    multiply_type_multiplier
)
from data.data import get_pokemons_data
from data.generators import (
    generate_start_team,
    generate_team_with_random_replacement,
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
    print(f"Stats sum: {get_sum_of_team_stats(current_team)}")
    best_opponents, total_opponents = find_the_best_opponent_team(
        pokemons,
        current_team,
        multiply_type_multiplier,
        damage_attack_minus_defense,
        True,
        results_amount=1,
    )
    for i, opponent in enumerate(best_opponents, start=1):
        print(f"Opponent Team {i}:")
        print(opponent.team[[NAME_COL, FIRST_TYPE_COL, SECOND_TYPE_COL]])
        print(
            f"Average Remaining HP: {opponent.average_remaining_hp} "
            f"({opponent.percentage_remaining_hp*100:.2f}%)"
        )
        print(f"Stats Sum: {opponent.stats_sum}")
    print(f"Total Opponents Evaluated: {total_opponents}")
    current_team = generate_team_with_random_replacement(
        pokemons,
        current_team,
    )
    print("New Current Team after Replacement:")
    print(current_team[[NAME_COL, FIRST_TYPE_COL, SECOND_TYPE_COL]])
    print(f"Stats sum: {get_sum_of_team_stats(current_team)}")
    opponent, remaining_hp, original_hp = simulate_battle(
        current_team,
        best_opponents[0].team,
        multiply_type_multiplier,
        damage_attack_minus_defense,
    )
    print("Battle Result:")
    print("Opponent Team:")
    print(opponent[[NAME_COL, FIRST_TYPE_COL, SECOND_TYPE_COL]])
    print(
        f"Current Team Remaining HP: {remaining_hp} "
        f"out of {original_hp} "
    )
