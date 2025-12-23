from pathlib import Path

import pandas as pd
from pandera.typing import DataFrame

from constants import (
    COMPLETE_POKEMON_DATA_SET_PATH,
    EXCLUDED_COLS,
    FINAL_EVOLUTION_COMPLETE,
    ID,
    ID_COMPLETE,
    IS_LEGENDARY,
    POKEMON_DATA_SET_PATH,
)
from schemas import PokemonSchema


def get_final_evolutions_ids(
    data_set_path: Path = COMPLETE_POKEMON_DATA_SET_PATH,
) -> list[str]:
    data = pd.read_csv(data_set_path)
    final_evolutions = data[data[FINAL_EVOLUTION_COMPLETE] == 1.0]

    return final_evolutions[ID_COMPLETE].astype(str).tolist()


def get_pokemons(
    data_set_path: Path = POKEMON_DATA_SET_PATH,
    include_legendary: bool = False,
    include_only_final_evolutions: bool = True,
) -> DataFrame[PokemonSchema]:
    data = pd.read_csv(data_set_path)

    if not include_legendary and IS_LEGENDARY in data.columns:
        data = data[data[IS_LEGENDARY] == 0]

    if include_only_final_evolutions:
        final_evolutions_ids = get_final_evolutions_ids()
        data = data[data[ID].astype(str).isin(final_evolutions_ids)]

    for column in EXCLUDED_COLS:
        if column in data.columns:
            data = data.drop(columns=[column])

    return PokemonSchema.validate(data, lazy=True)


def get_pokemon_with_excluded_ids(
    excluded_ids: list[str],
    pokemons: DataFrame[PokemonSchema] | None = None,
    data_set_path: Path | None = POKEMON_DATA_SET_PATH,
    include_legendary: bool = False,
    include_only_final_evolutions: bool = True,
) -> DataFrame[PokemonSchema]:
    if pokemons is None:
        if data_set_path is None:
            raise ValueError("Either 'pokemons' or 'data_set_path' must be provided.")

        pokemons = get_pokemons(
            data_set_path=data_set_path,
            include_legendary=include_legendary,
            include_only_final_evolutions=include_only_final_evolutions,
        )

    mask = ~pokemons[ID].astype(str).isin(excluded_ids)
    return pokemons[mask]
