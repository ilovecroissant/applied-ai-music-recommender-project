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
    late_night_study = {
        "favorite_genre":          "lofi",
        "favorite_mood":           "focused",
        "target_energy":           0.40,   # prefer quieter, low-intensity tracks
        "likes_acoustic":          True,   # acoustic textures over electronic production
        "target_valence":          0.58,   # slightly positive but not upbeat
        "target_danceability":     0.55,   # moderate groove is fine; not dance-floor ready
        "target_instrumentalness": 0.50,   # lean instrumental — fewer distracting lyrics
        "target_speechiness":      0.04,   # minimal spoken word / rap
    }

    # Taste profile: "High-Energy Pop"
    # A listener who wants upbeat, danceable pop bangers —
    # high energy, high valence, electronic production, and a happy mood.
    high_energy_pop = {
        "favorite_genre":          "pop",
        "favorite_mood":           "happy",
        "target_energy":           0.90,   # loud and punchy
        "likes_acoustic":          False,  # electronic production preferred
        "target_valence":          0.90,   # as upbeat and positive as possible
        "target_danceability":     0.85,   # made for the dance floor
        "target_instrumentalness": 0.05,   # wants vocals front and center
        "target_speechiness":      0.08,   # sung lyrics, not rap-heavy
    }

    # Taste profile: "Deep Intense Rock"
    # A listener who wants raw, heavy guitar-driven tracks —
    # high energy, low valence, low acousticness (electric/distorted), and an angry mood.
    deep_intense_rock = {
        "favorite_genre":          "rock",
        "favorite_mood":           "angry",
        "target_energy":           0.95,   # maximum intensity
        "likes_acoustic":          False,  # electric guitars, not acoustic
        "target_valence":          0.20,   # dark and brooding tone
        "target_danceability":     0.40,   # headbang-worthy, not club-ready
        "target_instrumentalness": 0.15,   # some vocals but guitar solos welcome
        "target_speechiness":      0.06,   # sung/screamed lyrics, not spoken word
    }

    profiles = [
        ("Late-night Study Session", late_night_study),
        ("High-Energy Pop",          high_energy_pop),
        ("Deep Intense Rock",        deep_intense_rock),
    ]

    for label, user_prefs in profiles:
        print(f"\n{'='*50}")
        print(f"Profile: {label}")
        print(f"{'='*50}")
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
