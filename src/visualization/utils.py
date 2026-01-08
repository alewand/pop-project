from constants import (
    ATTACK,
    DEFENSE,
    HP,
    SPECIAL_ATTACK,
    SPECIAL_DEFENSE,
    STATS_COLS,
    STATS_SUM,
)
from classes import PokemonTeam
import pandas as pd


def get_typing_distribution(opponents):
    typings_count = {}
    for team in opponents:
        types_1 = team.members["type1"].to_list()
        types_2 = team.members["type2"].to_list()

        for t in types_1 + types_2:
            if t not in typings_count:
                typings_count[t] = 0
            typings_count[t] += 1
    return typings_count


def sort_typing_distribution(typing_distribution):
    sorted_typings = dict(
        sorted(typing_distribution.items(), key=lambda item: item[1], reverse=True)
    )
    return sorted_typings


def sort_alphabetically(typing_distribution: dict) -> dict:
    return dict(sorted(typing_distribution.items(), key=lambda kv: str(kv[0]).lower()))


def get_opponents_statistics_df(opponents: list[PokemonTeam]) -> pd.DataFrame:
    rows = []
    for i, team in enumerate(opponents):
        m = team.members

        hp_sum = int(pd.to_numeric(m[HP], errors="coerce").sum())
        atk_sum = int(pd.to_numeric(m[ATTACK], errors="coerce").sum())
        spa_sum = int(pd.to_numeric(m[SPECIAL_ATTACK], errors="coerce").sum())
        def_sum = int(pd.to_numeric(m[DEFENSE], errors="coerce").sum())
        spd_sum = int(pd.to_numeric(m[SPECIAL_DEFENSE], errors="coerce").sum())

        stats_df = m[STATS_COLS].apply(pd.to_numeric, errors="coerce")
        stats_sum = int(stats_df.sum().sum())

        n = len(m)

        rows.append(
            {
                "team_idx": i,
                HP: hp_sum,
                ATTACK: atk_sum,
                SPECIAL_ATTACK: spa_sum,
                DEFENSE: def_sum,
                SPECIAL_DEFENSE: spd_sum,
                STATS_SUM: stats_sum,
                f"{HP}_mean": hp_sum / n,
                f"{ATTACK}_mean": atk_sum / n,
                f"{SPECIAL_ATTACK}_mean": spa_sum / n,
                f"{DEFENSE}_mean": def_sum / n,
                f"{SPECIAL_DEFENSE}_mean": spd_sum / n,
                f"{STATS_SUM}_mean": stats_sum / n,
            }
        )

    return pd.DataFrame(rows)


def summarize(df_long, decimals: int = 4):
    summary = (
        df_long.groupby("solver")["fitness"]
        .agg(["mean", "median", "std", "min", "max", "count"])
        .reset_index()
        .sort_values("mean", ascending=False)
    )
    num_cols = summary.select_dtypes(include="number").columns
    summary[num_cols] = summary[num_cols].round(decimals)
    return summary
