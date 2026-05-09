---
name: extract-reel
description: >
  Extract structured data from Instagram reels. Takes a reel URL and returns JSON with
  timestamped transcript, visual descriptions, on-screen text, metadata (views, likes, comments,
  creator), and content structure. Uses yt-dlp for download and Gemini for video analysis.
  Triggers: 'extract this reel', 'reel extract', 'what's in this reel', 'break down this reel',
  'pull data from this reel', 'extract reel', or when another skill/workflow needs raw reel data.
---

# Extract Reel

Extract structured data from an Instagram reel URL. Returns JSON with transcript, visuals,
on-screen text, engagement metadata, and content structure.

## Requirements

- Python 3.10+
- `GEMINI_API_KEY` environment variable set
- Instagram login in a local browser (Chrome, Firefox, Safari, or Edge) for cookie-based auth

Dependencies (`yt-dlp`, `google-genai`, `pydantic`) are auto-installed on first run.

## Usage

### Standard extraction

1. User provides an Instagram reel URL.
2. Run the extraction script:

```bash
python3 <skill-dir>/extract_reel.py "<URL>" --model gemini-3.1-pro-preview
```

3. The script outputs JSON to stdout. Present a readable summary to the user.
4. If another skill in a chain needs the data, capture the JSON output and pass it forward.

### Dependency check

If this is the first time running the skill, or if the user reports missing packages:

```bash
python3 <skill-dir>/extract_reel.py --check-deps
```

### Model comparison

When the user wants to compare Flash vs Pro quality, or on first use for calibration:

1. Run with Flash:
```bash
python3 <skill-dir>/extract_reel.py "<URL>" --model gemini-3-flash-preview
```

2. Run with Pro:
```bash
python3 <skill-dir>/extract_reel.py "<URL>" --model gemini-3.1-pro-preview
```

3. Present both outputs side by side with a cost comparison.

## Error Handling

If the script exits with an error:

- **"GEMINI_API_KEY not set"**: Tell the user to set it:
  `claude config set --global env.GEMINI_API_KEY 'your-key'`
  or `export GEMINI_API_KEY='your-key'` in their shell profile.

- **"Instagram requires authentication"**: The user needs to be logged into Instagram in
  Chrome, Firefox, Safari, or Edge. The script reads browser cookies automatically.
  Alternatively, they can set `INSTAGRAM_COOKIES` env var to a cookies.txt file path.

- **Other download errors**: The URL may be invalid, the reel may be private, or Instagram
  may be rate-limiting. Ask the user to verify the URL and try again.

## Output Format

The script outputs a single JSON object to stdout:

```json
{
  "source_url": "https://www.instagram.com/reel/...",
  "platform": "instagram",
  "metadata": {
    "creator": "@handle",
    "creator_name": "Display Name",
    "post_date": "2026-04-10",
    "caption": "...",
    "hashtags": ["tag1", "tag2"],
    "views": 124000,
    "likes": 8500,
    "comments": 342,
    "audio_track": "Original Audio",
    "duration_seconds": 47
  },
  "extraction": {
    "transcript": [{ "timestamp": "00:00", "end": "00:05", "text": "..." }],
    "visuals": [{ "timestamp": "00:00", "end": "00:05", "description": "..." }],
    "on_screen_text": [{ "timestamp": "00:02", "text": "..." }],
    "content_structure": {
      "hook": "...",
      "body": "...",
      "cta": "..."
    }
  },
  "model_used": "gemini-3.1-pro-preview",
  "extracted_at": "2026-04-14T15:30:00+00:00"
}
```

## Available Models

| Model | ID | Cost per reel (~60s) | Quality |
|---|---|---|---|
| Gemini 3 Flash | `gemini-3-flash-preview` | ~$0.02 | Good |
| Gemini 3.1 Pro | `gemini-3.1-pro-preview` | ~$0.07 | Best |

Default: `gemini-3.1-pro-preview`
