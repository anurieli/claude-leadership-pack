# Extract Reel

Extract structured data from Instagram reels. Returns JSON with timestamped transcript, visual descriptions, on-screen text, engagement metrics, and content structure.

## What it does

Give it an Instagram reel URL, get back structured JSON with everything in the video: what was said, what was shown, what text appeared on screen, engagement stats, and how the content was structured (hook/body/CTA).

Uses **yt-dlp** to download the video and **Gemini** to analyze it. No local ML models needed.

## Setup

### 1. Get a Gemini API key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create an API key
3. The free tier works for Flash. Pro requires the paid tier.

### 2. Set the API key

In Claude Code:
```bash
claude config set --global env.GEMINI_API_KEY your-key-here
```

Or in your shell profile (`~/.zshrc` or `~/.bashrc`):
```bash
export GEMINI_API_KEY="your-key-here"
```

### 3. Log into Instagram

The script needs browser cookies to download reels. Just be logged into Instagram in **Chrome, Firefox, Safari, or Edge**. It detects cookies automatically.

Alternative: export a `cookies.txt` file and set:
```bash
export INSTAGRAM_COOKIES="/path/to/cookies.txt"
```

### 4. Install the skill

Copy the `extract-reel/` folder to `~/.claude/skills/`:
```
~/.claude/skills/extract-reel/
├── SKILL.md           # Claude reads this
├── extract_reel.py    # Pipeline script
└── README.md          # You're reading this
```

Python dependencies (`yt-dlp`, `google-genai`, `pydantic`) are auto-installed on first run.

To verify everything is set up:
```bash
python ~/.claude/skills/extract-reel/extract_reel.py --check-deps
```

## Usage

In Claude Code, say any of:
- "extract this reel: [url]"
- "what's in this reel: [url]"
- "break down this reel: [url]"

Or run directly:
```bash
python ~/.claude/skills/extract-reel/extract_reel.py "https://www.instagram.com/reel/..." --model gemini-3.1-pro-preview
```

## Models

| Model | Flag | Cost per ~60s reel | Quality |
|-------|------|--------------------|---------|
| Gemini 3.1 Pro | `--model gemini-3.1-pro-preview` | ~$0.07 | Best (default) |
| Gemini 3 Flash | `--model gemini-3-flash-preview` | ~$0.02 | Good |

## Output

JSON to stdout with this structure:

```json
{
  "source_url": "https://www.instagram.com/reel/...",
  "platform": "instagram",
  "metadata": {
    "creator": "@handle",
    "creator_name": "Display Name",
    "post_date": "2026-04-10",
    "caption": "...",
    "hashtags": [],
    "views": 124000,
    "likes": 8500,
    "comments": 342,
    "audio_track": "",
    "duration_seconds": 47
  },
  "extraction": {
    "transcript": [{ "timestamp": "00:00", "end": "00:05", "text": "..." }],
    "visuals": [{ "timestamp": "00:00", "end": "00:05", "description": "..." }],
    "on_screen_text": [{ "timestamp": "00:02", "text": "..." }],
    "content_structure": {
      "hook": "How the reel opens",
      "body": "Main content",
      "cta": "Call to action (empty string if none)"
    }
  },
  "model_used": "gemini-3.1-pro-preview",
  "extracted_at": "2026-04-14T15:30:00+00:00"
}
```

## Troubleshooting

| Error | Fix |
|-------|-----|
| "GEMINI_API_KEY not set" | Set the key (see Setup step 2) |
| "Instagram requires authentication" | Log into Instagram in your browser, or set INSTAGRAM_COOKIES |
| "RESOURCE_EXHAUSTED" / 429 | Free tier quota hit. Upgrade to paid Gemini API tier. |
| Download fails | Check the URL is valid and the reel isn't private |

## Requirements

- Python 3.10+
- A Gemini API key
- Instagram login in a browser (for cookie-based download)
