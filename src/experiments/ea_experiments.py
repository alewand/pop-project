from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from pandera.typing import DataFrame

from classes.pokemon_team import PokemonTeam
from constants import EXPERIMENTS_IMAGES_DIR
from data import get_pokemons
from schemas import PokemonSchema
from solvers import EvolutionaryAlgorithmPokemonSolver


def run_multiple_runs(
    pokemons: DataFrame[PokemonSchema],
    solver: EvolutionaryAlgorithmPokemonSolver,
    runs: int = 8,
) -> None:
    print(f"Running {runs} runs of the EA solver...")

    best_teams: list[PokemonTeam] = []
    best_fitnesses: list[float] = []

    for i in range(runs):
        print(f"Run {i + 1}/{runs}")
        best_team, best_fitness, _, _ = solver.solve(pokemons)
        print(f"Best team: {best_team}")
        print(f"Best fitness: {best_fitness}")
        print(f"Best team stats sum: {best_team.get_stats_sum()}")

        best_teams.append(best_team)
        best_fitnesses.append(best_fitness)

    fitness_array = np.array(best_fitnesses, dtype=float)
    mean_fitness = float(np.mean(fitness_array))
    median_fitness = float(np.median(fitness_array))
    std_fitness = float(np.std(fitness_array))
    best_fitness_index = int(np.argmax(fitness_array))
    best_team = best_teams[best_fitness_index]
    best_fitness = best_fitnesses[best_fitness_index]

    print("Summary of multiple runs:")
    print(f"Mean fitness: {mean_fitness:.6f}")
    print(f"Median fitness: {median_fitness:.6f}")
    print(f"Std fitness: {std_fitness:.6f}")
    print(f"Best fitness: {best_fitness:.6f}")
    print(f"Best team: {best_team}")
    print(f"Best team stats sum: {best_team.get_stats_sum()}")


def create_ea_plot(
    pokemons: DataFrame[PokemonSchema], solver: EvolutionaryAlgorithmPokemonSolver
) -> None:
    print("Creating EA fitness over generations plot...")
    best_team, best_fitness, history, _ = solver.solve(pokemons)

    for generation_index, generation in enumerate(history):
        fitnesses = [fitness for _, fitness in generation]
        plt.scatter(
            [generation_index + 1] * len(fitnesses), fitnesses, color="blue", alpha=0.5
        )

    rng = np.random.default_rng()

    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.title("Evolutionary Algorithm Fitness over Generations")
    plt.ylim(0, 1)
    plt.tight_layout()

    plot_name = f"ea_fitness_over_generations_{rng.integers(1_000_000)}.png"

    Path(EXPERIMENTS_IMAGES_DIR).mkdir(parents=True, exist_ok=True)

    plt.savefig(EXPERIMENTS_IMAGES_DIR / plot_name)
    plt.close()

    print(f"Plot saved as {plot_name}")
    print(f"Best team: {best_team}")
    print(f"Best fitness: {best_fitness}")
    print(f"Best team stats sum: {best_team.get_stats_sum()}")

    print("First generation (initial population)")
    for team, fitness in history[0]:
        print(f"Team: {team}, Fitness: {fitness:.6f} Stats sum: {team.get_stats_sum()}")

    print("Last generation")
    for team, fitness in history[-1]:
        print(f"Team: {team}, Fitness: {fitness:.6f} Stats sum: {team.get_stats_sum()}")


def compare_to_naive_solver(
    pokemons: DataFrame[PokemonSchema],
    solver: EvolutionaryAlgorithmPokemonSolver,
    runs: int = 8,
) -> None:
    print("Comparing EA solver to Naive solver...")
    naive_model_results: list[tuple[PokemonTeam, float]] = []
    ea_model_results: list[tuple[PokemonTeam, float]] = []

    for i in range(runs):
        print(f"Run {i + 1}/{runs}")
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
    # solver.elite_size = 0
    solver.generations = 30

    run_multiple_runs(pokemons, solver, runs=4)

    # compare_to_naive_solver(pokemons, solver)
    # create_ea_plot(pokemons, solver)
