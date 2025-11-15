import pandas as pd

from constants.constants import (
    COMPLETE_POKEMON_DATA_SET_PATH,
    EXCLUDED_PARAMETERS,
    FINAL_EVOLUTION_COL,
    ID_COL,
    IS_LEGENDARY_COL,
    POKEMON_DATA_SET_PATH,
    NUMBER_COL
)


def get_final_evolutions_ids(
        data_set_path: str = COMPLETE_POKEMON_DATA_SET_PATH
        ) -> list[str]:
    data = pd.read_csv(data_set_path)
    final_evolutions = data[data[FINAL_EVOLUTION_COL] == 1.0]

    return final_evolutions[NUMBER_COL].astype(str).tolist()


def get_pokemons_data(
        data_set_path: str = POKEMON_DATA_SET_PATH,
        include_legendary: bool = False,
        include_only_final_evolutions: bool = True
        ) -> pd.DataFrame:
    data = pd.read_csv(data_set_path)

    if not include_legendary:
        if IS_LEGENDARY_COL in data.columns:
            data = data[data[IS_LEGENDARY_COL] == 0]

    if include_only_final_evolutions:
        final_evolutions_ids = get_final_evolutions_ids()
        data = (data[data[ID_COL].astype(str)
                     .isin(final_evolutions_ids)])

    for parameter in EXCLUDED_PARAMETERS:
        if parameter in data.columns:
            data = data.drop(columns=[parameter])

    return data
