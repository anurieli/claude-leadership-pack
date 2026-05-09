#!/Users/jarvis/.claude/skills/extract-reel/.venv/bin/python
"""
extract_reel.py -- Download an Instagram reel and extract structured data via Gemini.

Usage:
    python extract_reel.py <url> [--model MODEL_ID]
    python extract_reel.py --check-deps

Output: JSON to stdout. Errors to stderr.
"""

import subprocess
import sys
import os
import json
import tempfile
import argparse
import re
import glob as glob_module
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Dependency auto-installer
# ---------------------------------------------------------------------------

REQUIRED_PACKAGES = {
    "yt_dlp": "yt-dlp",
    "google.genai": "google-genai",
    "pydantic": "pydantic",
}


def ensure_dependencies():
    """Check for required packages and install any that are missing."""
    missing = []
    for import_name, pip_name in REQUIRED_PACKAGES.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pip_name)

    if missing:
        print(f"Installing missing dependencies: {', '.join(missing)}", file=sys.stderr)
        # Try uv pip first (for uv-managed Python), fall back to regular pip
        try:
            subprocess.check_call(
                ["uv", "pip", "install", "--quiet", "--python", sys.executable] + missing
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--quiet"] + missing
            )
        # Re-check after install
        for import_name, pip_name in REQUIRED_PACKAGES.items():
            try:
                __import__(import_name)
            except ImportError:
                print(f"ERROR: Failed to install {pip_name}. Install manually: pip install {pip_name}", file=sys.stderr)
                sys.exit(1)


ensure_dependencies()

# Now safe to import
from pydantic import BaseModel, Field
from typing import Optional
from google import genai


# ---------------------------------------------------------------------------
# Output schema (Pydantic models)
# ---------------------------------------------------------------------------

class TranscriptSegment(BaseModel):
    timestamp: str = Field(description="Start timestamp in MM:SS format")
    end: str = Field(description="End timestamp in MM:SS format")
    text: str = Field(description="What was said in this segment")


class VisualSegment(BaseModel):
    timestamp: str = Field(description="Start timestamp in MM:SS format")
    end: str = Field(description="End timestamp in MM:SS format")
    description: str = Field(description="What was shown on screen in this segment")


class OnScreenText(BaseModel):
    timestamp: str = Field(description="Timestamp in MM:SS format when text appears")
    text: str = Field(description="The overlay text, title, subtitle, or CTA")


class ContentStructure(BaseModel):
    hook: str = Field(description="How the reel opens and grabs attention")
    body: str = Field(description="Main content, message, or teaching")
    cta: str = Field(description="Call to action if present, empty string if none")


class Extraction(BaseModel):
    transcript: list[TranscriptSegment] = Field(description="Timestamped transcript of speech")
    visuals: list[VisualSegment] = Field(description="Timestamped visual scene descriptions")
    on_screen_text: list[OnScreenText] = Field(description="Text overlays, titles, captions shown on screen")
    content_structure: ContentStructure = Field(description="Hook/body/CTA structure of the content")


class ReelMetadata(BaseModel):
    creator: str = Field(description="Instagram handle with @ prefix")
    creator_name: str = Field(default="", description="Display name of the creator")
    post_date: str = Field(default="", description="Post date in YYYY-MM-DD format")
    caption: str = Field(default="", description="Full caption text")
    hashtags: list[str] = Field(default_factory=list, description="Hashtags from the caption")
    views: Optional[int] = Field(default=None, description="View count")
    likes: Optional[int] = Field(default=None, description="Like count")
    comments: Optional[int] = Field(default=None, description="Comment count")
    audio_track: str = Field(default="", description="Music or audio source")
    duration_seconds: Optional[float] = Field(default=None, description="Video duration in seconds")


class ReelExtraction(BaseModel):
    source_url: str
    platform: str = "instagram"
    metadata: ReelMetadata
    extraction: Extraction
    model_used: str
    extracted_at: str


# ---------------------------------------------------------------------------
# Pipeline functions (implemented in subsequent tasks)
# ---------------------------------------------------------------------------

def _parse_hashtags(caption: str) -> list[str]:
    """Extract hashtags from caption text."""
    return re.findall(r"#(\w+)", caption)


def download_reel(url: str, output_dir: str) -> tuple[str, dict]:
    """Download reel video and extract page metadata via yt-dlp."""
    import yt_dlp

    output_template = os.path.join(output_dir, "%(id)s.%(ext)s")

    # Try cookie sources in order: browser cookies, env var cookies file, no cookies
    cookie_opts = {}
    cookies_file = os.environ.get("INSTAGRAM_COOKIES")
    if cookies_file and os.path.exists(cookies_file):
        cookie_opts["cookiefile"] = cookies_file
        print("Using cookies file from INSTAGRAM_COOKIES env var", file=sys.stderr)
    else:
        # Try common browsers for automatic cookie extraction
        for browser in ["chrome", "firefox", "safari", "edge"]:
            try:
                test_opts = {
                    "cookiesfrombrowser": (browser,),
                    "quiet": True,
                    "simulate": True,
                }
                with yt_dlp.YoutubeDL(test_opts) as ydl:
                    ydl.extract_info(url, download=False)
                cookie_opts["cookiesfrombrowser"] = (browser,)
                print(f"Using cookies from {browser}", file=sys.stderr)
                break
            except Exception:
                continue

    ydl_opts = {
        "outtmpl": output_template,
        "writeinfojson": True,
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        **cookie_opts,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "login" in error_msg.lower() or "cookie" in error_msg.lower() or "403" in error_msg:
            print(
                f"ERROR: Instagram requires authentication to download this reel.\n"
                f"Options:\n"
                f"  1. Log into Instagram in Chrome/Firefox (cookies are read automatically)\n"
                f"  2. Set INSTAGRAM_COOKIES env var to a cookies.txt file path\n"
                f"Original error: {error_msg}",
                file=sys.stderr,
            )
        else:
            print(f"ERROR: Failed to download reel: {error_msg}", file=sys.stderr)
        sys.exit(1)

    # Find the downloaded video file
    video_files = glob_module.glob(os.path.join(output_dir, "*.mp4"))
    if not video_files:
        video_files = glob_module.glob(os.path.join(output_dir, "*.webm"))
    if not video_files:
        # Grab any video file
        all_files = os.listdir(output_dir)
        video_files = [
            os.path.join(output_dir, f) for f in all_files
            if not f.endswith(".json") and not f.startswith(".")
        ]
    if not video_files:
        print("ERROR: No video file found after download", file=sys.stderr)
        sys.exit(1)

    video_path = video_files[0]

    # Build metadata dict from yt-dlp info
    caption = info.get("description", "") or ""
    metadata = {
        "creator": f"@{info.get('uploader_id', info.get('channel_id', 'unknown'))}",
        "creator_name": info.get("uploader", info.get("channel", "")),
        "post_date": info.get("upload_date", ""),
        "caption": caption,
        "hashtags": _parse_hashtags(caption),
        "views": info.get("view_count"),
        "likes": info.get("like_count"),
        "comments": info.get("comment_count"),
        "audio_track": info.get("track", info.get("artist", "")),
        "duration_seconds": info.get("duration"),
    }

    # Format date from YYYYMMDD to YYYY-MM-DD
    if metadata["post_date"] and len(metadata["post_date"]) == 8:
        d = metadata["post_date"]
        metadata["post_date"] = f"{d[:4]}-{d[4:6]}-{d[6:8]}"

    return video_path, metadata


EXTRACTION_PROMPT = """Analyze this Instagram reel video completely. Extract ALL of the following:

1. TRANSCRIPT: Every word spoken in the video, broken into natural segments with timestamps.
   - If no one speaks, return an empty list.

2. VISUALS: Describe what is shown on screen in each distinct scene or visual change.
   - Include: settings, people, actions, camera angles, transitions, b-roll.
   - Be specific and descriptive, not generic.

3. ON-SCREEN TEXT: Every piece of text that appears overlaid on the video.
   - Include: titles, subtitles, captions, bullet points, CTAs, watermarks, handles.
   - Capture the exact text as shown.

4. CONTENT STRUCTURE:
   - hook: How does the reel open? What grabs attention in the first 1-3 seconds?
   - body: What is the main message, teaching, story, or content?
   - cta: Is there a call to action? (follow, comment, link in bio, etc.) Empty string if none.

Be thorough. Capture everything. Timestamps should be in MM:SS format."""


def extract_with_gemini(video_path: str, model: str) -> Extraction:
    """Upload video to Gemini and return structured extraction."""
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    print(f"Uploading video to Gemini...", file=sys.stderr)
    uploaded_file = client.files.upload(file=video_path)

    # Wait for file to finish processing
    import time
    while uploaded_file.state.name == "PROCESSING":
        print("Waiting for video processing...", file=sys.stderr)
        time.sleep(3)
        uploaded_file = client.files.get(name=uploaded_file.name)

    if uploaded_file.state.name != "ACTIVE":
        print(f"ERROR: File processing failed with state: {uploaded_file.state.name}", file=sys.stderr)
        sys.exit(1)

    print(f"Upload complete. Extracting with {model}...", file=sys.stderr)

    response = client.models.generate_content(
        model=model,
        contents=[uploaded_file, EXTRACTION_PROMPT],
        config={
            "response_mime_type": "application/json",
            "response_json_schema": Extraction.model_json_schema(),
        },
    )

    try:
        extraction = Extraction.model_validate_json(response.text)
    except Exception as e:
        print(f"WARNING: Failed to parse structured response, attempting raw JSON parse: {e}", file=sys.stderr)
        raw = json.loads(response.text)
        extraction = Extraction.model_validate(raw)

    # Clean up uploaded file
    try:
        client.files.delete(name=uploaded_file.name)
    except Exception:
        pass  # Best effort cleanup

    return extraction


def build_output(url: str, metadata: dict, extraction: Extraction, model: str) -> ReelExtraction:
    """Merge yt-dlp metadata with Gemini extraction into final output."""
    return ReelExtraction(
        source_url=url,
        platform="instagram",
        metadata=ReelMetadata(**metadata),
        extraction=extraction,
        model_used=model,
        extracted_at=datetime.now(timezone.utc).isoformat(),
    )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Extract structured data from an Instagram reel")
    parser.add_argument("url", nargs="?", help="Instagram reel URL")
    parser.add_argument("--model", default="gemini-3.1-pro-preview", help="Gemini model ID")
    parser.add_argument("--check-deps", action="store_true", help="Check/install dependencies and exit")

    args = parser.parse_args()

    if args.check_deps:
        print("All dependencies installed.", file=sys.stderr)
        sys.exit(0)

    if not args.url:
        parser.error("URL is required")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(
            "ERROR: GEMINI_API_KEY not set.\n"
            "Set it with: export GEMINI_API_KEY='your-key'\n"
            "Or in Claude Code: claude config set --global env.GEMINI_API_KEY 'your-key'",
            file=sys.stderr,
        )
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmp_dir:
        video_path, metadata = download_reel(args.url, tmp_dir)
        extraction = extract_with_gemini(video_path, args.model)
        result = build_output(args.url, metadata, extraction, args.model)
        print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
