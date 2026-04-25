"""
Command line runner for the Music Recommender Simulation.

Runs three taste profiles through the recommender, then calls the Gemini RAG
layer to generate a personalized narrative for each profile.

Requires a valid GEMINI_API_KEY in .env (see .env.example).
If the key is missing the app falls back to the standard score output.
"""

import os
import logging

from .recommender import load_songs, recommend_songs
from .rag import generate_rag_recommendation

_HERE = os.path.dirname(os.path.abspath(__file__))

# --- Logging setup -----------------------------------------------------------
# Writes INFO+ to the console and to recommender.log in the project root.
_log_file = os.path.join(_HERE, "..", "recommender.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(_log_file, encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def main() -> None:
    songs = load_songs(os.path.join(_HERE, "..", "data", "songs.csv"))
    logger.info("Loaded %d songs from catalog", len(songs))

    # Taste profile: "Late-night Study Session"
    late_night_study = {
        "favorite_genre":          "lofi",
        "favorite_mood":           "focused",
        "target_energy":           0.40,
        "likes_acoustic":          True,
        "target_valence":          0.58,
        "target_danceability":     0.55,
        "target_instrumentalness": 0.50,
        "target_speechiness":      0.04,
    }

    # Taste profile: "High-Energy Pop"
    high_energy_pop = {
        "favorite_genre":          "pop",
        "favorite_mood":           "happy",
        "target_energy":           0.90,
        "likes_acoustic":          False,
        "target_valence":          0.90,
        "target_danceability":     0.85,
        "target_instrumentalness": 0.05,
        "target_speechiness":      0.08,
    }

    # Taste profile: "Deep Intense Rock"
    deep_intense_rock = {
        "favorite_genre":          "rock",
        "favorite_mood":           "angry",
        "target_energy":           0.95,
        "likes_acoustic":          False,
        "target_valence":          0.20,
        "target_danceability":     0.40,
        "target_instrumentalness": 0.15,
        "target_speechiness":      0.06,
    }

    profiles = [
        ("Late-night Study Session", late_night_study),
        ("High-Energy Pop",          high_energy_pop),
        ("Deep Intense Rock",        deep_intense_rock),
    ]

    for label, user_prefs in profiles:
        print(f"\n{'='*55}")
        print(f"  Profile: {label}")
        print(f"{'='*55}")

        logger.info("Running profile: %r", label)

        # --- Retrieval step: score and rank songs from the catalog -----------
        try:
            recommendations = recommend_songs(user_prefs, songs, k=5)
        except ValueError as exc:
            logger.error("Invalid user_prefs for profile %r: %s", label, exc)
            print(f"[ERROR] Skipping profile — {exc}")
            continue

        print("\nTop retrieved songs:\n")
        for song, score, explanation in recommendations:
            print(f"  {song['title']} by {song['artist']}  —  score: {score:.2f}")
            print(f"  Because: {explanation}\n")

        # --- Generation step: Gemini turns retrieved songs into a narrative --
        print("[AI Recommendation]")
        try:
            narrative = generate_rag_recommendation(label, user_prefs, recommendations)
            print(narrative)
            logger.info("RAG narrative generated for profile: %r", label)
        except EnvironmentError as exc:
            logger.warning("RAG skipped for %r: %s", label, exc)
            print(f"(RAG unavailable — {exc})")
        except Exception as exc:
            logger.error("RAG failed for profile %r: %s", label, exc, exc_info=True)
            print(f"(RAG error — {exc})")


if __name__ == "__main__":
    main()
