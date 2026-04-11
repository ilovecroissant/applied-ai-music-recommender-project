"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import os
from .recommender import load_songs, recommend_songs

_HERE = os.path.dirname(os.path.abspath(__file__))

def main() -> None:
    songs = load_songs(os.path.join(_HERE, "..", "data", "songs.csv"))
    print(f"Loaded songs: {len(songs)}")

    # Taste profile: "Late-night study session"
    # A listener who wants calm, instrumental-leaning tracks to stay focused —
    # low energy, high acousticness, minimal vocals, and a neutral-to-positive mood.
    user_prefs = {
        "favorite_genre":          "lofi",
        "favorite_mood":           "focused",
        "target_energy":           0.40,   # prefer quieter, low-intensity tracks
        "likes_acoustic":          True,   # acoustic textures over electronic production
        "target_valence":          0.58,   # slightly positive but not upbeat
        "target_danceability":     0.55,   # moderate groove is fine; not dance-floor ready
        "target_instrumentalness": 0.50,   # lean instrumental — fewer distracting lyrics
        "target_speechiness":      0.04,   # minimal spoken word / rap
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()
