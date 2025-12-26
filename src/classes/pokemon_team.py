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

    def get_stats_sum(self) -> int:
        return int(self.members[STATS_COLS].astype(int).sum().sum())

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

    def generate_neighbors(
        self,
        pokemons: DataFrame[PokemonSchema],
        unique_types: bool = True,
        limit: int | None = None,
    ) -> list["PokemonTeam"]:
        if limit is not None and limit <= 0:
            raise ValueError("Limit must be positive or None.")

        rng = np.random.default_rng()

        neighbors: list[PokemonTeam] = []
        possible_pokemons = get_pokemon_with_excluded_ids(self.get_ids(), pokemons)

        candidate_indexes = rng.permutation(possible_pokemons.index.to_numpy())

        for member_position in range(self.get_size()):
            for candidate_index in candidate_indexes:
                neighbor_members = self.members.copy()
                neighbor_members.iloc[member_position] = possible_pokemons.loc[
                    candidate_index
                ]

                if unique_types and not self.are_types_unique(neighbor_members):
                    continue

                neighbors.append(PokemonTeam(neighbor_members))

                if limit is not None and len(neighbors) >= limit:
                    break

            if limit is not None and len(neighbors) >= limit:
                break

        return neighbors

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

    @classmethod
    def generate_unique_teams(
        cls,
        pokemons: DataFrame[PokemonSchema],
        opponents_limit: int | None = None,
        max_attempts: int | None = None,
        team_size: int = TEAM_SIZE,
        unique_types: bool = True,
    ) -> list["PokemonTeam"]:
        if opponents_limit is not None and opponents_limit <= 0:
            raise ValueError("opponents_limit must be positive or None")

        if max_attempts is not None and max_attempts <= 0:
            raise ValueError("max_attempts must be positive")

        if max_attempts is None and opponents_limit is None:
            raise ValueError(
                "When opponents_limit is None, you must provide max_attempts "
                "to avoid an infinite loop."
            )
        elif max_attempts is None or max_attempts <= 0:
            raise ValueError("max_attempts must be positive")

        opponents: list[PokemonTeam] = []
        seen_signatures: set[tuple[str, ...]] = set()

        attempts = 0
        while attempts < max_attempts and (
            opponents_limit is None or len(opponents) < opponents_limit
        ):
            attempts += 1

            team = cls.generate_team(pokemons, team_size, unique_types)
            signature = tuple(sorted(team.get_ids()))

            if signature in seen_signatures:
                continue

            seen_signatures.add(signature)
            opponents.append(team)

        return opponents

    @staticmethod
    def are_types_unique(members: DataFrame[PokemonSchema]) -> bool:
        types = members[[FIRST_TYPE, SECOND_TYPE]].to_numpy().ravel().tolist()
        types = [t for t in types if pd.notna(t)]
        return len(types) == len(set(types))
