POKEMON_DATA_SET_PATH = "data/sets/pokemon.csv"
COMPLETE_POKEMON_DATA_SET_PATH = "data/sets/complete_pokemon.csv"

TEAM_SIZE = 6
POKEMON_TO_REPLACE_AMOUNT = 3

ID_COL = "pokedex_number"
NAME_COL = "name"
FIRST_TYPE_COL = "type1"
SECOND_TYPE_COL = "type2"
ATTACK_COL = "attack"
SPECIAL_ATTACK_COL = "sp_attack"
DEFENSE_COL = "defense"
SPECIAL_DEFENSE_COL = "sp_defense"
AGAINST_COL = "against_"
HP_COL = "hp"
SPEED_COL = "speed"
IS_LEGENDARY_COL = "is_legendary"

STATS_COLS = [
    ATTACK_COL,
    SPECIAL_ATTACK_COL,
    DEFENSE_COL,
    SPECIAL_DEFENSE_COL,
]

EXCLUDED_PARAMETERS = ["abilities",
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
                       "generation"]

NUMBER_COL = "Number"
FINAL_EVOLUTION_COL = "Final Evolution"

CURRENT = "current"
OPPONENT = "opponent"
