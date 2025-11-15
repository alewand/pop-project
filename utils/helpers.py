import pandas as pd

from constants.constants import (
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
