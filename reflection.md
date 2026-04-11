# Reflection: Comparing User Profile Outputs

---

## Pair 1: Late-night Study Session vs. High-Energy Pop

**Study Session top 5:** Focus Flow, Library Rain, Midnight Coding, Coffee Shop Stories, Old Oak Road  
**High-Energy Pop top 5:** Sunrise City, Rooftop Lights, Gym Hero, Street Chronicles, Hyperdrive

These two profiles have almost nothing in common, and neither does their output. The study profile wants quiet, acoustic, focused music — low energy around 0.40. The pop profile wants the opposite: loud, danceable, upbeat songs with energy near 0.90.

The study profile gravitates toward lofi tracks (Focus Flow, Library Rain, Midnight Coding) because they match both the genre preference and the acoustic texture. Coffee Shop Stories and Old Oak Road sneak in because they are acoustic enough, even though they are jazz and folk — the recommender is rewarding the "feels like a quiet room" quality more than the genre label.

The pop profile rewards energy above almost anything else. Sunrise City wins because it nails genre (pop), mood (happy), and energy (0.82) all at once. The two lists share zero songs, which makes sense — a song that works for late-night studying would feel wrong blasting at a party.

---

## Pair 2: High-Energy Pop vs. Deep Intense Rock

**High-Energy Pop top 5:** Sunrise City, Rooftop Lights, Gym Hero, Street Chronicles, Hyperdrive  
**Deep Intense Rock top 5:** Iron Collapse, Storm Runner, Hyperdrive, Gym Hero, Street Chronicles

This is where things get interesting. Both profiles want high energy and both dislike acoustic textures. That shared preference pulls some of the same songs into both lists — Gym Hero, Street Chronicles, and Hyperdrive all show up for both.

What separates them is mood and emotional tone. The pop fan wants happy and upbeat (high valence). The rock fan wants angry and dark (low valence, around 0.20). So Sunrise City and Rooftop Lights are great for pop but would feel too cheerful for the rock listener. Iron Collapse flips that: it is heavy, dark, and angry, which is exactly what the rock profile wants — but it would feel jarring on a pop playlist.

Think of it this way: both fans want to turn the volume up, but one wants to dance and the other wants to headbang.

---

## Pair 3: Late-night Study Session vs. Deep Intense Rock

**Study Session top 5:** Focus Flow, Library Rain, Midnight Coding, Coffee Shop Stories, Old Oak Road  
**Deep Intense Rock top 5:** Iron Collapse, Storm Runner, Hyperdrive, Gym Hero, Street Chronicles

These two profiles are complete opposites, and their outputs reflect that perfectly. Not a single song overlaps. The study profile pulls calm, acoustic, low-energy tracks. The rock profile pulls loud, electric, high-energy tracks. The energy targets alone (0.40 vs. 0.95) are so far apart that a song that scores well for one will almost always score poorly for the other.

This is a good sign that the recommender is actually working. Two very different users get two very different results.

---

## Why Does "Gym Hero" Keep Showing Up for Happy Pop Fans?

Gym Hero is tagged as **intense**, not happy. So why does it appear at #3 for someone who specifically asked for happy music?

The recommender scores songs on eight different qualities. Getting the mood right is worth 0.25 points. But matching energy is worth 0.30 points — slightly more. Gym Hero has an energy of 0.93, and the pop fan's target is 0.90. That is an almost perfect match. On top of that, Gym Hero is genre pop, which adds another 0.15.

So even though the mood is wrong (no bonus there), Gym Hero still earns a high score because it nails the genre and comes very close on energy. The recommender does not think "this song has the wrong mood, disqualify it." It just adds up the points, and Gym Hero has enough points to land in the top 5.

The real-world version of this happens on Spotify all the time. If you tell the algorithm you want upbeat pop and set your energy preference high, it will sometimes surface a high-energy workout track that feels a bit aggressive — because the algorithm matched your energy target even though the mood is slightly off. The fix would be to increase the weight of mood, or to add a penalty when the mood is a complete mismatch.
