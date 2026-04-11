# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python -m src.main

# Run all tests
pytest

# Run a single test
pytest tests/test_recommender.py::test_recommend_returns_songs_sorted_by_score
```

## Architecture

This is a student project: a small music recommender simulation. There are two parallel implementations of the recommendation logic.

**Functional interface** (used by [src/main.py](src/main.py)):
- `load_songs(csv_path)` — reads [data/songs.csv](data/songs.csv) into a list of dicts
- `recommend_songs(user_prefs, songs, k)` — scores and ranks songs, returns `List[Tuple[dict, float, str]]` where each tuple is `(song, score, explanation)`

**OOP interface** (used by [tests/test_recommender.py](tests/test_recommender.py)):
- `Song` dataclass — fields: `id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, acousticness`
- `UserProfile` dataclass — fields: `favorite_genre, favorite_mood, target_energy, likes_acoustic`
- `Recommender(songs)` class — `recommend(user, k)` returns `List[Song]` sorted by score; `explain_recommendation(user, song)` returns a non-empty string

Both interfaces live in [src/recommender.py](src/recommender.py). The `main.py` runner uses dict-based songs while the tests use `Song` dataclass instances — keep both working.

The song catalog is [data/songs.csv](data/songs.csv) (10 songs across genres: pop, lofi, rock, ambient, jazz, synthwave, indie pop).

Student deliverables also include completing [model_card.md](model_card.md) and updating [README.md](README.md) with experiment notes and reflection.
