---
name: podcast-to-guide
description: Turn a podcast episode into a practical builder's guide. Takes a Spotify or YouTube URL, fetches the transcript (YouTube auto-subs first, Whisper API fallback), extracts a structured summary, and produces both a markdown working file and a CTE-branded PDF resource. Files outputs into Brain Vault under 05-Resources/sources/ and 05-Resources/assets/. Use when Ariel says "podcast to guide", "summarize this podcast", "guide from podcast", "transcribe this episode", "AI Daily Brief guide", "make a guide from this episode", or shares a Spotify/YouTube podcast URL and wants a guide. Default tone targets a builder skimming for what to act on, not a casual listener.
---

# Podcast To Guide

Turns a podcast URL into a structured guide. Two outputs:

- **`.md`** — internal working file. Frontmatter, structured guide content, full transcript appended at the bottom. Lives in `${PODCAST_GUIDE_DIR:-$HOME/podcast-guides}/sources/`.
- **`.pdf`** — Polished handout PDF. Lives in `${PODCAST_GUIDE_DIR:-$HOME/podcast-guides}/assets/`.

**Output location:** set `PODCAST_GUIDE_DIR` to control where guides are saved. Defaults to `~/podcast-guides/`. Create it if it doesn't exist.

Optimized for Nathaniel Whittemore's *AI Daily Brief* (the AI news podcast Ariel listens to daily), but works on any podcast that exists on YouTube.

## Pipeline

```
URL -> resolve to YouTube -> auto-subs (or Whisper fallback) -> structured guide -> md + pdf -> file in vault
```

## Step-by-step

### 1. Fetch transcript

Run the fetch script. It accepts Spotify or YouTube URLs.

```bash
python3 "$(dirname "$0")/scripts/fetch_transcript.py" "<URL>" --out /tmp/podcast.json
# (or absolute path: python3 <skill-dir>/scripts/fetch_transcript.py)
```

Output JSON keys: `title`, `channel`, `duration_s`, `upload_date`, `youtube_url`, `transcript`, `transcript_source` (`youtube-auto-subs` or `whisper-api`).

If you see `transcript_source = whisper-api`, Whisper was used (requires `OPENAI_API_KEY`). Cost: ~$0.006/min audio.

### 2. Read the transcript and structure the guide

Read `/tmp/podcast.json` and produce a structured guide following the schema in `references/guide_schema.md`. Always read that file before structuring the guide. The schema is strict, the quality bar matters.

Key extraction priorities (in this order):
1. **Top stories** — the meat of the episode. NLW's daily format usually has 3-6 distinct stories.
2. **Builder takeaways** — what should Ariel (a solo builder shipping AI products) actually do based on this episode.
3. **Tools/companies/models mentioned** — capture every name. This is the index later.
4. **TL;DR** — write this last, after the rest is structured.
5. **Quotes** — only if the wording itself carries the value.

Save the structured guide to `/tmp/guide.json`.

### 3. Render the PDF

```bash
python3 <skill-dir>/scripts/render_pdf.py /tmp/guide.json -o /tmp/guide.pdf
```

The script handles all branding (dark mode, #00B050 accent, DejaVu fonts, headers, footers, page numbers). Don't customize per-episode.

### 4. Write the markdown working file

Use this layout. Filename slug pattern: `podcast-<creator-slug>-YYYY-MM-DD-<title-slug>.md` (e.g., `podcast-ai-daily-brief-2026-05-01-anthropic-ships-mcp-2.md`).

```markdown
---
type: wiki
category: source
date: <today YYYY-MM-DD>
updated: <today YYYY-MM-DD>
source_type: podcast
source_url: <original URL the user gave>
youtube_url: <resolved YouTube URL>
creator: <channel handle if known>
creator_name: <channel display name>
date_posted: <upload_date YYYY-MM-DD>
date_ingested: <today YYYY-MM-DD>
domain: ai-tools
topics:
  - <topic-1>
  - <topic-2>
transcript_source: <youtube-auto-subs | whisper-api>
duration_s: <integer>
pdf_asset: ../assets/<same-slug>.pdf
tags:
  - wiki/resources
  - source/podcast
---

> [!nav] <- [[05-Resources/index|Resources Wiki]]

# <Episode Title>

**PDF guide**: [[../assets/<same-slug>.pdf|Download branded PDF]]

## TL;DR
- ...

## Top Stories
### <Headline>
**Why it matters**: ...
- ...

## Builder Takeaways
1. ...

## Tools & Names Mentioned
- **<Name>**: <note>

## Notable Quotes
> "<text>"
> source: <speaker>

---

## Full Transcript
<source: <transcript_source>>

<paste full transcript here, lightly cleaned (no double blank lines)>
```

### 5. File outputs in the vault

```bash
OUT_DIR="${PODCAST_GUIDE_DIR:-$HOME/podcast-guides}"
mkdir -p "$OUT_DIR/sources" "$OUT_DIR/assets"
SLUG="podcast-ai-daily-brief-2026-05-01-<title-slug>"
mv /tmp/guide.md "$OUT_DIR/sources/${SLUG}.md"
mv /tmp/guide.pdf "$OUT_DIR/assets/${SLUG}.pdf"
```

Then append a one-line entry to `$OUT_DIR/log.md` with the date, slug, and a 1-sentence "what this episode was about".

### 6. Confirm to user

Reply briefly: vault path of the .md, vault path of the .pdf, and what the episode covered in one sentence. Offer to open the PDF (`open <path>`).

## Slugging rules

- Lowercase, hyphenated, ASCII only.
- Strip stopwords aggressively: drop "the", "a", "an", "and".
- Keep proper nouns and numbers.
- Cap title-slug at 6 words.

## When auto-subs are bad

YouTube auto-subs occasionally garble names ("ChatGPT" -> "chat GPT"). When rendering the guide, lightly correct obvious entity-name errors using context. Don't over-correct. The raw transcript stays in the .md as ground truth.

## Hermes / cron portability

This skill is self-contained. Required runtime: Python 3, `yt-dlp`, `reportlab`, DejaVu fonts in one of `~/Library/Fonts`, `/usr/share/fonts/truetype/dejavu`, or `/Library/Fonts`. Optional: `OPENAI_API_KEY` for Whisper fallback. No other env needed.

For a Jarvis cron that auto-runs on new AI Daily Brief episodes, point it at the YouTube channel feed (`https://www.youtube.com/@AIDailyBrief`) and pass the latest video URL straight to `fetch_transcript.py`.

## Style guardrails

- No em dashes anywhere in output. Use periods, commas, colons, semicolons.
- The .md is internal: be terse and concrete, no marketing voice.
- The PDF is a resource: tighter prose, but still no hype. Bullet substance, not adjectives.
