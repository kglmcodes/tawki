# languages — frequency-first language study

A folder for studying languages using the **frequency-first method** (the "CIA
method" you described): front-load the highest-frequency vocabulary *and* the
highest-frequency grammar/sentence patterns, in parallel, then combine them to
ramp up fast instead of following a textbook from chapter 1.

## The method

Two tracks, run side by side:

1. **Vocabulary track — most frequent words first.**
   Learn the top slice of the frequency list before anything else. Rough
   coverage of running text:
   - top ~100 words -> ~50%
   - top ~1,000 words -> ~75-80%
   - top ~2,000 words -> ~80-85%
   Target the **top 5-20%** of the frequency list first (the "core"), not
   random topic vocabulary.

2. **Grammar / pattern track — most frequent patterns first.**
   Learn the grammar structures and **sentence frames** in frequency order:
   the handful of patterns that appear in almost every conversation (word
   order, particles/markers, tense/aspect, question forms, negation,
   politeness levels, common connectors). Frame-first, not rule-first.

3. **Combine.**
   With the core words + core patterns you can already read/listen to real
   input and start producing. Everything after that is filling gaps and
   raising coverage, at high speed.

## How the repo is organised

```
languages/
  README.md            this file — the method
  _template/           scaffold to copy when starting a new language
  <language>/          one folder per language, e.g. burmese/, thai/, japanese/
```

Each language folder follows the same layout (copy `_template/`):

```
<language>/
  README.md            goal, level, sources, current focus
  vocab-frequency.md   the ranked word list + progress (% of core covered)
  grammar-patterns.md  ranked grammar patterns / sentence frames + examples
  notes.md             observations, gotchas, mnemonics
  progress.md          coverage log (words known, patterns known, dates)
  sources.md           where the frequency data came from
```

## Working rules

- **Rank first, study second.** Every list in here is ordered by frequency;
  keep it that way. Add new items at their rank, don't append randomly.
- **Coverage over count.** Track "% of running text covered" (words) and
  "patterns seen in the wild", not raw tallies.
- **Input as soon as the core is up.** Start reading/listening with ~top 1,000
  words + core patterns, even if imperfect.
- **One source of truth per language** for the frequency ranking (see
  `sources.md`), so two lists never disagree silently.
- **No emojis in files.**

## Starting a new language

1. `cp -r _template <language>`
2. Fill `sources.md` with a real frequency list (corpus-based, ideally
   subtitle/conversation data for everyday language).
3. Import the top ranks into `vocab-frequency.md` and `grammar-patterns.md`.
4. Log the first entry in `progress.md`.
