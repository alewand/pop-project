import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series

from constants import TYPES


class PokemonSchema(pa.DataFrameModel):
    pokedex_number: Series[int] = pa.Field(ge=1, coerce=True)
    name: Series[str] = pa.Field(str_length={"min_value": 1}, nullable=False)
    type1: Series[str] = pa.Field(nullable=False)
    type2: Series[str] = pa.Field(nullable=True)

    hp: Series[int] = pa.Field(ge=1, coerce=True)
    attack: Series[int] = pa.Field(ge=1, coerce=True)
    sp_attack: Series[int] = pa.Field(ge=1, coerce=True)
    defense: Series[int] = pa.Field(ge=1, coerce=True)
    sp_defense: Series[int] = pa.Field(ge=1, coerce=True)
    speed: Series[int] = pa.Field(ge=1, coerce=True)

    is_legendary: Series[int] = pa.Field(isin=[0, 1], coerce=True)

    against_bug: Series[float] = pa.Field(ge=0.0, coerce=True)
    against_dark: Series[float] = pa.Field(ge=0.0, coerce=True)
    against_dragon: Series[float] = pa.Field(ge=0.0, coerce=True)
    against_electric: Series[float] = pa.Field(ge=0.0, coerce=True)
    against_fairy: Series[float] = pa.Field(ge=0.0, coerce=True)
    against_fighting: Series[float] = pa.Field(ge=0.0, coerce=True)
    against_fire: Series[float] = pa.Field(ge=0.0, coerce=True)
    against_flying: Series[float] = pa.Field(ge=0.0, coerce=True)
    against_ghost: Series[float] = pa.Field(ge=0.0, coerce=True)
    against_grass: Series[float] = pa.Field(ge=0.0, coerce=True)
    against_ground: Series[float] = pa.Field(ge=0.0, coerce=True)
    against_ice: Series[float] = pa.Field(ge=0.0, coerce=True)
    against_normal: Series[float] = pa.Field(ge=0.0, coerce=True)
    against_poison: Series[float] = pa.Field(ge=0.0, coerce=True)
    against_psychic: Series[float] = pa.Field(ge=0.0, coerce=True)
    against_rock: Series[float] = pa.Field(ge=0.0, coerce=True)
    against_steel: Series[float] = pa.Field(ge=0.0, coerce=True)
    against_water: Series[float] = pa.Field(ge=0.0, coerce=True)

    @pa.check("type1")
    def _type1_in_types(cls, s: pd.Series) -> pd.Series:
        return s.isin(TYPES)

    @pa.check("type2")
    def _type2_in_types_or_null(cls, s: pd.Series) -> pd.Series:
        return s.isna() | s.isin(TYPES)

    class Config:
        strict = True
        coerce = True
