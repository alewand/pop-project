import matplotlib.pyplot as plt
import seaborn as sns
from classes import PokemonTeam
from constants import ATTACK, DEFENSE, HP, SPECIAL_ATTACK, SPECIAL_DEFENSE
from visualization.utils import (
    get_typing_distribution,
    sort_typing_distribution,
    sort_alphabetically,
    get_opponents_statistics_df,
)


def visualize_opponents_typing_distribution(
    opponents: list[PokemonTeam], sorted=False
) -> plt.figure:
    typings_count = get_typing_distribution(opponents)

    if sorted:
        typings_count = sort_typing_distribution(typings_count)
    else:
        typings_count = sort_alphabetically(typings_count)

    types = list(typings_count.keys())
    counts = list(typings_count.values())

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=types, y=counts, ax=ax)  # avoid setting palette unless you explicitly want it
    ax.set_title("Distribution of Opponent Teams Typing")
    ax.set_xlabel("Pokemon Types")
    ax.set_ylabel("Count")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()

    return fig


def visualize_opponents_stat_sums_violin(opponents: list[PokemonTeam], figsize=None) -> plt.figure:
    stats_df = get_opponents_statistics_df(opponents)

    stat_cols = [HP, ATTACK, SPECIAL_ATTACK, DEFENSE, SPECIAL_DEFENSE]

    long_df = stats_df.melt(
        id_vars=["team_idx"],
        value_vars=stat_cols,
        var_name="stat",
        value_name="sum_value",
    ).dropna()

    if figsize is None:
        figsize = (max(10, int(1.2 * len(stat_cols))), 6)

    fig, ax = plt.subplots(figsize=figsize)
    sns.violinplot(
        data=long_df,
        x="stat",
        y="sum_value",
        inner="box",
        cut=0,
        scale="width",
        ax=ax,
    )
    ax.set_title("Opponents: distribution of team stat sums")
    ax.set_xlabel("Stat")
    ax.set_ylabel("Sum across 6 Pokémon in team")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()

    return fig
