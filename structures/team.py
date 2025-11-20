import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List

from constants.constants import (
    FIRST_TYPE_COL,
    HP_COL,
    ID_COL,
    NAME_COL,
    SECOND_TYPE_COL,
    STATS_COLS,
    TEAM_SIZE
)


@dataclass
class PokemonTeam:
    _members: pd.DataFrame

    @property
    def members(self) -> pd.DataFrame:
        return self._members

    @members.setter
    def members(self, members: pd.DataFrame):
        self._members = members

    @property
    def stats(self) -> int:
        return self._members[STATS_COLS].astype(int).to_numpy().sum()

    @property
    def ids(self) -> List[str]:
        return self._members[ID_COL].astype(str).to_list()

    @property
    def hps(self) -> List[int]:
        return self._members[HP_COL].astype(int).to_list()

    @property
    def size(self) -> int:
        return len(self._members)

    def copy(self) -> "PokemonTeam":
        return PokemonTeam(self._members.copy())

    def swap_members(self, first_index: int, second_index: int) -> None:
        new_members = self._members.copy()
        temp = new_members.iloc[first_index].copy()
        new_members.iloc[first_index] = new_members.iloc[second_index]
        new_members.iloc[second_index] = temp
        self.members = new_members

    def get_pokemons_without_team(
        self,
        pokemons: pd.DataFrame
    ) -> pd.DataFrame:
        mask = (~pokemons[ID_COL].astype(str).isin(self.ids))
        return pokemons[mask]

    def generate_opponents(
        self,
        pokemons: pd.DataFrame,
        unique_types: bool = True,
        team_size: int = TEAM_SIZE,
        limit: int | None = None
    ) -> List["PokemonTeam"]:
        if limit is not None and limit <= 0:
            raise ValueError("Limit must be a positive integer or None.")

        opponents: List["PokemonTeam"] = []
        possible_pokemons = self.get_pokemons_without_team(pokemons)

        for i, _ in self._members.iterrows():
            for _, possible_opponent_member in possible_pokemons.iterrows():
                opponent_members = self._members.copy()
                opponent_members.iloc[i] = possible_opponent_member

                if unique_types and not self.unique_types(opponent_members):
                    continue

                if len(opponent_members) != team_size:
                    opponents.append(
                        PokemonTeam(opponent_members.reset_index(drop=True))
                    )

                if limit is not None and len(opponents) >= limit:
                    break

            if limit is not None and len(opponents) >= limit:
                break

        return opponents

    def generate_team_with_random_replacement(
        self,
        pokemons: pd.DataFrame,
        replacements: int = 2,
        unique_types: bool = True,
    ) -> "PokemonTeam":
        team_size = self.size
        new_members = self._members.copy()
        rng = np.random.default_rng()

        members_to_replace_indexes = rng.choice(
            team_size,
            size=replacements,
            replace=False
        )

        possible_pokemons = self.get_pokemons_without_team(pokemons)

        for member_index in members_to_replace_indexes:
            if possible_pokemons.empty:
                break

            possible_members_indexes = rng.permutation(possible_pokemons.index)

            for possible_member_index in possible_members_indexes:
                possible_member = possible_pokemons.loc[possible_member_index]

                possible_members = new_members.copy()
                possible_members.iloc[member_index] = possible_member

                if unique_types and not self.unique_types(possible_members):
                    continue

                new_members = possible_members
                possible_pokemons = (
                    possible_pokemons.drop(possible_member.name)
                )

                break

        return PokemonTeam(new_members.reset_index(drop=True))

    def print(self) -> None:
        print(self._members[[NAME_COL, FIRST_TYPE_COL, SECOND_TYPE_COL]])

    @classmethod
    def generate(
        cls,
        pokemons: pd.DataFrame,
        unique_types: bool = True,
        team_size: int = TEAM_SIZE,
    ) -> "PokemonTeam":
        remaining_pokemons = pokemons.copy()
        members = pd.DataFrame()
        rng = np.random.default_rng()

        while (
            len(members) < team_size and
                not remaining_pokemons.empty):

            chosen_index: int = rng.choice(remaining_pokemons.index)
            possible_member: pd.Series = (
                remaining_pokemons.loc[chosen_index]
                )

            possible_members = members.copy()
            possible_members: pd.DataFrame = pd.concat(
                [members, possible_member.to_frame().T],
                ignore_index=True
            )

            if unique_types and not cls.unique_types(possible_members):
                continue

            members = possible_members
            remaining_pokemons = remaining_pokemons.drop(chosen_index)

        return cls(members.reset_index(drop=True))

    @staticmethod
    def unique_types(members: pd.DataFrame) -> bool:
        types = members[[FIRST_TYPE_COL, SECOND_TYPE_COL]].to_numpy().ravel()
        types = [member_type for member_type in types if pd.notna(member_type)]
        return len(types) == len(set(types))
