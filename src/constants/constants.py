from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = PROJECT_ROOT / "data" / "datasets"
POKEMON_DATA_SET_PATH = DATASETS_DIR / "pokemon.csv"
COMPLETE_POKEMON_DATA_SET_PATH = DATASETS_DIR / "complete_pokemon.csv"

TEAM_SIZE = 6
POKEMON_TO_REPLACE_AMOUNT = 2

ID = "pokedex_number"
NAME = "name"
FIRST_TYPE = "type1"
SECOND_TYPE = "type2"

TYPES = [
    "bug",
    "dark",
    "dragon",
    "electric",
    "fairy",
    "fighting",
    "fire",
    "flying",
    "ghost",
    "grass",
    "ground",
    "ice",
    "normal",
    "poison",
    "psychic",
    "rock",
    "steel",
    "water",
]

HP = "hp"
ATTACK = "attack"
SPECIAL_ATTACK = "sp_attack"
DEFENSE = "defense"
SPECIAL_DEFENSE = "sp_defense"

STATS_COLS = [
    ATTACK,
    SPECIAL_ATTACK,
    DEFENSE,
    SPECIAL_DEFENSE,
]

SPEED = "speed"

AGAINST = "against_"
AGAINST_COLS = [f"{AGAINST}{type_name}" for type_name in TYPES]

IS_LEGENDARY = "is_legendary"


EXCLUDED_COLS = [
    "abilities",
    "base_egg_steps",
    "base_happiness",
    "base_total",
    "capture_rate",
    "classfication",
    "experience_growth",
    "height_m",
    "japanese_name",
    "percentage_male",
    "weight_kg",
    "generation",
]

ID_COMPLETE = "Number"
FINAL_EVOLUTION_COMPLETE = "Final Evolution"

CURRENT = "current"
OPPONENT = "opponent"

DEFAULT_POPULATION_SIZE = 5
DEFAULT_GENERATIONS = 20
DEFAULT_MUTATION_RATE = 0.6
DEFAULT_ELITE_SIZE = 1
DEFAULT_TOURNAMENT_SIZE = 3
DEFAULT_OPPONENTS_LIMIT = 100

MAX_STEPS_PER_BATTLE = 1000
