# Changelog

---

## 2026-04-14 21:04 | 46ad27a | feat(extract-reel): Gemini upload and structured video extraction

**Title:** Implement extract_with_gemini (Task 3)

**Summary:** Replaced the `extract_with_gemini` stub with a full implementation using the `google-genai` SDK. Added the `EXTRACTION_PROMPT` constant (covering transcript, visuals, on-screen text, and content structure). The function uploads the video file to Gemini, requests structured JSON output using `Extraction.model_json_schema()`, parses the response via Pydantic, and cleans up the uploaded file with best-effort deletion.

**Files touched:**
- `extract-reel/extract_reel.py`

---

## 2026-04-14 18:10 | 68a5420 | feat(extract-reel): scaffold script with dep installer, output models, and CLI

**Title:** Initial scaffold (Tasks 1 and 2)

**Summary:** Created `extract_reel.py` with dependency auto-installer, all Pydantic output models (TranscriptSegment, VisualSegment, OnScreenText, ContentStructure, Extraction, ReelMetadata, ReelExtraction), the `download_reel` function with yt-dlp and auto cookie detection, and the CLI entry point. Stubs left for Tasks 3 and 4.

**Files touched:**
- `extract-reel/extract_reel.py`
