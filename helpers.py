import pandas as pd
import numpy as np
from typing import List

from constants import (
    TEAM_SIZE,
    POKEMON_TO_REPLACE_AMOUNT,
    FIRST_TYPE_COL,
    SECOND_TYPE_COL,
    ID_COL,
)


def are_team_types_unique(team: pd.DataFrame) -> bool:
    types = team[[FIRST_TYPE_COL, SECOND_TYPE_COL]].to_numpy().ravel()
    types = [pokemon_type for pokemon_type in types if pd.notna(pokemon_type)]
    return len(types) == len(set(types))


def get_pokemons_without_current_team(
        all_pokemons: pd.DataFrame,
        current_team: pd.DataFrame) -> pd.DataFrame:
    current_team_pokemon_ids = current_team[ID_COL].astype(str)
    mask = (~all_pokemons[ID_COL]
            .astype(str).isin(current_team_pokemon_ids))
    return all_pokemons[mask]


def generate_start_team(
        pokemons: pd.DataFrame,
        team_size: int = TEAM_SIZE) -> pd.DataFrame:
    remaining_pokemons = pokemons.copy()
    selected_pokemons = []
    rng = np.random.default_rng()
    used_types = set()

    while len(selected_pokemons) < team_size and not remaining_pokemons.empty:
        chosen_pokemon_index = rng.choice(remaining_pokemons.index.to_numpy())
        chosen_pokemon = remaining_pokemons.loc[chosen_pokemon_index]
        first_type = chosen_pokemon[FIRST_TYPE_COL]
        second_type = chosen_pokemon[SECOND_TYPE_COL]

        if (first_type not in used_types and
                (second_type not in used_types or pd.isna(second_type))):
            selected_pokemons.append(chosen_pokemon)
            used_types.add(first_type)
            if pd.notna(second_type):
                used_types.add(second_type)

        remaining_pokemons = remaining_pokemons.drop(chosen_pokemon_index)

    return pd.DataFrame(selected_pokemons).reset_index(drop=True)


def generate_team_with_replacement(
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
        for _, candidate in possible_pokemons.iterrows():
            candidate_team = new_team.copy()
            candidate_team.iloc[pokemon_in_team_index] = candidate

            if unique_types and not are_team_types_unique(candidate_team):
                continue

            new_team = candidate_team
            possible_pokemons = possible_pokemons.drop(candidate.name)
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
                opponent_teams.append(opponent_team)

            if limit is not None and len(opponent_teams) >= limit:
                break

        if limit is not None and len(opponent_teams) >= limit:
            break

    return opponent_teams
