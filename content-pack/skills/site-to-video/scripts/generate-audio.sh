#!/usr/bin/env bash
# Generate narration + music + transcript for a project.
# Reads .build/SCRIPT.md for the narration text (everything after "## Narration").
#
# Usage: generate-audio.sh <voice-id> [music-prompt] [music-length-ms]
#
# Run from the project root (not .build/). Outputs land in .build/audio/.
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <voice-id> [music-prompt] [music-length-ms]" >&2
  echo "  Voice IDs: see references/voices.json (brian, bill, liam, mark)" >&2
  exit 1
fi

VOICE_ID="$1"
MUSIC_PROMPT="${2:-Upbeat modern app trailer instrumental, 105 BPM, driving synth bass, crisp clap percussion, bright melodic plucky lead, optimistic, builds steadily, NO vocals}"
MUSIC_LEN_MS="${3:-40000}"

if [[ -z "${ELEVENLABS_KEY:-}" ]]; then
  echo "ELEVENLABS_KEY env var not set." >&2
  exit 1
fi
if [[ ! -f .build/SCRIPT.md ]]; then
  echo "No .build/SCRIPT.md found. Run from project root." >&2
  exit 1
fi

mkdir -p .build/audio/sfx

# Extract narration text (everything after "## Narration" header, until next ## header or EOF)
NARRATION=$(awk '/^## Narration/{flag=1; next} /^## /{flag=0} flag' .build/SCRIPT.md | sed '/^$/d')
if [[ -z "$NARRATION" ]]; then
  echo "Could not find '## Narration' section in .build/SCRIPT.md" >&2
  exit 1
fi

echo "→ Generating narration ..."
python3 -c "
import json, sys
print(json.dumps({
  'text': sys.argv[1],
  'model_id': 'eleven_v3',
  'voice_settings': {'stability':0.4,'similarity_boost':0.75,'style':0.5,'use_speaker_boost':True}
}))" "$NARRATION" | \
curl -s -X POST \
  -H "xi-api-key: $ELEVENLABS_KEY" \
  -H "Content-Type: application/json" \
  -o .build/audio/narration.mp3 \
  -d @- \
  "https://api.elevenlabs.io/v1/text-to-speech/$VOICE_ID"

echo "→ Converting to WAV (48kHz stereo) ..."
ffmpeg -y -loglevel error -i .build/audio/narration.mp3 -ar 48000 -ac 2 .build/audio/narration.wav

DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 .build/audio/narration.wav)
echo "  Narration duration: ${DURATION}s"

echo "→ Generating music (${MUSIC_LEN_MS}ms) ..."
curl -s -X POST \
  -H "xi-api-key: $ELEVENLABS_KEY" \
  -H "Content-Type: application/json" \
  -o .build/audio/music.mp3 \
  -d "{\"prompt\":$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$MUSIC_PROMPT"),\"music_length_ms\":$MUSIC_LEN_MS}" \
  "https://api.elevenlabs.io/v1/music"
ffmpeg -y -loglevel error -i .build/audio/music.mp3 -ar 48000 -ac 2 .build/audio/music.wav

echo "→ Transcribing for word-level timestamps ..."
HF=$(command -v hyperframes || echo "npx --yes hyperframes@latest")
$HF transcribe .build/audio/narration.wav --model small.en --language en --output .build/transcript.json

echo
echo "✓ Audio ready. Narration: ${DURATION}s. Set composition data-duration to $(python3 -c "print(round($DURATION + 1.2, 1))")"
echo "  Now generate SFX with curl per the storyboard, then build .build/index.html scenes."
