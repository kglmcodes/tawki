# Tawki

**Frequency-first language study.** Build the core of a language fast: learn
the highest-frequency vocabulary and the highest-frequency grammar patterns in
parallel, then combine them and start using the language — instead of grinding
through a textbook from page one.

*Tawki* is this repo's name. It holds the frequency-first core of every language
you study — the words and patterns worth learning first.

## The method

Two tracks run side by side:

1. **Vocabulary — the most frequent words first.** Front-load the top slice of
   a frequency list before anything else. Rough coverage of running text:
   - top ~100 words -> ~50%
   - top ~1,000 words -> ~75-80%
   - top ~2,000 words -> ~80-85%
   Target the top 5-20% (the core), not random topic vocabulary.

2. **Grammar / patterns — the most frequent structures first.** Learn the
   grammar and **sentence frames** in frequency order: word order, particles,
   tense/aspect, question forms, negation, politeness, connectors.
   Frame-first, not rule-first.

3. **Combine.** With the core words + core patterns you can read, listen, and
   start producing right away. Everything after that is filling gaps at speed.

## Layout

```
tawki/
  README.md            this file — the method
  _template/           scaffold to copy when starting a new language
  <language>/          one folder per language, e.g. zh-tw/
```

Each language folder:

```
<language>/
  README.md            goal, level, sources, current focus
  vocab-frequency.md   ranked word list + progress
  grammar-patterns.md  ranked grammar patterns / sentence frames + examples
  notes.md             observations, gotchas, mnemonics
  progress.md          coverage log
  sources.md           where the frequency data came from
```

## Languages

| Folder | Language | Status |
|---|---|---|
| `zh-tw` | Traditional Chinese (Taiwan) | seed: top ~75 words, 15 core patterns |

## Web app (mobile-first)

A static, offline-capable study app lives in `web/`. It reads JSON generated
from each language folder's markdown, so the markdown stays the source of
truth.

The repo is public, so it can be hosted on GitHub Pages. Locally, serve the
folder directly; or deploy `web/` to GitHub Pages / Cloudflare Pages / Netlify /
Vercel.

Screens:
- **Learn** — a Vocabulary | Patterns segmented switch. Vocabulary shows a grid of lessons (20 words each) with per-lesson progress; search filters the full list. Patterns lists the grammar frames and sentence patterns.
- **Practice** — flashcards scoped to Unseen / All words / a single lesson; tap to reveal pinyin, meaning, example; Know / Again, with shuffle.
- **Progress** — known count, list coverage, frequency-band coverage (top 100/300/1000/2000), and per-lesson progress.

Progress is stored per language in the browser (`localStorage`).

```bash
python3 scripts/build_data.py zh-tw     # markdown -> web/data/zh-tw.json
python3 -m http.server -d web           # then open http://localhost:8000
```

Reach it from a phone on the same network, or add to home screen (a web
manifest is included). `web/data/*.json` is generated but committed so the app
works when served directly.

## Working rules

- **Rank first, study second.** Keep every list ordered by frequency.
- **Coverage over count.** Track "% of running text covered", not raw tallies.
- **Input as soon as the core is up** — start reading/listening once the top
  ~1,000 words and core patterns are there.
- **One source of truth per language** for the ranking (see each `sources.md`).
- **No emojis in files.**

## Starting a new language

1. `cp -r _template <language>`
2. Fill `sources.md` with a real corpus-based frequency list (subtitle /
   conversation data is best for everyday language).
3. Import the top ranks into `vocab-frequency.md` and `grammar-patterns.md`.
4. Log the first entry in `progress.md`.
