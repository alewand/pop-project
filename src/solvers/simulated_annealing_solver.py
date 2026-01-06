import math
import numpy as np
from typing import Optional
from dataclasses import dataclass
from pandera.typing import DataFrame
from pydantic import BaseModel, ConfigDict, Field, model_validator
from constants import (
    DEFAULT_INITIAL_TEMPERATURE,
    DEFAULT_MIN_TEMPERATURE,
    DEFAULT_ALPHA,
    DEFAULT_ITERS_PER_TEMP,
    DEFAULT_MAX_EVALUATIONS,
    DEFAULT_NEIGHBOR_REPLACEMENTS,
    DEFAULT_SA_OPPONENTS_LIMIT,
    DEFAULT_PATIENCE,
    DEFAULT_RESTARTS,
    TEAM_SIZE,
)

from classes import PokemonTeam
from schemas import PokemonSchema
from simulation import (
    TypeMultiplierFormula,
    DamageFormula,
    multiply_type_multiplier,
    damage_attack_devide_defense,
    simulate_battle,
)


@dataclass
class SAHistoryEntry:
    step: int
    temperature: float
    current_fitness: float
    best_fitness: float
    accepted: bool


class SimulatedAnnealingPokemonSolver(BaseModel):
    model_config = ConfigDict(validate_assignment=True, populate_by_name=True)

    T0: float = Field(
        default=DEFAULT_INITIAL_TEMPERATURE,
        gt=0.0,
        alias="initial_temperature",
    )
    Tmin: float = Field(
        default=DEFAULT_MIN_TEMPERATURE,
        gt=0.0,
        alias="min_temperature",
    )

    alpha: float = Field(
        default=DEFAULT_ALPHA,
        gt=0.0,
        lt=1.0,
    )

    iters_per_temp: int = Field(
        default=DEFAULT_ITERS_PER_TEMP,
        gt=0,
    )

    max_evaluations: int = Field(
        default=DEFAULT_MAX_EVALUATIONS,
        gt=0,
    )

    neighbor_replacements: int = Field(
        default=DEFAULT_NEIGHBOR_REPLACEMENTS,
        gt=0,
    )

    opponents_limit: int | None = Field(
        default=DEFAULT_SA_OPPONENTS_LIMIT,
        gt=0,
    )

    unique_types: bool = Field(
        default=True,
    )

    seed: int | None = Field(
        default=None,
    )

    patience: int | None = Field(
        default=DEFAULT_PATIENCE,
        gt=0,
    )

    restarts: int = Field(
        default=DEFAULT_RESTARTS,
        ge=0,
    )

    @model_validator(mode="after")
    def _check_params(self) -> "SimulatedAnnealingSolver":
        if self.Tmin >= self.T0:
            raise ValueError(
                "min_temperature (Tmin) must be smaller than initial_temperature (T0)."
            )

        if self.neighbor_replacements > TEAM_SIZE:
            raise ValueError(
                f"neighbor_replacements must be <= TEAM_SIZE ({TEAM_SIZE})."
            )

        return self

    def _evaluate(
        self,
        team: PokemonTeam,
        opponents: list[PokemonTeam],
        type_multiplier_formula: TypeMultiplierFormula,
        damage_formula: DamageFormula,
    ) -> float:
        # Mean remaining HP ratio vs opponents
        ratios = []
        base_hp = sum(team.get_hps())
        for opp in opponents:
            remaining = simulate_battle(
                team, opp, type_multiplier_formula, damage_formula
            )
            ratios.append(remaining / base_hp)
        return float(np.mean(np.array(ratios, dtype=float)))

    def _accept(self, rng: np.random.Generator, delta: float, T: float) -> bool:
        if delta >= 0:
            return True
        if T <= 0:
            return False
        return rng.random() < math.exp(delta / T)

    def _random_team(self, pokemons: DataFrame[PokemonSchema]) -> PokemonTeam:
        return PokemonTeam.generate_team(
            pokemons, team_size=6, unique_types=self.unique_types
        )

    def _generate_opponents(
        self, pokemons: DataFrame[PokemonSchema]
    ) -> list[PokemonTeam]:
        return PokemonTeam.generate_unique_teams(
            pokemons,
            self.opponents_limit,
            self.opponents_limit * 10 if self.opponents_limit is not None else 10000,
            team_size=6,
            unique_types=self.unique_types,
        )

    def _fitness(
        self,
        team: PokemonTeam,
        opponents: list[PokemonTeam],
        cache: dict[tuple[str, ...], float],
        type_multiplier_formula: TypeMultiplierFormula,
        damage_formula: DamageFormula,
    ) -> float:
        sig = tuple(team.get_ids())
        if sig in cache:
            return cache[sig]
        val = self._evaluate(team, opponents, type_multiplier_formula, damage_formula)
        cache[sig] = val
        return val

    def _run_once(
        self,
        pokemons: DataFrame[PokemonSchema],
        opponents: list[PokemonTeam],
        rng: np.random.Generator,
        cache: dict[tuple[str, ...], float],
        history: list[SAHistoryEntry],
        evaluations: int,
        step: int,
        type_multiplier_formula: TypeMultiplierFormula,
        damage_formula: DamageFormula,
        start_team: Optional[PokemonTeam] = None,
    ) -> tuple[PokemonTeam, float, int, int]:
        current = (
            start_team.copy() if start_team is not None else self._random_team(pokemons)
        )
        current_fit = self._fitness(
            current, opponents, cache, type_multiplier_formula, damage_formula
        )
        evaluations += 1

        local_best = current.copy()
        local_best_fit = current_fit

        T = self.T0
        no_improve = 0

        while T > self.Tmin and evaluations < self.max_evaluations:
            for _ in range(self.iters_per_temp):
                if evaluations >= self.max_evaluations:
                    break

                candidate = current.generate_team_with_random_replacement(
                    pokemons,
                    replacements=self.neighbor_replacements,
                    unique_types=self.unique_types,
                )
                cand_fit = self._fitness(
                    candidate, opponents, cache, type_multiplier_formula, damage_formula
                )
                evaluations += 1

                delta = cand_fit - current_fit
                accepted = self._accept(rng, delta, T)

                if accepted:
                    current = candidate
                    current_fit = cand_fit

                if current_fit > local_best_fit:
                    local_best = current.copy()
                    local_best_fit = current_fit
                    no_improve = 0
                else:
                    no_improve += 1

                step += 1
                history.append(
                    SAHistoryEntry(step, T, current_fit, local_best_fit, accepted)
                )

                if self.patience is not None and no_improve >= self.patience:
                    return local_best, local_best_fit, evaluations, step

            T *= self.alpha

        return local_best, local_best_fit, evaluations, step

    def solve(
        self,
        pokemons: DataFrame[PokemonSchema],
        opponents: Optional[list[PokemonTeam]] = None,
        start_team: Optional[PokemonTeam] = None,
        type_multiplier_formula: TypeMultiplierFormula = multiply_type_multiplier,
        damage_formula: DamageFormula = damage_attack_devide_defense,
    ) -> tuple[PokemonTeam, float, list[SAHistoryEntry], list[PokemonTeam]]:
        rng = np.random.default_rng(self.seed)

        # If not opponents given, generate them
        opponents = (
            opponents if opponents is not None else self._generate_opponents(pokemons)
        )

        cache: dict[tuple[str, ...], float] = {}
        history: list[SAHistoryEntry] = []

        # If not start_team given, best_team starts as random team
        best_team = (
            start_team.copy() if start_team is not None else self._random_team(pokemons)
        )
        best_fit = self._fitness(
            best_team, opponents, cache, type_multiplier_formula, damage_formula
        )
        evaluations = 1
        step = 0

        restarts = 1 if start_team is not None else self.restarts + 1

        for run_idx in range(restarts):
            run_start = (
                start_team if (run_idx == 0 and start_team is not None) else None
            )

            team_r, fit_r, evaluations, step = self._run_once(
                pokemons,
                opponents,
                rng,
                cache,
                history,
                evaluations,
                step,
                type_multiplier_formula,
                damage_formula,
                start_team=run_start,
            )

            if fit_r > best_fit:
                best_team, best_fit = team_r.copy(), fit_r

            if evaluations >= self.max_evaluations:
                break

        return best_team, best_fit, history, opponents
