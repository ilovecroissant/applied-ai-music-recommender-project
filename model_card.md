# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatcher 1.0**

---

## 2. Intended Use  

VibeMatcher is designed to suggest songs that fit a user's mood and listening habits. You tell it your favorite genre, favorite mood, how energetic you want the music, and whether you like acoustic sounds. It gives you a ranked list of songs from a small catalog.

This is a classroom simulation, not a production app. It is meant to show how a basic recommender system works, not to replace Spotify.

---

## 3. How the Model Works  

Each song gets a score between 0 and 1 based on how well it matches your preferences. The score is a weighted average of eight comparisons:

- **Genre match** — does the song's genre match your favorite? (15% of the score)
- **Mood match** — does the mood label match? (25%)
- **Energy closeness** — how close is the song's energy to your target? (30%)
- **Acoustic preference** — does the song's acoustic level line up with whether you like acoustic music? (10%)
- **Valence closeness** — how close is the song's positivity to your preference? (8%)
- **Danceability closeness** — how close is its danceability? (6%)
- **Instrumentalness closeness** — how much of the song is instrumental vs. vocal? (4%)
- **Speechiness closeness** — how much spoken word is in the track? (2%)

Songs are ranked highest to lowest by score. The top results are returned with a short explanation of why each one matched.

The main change from the starter version was doubling the energy weight from 0.15 to 0.30 and halving the genre weight from 0.30 to 0.15. This makes energy level the strongest single signal, which felt more realistic — people often care more about vibe than genre label.

---

## 4. Data  

The catalog has 20 songs. Each song has a title, artist, genre, mood, and seven numeric features (energy, tempo, valence, danceability, acousticness, instrumentalness, speechiness).

Genres in the catalog: pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, classical, r&b, metal, folk, country, reggae, drum and bass, bossa nova, blues.

Moods in the catalog: happy, chill, intense, relaxed, moody, focused, energetic, melancholic, romantic, angry, nostalgic, uplifting, peaceful, sad, euphoric, dreamy.

The original starter had 10 songs. 10 more were added to cover a wider range of genres and moods.

Some tastes are still missing — there is no Latin pop, K-pop, gospel, or electronic dance music beyond drum and bass. The catalog is also too small to give meaningfully diverse results if your preferences are niche.

---

## 5. Strengths  

The system works best when a user has clear, strong preferences. If you want high-energy, intense-mood rock, the scoring pushes the right songs to the top quickly.

The energy weight being the largest single factor (30%) tends to produce results that feel right — a high-energy user gets energetic songs regardless of genre, which matches how many people actually listen.

Mood matching (25%) also works well when the catalog has songs tagged with that exact mood. The lofi-focused and ambient-chill songs cluster together nicely for a user studying or relaxing.

---

## 6. Limitations and Bias 

The acoustic preference is a yes/no flag (`likes_acoustic: true/false`). A user who is indifferent to acoustic texture must still be bucketed into True or False. There is no neutral option. Whichever they pick, mid-acousticness songs (0.4–0.6) score around 0.5, but high-acoustic songs (0.91–0.96) swing to either a high or low acoustic score depending on the flag.

The energy floor in the catalog is ~0.28 (Spacewalk Thoughts). A user who sets `target_energy=0.1` can never score above 0.82 on energy — they are structurally penalized through no fault of the model logic. The catalog simply does not have songs quiet enough.

Genre and mood matching are binary (exact match or zero). There is no concept of "similar genres" — metal and rock are completely unrelated to the model even though many listeners enjoy both.

The catalog skews toward Western genres. Users who prefer music outside that range will find poor coverage.

---

## 7. Evaluation  

I tested two profiles: a lofi fan (low energy, focused mood) and a rock fan (high energy, intense mood). For the lofi fan, I checked that the top result had low energy and matched the focused mood. For the rock fan, Storm Runner and Gym Hero came out on top, which made sense.

What surprised me was that the energy weight (0.30) is higher than genre (0.15), so sometimes a song from the wrong genre but closer in energy scored higher than a genre match — which actually felt realistic. A lofi listener might enjoy an ambient track more than a lofi track that is too upbeat.

I also ran the pytest suite to confirm that results are sorted correctly by score and that the explain function always returns a non-empty string.

---

## 8. Future Work  

- **Similar-genre groups**: Instead of exact genre matching, songs in related genres (like rock and metal, or lofi and ambient) could get partial credit.
- **Neutral acoustic option**: Replace the yes/no acoustic flag with a 0–1 target, the same way energy works.
- **Better explanations**: The current explanation just lists matching labels. It could say something like "this song is 0.05 away from your target energy."
- **Diversity in results**: Right now the top 5 could all be from the same genre. A re-ranking step could spread results across genres.
- **More songs**: A catalog of 20 is enough to learn from but too small for real variety. Adding 100+ songs would make the scoring differences more meaningful.

---

## 9. Personal Reflection

### Limitations and Biases

VibeMatcher has several structural biases baked in before any user runs it. The catalog of 20 songs skews heavily toward Western genres — there is no Latin pop, K-pop, or gospel, so users with those tastes are underserved from the start. Genre and mood matching are binary: metal and rock share no credit, and "melancholic" and "sad" are treated as completely different labels. The acoustic preference is a yes/no flag, so listeners who are indifferent to acoustic texture must still choose a side, which skews scoring for songs with mid-range acousticness. The energy floor in the catalog (~0.28) means a user asking for very quiet music can never reach a perfect score — not because the logic is wrong, but because the data does not go that low. Finally, the weights themselves are a bias: setting energy at 0.30 is an editorial decision that says "vibe matters more than genre," which will feel right for some users and wrong for others.

### Potential for Misuse

At the scale of this project the misuse risk is low — it is a simulation with a tiny catalog and no user data. But the same design pattern, applied at a larger scale, has real risk. A weighted recommender can reinforce filter bubbles: if a user always scores "rock" at 1.0 and everything else at 0.0, the system will never surface anything outside that box. At Spotify scale that kind of narrowing can reduce exposure to unfamiliar music for years. A second risk is the RAG layer: Gemini is instructed to reference only retrieved songs, but if the retriever surfaces low-quality matches, the LLM will describe them confidently anyway — the language sounds authoritative even when the underlying match is weak. To prevent these: a diversity re-ranking step (force at least one song from a different genre into the top 5) would address filter-bubble narrowing, and a minimum-score threshold (do not pass songs below 0.50 to Gemini) would prevent the LLM from narrating poor matches as if they were great fits.

### Surprises While Testing Reliability

The biggest surprise was how confident the system sounds when it is wrong. When a rock fan got Iron Collapse (metal) as the top result, the Gemini narrative explained it as a compelling cross-genre match — and the explanation was genuinely persuasive. The model was not lying; the audio features did align. But a user who wanted rock specifically would have felt misled. Confidence and accuracy are not the same thing, and the system never flags its own uncertainty.

A second surprise was how much a single weight change changed behavior. Swapping genre from 0.30 to 0.15 did not just reorder a few results — it changed the character of the entire output. Songs I thought would always be obvious matches dropped out of the top 5 entirely. This made me realize that a recommender's "personality" is almost entirely contained in its weights, not in its logic.

### Collaboration with AI

I used Claude as a coding collaborator throughout the project.

**One instance where AI was genuinely helpful:** When I was stuck on how to decouple the RAG generator from the retriever, Claude suggested keeping `rag.py` stateless — accept a pre-ranked list as input rather than running retrieval internally. This was the right call. It meant I could test the RAG layer by passing in any list of songs without needing the CSV or the scoring logic, and it let `main.py` fall back gracefully when no Gemini key was set. I would not have designed it that cleanly on my own.

**One instance where AI's suggestion was flawed:** Claude initially suggested using `target_genre` as a continuous field (0–1 affinity toward a genre) instead of a binary exact-match, to make genre scoring smoother. The idea sounds good in theory, but it would require the user to specify a numeric affinity for every genre in the catalog — which defeats the point of a simple "favorite genre" input. It also would have broken the test suite, which assumes a single favorite-genre string. The suggestion was elegant but impractical for this interface. I kept the binary match and noted it as a future improvement instead.
