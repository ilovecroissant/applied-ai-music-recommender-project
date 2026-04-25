import pytest
from src.recommender import Song, UserProfile, Recommender, recommend_songs

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_explain_mentions_genre_and_mood_when_matching():
    """Explanation must name specific matching attributes, not just emit a fallback."""
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    pop_song = rec.songs[0]  # genre=pop, mood=happy

    explanation = rec.explain_recommendation(user, pop_song)
    assert "pop" in explanation.lower()
    assert "happy" in explanation.lower()


def test_recommend_with_scores_confidence_in_range():
    """All confidence scores must be in [0.0, 1.0] — the scoring formula guarantees this."""
    user = UserProfile(
        favorite_genre="lofi",
        favorite_mood="chill",
        target_energy=0.4,
        likes_acoustic=True,
    )
    rec = make_small_recommender()
    results = rec.recommend_with_scores(user, k=2)

    assert len(results) == 2
    for song, confidence in results:
        assert 0.0 <= confidence <= 1.0, f"Confidence {confidence:.3f} out of range for {song.title!r}"


def test_acoustic_preference_promotes_acoustic_song():
    """A user who likes acoustic should rank the lofi/acoustic song above the pop/electric one."""
    user = UserProfile(
        favorite_genre="any",
        favorite_mood="any",
        target_energy=0.5,
        likes_acoustic=True,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    # Chill Lofi Loop has acousticness=0.9; Test Pop Track has acousticness=0.2
    assert results[0].title == "Chill Lofi Loop"


def test_recommend_k_larger_than_catalog_returns_all():
    """Asking for more songs than exist should return the whole catalog, not crash."""
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=100)

    assert len(results) == len(rec.songs)


def test_recommend_songs_raises_on_missing_fields():
    """The functional interface must raise ValueError for incomplete user_prefs."""
    bad_prefs = {"favorite_genre": "pop"}  # missing required fields
    songs = [{"id": 1, "title": "X", "artist": "Y", "genre": "pop", "mood": "happy",
               "energy": 0.8, "valence": 0.8, "danceability": 0.8,
               "acousticness": 0.2, "instrumentalness": 0.05, "speechiness": 0.05}]
    with pytest.raises(ValueError, match="missing required fields"):
        recommend_songs(bad_prefs, songs)
