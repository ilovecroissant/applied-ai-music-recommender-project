"""
RAG (Retrieval-Augmented Generation) layer for the music recommender.

Flow:
  1. Retrieve  — recommend_songs() scores and ranks songs from the catalog
  2. Augment   — retrieved songs are packed as grounded context for Gemini
  3. Generate  — Gemini writes a personalized recommendation narrative

This module only handles step 3. The retrieval is done in main.py so that
the two concerns stay decoupled and this file is easy to test in isolation.
"""

import os
import logging
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load .env from the project root (one level above this file's directory)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logger = logging.getLogger(__name__)

_MODEL = "gemini-2.5-flash"

_SYSTEM_PROMPT = (
    "You are a knowledgeable, friendly music guide. "
    "Be concise and specific — always reference actual song titles and audio features. "
    "Never invent songs or artists that were not provided to you."
)


def _build_song_context(recommendations: list) -> str:
    """Format pre-scored songs into structured text Gemini can reason over."""
    lines = []
    for i, (song, score, explanation) in enumerate(recommendations, 1):
        lines.append(
            f"{i}. \"{song['title']}\" by {song['artist']}\n"
            f"   Genre: {song['genre']} | Mood: {song['mood']} | "
            f"Energy: {song['energy']:.2f} | Compatibility: {score:.2f}\n"
            f"   Matched because: {explanation}"
        )
    return "\n".join(lines)


def generate_rag_recommendation(profile_name: str, user_prefs: dict, recommendations: list) -> str:
    """
    Call Gemini to produce a personalized recommendation narrative.

    Parameters
    ----------
    profile_name    : human-readable label for the listening session
    user_prefs      : dict of user taste preferences (same shape as main.py profiles)
    recommendations : list of (song_dict, score, explanation) tuples from recommend_songs()

    Returns
    -------
    str — Gemini's generated recommendation text

    Raises
    ------
    EnvironmentError  if GEMINI_API_KEY is not set in .env or environment
    ValueError        if recommendations list is empty
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your-gemini-api-key-here":
        raise EnvironmentError(
            "GEMINI_API_KEY is not configured.\n"
            "Edit your .env file and set:  GEMINI_API_KEY=your-actual-key"
        )

    if not recommendations:
        raise ValueError("recommendations list is empty — nothing to generate from")

    client = genai.Client(api_key=api_key)

    song_context = _build_song_context(recommendations)
    user_context = (
        f"Preferred genre    : {user_prefs.get('favorite_genre', 'any')}\n"
        f"Preferred mood     : {user_prefs.get('favorite_mood', 'any')}\n"
        f"Target energy (0-1): {user_prefs.get('target_energy', 0.5)}\n"
        f"Likes acoustic     : {user_prefs.get('likes_acoustic', False)}"
    )

    prompt = (
        f'You are helping curate a "{profile_name}" listening session.\n\n'
        f"User taste profile:\n{user_context}\n\n"
        f"Songs retrieved from the catalog (ranked by compatibility score):\n{song_context}\n\n"
        "Write a warm, personalized recommendation (4-6 sentences) that:\n"
        "- Opens by capturing what the user is in the mood for\n"
        "- Highlights 2-3 of the top songs by name and explains specifically why each fits\n"
        "- Uses actual song data (genre, mood, energy) to justify your picks\n"
        "- Closes with an encouraging note\n\n"
        "Only reference songs from the retrieved list above."
    )

    logger.info(
        "RAG generate: profile=%r | retrieved=%d songs | model=%s",
        profile_name, len(recommendations), _MODEL,
    )

    response = client.models.generate_content(
        model=_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=_SYSTEM_PROMPT,
            max_output_tokens=2048,
            temperature=0.7,
        ),
    )

    logger.info(
        "RAG complete: profile=%r | input_tokens=%s | output_tokens=%s",
        profile_name,
        getattr(response.usage_metadata, "prompt_token_count", "n/a"),
        getattr(response.usage_metadata, "candidates_token_count", "n/a"),
    )

    return response.text
