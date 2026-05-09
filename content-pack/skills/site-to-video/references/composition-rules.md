# Composition Rules (HyperFrames + GSAP)

The HyperFrames engine is deterministic. The rules below exist because violating them causes silent failures or render artifacts. Most are real bugs from prior builds.

## Hard rules

1. **One root composition** — `<div id="root" data-composition-id="main" data-start="0" data-duration="N" data-width="1920" data-height="1080">`.
2. **One GSAP timeline**, paused, registered at `window.__timelines["main"] = tl`. Pad with `tl.set({}, {}, N)` at the end so timeline ≥ root duration.
3. **Absolute time positions only**: `tl.to(el, vars, 12.6)`. Never relative `+=`.
4. **Never** `transform: translate(-50%, -50%)` for centering. GSAP overwrites `transform`. Use flexbox wrappers (`display:flex; align-items:center; justify-content:center`).
5. **No** `repeat: -1`, **no** `Math.random()`, **no** async wrappers in timeline code. Calculate exact repeats from beat duration.
6. Min font sizes: **20px body, 16px labels**. Smaller pixels disintegrate after H.264 encoding.
7. **No full-screen dark linear gradients** — H.264 banding. Use solid + localized radial glow.
8. **Don't manually `.play()` / `.pause()` media** — the engine owns the clock.
9. Use `gsap.from()` for entrances. The CSS position is the resting state; animations describe the journey to and from it.
10. Word stagger via `nth-child` — text-node spaces are NOT element children. Use `:nth-child(${i+1})`, NOT `${i*2+1}`.

## Architecture: stacked scenes + crossfade

ONE `index.html` with N `<div class="scene">` siblings stacked at `position: absolute; inset: 0; opacity: 0`. The master GSAP timeline crossfades them at beat boundaries.

This is *not* HyperFrames' native multi-clip scheduling — we deliberately use GSAP opacity so the engine sees one continuous scene. Lint will warn `timed_element_missing_clip_class`; that's expected and ignorable for this architecture.

## Audio elements (inside root, before scenes)

```html
<audio id="narration" src="audio/narration.wav" data-start="0" data-duration="40" data-track-index="0" data-volume="1"></audio>
<audio id="music"     src="audio/music.wav"     data-start="0" data-duration="40" data-track-index="1" data-volume="0.12"></audio>
<audio id="sfx-tap"   src="audio/sfx/tap.mp3"   data-start="27.8" data-duration="0.5" data-track-index="20" data-volume="0.55"></audio>
<!-- reuse same file at another time = different track-index -->
<audio id="sfx-thud1" src="audio/sfx/thud.mp3" data-start="29.85" data-duration="0.5" data-track-index="20"></audio>
<audio id="sfx-thud2" src="audio/sfx/thud.mp3" data-start="30.20" data-duration="0.5" data-track-index="21"></audio>
```

## Captions overlay

Absolute-positioned div at bottom 80px. Ink-pill background with bone-color text, hard 4px block-shadow in the brand accent color. One caption div per sentence, all stacked, swapped via `tl.set` + `tl.fromTo` at sentence-start times. Inter 600 32px.

## Grain layer

Full-bleed inline SVG noise, `mix-blend-mode: multiply`, opacity ~0.06, `pointer-events: none`. Drift `background-position` linearly across the composition for organic motion.

## Brand-mark patterns (generalize per site)

- Background dominant color = light/paper, not Silicon-Valley dark mode (unless brand demands)
- Hard offset block-shadows `8px 8px 0 #0A0A0A` — *no blur* — give a printed/sticker feel
- Inline highlights: wrap key facts in `<mark>` with `background: <accent-soft>; padding: 0 6px; border-radius: 3px;`
- Mono eyebrows: 11–14px JetBrains Mono uppercase, `letter-spacing: 0.12em`, ink-muted color
- Status pulse dot: 8px circle, `gsap.to(scale: 1↔1.18, sine.inOut, yoyo, calculated repeat)`

## Per-beat density

Aim for **6–10 visual elements per beat**: background texture, midground content, foreground accents, animated icons, typographic detail. Sparse beats look like JPEGs with progress bars. Heroes fill 50–70% of frame; every visible element gets mid-scene activity (Ken Burns drift, pulse, color shift).

## Common bugs (real ones from past builds)

| Bug | Symptom | Fix |
|---|---|---|
| `nth-child(i*2+1)` for word stagger | Only every other word animates in | Use `nth-child(i+1)` — text-node spaces aren't element children |
| ElevenLabs reads "live" as verb | "We're liv on the API" | Rewrite to "Built on" / "Running on" |
| SFX duration < 0.5s | API 400 with `invalid_generation_settings` | Min 0.5, max 30 seconds |
| Same SFX file overlaps on one track | Engine error or muted | Different `data-track-index` per `<audio>` instance |
| `transform: translate(-50%, -50%)` for centering | Element flies offscreen at first GSAP tween | Wrap in flexbox parent |
| Music too loud | VO unintelligible | Always `data-volume="0.10"–"0.15"` for underscore |
| Narration ≠ composition length | Trailing silence or audio cut off | Read narration duration with ffprobe FIRST, set composition to that + 1–1.5s |
| Static images at 100×100 | "JPEG with progress bar" | Heroes fill 50–70% of frame, every visible element gets mid-scene activity |

## Render quality presets

| Preset | CRF | Use for |
|---|---|---|
| `draft` | 28 | Iteration |
| `standard` | 18 | Internal review |
| `high` | 15 | Delivery |

For CI determinism: `--docker` (pinned Chrome + fonts → byte-stable output). For HDR delivery: `--hdr` (10-bit H.265 + HDR10 metadata).
