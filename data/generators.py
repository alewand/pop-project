import pandas as pd
import numpy as np
from typing import List

from constants.constants import (
    TEAM_SIZE,
    POKEMON_TO_REPLACE_AMOUNT,
)

from data.helpers import (
    are_team_types_unique,
    get_pokemons_without_current_team,
)


def generate_start_team(
        pokemons: pd.DataFrame,
        team_size: int = TEAM_SIZE,
        unique_types: bool = True) -> pd.DataFrame:
    remaining_pokemons = pokemons.copy()
    selected_pokemons = pd.DataFrame()
    rng = np.random.default_rng()

    while len(selected_pokemons) < team_size and not remaining_pokemons.empty:
        chosen_pokemon_index: int = rng.choice(remaining_pokemons.index)
        chosen_pokemon: pd.Series = (
            remaining_pokemons.loc[chosen_pokemon_index]
        )

        candidate_team = selected_pokemons.copy()
        candidate_team = pd.concat(
            [selected_pokemons, chosen_pokemon.to_frame().T],
            ignore_index=True
        )

        if unique_types and not are_team_types_unique(candidate_team):
            continue

        selected_pokemons = candidate_team
        remaining_pokemons = remaining_pokemons.drop(chosen_pokemon_index)

    return selected_pokemons.reset_index(drop=True)


def generate_team_with_random_replacement(
        all_pokemons: pd.DataFrame,
        current_team: pd.DataFrame,
        pokemon_to_replace_amount: int = POKEMON_TO_REPLACE_AMOUNT,
        unique_types: bool = True
        ) -> pd.DataFrame:
    team_size = len(current_team)
    new_team = current_team.copy()
    rng = np.random.default_rng()

    pokemon_chosen_to_replace_indexes = rng.choice(
        team_size,
        size=pokemon_to_replace_amount,
        replace=False
    )

    possible_pokemons = get_pokemons_without_current_team(
        all_pokemons, current_team
    )

    for pokemon_in_team_index in pokemon_chosen_to_replace_indexes:
        if possible_pokemons.empty:
            break

        candidate_indexes = rng.permutation(possible_pokemons.index)

        for candidate_index in candidate_indexes:
            candidate = possible_pokemons.loc[candidate_index]

            candidate_team = new_team.copy()
            candidate_team.iloc[pokemon_in_team_index] = candidate

            if unique_types and not are_team_types_unique(candidate_team):
                continue

            new_team = candidate_team
            possible_pokemons = possible_pokemons.drop(candidate.index)
            break

    return new_team.reset_index(drop=True)


def generate_opponent_teams(
        all_pokemons: pd.DataFrame,
        current_team: pd.DataFrame,
        team_size: int = TEAM_SIZE,
        unique_types: bool = True,
        limit: int | None = None) -> List[pd.DataFrame]:
    opponent_teams: List[pd.DataFrame] = []
    possible_pokemons = get_pokemons_without_current_team(
        all_pokemons, current_team)

    for i, _ in current_team.iterrows():
        for _, candidate in possible_pokemons.iterrows():
            opponent_team = current_team.copy()
            opponent_team.iloc[i] = candidate

            if unique_types and not are_team_types_unique(opponent_team):
                continue

            if len(opponent_team) == team_size:
                opponent_teams.append(opponent_team.reset_index(drop=True))

            if limit is not None and len(opponent_teams) >= limit:
                break

        if limit is not None and len(opponent_teams) >= limit:
            break

    return opponent_teams
