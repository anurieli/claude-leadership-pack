#!/usr/bin/env python3
"""Resolve a podcast URL to a transcript + metadata.

Pipeline:
1. Spotify URL -> scrape episode title -> YouTube search
2. YouTube URL -> direct
3. Try YouTube auto-subs via yt-dlp (free, fast)
4. Fallback: download audio + transcribe via OpenAI Whisper API

Output: JSON to stdout with {title, channel, duration_s, date, source_url, youtube_url, transcript, transcript_source}.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

YT_HOSTS = ("youtube.com", "youtu.be", "music.youtube.com")
SPOTIFY_HOSTS = ("open.spotify.com", "spotify.com")


def log(msg: str) -> None:
    print(f"[fetch_transcript] {msg}", file=sys.stderr, flush=True)


def is_youtube(url: str) -> bool:
    return any(h in url for h in YT_HOSTS)


def is_spotify(url: str) -> bool:
    return any(h in url for h in SPOTIFY_HOSTS)


def fetch_spotify_title(url: str) -> str:
    """Scrape <title> from a Spotify episode page (no auth needed)."""
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=20) as r:
        html = r.read().decode("utf-8", errors="ignore")
    m = re.search(r"<title>([^<]+)</title>", html)
    if not m:
        raise RuntimeError("Could not parse Spotify page title")
    title = m.group(1)
    title = re.sub(r"\s*\|\s*Spotify.*$", "", title)
    title = re.sub(r"\s*-\s*Podcast on Spotify.*$", "", title)
    return title.strip()


def youtube_search(query: str) -> str:
    """Use yt-dlp to find the top YouTube hit for a query. Returns full URL."""
    cmd = [
        "yt-dlp",
        f"ytsearch1:{query}",
        "--print", "%(webpage_url)s",
        "--no-download",
        "--no-warnings",
        "--quiet",
    ]
    out = subprocess.check_output(cmd, text=True).strip()
    if not out.startswith("http"):
        raise RuntimeError(f"yt-dlp search returned no URL for: {query}")
    return out.splitlines()[0]


def yt_metadata(url: str) -> dict:
    cmd = [
        "yt-dlp", url,
        "--dump-json",
        "--no-download",
        "--no-warnings",
        "--quiet",
    ]
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)


def vtt_to_text(vtt_path: Path) -> str:
    """Strip VTT timing/cue lines, dedupe consecutive duplicate captions, return plain text."""
    lines = vtt_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    out: list[str] = []
    last = None
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if s.startswith("WEBVTT") or s.startswith("Kind:") or s.startswith("Language:"):
            continue
        if "-->" in s:
            continue
        if re.fullmatch(r"\d+", s):
            continue
        s = re.sub(r"<[^>]+>", "", s)
        s = re.sub(r"\s+", " ", s).strip()
        if not s or s == last:
            continue
        out.append(s)
        last = s
    return "\n".join(out)


def fetch_auto_subs(url: str, workdir: Path) -> str | None:
    """Try YouTube auto-subs (en). Returns plain text or None."""
    cmd = [
        "yt-dlp", url,
        "--skip-download",
        "--write-auto-subs",
        "--sub-lang", "en.*",
        "--sub-format", "vtt",
        "--convert-subs", "vtt",
        "-o", str(workdir / "%(id)s.%(ext)s"),
        "--no-warnings",
        "--quiet",
    ]
    subprocess.run(cmd, check=False)
    vtts = sorted(workdir.glob("*.vtt"))
    if not vtts:
        return None
    log(f"using auto-subs: {vtts[0].name}")
    return vtt_to_text(vtts[0])


def fetch_whisper(url: str, workdir: Path) -> str:
    """Download audio and transcribe via OpenAI Whisper API."""
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "No YouTube captions found and OPENAI_API_KEY is not set. "
            "Set it to enable Whisper fallback transcription."
        )
    audio_path = workdir / "audio.m4a"
    cmd = [
        "yt-dlp", url,
        "-f", "bestaudio[ext=m4a]/bestaudio",
        "-o", str(audio_path),
        "--no-warnings",
        "--quiet",
    ]
    subprocess.run(cmd, check=True)
    if not audio_path.exists():
        candidates = list(workdir.glob("audio.*"))
        if not candidates:
            raise RuntimeError("yt-dlp did not produce an audio file")
        audio_path = candidates[0]

    log(f"transcribing via Whisper API: {audio_path.name} ({audio_path.stat().st_size // 1024} KB)")
    from openai import OpenAI
    client = OpenAI()
    with open(audio_path, "rb") as f:
        resp = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="text",
        )
    return resp if isinstance(resp, str) else getattr(resp, "text", str(resp))


def resolve_to_youtube(url: str) -> str:
    if is_youtube(url):
        return url
    if is_spotify(url):
        title = fetch_spotify_title(url)
        log(f"spotify title: {title}")
        return youtube_search(title)
    raise SystemExit(f"Unsupported URL host: {url}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("url", help="Spotify or YouTube URL")
    ap.add_argument("--force-whisper", action="store_true",
                    help="Skip auto-subs and go straight to Whisper API")
    ap.add_argument("--out", help="Optional path to write JSON output")
    args = ap.parse_args()

    yt_url = resolve_to_youtube(args.url)
    log(f"youtube: {yt_url}")
    meta = yt_metadata(yt_url)

    with tempfile.TemporaryDirectory() as td:
        wd = Path(td)
        transcript = None
        source = None

        if not args.force_whisper:
            transcript = fetch_auto_subs(yt_url, wd)
            if transcript:
                source = "youtube-auto-subs"

        if not transcript:
            log("no usable captions, falling back to Whisper")
            transcript = fetch_whisper(yt_url, wd)
            source = "whisper-api"

    result = {
        "title": meta.get("title"),
        "channel": meta.get("channel") or meta.get("uploader"),
        "channel_url": meta.get("channel_url") or meta.get("uploader_url"),
        "duration_s": meta.get("duration"),
        "upload_date": meta.get("upload_date"),
        "source_url": args.url,
        "youtube_url": yt_url,
        "video_id": meta.get("id"),
        "description": meta.get("description"),
        "transcript_source": source,
        "transcript": transcript,
    }
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        log(f"wrote {args.out}")
    print(payload)


if __name__ == "__main__":
    main()
