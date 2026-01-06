import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pandera.typing import DataFrame
from typing import Optional

from classes import PokemonTeam
from schemas import PokemonSchema
from simulation import (
    TypeMultiplierFormula,
    DamageFormula,
    multiply_type_multiplier,
    damage_attack_devide_defense,
    simulate_battle,
)
from constants import (
    DEFAULT_HILL_CLIMBING_MAX_EVALUATIONS,
    DEFAULT_HILL_CLIMBING_NEIGHBOUR_PER_STEP,
    DEFAULT_HILL_CLIMBING_NEIGHBOUR_REPLACEMENTS,
    DEFAULT_HILL_CLIMBING_OPPONENTS_LIMIT,
    DEFAULT_HILL_CLIMBING_PATIENCE,
    DEFAULT_HILL_CLIMBING_RESTARTS,
)


class HillClimbingPokemonSolver(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    max_evaluations: int = Field(default=DEFAULT_HILL_CLIMBING_MAX_EVALUATIONS, gt=0)
    neighbors_per_step: int = Field(
        default=DEFAULT_HILL_CLIMBING_NEIGHBOUR_PER_STEP, gt=0
    )
    neighbor_replacements: int = Field(
        default=DEFAULT_HILL_CLIMBING_NEIGHBOUR_REPLACEMENTS, gt=0
    )

    opponents_limit: int | None = Field(
        default=DEFAULT_HILL_CLIMBING_OPPONENTS_LIMIT, gt=0
    )
    unique_types: bool = Field(default=True)
    seed: int | None = Field(default=None)

    restarts: int = Field(default=DEFAULT_HILL_CLIMBING_RESTARTS, ge=0)
    patience: int | None = Field(default=DEFAULT_HILL_CLIMBING_PATIENCE, gt=0)

    @model_validator(mode="after")
    def _check(self) -> "HillClimbingPokemonSolver":
        if self.neighbors_per_step <= 0:
            raise ValueError("neighbors_per_step must be > 0")
        return self

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

    def _random_team(self, pokemons: DataFrame[PokemonSchema]) -> PokemonTeam:
        return PokemonTeam.generate_team(
            pokemons, team_size=6, unique_types=self.unique_types
        )

    def solve(
        self,
        pokemons: DataFrame[PokemonSchema],
        opponents: list[PokemonTeam] | None = None,
        start_team: Optional[PokemonTeam] = None,
        type_multiplier_formula: TypeMultiplierFormula = multiply_type_multiplier,
        damage_formula: DamageFormula = damage_attack_devide_defense,
    ) -> tuple[PokemonTeam, float, list[tuple[PokemonTeam, float]], list[PokemonTeam]]:

        rng = np.random.default_rng(self.seed)
        opponents = self._get_opponents(pokemons, opponents)

        history: list[tuple[PokemonTeam, float]] = []

        best_team = None
        best_fit = float("-inf")
        evaluations = 0

        for run_idx in range(self.restarts + 1):
            if evaluations >= self.max_evaluations:
                break

            if run_idx == 0 and start_team is not None:
                current = start_team.copy()
            else:
                current = self._random_team(pokemons)

            current_fit = self._evaluate(
                current, opponents, type_multiplier_formula, damage_formula
            )
            evaluations += 1

            if current_fit > best_fit:
                best_fit = current_fit
                best_team = current.copy()

            no_improve = 0

            while evaluations < self.max_evaluations:
                best_neighbor = None
                best_neighbor_fit = float("-inf")

                for _ in range(self.neighbors_per_step):
                    if evaluations >= self.max_evaluations:
                        break

                    cand = current.generate_team_with_random_replacement(
                        pokemons,
                        replacements=self.neighbor_replacements,
                        unique_types=self.unique_types,
                    )
                    cand_fit = self._evaluate(
                        cand, opponents, type_multiplier_formula, damage_formula
                    )
                    evaluations += 1

                    if cand_fit > best_neighbor_fit:
                        best_neighbor_fit = cand_fit
                        best_neighbor = cand

                history.append((current.copy(), current_fit))

                if best_neighbor is not None and best_neighbor_fit > current_fit:
                    current = best_neighbor
                    current_fit = best_neighbor_fit
                    no_improve = 0

                    if current_fit > best_fit:
                        best_fit = current_fit
                        best_team = current.copy()
                else:
                    no_improve += 1
                    if self.patience is None or no_improve >= self.patience:
                        break

        if best_team is None:
            best_team = self._random_team(pokemons)
            best_fit = self._evaluate(
                best_team, opponents, type_multiplier_formula, damage_formula
            )

        return best_team, best_fit, history, opponents
