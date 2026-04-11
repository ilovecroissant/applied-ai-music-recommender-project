from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py

    Core fields (required):
      favorite_genre       — preferred genre string, e.g. "lofi"
      favorite_mood        — preferred mood string, e.g. "focused"
      target_energy        — ideal energy level (0.0–1.0)
      likes_acoustic       — True if the user prefers acoustic-leaning tracks

    Extended fields (optional, default to neutral midpoints):
      target_valence       — ideal positiveness / happiness (0.0–1.0)
      target_danceability  — ideal danceability (0.0–1.0)
      target_instrumentalness — ideal instrumental vs. vocal ratio (0.0–1.0)
      target_speechiness   — ideal spoken-word presence (0.0–1.0)
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_valence: float = 0.5
    target_danceability: float = 0.5
    target_instrumentalness: float = 0.1
    target_speechiness: float = 0.05

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv

    int_fields = {"id", "tempo_bpm"}
    float_fields = {"energy", "valence", "danceability", "acousticness", "instrumentalness", "speechiness"}

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field in int_fields:
                row[field] = int(row[field])
            for field in float_fields:
                row[field] = float(row[field])
            songs.append(row)
    return songs

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    def score(song: Dict) -> float:
        genre_score        = 1.0 if song["genre"] == user_prefs.get("favorite_genre") else 0.0
        mood_score         = 1.0 if song["mood"] == user_prefs.get("favorite_mood") else 0.0
        energy_score       = 1.0 - abs(song["energy"] - user_prefs.get("target_energy", 0.5))
        acoustic_score     = song["acousticness"] if user_prefs.get("likes_acoustic") else (1.0 - song["acousticness"])
        valence_score      = 1.0 - abs(song["valence"] - user_prefs.get("target_valence", 0.5))
        dance_score        = 1.0 - abs(song["danceability"] - user_prefs.get("target_danceability", 0.5))
        instrumental_score = 1.0 - abs(song["instrumentalness"] - user_prefs.get("target_instrumentalness", 0.1))
        speech_score       = 1.0 - abs(song["speechiness"] - user_prefs.get("target_speechiness", 0.05))
        return (0.15 * genre_score          # halved (was 0.30)
                + 0.25 * mood_score
                + 0.30 * energy_score          # doubled (was 0.15)
                + 0.10 * acoustic_score
                + 0.08 * valence_score
                + 0.06 * dance_score
                + 0.04 * instrumental_score
                + 0.02 * speech_score)

    def explain(song: Dict, s: float) -> str:
        reasons = []
        if song["genre"] == user_prefs.get("favorite_genre"):
            reasons.append(f"matches your favorite genre ({song['genre']})")
        if song["mood"] == user_prefs.get("favorite_mood"):
            reasons.append(f"mood is {song['mood']}")
        if user_prefs.get("likes_acoustic") and song["acousticness"] >= 0.6:
            reasons.append("has an acoustic texture you like")
        if not reasons:
            reasons.append(f"overall score {s:.2f} fits your taste profile")
        return ", ".join(reasons).capitalize()

    scored = sorted(songs, key=score, reverse=True)
    return [(song, score(song), explain(song, score(song))) for song in scored[:k]]

def score_song(user, song):
    genre_score        = 1.0 if song.genre == user.favorite_genre else 0.0
    mood_score         = 1.0 if song.mood == user.favorite_mood else 0.0
    energy_score       = 1.0 - abs(song.energy - user.target_energy)
    acoustic_score     = song.acousticness if user.likes_acoustic else (1.0 - song.acousticness)
    valence_score      = 1.0 - abs(song.valence - user.target_valence)
    dance_score        = 1.0 - abs(song.danceability - user.target_danceability)
    instrumental_score = 1.0 - abs(song.instrumentalness - user.target_instrumentalness)
    speech_score       = 1.0 - abs(song.speechiness - user.target_speechiness)

    # Weights sum to 1.0; energy doubled (0.30), genre halved (0.15) to test sensitivity
    return (0.15 * genre_score          # halved (was 0.30)
            + 0.25 * mood_score
            + 0.30 * energy_score          # doubled (was 0.15)
            + 0.10 * acoustic_score
            + 0.08 * valence_score
            + 0.06 * dance_score
            + 0.04 * instrumental_score
            + 0.02 * speech_score)

def recommended(user, songs, k):
    scored = [(song, score_song(user, song)) for song in songs]
    scored.sort(key=lambda x: (-x[1], x[0].id)) 
    return [song for song, _ in scored[:k]]