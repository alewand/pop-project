def min_type_multiplier(firstEffectivness: float, secondEffectivness: float) -> float:
    return min(firstEffectivness, secondEffectivness)


def max_type_multiplier(firstEffectivness: float, secondEffectivness: float) -> float:
    return max(firstEffectivness, secondEffectivness)


def multiply_type_multiplier(
    firstEffectivness: float, secondEffectivness: float
) -> float:
    return firstEffectivness * secondEffectivness


def damage_attack_minus_defense(
    combined_attack: int, combined_defense: int, type_multiplier: float
) -> int:
    return int(round((combined_attack * type_multiplier) - combined_defense, 1))


def damage_attack_devide_defense(
    combined_attack: int, combined_defense: int, type_multiplier: float
) -> int:
    if combined_defense == 0:
        return int(round(combined_attack * type_multiplier, 1))
    return int(round((combined_attack / combined_defense) * type_multiplier, 1))
