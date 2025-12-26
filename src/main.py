from data import get_pokemons
from simulation import damage_attack_devide_defense, multiply_type_multiplier
from solvers import EvolutionAlgorithmPokemonSolver

if __name__ == "__main__":
    pokemons = get_pokemons()
    solver = EvolutionAlgorithmPokemonSolver(
        population_size=5,
        elite_size=1,
        generations=20,
        mutation_rate=0.6,
        opponents_limit=100,
    )
    best_team, best_fitness, history = solver.solve(
        pokemons,
        multiply_type_multiplier,
        damage_attack_devide_defense,
    )

    print("Best team found:")
    print(best_team)
    print(f"Best fitness: {best_fitness}")
