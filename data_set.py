import pandas as pd
import constants as const


def get_final_evolutions_pokedex_numbers(
        data_set_path: str = const.COMPLETE_POKEMON_DATA_SET_PATH
        ) -> list[str]:
    data = pd.read_csv(data_set_path)
    final_evolutions = data[data["Final Evolution"] == 1.0]

    return final_evolutions["Number"].astype(str).tolist()


def get_pokemon_data(
        data_set_path: str = const.POKEMON_DATA_SET_PATH,
        include_legendary: bool = False,
        include_only_final_evolutions: bool = True
        ) -> pd.DataFrame:
    data = pd.read_csv(data_set_path)

    for parameter in const.EXCLUDED_PARAMETERS:
        if parameter in data.columns:
            data = data.drop(columns=[parameter])

    if not include_legendary:
        if "is_legendary" in data.columns:
            data = data[data["is_legendary"] == 0]

    if include_only_final_evolutions:
        pokedex_numbers = get_final_evolutions_pokedex_numbers()
        data = (data[data["pokedex_number"].astype(str)
                     .isin(pokedex_numbers)])

    return data
