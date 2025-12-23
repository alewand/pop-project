import numpy as np
import pandas as pd
from pandera.typing import DataFrame

from constants import (
    FIRST_TYPE,
    ID,
    NAME,
    POKEMON_TO_REPLACE_AMOUNT,
    SECOND_TYPE,
    STATS_COLS,
    TEAM_SIZE,
)
from data import get_pokemon_with_excluded_ids
from schemas import PokemonSchema


class PokemonTeam:
    def __init__(self, members: DataFrame[PokemonSchema]) -> None:
        if len(members) != TEAM_SIZE:
            raise ValueError(f"Pokemon team must have exactly {TEAM_SIZE} members.")

        self.members = members.copy().reset_index(drop=True)

    def get_stats(self) -> int:
        return self.members[STATS_COLS].astype(int).to_numpy().sum()

    def get_ids(self) -> list[str]:
        return self.members[ID].astype(str).to_list()

    def get_hps(self) -> list[int]:
        return self.members["hp"].astype(int).to_list()

    def get_size(self) -> int:
        return len(self.members)

    def copy(self) -> "PokemonTeam":
        return PokemonTeam(self.members.copy().reset_index(drop=True))

    def swap_members(self, first_index: int, second_index: int) -> None:
        new_members = self.members.copy()
        temp = new_members.iloc[first_index].copy()
        new_members.iloc[first_index] = new_members.iloc[second_index]
        new_members.iloc[second_index] = temp
        self.members = new_members.reset_index(drop=True)

    def generate_opponents(
        self,
        pokemons: DataFrame[PokemonSchema],
        unique_types: bool = True,
        limit: int | None = None,
    ) -> list["PokemonTeam"]:
        if limit is not None and limit <= 0:
            raise ValueError("Limit must be positive or None.")

        opponents: list[PokemonTeam] = []
        possible_pokemons = get_pokemon_with_excluded_ids(self.get_ids(), pokemons)

        for member_position in range(self.get_size()):
            for _, possible_opponent_member in possible_pokemons.iterrows():
                opponent_members = self.members.copy()
                opponent_members.iloc[member_position] = possible_opponent_member

                if unique_types and not self.are_types_unique(opponent_members):
                    continue

                opponents.append(PokemonTeam(opponent_members))

                if limit is not None and len(opponents) >= limit:
                    break

            if limit is not None and len(opponents) >= limit:
                break

        return opponents

    def generate_team_with_random_replacement(
        self,
        pokemons: DataFrame[PokemonSchema],
        replacements: int = POKEMON_TO_REPLACE_AMOUNT,
        unique_types: bool = True,
    ) -> "PokemonTeam":
        rng = np.random.default_rng()

        members_to_replace_indexes = rng.choice(
            self.get_size(), size=replacements, replace=False
        )

        possible_pokemons = get_pokemon_with_excluded_ids(self.get_ids(), pokemons)

        new_members = self.members.copy()

        for member_index in members_to_replace_indexes:
            if possible_pokemons.empty:
                break

            possible_members_indexes = rng.permutation(possible_pokemons.index)

            for possible_member_index in possible_members_indexes:
                possible_member = possible_pokemons.loc[possible_member_index].copy()

                possible_members = new_members.copy()

                possible_members.iloc[member_index] = possible_member

                if unique_types and not self.are_types_unique(possible_members):
                    continue

                new_members = possible_members
                possible_pokemons = possible_pokemons.drop(possible_member.name)
                break

        return PokemonTeam(new_members)

    def __repr__(self) -> str:
        names = self.members[NAME].tolist()
        return f"{self.__class__.__name__}(size={self.get_size()}, names={names})"

    @classmethod
    def generate_team(
        cls,
        pokemons: DataFrame[PokemonSchema],
        team_size: int = TEAM_SIZE,
        unique_types: bool = True,
    ) -> "PokemonTeam":
        rng = np.random.default_rng()

        members: DataFrame[PokemonSchema] = pokemons.iloc[0:0].copy()

        possible_members_indexes = rng.permutation(pokemons.index)

        for candidate_index in possible_members_indexes:
            if len(members) >= team_size:
                break

            candidate = pokemons.loc[candidate_index].copy()
            candidate_members: DataFrame[PokemonSchema] = pd.concat(
                [members, candidate.to_frame().T],
                ignore_index=True,
            )

            if unique_types and not cls.are_types_unique(candidate_members):
                continue

            members = candidate_members

        return cls(members)

    @staticmethod
    def are_types_unique(members: DataFrame[PokemonSchema]) -> bool:
        types = members[[FIRST_TYPE, SECOND_TYPE]].to_numpy().ravel().tolist()
        types = [t for t in types if pd.notna(t)]
        return len(types) == len(set(types))
