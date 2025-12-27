import numpy as np
from pandera.typing import DataFrame

from classes.pokemon_team import PokemonTeam
from data import get_pokemons
from schemas import PokemonSchema
from solvers.evolution_algorithm_solver import EvolutionaryAlgorithmPokemonSolver


def compare_to_naive_solver(
    pokemons: DataFrame[PokemonSchema],
    solver: EvolutionaryAlgorithmPokemonSolver,
    runs: int = 8,
) -> None:
    naive_model_results: list[tuple[PokemonTeam, float]] = []
    ea_model_results: list[tuple[PokemonTeam, float]] = []

    for _ in range(runs):
        best_team, best_finess, _, opponents = solver.solve(pokemons)
        print(best_team)
        print(best_finess)
        print(best_team.get_stats_sum())
        ea_model_results.append((best_team, best_finess))

        naive_team = PokemonTeam.generate_team(pokemons)
        naive_team_fitness = solver._evaluate(naive_team, opponents)
        print(naive_team)
        print(naive_team_fitness)
        print(naive_team.get_stats_sum())
        naive_model_results.append((naive_team, naive_team_fitness))

    naive_fitnesses = np.array([fitness for _, fitness in naive_model_results])
    ea_fitnesses = np.array([fitness for _, fitness in ea_model_results])

    naive_best_index = int(np.argmax(naive_fitnesses))
    ea_best_index = int(np.argmax(ea_fitnesses))

    naive_best_team, naive_best_fitness = naive_model_results[naive_best_index]
    ea_best_team, ea_best_fitness = ea_model_results[ea_best_index]

    print("Naive Solver:")
    print(f"Mean fitness: {float(np.mean(naive_fitnesses)):.6f}")
    print(f"Median fitness: {float(np.median(naive_fitnesses)):.6f}")
    print(f"Std fitness: {float(np.std(naive_fitnesses)):.6f}")
    print(f"Best fitness: {naive_best_fitness:.6f}")
    print(f"Best team: {naive_best_team}")
    print(f"Best team stats sum: {naive_best_team.get_stats_sum()}")

    print("Evolutionary Algorithm Solver:")
    print(f"Mean fitness: {float(np.mean(ea_fitnesses)):.6f}")
    print(f"Median fitness: {float(np.median(ea_fitnesses)):.6f}")
    print(f"Std fitness: {float(np.std(ea_fitnesses)):.6f}")
    print(f"Best fitness: {ea_best_fitness:.6f}")
    print(f"Best team: {ea_best_team}")
    print(f"Best team stats sum: {ea_best_team.get_stats_sum()}")


def perform_ea_experiments():
    pokemons = get_pokemons()

    solver = EvolutionaryAlgorithmPokemonSolver()

    compare_to_naive_solver(pokemons, solver)
