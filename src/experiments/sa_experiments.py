from pathlib import Path
from pandera.typing import DataFrame
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pandera.typing import DataFrame
from classes import PokemonTeam
from constants import EXPERIMENTS_IMAGES_DIR
from data import get_pokemons
from schemas import PokemonSchema
from solvers import (
    SimulatedAnnealingPokemonSolver,
    HillClimbingPokemonSolver,
    RandomSearchPokemonSolver,
)


def run_multiple_runs(
    pokemons: DataFrame[PokemonSchema],
    solver: SimulatedAnnealingPokemonSolver,
    opponents: list[PokemonTeam] = None,
    runs: int = 8,
) -> None:
    print(f"Running {runs} runs of the SA solver...")

    rows = []

    for i in range(runs):
        best_team, best_fitness, history, used_opponents = solver.solve(pokemons, opponents=opponents)
        names = best_team.members['name'].tolist()

        rows.append({
            "run": i,
            "solver": "SA",
            "fitness": round(float(best_fitness), 4),
            "stats_sum": int(best_team.get_stats_sum()),
            "pokemons": "|".join(names),
        })

        if opponents is None:
            opponents = used_opponents

    return pd.DataFrame(rows)


def compare_to_random_search(
    pokemons: DataFrame[PokemonSchema],
    solver: SimulatedAnnealingPokemonSolver,
    baseline_solver: RandomSearchPokemonSolver,
    opponents: list[PokemonTeam] = None,
    runs: int = 8,
) -> None:
    print("Comparing SA solver to Random Search solver...")
    rows = []
    for i in range(runs):
        starting_team = PokemonTeam.generate_team(
            pokemons, team_size=6, unique_types=True
        )

        sa_team, sa_fit, sa_hist, _ = solver.solve(pokemons, opponents=opponents, start_team=starting_team)
        rs_team, rs_fit, rs_hist, _ = baseline_solver.solve(pokemons, opponents=opponents)

        sa_names = sa_team.members['name'].tolist()
        rs_names = rs_team.members['name'].tolist()

        rows.extend([
            {
                "run": i,
                "solver": "SA",
                "fitness": round(float(sa_fit), 4),
                "stats_sum": int(sa_team.get_stats_sum()),
                "pokemons": "|".join(sa_names),
            },
            {
                "run": i,
                "solver": "RS",
                "fitness": round(float(rs_fit), 4),
                "stats_sum": int(rs_team.get_stats_sum()),
                "pokemons": "|".join(rs_names),
            },
        ])

    df = pd.DataFrame(rows)

    pivot = df.pivot(index="run", columns="solver", values="fitness")
    df_winner = pivot.apply(lambda r: "SA" if r["SA"] > r["RS"] else ("RS" if r["RS"] > r["SA"] else "DRAW"), axis=1)
    df = df.merge(df_winner.rename("winner").reset_index(), on="run", how="left")

    return df


def compare_to_hill_climb(
    pokemons: DataFrame[PokemonSchema],
    solver: SimulatedAnnealingPokemonSolver,
    baseline_solver: HillClimbingPokemonSolver,
    opponents: list[PokemonTeam] = None,
    runs: int = 8,
) -> None:
    print("Comparing SA solver to Hill Climbing solver...")
    rows = []
    for i in range(runs):
        starting_team = PokemonTeam.generate_team(
            pokemons, team_size=6, unique_types=True
        )

        sa_team, sa_fit, sa_hist, _ = solver.solve(pokemons, opponents=opponents, start_team=starting_team)
        hc_team, hc_fit, hc_hist, _ = baseline_solver.solve(pokemons, opponents=opponents, start_team=starting_team)

        sa_names = sa_team.members['name'].tolist()
        hc_names = hc_team.members['name'].tolist()

        rows.extend([
            {
                "run": i,
                "solver": "SA",
                "fitness": round(float(sa_fit), 4),
                "stats_sum": int(sa_team.get_stats_sum()),
                "pokemons": "|".join(sa_names),
            },
            {
                "run": i,
                "solver": "HC",
                "fitness": round(float(hc_fit), 4),
                "stats_sum": int(hc_team.get_stats_sum()),
                "pokemons": "|".join(hc_names),
            },
        ])

    df = pd.DataFrame(rows)

    pivot = df.pivot(index="run", columns="solver", values="fitness")
    df_winner = pivot.apply(lambda r: "SA" if r["SA"] > r["HC"] else ("HC" if r["HC"] > r["SA"] else "DRAW"), axis=1)
    df = df.merge(df_winner.rename("winner").reset_index(), on="run", how="left")

    return df


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


