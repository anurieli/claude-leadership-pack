---
name: site-to-video
description: Use when the user asks for a marketing video, promo, ad, reel, teaser, or trailer from a website URL — any "make a video for [URL]", "turn this site into a video", "30-second SaaS promo", or similar. Covers landscape, portrait, and square formats from 10s to 60s.
---

# site-to-video

Produces a polished marketing video from a captured website. Audio-first pipeline: ElevenLabs V3 narration drives the timeline, music + SFX layer in, GSAP-animated HTML scenes render to MP4 via HyperFrames.

## Prereqs

- `npx` (Node ≥ 18) — scripts auto-fetch `hyperframes@latest` via npx if not on PATH
- `ffmpeg` / `ffprobe` — `brew install ffmpeg`
- `python3` with `Pillow` (only for `qa-snapshots.py`) — `pip3 install Pillow`
- `ELEVENLABS_KEY` env var — required from step 5 onward (capture in step 1 works without it)

## Project layout (deliverable-first)

Projects land in `~/Downloads/<slug>/` by default (override with `SITE_TO_VIDEO_DIR`). The project root holds only what you'd hand off; scaffolding lives in `.build/`.

```
project/
├── final.mp4              ← deliverable
├── final.srt              ← auto-generated from .build/transcript.json
└── .build/                ← scaffolding + intermediates
    ├── DESIGN.md
    ├── SCRIPT.md
    ├── STORYBOARD.md
    ├── index.html         ← what hyperframes renders
    ├── transcript.json
    ├── audio/
    │   ├── narration.wav
    │   ├── music.wav
    │   └── sfx/
    ├── assets/            ← captured site (screenshots, tokens, fonts)
    └── snapshots/         ← QA verification PNGs
```

## The 7-step workflow

Each step has a gate. Don't proceed until clean.

### 1. Scaffold + capture

```bash
scripts/make-video.sh <URL> [project-name] [template]
# templates: saas-30s (default) | launch-teaser-15s | portrait-reel
```

Pulls scroll screenshots, design tokens, fonts, asset descriptions into `.build/assets/`. Optional `GEMINI_API_KEY` enriches asset descriptions.

**Gate:** print site name, top 3 hex colors, fonts, count of sections/CTAs, key assets, one-sentence vibe.

### 2. Fill `.build/DESIGN.md` (≤100 lines)

Cheat sheet only — six sections: Overview, Colors, Typography, Elevation, Components, Do's/Don'ts. Use *exact* hex from `.build/assets/extracted/tokens.json` — never approximate. Component names by what you SEE, not generic "Card" / "Section".

### 3. Fill `.build/SCRIPT.md`

Pacing: **2.3–2.5 words/sec**. So 30s ≈ 70–75 words, 40s ≈ 90–100 words, 60s ≈ 140–150 words.

**GROUND THE HOOK IN THE CAPTURED HERO.** Read `.build/assets/extracted/visible-text.txt` first. The H1, sub-headline, and any pull-quotes ARE the thesis. Open with the site's actual argument, paraphrased. Generic SaaS-promo openers ("most companies approach X the same way", "tired of Y?", "what if Z?") are a fail signal — rewrite.

Structure: Hook (site's thesis) → Stakes → Brand answer → Proof → CTA. Tone: contractions, varied sentences, read aloud test.

V3 emotion tags + TTS substitutions: `references/voices.json`.

### 4. Fill `.build/STORYBOARD.md`

Each beat is a WORLD, not a layout. Aim for **6–10 visual elements per beat** (background texture, midground content, foreground accents, animated icons, typographic detail). Sparse beats look like JPEGs with progress bars.

Per-beat sections: Concept · VO cue · Visual (≥5 elements, layered fg/mg/bg) · Mood direction (cultural references, not hex) · Assets · Animation choreography (motion verbs) · Transition · Depth layers · SFX cues. Asset audit table at top — every captured asset assigned to a beat or marked SKIP.

### 5. Generate VO + Music + SFX

**Audio drives the video, not the reverse.** Generate audio FIRST, get its duration with `ffprobe`, then size composition to fit (narration + 1–1.5s tail).

```bash
scripts/audition-voices.sh "<your hook sentence>"      # pick a voice
scripts/generate-audio.sh <voice-id> ["music prompt"] [length-ms]
# generates .build/audio/narration.{mp3,wav}, music.{mp3,wav}, .build/transcript.json
```

SFX (6–10 hits per video) — generate per-prompt with curl. Min duration 0.5s. See `references/audio-pipeline.md` for prompts and the API call.

Detail: `references/audio-pipeline.md` (voice catalog, V3 emotion tags, music prompt anatomy, SFX prompt table, beat-boundary computation, SRT generation).

### 6. Build `.build/index.html`

ONE file. Stacked `<div class="scene">` siblings crossfaded by ONE paused GSAP timeline. Audio elements at top of root, captions overlay, grain layer.

Start from the chosen template — already has root, audio scaffolding, scene divs, captions layer, grain, and a working crossfade timeline. Fill in per-beat content + animations.

Hard rules (one-line each — full reasoning in `references/composition-rules.md`):
- Absolute time positions only (`tl.to(el, vars, 12.6)`), never relative `+=`
- Never `transform: translate(-50%, -50%)` — use flexbox wrappers
- `:nth-child(${i+1})` for word stagger, NOT `${i*2+1}` (text-node spaces aren't children)
- Min font: 20px body, 16px labels
- No full-screen dark linear gradients (H.264 banding)
- Music ducked to `data-volume="0.10"–"0.15"`
- Same SFX file at multiple times → unique `data-track-index` per `<audio>`

### 7. Validate, snapshot, render

```bash
hyperframes lint                                    # 0 errors required
hyperframes validate                                # runtime load check
hyperframes snapshot . --at <beat-midpoints>        # PNG per beat
scripts/qa-snapshots.py .build/snapshots            # auto-flag empty scenes
hyperframes render --output final.mp4 --fps 30 --quality high
```

**Always snapshot at 60–70% into each beat** (after entrances finish, before exits start). The QA script flags scenes below 40% non-flat coverage. Eye-check every flagged frame: assigned assets visible, text contrast against background, no off-edge bleed.

After render, generate `final.srt` from `.build/transcript.json` (snippet in `references/audio-pipeline.md`).

## When the script changes mid-build

Don't rebuild from scratch — piecewise-remap old beat boundaries to new ones. See `references/retiming.md`.

## Pacing & format cheat sheet

| Format | Duration | Beats | Words | Template |
|---|---|---|---|---|
| Social ad (IG/TikTok) | 10–15s | 3–4 | 25–37 | launch-teaser-15s |
| Launch teaser | 10–20s | 2–4 | minimal | launch-teaser-15s |
| Feature announcement | 15–30s | 3–5 | 35–75 | saas-30s |
| Product demo | 30–60s | 5–8 | 75–150 | saas-30s |
| Stories/Reels | 15–30s | 3–5 | 35–75 | portrait-reel |

Aspect ratios: 1920×1080 landscape · 1080×1920 portrait · 1080×1080 square (adapt portrait template).

## Don't invoke for

- Editing/cutting existing video footage (HyperFrames is HTML-rendered, not an NLE)
- Live-action / real-camera production
- Audio-only deliverables
- Static graphics / images
