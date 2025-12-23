from classes import PokemonTeam
from data import get_pokemons

if __name__ == "__main__":
    pokemons = get_pokemons()
    print(f"Total Pokémons fetched: {len(pokemons)}")
    team = PokemonTeam.generate_team(pokemons)
    print(team)
