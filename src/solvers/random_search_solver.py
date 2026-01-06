import numpy as np
from pydantic import BaseModel, ConfigDict, Field
from pandera.typing import DataFrame

from classes import PokemonTeam
from schemas import PokemonSchema
from simulation import (
    TypeMultiplierFormula,
    DamageFormula,
    multiply_type_multiplier,
    damage_attack_devide_defense,
    simulate_battle,
)

from constants import DEFAULT_TRIALS, DEFAULT_OPPONENTS_LIMIT


class RandomSearchPokemonSolver(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    trials: int = Field(default=DEFAULT_TRIALS, gt=0)
    opponents_limit: int | None = Field(default=DEFAULT_OPPONENTS_LIMIT, gt=0)
    unique_types: bool = Field(default=True)
    seed: int | None = Field(default=None)

    def _evaluate(
        self,
        team: PokemonTeam,
        opponents: list[PokemonTeam],
        type_multiplier_formula: TypeMultiplierFormula,
        damage_formula: DamageFormula,
    ) -> float:
        base_hp = sum(team.get_hps())
        ratios = []
        for opp in opponents:
            remaining = simulate_battle(
                team, opp, type_multiplier_formula, damage_formula
            )
            ratios.append(remaining / base_hp)
        return float(np.mean(np.array(ratios, dtype=float)))

    def _get_opponents(
        self,
        pokemons: DataFrame[PokemonSchema],
        opponents: list[PokemonTeam] | None,
    ) -> list[PokemonTeam]:
        if opponents is not None:
            return opponents
        if self.opponents_limit is None:
            raise ValueError("If opponents is None, opponents_limit must be provided.")
        return PokemonTeam.generate_unique_teams(
            pokemons,
            opponents_limit=self.opponents_limit,
            max_attempts=self.opponents_limit * 20,
            team_size=6,
            unique_types=self.unique_types,
        )

    def _get_random_team(
        self, pokemons: DataFrame[PokemonSchema]) -> PokemonTeam:
        return PokemonTeam.generate_team(
            pokemons,
            team_size=6,
            unique_types=self.unique_types,
        )

    def solve(
        self,
        pokemons: DataFrame[PokemonSchema],
        opponents: list[PokemonTeam] | None = None,
        type_multiplier_formula: TypeMultiplierFormula = multiply_type_multiplier,
        damage_formula: DamageFormula = damage_attack_devide_defense,
    ) -> tuple[PokemonTeam, float, list[tuple[PokemonTeam, float]], list[PokemonTeam]]:
        rng = np.random.default_rng(self.seed)
        opponents = self._get_opponents(pokemons, opponents)

        best_team = self._get_random_team(pokemons)
        best_fit = self._evaluate(
            best_team, opponents, type_multiplier_formula, damage_formula
        )

        history: list[tuple[PokemonTeam, float]] = [(best_team.copy(), best_fit)]

        for _ in range(self.trials - 1):
            team = PokemonTeam.generate_team(
                pokemons, team_size=6, unique_types=self.unique_types
            )
            fit = self._evaluate(
                team, opponents, type_multiplier_formula, damage_formula
            )
            history.append((team.copy(), fit))

            if fit > best_fit:
                best_fit = fit
                best_team = team.copy()

        return best_team, best_fit, history, opponents
