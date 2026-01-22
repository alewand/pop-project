import numpy as np
from pandera.typing import DataFrame
from pydantic import BaseModel, ConfigDict, Field, model_validator

from classes import PokemonTeam
from constants import (
    DEFAULT_ELITE_SIZE,
    DEFAULT_GENERATIONS,
    DEFAULT_MUTATION_RATE,
    DEFAULT_OPPONENTS_LIMIT,
    DEFAULT_POPULATION_SIZE,
    DEFAULT_TOURNAMENT_SIZE,
    POKEMON_TO_REPLACE_AMOUNT,
)
from schemas import PokemonSchema
from simulation import (
    DamageFormula,
    TypeMultiplierFormula,
    damage_attack_devide_defense,
    multiply_type_multiplier,
    simulate_battle,
)


class EvolutionaryAlgorithmPokemonSolver(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    population_size: int = Field(
        default=DEFAULT_POPULATION_SIZE,
        gt=0,
    )

    elite_size: int = Field(
        default=DEFAULT_ELITE_SIZE,
        ge=0,
    )

    generations: int = Field(
        default=DEFAULT_GENERATIONS,
        gt=0,
    )

    tournament_size: int = Field(
        default=DEFAULT_TOURNAMENT_SIZE,
        gt=0,
    )

    mutation_rate: float = Field(
        default=DEFAULT_MUTATION_RATE,
        ge=0.0,
        le=1.0,
    )

    mutation_replacements: int = Field(
        default=POKEMON_TO_REPLACE_AMOUNT,
        gt=0,
    )

    opponents_limit: int | None = Field(
        default=DEFAULT_OPPONENTS_LIMIT,
        gt=0,
    )

    unique_types: bool = Field(
        default=True,
    )

    @model_validator(mode="after")
    def check_elite_size(self) -> "EvolutionaryAlgorithmPokemonSolver":
        if self.elite_size >= self.population_size:
            raise ValueError("elite_size must be smaller than population_size")

        if self.tournament_size > self.population_size:
            raise ValueError(
                "tournament_size must be smaller than or equal to population_size"
            )

        return self

    def _initialize_population(
        self, pokemons: DataFrame[PokemonSchema]
    ) -> list[PokemonTeam]:
        population: list[PokemonTeam] = []

        for _ in range(self.population_size):
            population.append(
                PokemonTeam.generate_team(
                    pokemons,
                    unique_types=self.unique_types,
                )
            )

        return population

    def _tournament_select(
        self,
        rng: np.random.Generator,
        population: list[PokemonTeam],
        fitnesses: list[float],
    ) -> PokemonTeam:
        selected_indexes = rng.choice(
            self.population_size, size=self.tournament_size, replace=False
        )

        selected_teams = [population[int(i)] for i in selected_indexes]
        selected_fitnesses = [fitnesses[int(i)] for i in selected_indexes]

        best_fitness_index = int(np.argmax(selected_fitnesses))
        return selected_teams[best_fitness_index].copy()

    def _mutate(
        self, team: PokemonTeam, pokemons: DataFrame[PokemonSchema]
    ) -> PokemonTeam:
        return team.generate_team_with_random_replacement(
            pokemons, self.mutation_replacements, self.unique_types
        )

    def _evaluate(
        self,
        team: PokemonTeam,
        opponents: list[PokemonTeam],
        type_multiplier_formula: TypeMultiplierFormula = multiply_type_multiplier,
        damage_formula: DamageFormula = damage_attack_devide_defense,
    ) -> float:
        team_remaining_hps_percentage: list[float] = []

        for opponent in opponents:
            team_remaining_hp = simulate_battle(
                team,
                opponent,
                type_multiplier_formula,
                damage_formula,
            )

            team_remaining_hps_percentage.append(
                team_remaining_hp / sum(team.get_hps())
            )

        return float(np.mean(np.array(team_remaining_hps_percentage, dtype=float)))

    def solve(
        self,
        pokemons: DataFrame[PokemonSchema],
        opponents: list[PokemonTeam] | None = None,
        type_multiplier_formula: TypeMultiplierFormula = multiply_type_multiplier,
        damage_formula: DamageFormula = damage_attack_devide_defense,
    ) -> tuple[
        PokemonTeam, float, list[list[tuple[PokemonTeam, float]]], list[PokemonTeam]
    ]:
        rng = np.random.default_rng()
        population = self._initialize_population(pokemons)
        if opponents is None:
            opponents = PokemonTeam.generate_unique_teams(
                pokemons,
                self.opponents_limit,
                self.opponents_limit * 10 if self.opponents_limit is not None else None,
                population[0].get_size(),
                self.unique_types,
            )

        best_team = population[0].copy()
        best_fitness = float("-inf")

        for team in population:
            fitness = self._evaluate(
                team, opponents, type_multiplier_formula, damage_formula
            )

            if fitness > best_fitness:
                best_fitness = fitness
                best_team = team.copy()

        history: list[list[tuple[PokemonTeam, float]]] = []

        for _ in range(self.generations):
            fitnesses: list[float] = []

            for team in population:
                fitness = self._evaluate(
                    team,
                    opponents,
                    type_multiplier_formula,
                    damage_formula,
                )

                fitnesses.append(fitness)

            history.append(list(zip(population, fitnesses, strict=True)))

            scored = sorted(
                zip(fitnesses, population, strict=True),
                key=lambda pair: pair[0],
                reverse=True,
            )

            sorted_fitnesses, sorted_population = zip(*scored, strict=True)

            if sorted_fitnesses[0] > best_fitness:
                best_fitness = sorted_fitnesses[0]
                best_team = sorted_population[0].copy()

            new_population: list[PokemonTeam] = [
                team.copy() for team in sorted_population[: self.elite_size]
            ]

            for _ in range(self.population_size - self.elite_size):
                selected_team = self._tournament_select(
                    rng, list(sorted_population), list(sorted_fitnesses)
                )

                if rng.random() < self.mutation_rate:
                    selected_team = self._mutate(selected_team, pokemons)

                new_population.append(selected_team)

            population = new_population

        return best_team, best_fitness, history, opponents
