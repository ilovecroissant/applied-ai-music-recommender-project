# Model Card: VibeMatcher 1.0 + Gemini RAG

## 1. Model Name

**VibeMatcher 1.0 + Gemini RAG**

---

## 2. Intended Use

VibeMatcher is a two-stage music recommendation system built as a classroom simulation. A user provides a taste profile — favorite genre, preferred mood, target energy, acoustic preference, and optional audio feature targets — and the system returns a ranked list of matching songs along with a personalized, human-readable recommendation narrative.

This is an educational prototype, not a production service. Its purpose is to make the mechanics of a recommender system and the RAG pattern visible and tunable at a scale where every design decision can be traced.

---

## 3. How the System Works

The system has two stages that run in sequence.

### Stage 1 — Retriever (`src/recommender.py`)

Every song in the catalog receives a score between 0.0 and 1.0. The score is a weighted sum across eight audio dimensions:

| Dimension | Weight | How it is computed |
|---|---|---|
| Energy closeness | 0.30 | `1 − |song.energy − target_energy|` |
| Mood match | 0.25 | 1.0 if exact label match, else 0.0 |
| Genre match | 0.15 | 1.0 if exact label match, else 0.0 |
| Acoustic preference | 0.10 | `acousticness` if `likes_acoustic`, else `1 − acousticness` |
| Valence closeness | 0.08 | `1 − |song.valence − target_valence|` |
| Danceability closeness | 0.06 | `1 − |song.danceability − target_danceability|` |
| Instrumentalness closeness | 0.04 | `1 − |song.instrumentalness − target_instrumentalness|` |
| Speechiness closeness | 0.02 | `1 − |song.speechiness − target_speechiness|` |

Songs are ranked descending by score. The top K (default 5) are returned as `(song, score, explanation)` tuples.

**Weight change from the starter:** Energy was raised from 0.15 to 0.30 and genre was lowered from 0.30 to 0.15. The intent was to make "vibe" the dominant signal — listeners often care more about how a song feels than what genre label it carries. This is a deliberate editorial choice, not a mathematically derived optimum.

### Stage 2 — RAG Generator (`src/rag.py`)

The top-K songs from Stage 1 are passed as structured text context to Gemini 2.5 Flash. A system prompt instructs Gemini to act as a music guide, reference only the songs it was given, and write a warm, specific 4–6 sentence recommendation narrative. The model cannot invent songs or artists; retrieval constrains its output to verified catalog entries.

If no Gemini API key is configured, Stage 2 is skipped and the app prints the scored list only.

---

## 4. Data

**Catalog size:** 20 songs.

**Audio features per song:** `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`, `instrumentalness`, `speechiness` (all numeric), plus categorical `genre` and `mood`.

**Genres covered:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, classical, r&b, metal, folk, country, reggae, drum and bass, bossa nova, blues

**Moods covered:** happy, chill, intense, relaxed, focused, moody, melancholic, romantic, energetic, angry, nostalgic, uplifting, peaceful, sad, euphoric, dreamy

The catalog was expanded from 10 to 20 songs during Module 3 to improve genre and mood coverage. Gaps remain: there is no Latin pop, K-pop, gospel, or EDM beyond drum and bass. A catalog of 20 is sufficient for learning but too small to produce meaningfully diverse results when a user's preferences are niche.

---

## 5. Strengths

- **Transparent scoring.** Every weight is a named constant in the code. Changing a weight immediately changes behavior in a traceable way, which makes the system easy to audit and experiment with.
- **Energy-dominant ranking.** At weight 0.30, energy is the strongest single factor. In practice this surfaces songs that feel right even when the genre label does not match, which aligns with how many listeners experience music.
- **Grounded generation.** The RAG layer is instructed to reference only retrieved songs. In manual tests across three profiles, Gemini cited actual feature values (e.g., "acousticness 0.78") and never invented tracks.
- **Graceful degradation.** The app works without a Gemini API key — it prints the scored list and skips the narrative rather than failing.

---

## 6. Limitations and Bias

**Binary genre and mood matching.** Metal and rock share zero credit. "Melancholic" and "sad" are treated as completely different labels. A listener who enjoys both rock and metal, or both sad and melancholic music, will see one category favored and the other penalized.

**Binary acoustic preference.** `likes_acoustic` is a yes/no flag. A user who is indifferent to acoustic texture must still pick a side. Mid-acousticness songs (0.40–0.60) score around 0.50 regardless of the flag, but high-acousticness songs (0.91–0.96) swing dramatically depending on the choice.

**Catalog energy floor.** The quietest song in the catalog has energy 0.28 (Spacewalk Thoughts). A user who sets `target_energy = 0.1` can never score above ~0.82 on the energy dimension — not because the logic is wrong, but because the data does not reach that low.

**Western genre skew.** All 20 songs represent Western-origin genres. Users who prefer music outside that range will find poor coverage before the scoring logic even runs.

**Weights encode editorial judgment.** Setting energy at 0.30 is a claim that "vibe matters more than genre." That is defensible for many listeners and wrong for others. Users with strong genre loyalty may find that energy-close cross-genre songs displace obvious matches.

**LLM confidence without uncertainty.** When Gemini explains a match, its language is authoritative whether the underlying match is strong or marginal. The system never flags low-confidence recommendations to the user.

---

## 7. Evaluation

Two types of evaluation were used.

**Automated tests (`pytest`):**
- `test_recommend_returns_songs_sorted_by_score` — confirms that `Recommender.recommend()` returns songs in descending score order for a pop/happy/high-energy profile.
- `test_explain_recommendation_returns_non_empty_string` — confirms that `explain_recommendation()` always returns a non-empty string.
- Five additional tests cover edge cases: k larger than the catalog, score bounds, profile mismatches.

**Manual end-to-end evaluation (three profiles in `main.py`):**

| Profile | Expected top result | Observed top result | Match? |
|---|---|---|---|
| Late-night Study (lofi, focused, energy 0.40) | Focus Flow | Focus Flow (0.88) | Yes |
| High-Energy Pop (pop, happy, energy 0.90) | Gym Hero or Sunrise City | Gym Hero (0.92) | Yes |
| Deep Intense Rock (rock, angry, energy 0.95) | Storm Runner | Iron Collapse (0.86) | Partial — metal ranked above rock due to energy |

The rock profile result was the most instructive: Iron Collapse (metal, energy 0.97) outscored Storm Runner (rock, energy 0.91) because the 0.02 energy difference (weighted at 0.30) outweighed the genre match bonus (0.15). This is working as designed, but a user who explicitly wants rock would experience it as a miss.

---

## 8. Potential for Misuse

At the scale of this project the risk is low. But the same patterns, applied at production scale, carry real consequences:

- **Filter bubbles.** Binary genre/mood scoring with no partial credit means a user who always picks "rock" will never see adjacent genres (metal, indie, punk). At Spotify scale, years of this narrowing can meaningfully reduce music discovery.
- **LLM overconfidence.** Gemini is instructed to reference only retrieved songs, but it describes even marginal matches with confident, persuasive language. A user reading the narrative has no signal about whether the underlying compatibility score was 0.88 or 0.52. Adding a minimum-score threshold before calling the LLM, or surfacing the score in the narrative, would address this.
- **Catalog bias as invisible policy.** The choice of which 20 songs to include is itself a recommendation. A catalog that omits entire genres makes those genres unreachable — not through scoring logic, but through data curation.

---

## 9. Future Work

- **Similar-genre groups.** Rock and metal, lofi and ambient, classical and jazz could receive partial credit rather than zero when the genre label does not match exactly.
- **Continuous acoustic preference.** Replace the yes/no `likes_acoustic` flag with a 0–1 `target_acousticness` field, the same way energy works.
- **Minimum-score threshold for RAG.** Only pass songs above a configurable score floor (e.g., 0.50) to Gemini, so the LLM does not narrate poor matches as if they were strong fits.
- **Diversity re-ranking.** Ensure the top 5 results include at least one song from a different genre, reducing filter-bubble narrowing.
- **Richer explanations.** Instead of "overall score 0.61 fits your taste profile," say "energy 0.40 is only 0.05 from your target; acousticness 0.78 matches your acoustic preference."
- **Larger catalog.** A catalog of 20 is enough to learn from. Adding 100+ songs would make score differences more meaningful and expose more catalog-coverage gaps.

---

## 10. Personal Reflection

### Limitations and Biases

VibeMatcher has structural biases that exist before any user runs it. The catalog skews entirely toward Western genres — there is no Latin pop, K-pop, or gospel, so users with those tastes are underserved from the start. Genre and mood matching are binary: metal and rock share no credit, and "melancholic" and "sad" are treated as completely different labels. The acoustic preference is a yes/no flag, so listeners indifferent to acoustic texture must still choose a side, which skews scoring for songs with mid-range acousticness. The energy floor in the catalog (~0.28) means a user asking for very quiet music can never reach a perfect score — not because the logic is wrong, but because the data does not go that low. Finally, the weights themselves encode bias: setting energy at 0.30 is an editorial decision that says "vibe matters more than genre," which will feel right for some users and wrong for others.

### Potential for Misuse

The misuse risk at this project's scale is low. But the same design pattern at production scale has real consequences. A weighted recommender can reinforce filter bubbles: a user whose genre always scores 1.0 for "rock" and 0.0 for everything else will never see adjacent styles. At streaming-service scale that narrowing can reduce music discovery for years. The RAG layer introduces a second risk: Gemini is instructed to reference only retrieved songs, but if the retriever surfaces low-quality matches, the LLM will describe them confidently anyway — the language sounds authoritative even when the compatibility score is weak. Two mitigations: a diversity re-ranking step (force at least one different-genre song into the top 5) and a minimum-score threshold (do not pass songs below 0.50 to Gemini).

### Surprises While Testing

The biggest surprise was how confident the system sounds when it is wrong. When a rock fan received Iron Collapse (metal) as the top result, the Gemini narrative explained it as a compelling cross-genre match — and the explanation was genuinely persuasive. The model was not fabricating; the audio features did align. But a user who wanted rock specifically would feel misled. Confidence and accuracy are not the same thing, and the system never flags its own uncertainty.

A second surprise was how much a single weight change changed the character of the output. Moving genre from 0.30 to 0.15 did not just reorder a few songs — it changed which songs the system felt like it "cared about." Songs I assumed would always be obvious matches dropped out of the top 5 entirely. A recommender's personality is almost entirely in its weights.

### Collaboration with AI

I used Claude as a coding collaborator throughout the project.

**One instance where AI was genuinely helpful:** When I was stuck on how to decouple the RAG generator from the retriever, Claude suggested keeping `rag.py` stateless — accept a pre-ranked list as input rather than running retrieval internally. This was the right call. It meant I could test the RAG layer by passing in any list of songs without needing the CSV or the scoring logic, and it let `main.py` fall back gracefully when no Gemini key was configured. I would not have designed it that cleanly on my own.

**One instance where AI's suggestion was flawed:** Claude initially proposed using `target_genre` as a 0–1 affinity score instead of a binary exact-match string, to make genre scoring smoother. The idea sounds good in theory, but it would require the user to supply a numeric affinity for every genre in the catalog — which defeats the point of a simple "favorite genre" input. It would also have broken the test suite, which assumes a single genre string. I kept the binary match and noted it as a future improvement instead.
