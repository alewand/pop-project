from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from pandera.typing import DataFrame

from classes.pokemon_team import PokemonTeam
from constants import EXPERIMENTS_IMAGES_DIR
from data import get_pokemons
from schemas import PokemonSchema
from solvers import SimulatedAnnealingPokemonSolver, HillClimbingPokemonSolver, RandomSearchPokemonSolver


def run_multiple_runs(
    pokemons: DataFrame[PokemonSchema],
    solver: SimulatedAnnealingPokemonSolver,
    runs: int = 8,
) -> None:
    print(f"Running {runs} runs of the SA solver...")

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


def compare_to_random_search(
    pokemons: DataFrame[PokemonSchema],
    solver: SimulatedAnnealingPokemonSolver,
    baseline_solver: RandomSearchPokemonSolver,
    opponents: list[PokemonTeam] = None,
    runs: int = 8,
) -> None:
    print("Comparing SA solver to Random Search solver...")
    sa_model_results: list[tuple[PokemonTeam, float]] = []
    rs_model_results: list[tuple[PokemonTeam, float]] = []

    for i in range(runs):
        print(f"Run {i + 1}/{runs}")
        sa_best_team, sa_best_fitness, _, _ = solver.solve(pokemons, opponents=opponents)
        print(f"SA Best fitness: {sa_best_fitness}")
        rs_best_team, rs_best_fitness, _, _ = baseline_solver.solve(pokemons, opponents=opponents)
        print(f"RS Best fitness: {rs_best_fitness}")

        sa_model_results.append((sa_best_team, sa_best_fitness))
        rs_model_results.append((rs_best_team, rs_best_fitness))

    sa_fitnesses = np.array([fit for _, fit in sa_model_results], dtype=float)
    rs_fitnesses = np.array([fit for _, fit in rs_model_results], dtype=float)
    sa_mean_fitness = float(np.mean(sa_fitnesses))
    rs_mean_fitness = float(np.mean(rs_fitnesses))
    sa_std_fitness = float(np.std(sa_fitnesses))
    rs_std_fitness = float(np.std(rs_fitnesses))
    sa_wins = np.sum(sa_fitnesses > rs_fitnesses)
    rs_wins = np.sum(rs_fitnesses > sa_fitnesses)
    draws = runs - sa_wins - rs_wins


    best_sa_team, best_sa_fitness = sa_model_results[int(np.argmax(sa_fitnesses))]
    best_rs_team, best_rs_fitness = rs_model_results[int(np.argmax(rs_fitnesses))]

    print("Comparison summary:")
    print(f"SA Mean fitness: {sa_mean_fitness:.6f} ± {sa_std_fitness:.6f}")
    print(f"RS Mean fitness: {rs_mean_fitness:.6f} ± {rs_std_fitness:.6f}")
    print(f"SA wins: {sa_wins}, RS wins: {rs_wins   }, Draws: {draws}")

    print("Best SA team:")
    print(f"Team: {best_sa_team}", f"Fitness: {best_sa_fitness}, Stats sum: {best_sa_team.get_stats_sum()}")

    print("Best RS team:")
    print(f"Team: {best_rs_team}", f"Fitness: {best_rs_fitness}, Stats sum: {best_rs_team.get_stats_sum()}")



def compare_to_hill_climb(
    pokemons: DataFrame[PokemonSchema],
    solver: SimulatedAnnealingPokemonSolver,
    baseline_solver: HillClimbingPokemonSolver,
    opponents: list[PokemonTeam] = None,
    runs: int = 8,
) -> None:
    print("Comparing SA solver to Hill Climbing solver..."
)

    sa_model_results: list[tuple[PokemonTeam, float]] = []
    hc_model_results: list[tuple[PokemonTeam, float]] = []

    for i in range(runs):
        starting_team = PokemonTeam.generate_team(pokemons, team_size=TEAM_SIZE, unique_types=True)
        print(f"Run {i + 1}/{runs}")
        sa_best_team, sa_best_fitness, _, _ = solver.solve(pokemons, opponents=opponents, start_team=starting_team)
        print(f"SA Best fitness: {sa_best_fitness}")
        hc_best_team, hc_best_fitness, _, _ = baseline_solver.solve(pokemons, opponents=opponents, start_team=starting_team)
        print(f"HC Best fitness: {hc_best_fitness}")

        sa_model_results.append((sa_best_team, sa_best_fitness))
        hc_model_results.append((hc_best_team, hc_best_fitness))

    sa_fitnesses = np.array([fit for _, fit in sa_model_results], dtype=float)
    hc_fitnesses = np.array([fit for _, fit in hc_model_results], dtype=float)
    sa_mean_fitness = float(np.mean(sa_fitnesses))
    hc_mean_fitness = float(np.mean(hc_fitnesses))
    sa_std_fitness = float(np.std(sa_fitnesses))
    hc_std_fitness = float(np.std(hc_fitnesses))
    sa_wins = np.sum(sa_fitnesses > hc_fitnesses)
    hc_wins = np.sum(hc_fitnesses > sa_fitnesses)
    draws = runs - sa_wins - hc_wins

    print("Comparison summary:")
    print(f"SA Mean fitness: {sa_mean_fitness:.6f} ± {sa_std_fitness:.6f}")
    print(f"HC Mean fitness: {hc_mean_fitness:.6f} ± {hc_std_fitness:.6f}")
    print(f"SA wins: {sa_wins}, HC wins: {hc_wins}, Draws: {draws}")

    best_sa_team, best_sa_fitness = sa_model_results[int(np.argmax(sa_fitnesses))]
    best_hc_team, best_hc_fitness = hc_model_results[int(np.argmax(hc_fitnesses))]

    print("Best SA team:")
    print(f"Team: {best_sa_team}", f"Fitness: {best_sa_fitness}, Stats sum: {best_sa_team.get_stats_sum()}")
    print("Best HC team:")
    print(f"Team: {best_hc_team}", f"Fitness: {best_hc_fitness}, Stats sum: {best_hc_team.get_stats_sum()}")


def perform_sa_experiments() -> None:
    pokemons = get_pokemons()

    sa_solver = SimulatedAnnealingPokemonSolver()
    hc_solver = HillClimbingPokemonSolver()
    rs_solver = RandomSearchPokemonSolver()

    opponents_limit = 20

    opponents = PokemonTeam.generate_unique_teams(
        pokemons,
        opponents_limit=opponents_limit,
        max_attempts=opponents_limit * 3,
        team_size=6,
        unique_types=True,
        )

    run_multiple_runs(
        pokemons,
        sa_solver,
        runs=8,
    )

    compare_to_random_search(
        pokemons,
        sa_solver,
        rs_solver,
        opponents=opponents,
        runs=8,
    )

    compare_to_hill_climb(
        pokemons,
        sa_solver,
        hc_solver,
        opponents=opponents,
        runs=8,
    )
