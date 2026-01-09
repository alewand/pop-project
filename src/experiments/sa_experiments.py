from pathlib import Path
from pandera.typing import DataFrame
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pandera.typing import DataFrame
from classes import PokemonTeam
from constants import TEAM_SIZE, DEFAULT_OPPONENTS_LIMIT, SA_REPORT_PATH
from constants.constants import DEFAULT_MAX_EVALUATIONS
from data import get_pokemons
from schemas import PokemonSchema
from solvers import (
    SimulatedAnnealingPokemonSolver,
    HillClimbingPokemonSolver,
    RandomSearchPokemonSolver,
)
from visualization.plots import visualize_opponents_typing_distribution, visualize_opponents_stat_sums_violin
from report.reports import PdfReport
from visualization.utils import summarize


def run_multiple_runs(
    pokemons: DataFrame[PokemonSchema],
    solver: SimulatedAnnealingPokemonSolver,
    opponents: list[PokemonTeam] = None,
    runs: int = 8,
) -> None:
    print(f"Running {runs} runs of the SA solver...")

    rows = []

    for i in range(runs):
        print(f" Run {i+1}/{runs}...")
        best_team, best_fitness, history, used_opponents = solver.solve(pokemons, opponents=opponents)
        names = best_team.members['name'].tolist()

        print(f"  Best fitness: {best_fitness}")
        print(f"  Team: {names}")

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
        print(f" Run {i+1}/{runs}...")
        starting_team = PokemonTeam.generate_team(
            pokemons, team_size=6, unique_types=True
        )

        sa_team, sa_fit, sa_hist, _ = solver.solve(pokemons, opponents=opponents, start_team=starting_team)
        rs_team, rs_fit, rs_hist, _ = baseline_solver.solve(pokemons, opponents=opponents)

        sa_names = sa_team.members['name'].tolist()
        rs_names = rs_team.members['name'].tolist()

        print(f"  SA fitness: {sa_fit}, RS fitness: {rs_fit}")
        print(f"  SA team: {sa_names}")
        print(f"  RS team: {rs_names}")

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
        print(f" Run {i+1}/{runs}...")
        starting_team = PokemonTeam.generate_team(
            pokemons, team_size=6, unique_types=True
        )

        sa_team, sa_fit, sa_hist, _ = solver.solve(pokemons, opponents=opponents, start_team=starting_team)
        hc_team, hc_fit, hc_hist, _ = baseline_solver.solve(pokemons, opponents=opponents, start_team=starting_team)

        sa_names = sa_team.members['name'].tolist()
        hc_names = hc_team.members['name'].tolist()

        print(f"  SA fitness: {sa_fit}, HC fitness: {hc_fit}")
        print(f"  SA team: {sa_names}")
        print(f"  HC team: {hc_names}")

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
    opponents = PokemonTeam.generate_unique_teams(
        pokemons,
        opponents_limit=DEFAULT_OPPONENTS_LIMIT,
        max_attempts=DEFAULT_OPPONENTS_LIMIT * 30,
        team_size=TEAM_SIZE,
        unique_types=True,
    )

    rs = RandomSearchPokemonSolver()
    sa = SimulatedAnnealingPokemonSolver()
    hc = HillClimbingPokemonSolver()

    opponents_typings = visualize_opponents_typing_distribution(opponents)
    opponents_stats = visualize_opponents_stat_sums_violin(opponents)

    df_sa_runs = run_multiple_runs(pokemons, sa, opponents=opponents, runs=8)
    df_sa_vs_rs = compare_to_random_search(pokemons, sa, rs, opponents=opponents, runs=8)
    df_sa_vs_hc = compare_to_hill_climb(pokemons, sa, hc, opponents=opponents, runs=8)

    sum_sa_runs = summarize(df_sa_runs)
    sum_sa_rs = summarize(df_sa_vs_rs)
    sum_sa_hc = summarize(df_sa_vs_hc)

    report = PdfReport(SA_REPORT_PATH, title="SA experiments report (same opponents)")

    report.add_text(
        f"""Setup
        - Team size: {TEAM_SIZE}
        - Opponents limit: {DEFAULT_OPPONENTS_LIMIT}
        - Max evaluations: {DEFAULT_MAX_EVALUATIONS}
        - Number of opponents generated: {len(opponents)}
        - Number of runs per experiment: 8
        - Starting temperature: {sa.T0}
        - Minimum temperature: {sa.Tmin}
        - Alpha (cooling rate): {sa.alpha}
        - Iterations per temperature: {sa.iters_per_temp}
        - Neighbor replacements per step: {sa.neighbor_replacements}
        - Patience: {sa.patience}
        - Restarts: {sa.restarts}
        - Random Search max evaluations: {rs.trials}
        - Hill Climbing max evaluations: {hc.max_evaluations}
        - Hill Climbing neighbour per step: {hc.neighbors_per_step}
        """)

    report.add_figure(opponents_typings)
    report.add_figure(opponents_stats)

    report.add_dataframe(df_sa_runs, "SA: per-run results")
    report.add_dataframe(sum_sa_runs, "SA: summary stats")


    report.add_dataframe(df_sa_vs_rs, "SA vs RS: per-run results")
    report.add_dataframe(sum_sa_rs, "SA vs RS: summary stats")


    report.add_dataframe(df_sa_vs_hc, "SA vs HC (same start per run): per-run results")
    report.add_dataframe(sum_sa_hc, "SA vs HC: summary stats")


    report.write()
    print(f"Saved: {SA_REPORT_PATH}")
