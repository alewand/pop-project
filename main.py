from algorithms.evaluation import (
    evaluate_team,
    find_the_best_opponent_team,
)
from battle.battle_formulas import (
    damage_attack_minus_defense,
    multiply_type_multiplier
)
from data.data import get_pokemons
from structures.team import PokemonTeam


if __name__ == "__main__":
    pokemons = get_pokemons()
    current_team = PokemonTeam.generate(pokemons)
    print("CURRENT TEAM:")
    current_team.print()
    print(f"STATS SUM: {current_team.stats}")
    best_opponents, total_opponents = find_the_best_opponent_team(
        pokemons,
        current_team,
        multiply_type_multiplier,
        damage_attack_minus_defense,
        True,
        results_amount=10,
    )
    for i, opponent in enumerate(best_opponents, start=1):
        print(f"OPPONENT TEAM {i}:")
        opponent.team.print()
        print(
            f"REMAINING HP: {opponent.remaining_hp_percentage*100:.2f}"
        )
        print(f"STATS SUM: {opponent.team.stats}")
        print(f"EVALUATION: {evaluate_team(opponent)}")
    print(f"TOTAL OPPONENTS: {total_opponents}")
