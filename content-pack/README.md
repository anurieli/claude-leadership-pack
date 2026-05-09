# Content Pack

Skills for content creation, marketing, and shipping.

## Skills

### extract-reel
Extract structured data from Instagram reels: timestamped transcript, visual descriptions, on-screen text, metadata, and content structure. Uses `yt-dlp` for download and Gemini for video analysis.

**Triggers:** "extract this reel", "break down this reel", "what's in this reel".

### podcast-to-guide
Turn a podcast episode (Spotify or YouTube URL) into a practical builder's guide — structured markdown + polished PDF. YouTube auto-subs first, Whisper API fallback.

**Triggers:** "summarize this podcast", "guide from podcast", "make a guide from this episode".

### site-to-video
Generate a marketing video, promo, ad, reel, or trailer from a website URL. Covers landscape, portrait, and square formats from 10s to 60s.

**Triggers:** "make a video for [URL]", "turn this site into a video", "30-second SaaS promo".

### launch-repo
Launch an open-source GitHub repo across multiple platforms in one command — GitHub metadata, Twitter/X threads, Reddit posts, Discord webhooks. Generates content for Hacker News, Product Hunt, and directories.

**Triggers:** "launch this repo", "post this everywhere", "promote this project".

## Install

```
/plugin marketplace add anurieli/claude-leadership-pack
/plugin install content-pack@claude-leadership-pack
```

## Setup

### Required
- **Python 3** with `pip` for `extract-reel` and `podcast-to-guide` scripts.
- **`yt-dlp`** — `pip install yt-dlp`
- **`reportlab`** (for `podcast-to-guide` PDFs) — `pip install reportlab`
- **DejaVu fonts** — system-installed in one of `~/Library/Fonts`, `/usr/share/fonts/truetype/dejavu`, or `/Library/Fonts`.

### Environment variables
Set these in your shell profile or via `claude config set --global env.<NAME> <value>`.

| Variable | Used by | Required? | Notes |
|---|---|---|---|
| `GEMINI_API_KEY` | extract-reel | Yes | Get one at [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| `OPENAI_API_KEY` | podcast-to-guide | Optional | Only used if YouTube auto-subs are unavailable (Whisper fallback, ~$0.006/min audio) |
| `PODCAST_GUIDE_DIR` | podcast-to-guide | Optional | Output directory for guides + PDFs. Defaults to `~/podcast-guides/`. |
| GitHub / Twitter / Reddit / Discord credentials | launch-repo | Optional per platform | See `launch-repo/SKILL.md` for details — skips platforms whose creds aren't set. |

No keys are stored in this repo. See `.env.example` for the full list.
