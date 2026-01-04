# Projekt na POP (Przeszukiwanie i optymalizacja), Politechnika Warszawska
## Tytuł: Catch'em All
### By Bartosz Psik & Amadeusz Lewandowski

Celem projektu jest opracowanie i analiza mechanizmu uzyskania najlepszej możliwej drużyny sześciu pokemonów przy pomocy algorytmów przeszukujących przestrzeń.

Szczegóły i dokumentację można znaleźć [w tym miejscu](documentation.pdf).

Projekt został stworzony przy pomocy menadżera pakietów [uv](https://github.com/astral-sh/uv) i rekomenduje się jego instalację w celu uruchomienia.

## Instrukcja uruchomienia - Linux

1. Sklonowanie repozytorium
```bash
git clone https://github.com/alewand/pop-project.git
```
2. Instalacja uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
3. Pobranie odpowiednich bibliotek
```bash
uv sync
```
4. Uruchomienie projektu
```bash
uv run src/main.py
```

## Instrukcja uruchomienia - Windows

1. Sklonowanie repozytorium
```bash
git clone https://github.com/alewand/pop-project.git
```

2. Stworzenie wirtualnego środowiska
```bash
python -m venv .venv
```

3. Uruchomienie wirtualnego środowiska
```bash
.\venv\Scripts\activate
```

4. Instalacja wymaganych bibliotek
```bash
pip install -r .\requirements.txt
pip install -r .\requirements-dev.txt
```

5. Uruchomienie aplikacji
```bash
python .\src/main.py
```
