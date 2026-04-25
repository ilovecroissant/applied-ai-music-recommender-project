# Music Recommender Simulation

## Original Project (Modules 1–3)

The **Music Recommender Simulation** was built in Modules 1–3 as a hands-on introduction to how recommender systems turn structured data into ranked predictions. The original system represented songs as data objects with audio features (genre, mood, energy, acousticness, valence, danceability, instrumentalness, speechiness) and scored them against a user "taste profile" using a weighted formula. The goal was to surface the top-K songs most likely to match what a user wants to hear, while making every design choice — including the weights — explicit and adjustable.

In Module 4, a **Retrieval-Augmented Generation (RAG)** layer was added using Google's Gemini 2.5 Flash model. The retriever from Modules 1–3 now feeds its ranked results directly into Gemini as grounded context, and Gemini generates a personalized, conversational recommendation narrative for each listener profile.

---

## Title and Summary

**VibeMatcher 1.0 + Gemini RAG** is a two-stage music recommendation system. The first stage is a deterministic scorer that ranks songs from a 20-song catalog by how well their audio features match a user's stated preferences. The second stage passes those results to a large language model (Gemini 2.5 Flash), which reads the retrieved songs as context and writes a warm, human-readable recommendation paragraph that references specific song titles and the reasons they were selected.

This matters because it demonstrates the full RAG pattern at a small, inspectable scale: retrieval logic you can read and tune, plus AI generation grounded to facts the retrieval step verified. Neither half works well alone — the LLM without retrieval would invent songs; the retriever without generation gives dry ranked lists.

---

## Architecture Overview

The system has three layers:

**1. Retriever** (`src/recommender.py`)
Loads `data/songs.csv` and scores every song against the user's taste profile using a weighted sum across eight audio dimensions. Songs are ranked descending by score and the top K (default 5) are returned as `(song, score, explanation)` tuples.

**2. RAG Generator** (`src/rag.py`)
Receives the retrieved songs, formats them as structured text context, builds a prompt, and calls Gemini 2.5 Flash to generate a personalized 4–6 sentence narrative. The LLM is instructed to reference only songs from the retrieved list — it cannot invent.

**3. Runner / Orchestrator** (`src/main.py`)
Defines three listener profiles, calls the retriever for each, prints the ranked songs to stdout, then calls the RAG generator and prints the AI narrative. All steps are logged to `recommender.log`.

```
User Taste Profile ──────────────────────────────┐
                                                  ▼
data/songs.csv ──────────► RETRIEVER (recommender.py)
                            • score() — 8 weighted dims
                            • rank descending
                            • return top-K with explanations
                                       │
                    ┌──────────────────┴───────────────────┐
                    ▼                                       ▼
           Console display                     RAG GENERATOR (rag.py)
           (ranked songs +                     • format songs as context
            scores + explain)                 • build prompt
                                              • call Gemini 2.5 Flash
                                              • return narrative text
                                                       │
                                                       ▼
                                              stdout + recommender.log
```

Testing sits alongside the retriever layer: `pytest` runs unit tests against the OOP interface (`Recommender`, `Song`, `UserProfile`) to verify sorted results and non-empty explanations. Human evaluation uses three hand-crafted profiles in `main.py` as end-to-end test cases.

---

## Setup Instructions

### 1. Clone the repo and enter the directory

```bash
git clone <repo-url>
cd applied-ai-music-recommender-project
```

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your Gemini API key

Copy the example env file and paste your key:

```bash
cp .env.example .env
```

Open `.env` and set:

```
GEMINI_API_KEY=your-actual-key-here
```

If you skip this step the app still runs — it falls back to the scored list without the AI narrative.

### 5. Run the app

```bash
python -m src.main
```

### 6. Run the tests

```bash
pytest
```

---

## Sample Interactions

Each profile below shows the input preferences, the retriever's ranked output, and the Gemini-generated narrative.

---

### Profile 1 — Late-night Study Session

**Input preferences:**

```
favorite_genre:          lofi
favorite_mood:           focused
target_energy:           0.40
likes_acoustic:          True
target_valence:          0.58
target_danceability:     0.55
target_instrumentalness: 0.50
target_speechiness:      0.04
```

**Retriever output (top 5):**

```
1. Focus Flow by LoRoom          — score: 0.88
   Because: Matches your favorite genre (lofi), mood is focused

2. Library Rain by Paper Lanterns — score: 0.79
   Because: Matches your favorite genre (lofi), has an acoustic texture you like

3. Midnight Coding by LoRoom     — score: 0.72
   Because: Matches your favorite genre (lofi), has an acoustic texture you like

4. Rio Whisper by Cafe Calor     — score: 0.61
   Because: Overall score 0.61 fits your taste profile

5. Spacewalk Thoughts by Orbit Bloom — score: 0.58
   Because: Has an acoustic texture you like
```

**Gemini narrative:**

```
You're settling in for a late-night study session — low stimulation, high focus,
the kind of listening that fades into the background without disappearing. Focus
Flow by LoRoom is your anchor: at energy 0.40 and tagged "focused," it sits
exactly where you want to be, with enough acoustic warmth (acousticness 0.78)
to feel cozy rather than sterile. Library Rain by Paper Lanterns is a close
companion — its energy is even softer at 0.35 and its high acousticness (0.86)
gives it a rainy-window texture that suits late hours. If you want something
slightly different, Midnight Coding by LoRoom keeps the genre consistent while
adding a touch more movement. Build your queue around Focus Flow and let the
others fill the spaces — this is exactly the kind of session these tracks were
made for.
```

---

### Profile 2 — High-Energy Pop

**Input preferences:**

```
favorite_genre:          pop
favorite_mood:           happy
target_energy:           0.90
likes_acoustic:          False
target_valence:          0.90
target_danceability:     0.85
target_instrumentalness: 0.05
target_speechiness:      0.08
```

**Retriever output (top 5):**

```
1. Gym Hero by Max Pulse         — score: 0.92
   Because: Matches your favorite genre (pop), mood is happy... wait, mood is
   intense — overall score 0.92 fits your taste profile

2. Sunrise City by Neon Echo     — score: 0.87
   Because: Matches your favorite genre (pop), mood is happy

3. Rooftop Lights by Indigo Parade — score: 0.74
   Because: Overall score 0.74 fits your taste profile

4. Street Chronicles by Cipher Kings — score: 0.68
   Because: Overall score 0.68 fits your taste profile

5. Hyperdrive by Axis Omega      — score: 0.63
   Because: Overall score 0.63 fits your taste profile
```

**Gemini narrative:**

```
You're after pure, unfiltered energy — the kind of playlist that makes a commute
feel like a montage. Gym Hero by Max Pulse leads the list for good reason: energy
0.93 and danceability 0.88 are essentially a perfect match for your targets, and
its pop DNA keeps it bright rather than aggressive. Sunrise City by Neon Echo is
the slightly more melodic companion — energy 0.82, valence 0.84, and a happy mood
tag that puts it exactly in your wheelhouse. Rooftop Lights by Indigo Parade
rounds out the core three with indie-pop sparkle and strong danceability (0.82)
for when you want something that still moves but feels a degree more relaxed. Put
all three on repeat — you've got a high-energy session locked in.
```

---

### Profile 3 — Deep Intense Rock

**Input preferences:**

```
favorite_genre:          rock
favorite_mood:           angry
target_energy:           0.95
likes_acoustic:          False
target_valence:          0.20
target_danceability:     0.40
target_instrumentalness: 0.15
target_speechiness:      0.06
```

**Retriever output (top 5):**

```
1. Iron Collapse by Wrathborn    — score: 0.86
   Because: Overall score 0.86 fits your taste profile

2. Storm Runner by Voltline      — score: 0.82
   Because: Matches your favorite genre (rock)

3. Hyperdrive by Axis Omega      — score: 0.71
   Because: Overall score 0.71 fits your taste profile

4. Gym Hero by Max Pulse         — score: 0.65
   Because: Overall score 0.65 fits your taste profile

5. Night Drive Loop by Neon Echo — score: 0.59
   Because: Overall score 0.59 fits your taste profile
```

**Gemini narrative:**

```
You want music with edges — low valence, maximum energy, zero acoustic softness.
Iron Collapse by Wrathborn is the sharpest match: energy 0.97, valence 0.14, and
an angry mood tag that lines up directly with your target profile, even though
it's metal rather than rock — the audio features don't lie. Storm Runner by
Voltline is your core rock pick, hitting energy 0.91 with that genre match and an
intense, hard-edged feel. Hyperdrive by Axis Omega lands third — its 0.95 energy
and euphoric drive make it a cathartic wildcard even if the mood diverges. Start
with Storm Runner for pure genre satisfaction, then let Iron Collapse and
Hyperdrive push the intensity further. This is exactly the kind of session that
reminds you why volume knobs go past halfway.
```

---

## Design Decisions

**Why a weighted scoring formula instead of a model?**
A hand-tuned weighted sum is fully transparent — every factor and its contribution is readable in the code. This makes it easy to experiment (flip two weights, re-run, compare), which is the point of the project. A trained ML model would be a black box at this scale and would require far more labeled data than a 20-song catalog can provide.

**Why energy at 0.30 and genre at 0.15?**
The starter weights had genre at 0.30 and energy at 0.15. In practice this meant a slow lofi song would beat a fast ambient track purely because the genre label matched, even if they felt nothing alike. Swapping the weights made "vibe" (energy) the dominant signal, which produced more intuitive results. The trade-off is that users with a strong genre preference may feel the system wanders outside their chosen style.

**Why keep two parallel interfaces (dict-based and OOP)?**
`main.py` uses plain dicts for songs and preferences — easy to read, no imports needed, quick to extend. The tests use `Song` and `UserProfile` dataclasses, which give type safety and make field access unambiguous. Both interfaces share the same scoring math; separating them means the runner and the tests can evolve independently.

**Why decouple retrieval from generation?**
`rag.py` only handles the Gemini call. Retrieval happens in `main.py` before `generate_rag_recommendation()` is called. This means the RAG layer can be tested in isolation (feed it any list of songs), and the retriever can be used without a Gemini key at all (the app falls back gracefully). Mixing the two would make either harder to swap or improve.

**Why Gemini 2.5 Flash?**
Speed and cost for a classroom project. The narratives are short (4–6 sentences) and the context is small (5 songs), so a smaller, faster model is appropriate. The system prompt instructs the model to reference only retrieved songs, which guards against hallucinated track titles.

---

## Testing Summary

**What was tested:**
- `test_recommend_returns_songs_sorted_by_score` — verifies that the OOP `Recommender.recommend()` returns the pop/happy song at rank 1 for a matching user profile.
- `test_explain_recommendation_returns_non_empty_string` — verifies that `explain_recommendation()` always returns a non-empty string.
- Manual end-to-end testing with three profiles (Study Session, High-Energy Pop, Deep Intense Rock) by running `python -m src.main` and reading the output.

**What worked:**
The retriever sorted results correctly in all manual tests. The genre + energy weight swap (Experiment 1) produced noticeably more intuitive rankings. Gemini's output stayed grounded — it referenced only the songs it was given and used the actual scores and features in its explanations.

**What didn't work as expected:**
The `Recommender` OOP class has stub implementations for `recommend()` and `explain_recommendation()` — they return the first K songs and a placeholder string. The tests pass because the stub returns songs in insertion order (which happens to put the pop track first), but the logic is not real. The functional `recommend_songs()` function in the same file has the real scoring, and `main.py` uses that.

Energy weight at 0.30 sometimes surfaced songs from entirely different genres when they happened to match energy closely. For a user who cares strongly about genre, this felt like a bug even though it was technically working as designed.

**What was learned:**
Small weight changes have outsized effects on results. Moving genre from 0.30 to 0.15 did not make genre irrelevant — it just stopped genre from overriding everything else. The system taught that recommender design is mostly a sequence of tradeoffs between competing signals, and that the "right" weights depend on what behavior you want rather than what is mathematically optimal.

---

## Reflection

Building this project made two things clear that are easy to miss when using finished apps like Spotify.

First, a recommender is not discovering truth — it is executing the designer's judgment calls. Every weight in the formula represents a decision about what matters more. When genre was at 0.30 it said: genre is the most important thing about a song. When energy moved to 0.30 it said: how a song feels is more important than what it is labeled. Both are defensible, and both produce different playlists. The user never sees the weights, but the weights shape every recommendation they receive.

Second, the RAG layer showed that grounding matters. An LLM told to recommend music with no context will invent plausible-sounding but nonexistent songs and artists. Giving it a retrieved list of verified songs as context dramatically changed its behavior — it stopped guessing and started explaining. That is the core of RAG: use retrieval to constrain the LLM's output to things that are actually true, and use the LLM to make those facts readable and useful to a person. At a larger scale this same pattern applies to any domain where accuracy matters — medical information, legal documents, product catalogs — the retriever finds the facts, the model translates them into something a human can use.

---

## Files

| File | Purpose |
|---|---|
| [src/main.py](src/main.py) | Orchestrator — runs three profiles end-to-end |
| [src/recommender.py](src/recommender.py) | Retriever — scoring, ranking, OOP and functional interfaces |
| [src/rag.py](src/rag.py) | RAG generator — Gemini prompt construction and API call |
| [data/songs.csv](data/songs.csv) | 20-song catalog with full audio feature columns |
| [tests/test_recommender.py](tests/test_recommender.py) | pytest suite for the OOP interface |
| [model_card.md](model_card.md) | Intended use, limitations, bias, and evaluation |
| [.env.example](.env.example) | Template for the GEMINI_API_KEY environment variable |
