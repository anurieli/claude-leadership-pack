#!/usr/bin/env bash
# Generate audition samples from every voice in references/voices.json
# on a single sentence so you can pick before committing.
#
# Usage: audition-voices.sh "Your hook sentence here." [output-dir]
#
# Requires: ELEVENLABS_KEY env var.
# Outputs: audition-{name}.mp3 in cwd (or chosen dir).
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 \"<sentence>\" [output-dir]" >&2
  exit 1
fi

if [[ -z "${ELEVENLABS_KEY:-}" ]]; then
  echo "ELEVENLABS_KEY env var not set." >&2
  exit 1
fi

TEXT="$1"
OUTDIR="${2:-.}"
mkdir -p "$OUTDIR"

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VOICES_JSON="$SKILL_DIR/references/voices.json"

VOICE_LIST=$(python3 - "$VOICES_JSON" <<'PY'
import json, sys
v = json.load(open(sys.argv[1]))
for name, meta in v["voices"].items():
    print(f"{name}\t{meta['id']}")
PY
)

while IFS=$'\t' read -r name id; do
  [[ -z "$name" ]] && continue
  echo "→ Generating audition-$name.mp3 ..."
  PAYLOAD=$(python3 -c "
import json, sys
print(json.dumps({
  'text': sys.argv[1],
  'model_id': 'eleven_v3',
  'voice_settings': {'stability':0.4,'similarity_boost':0.75,'style':0.5,'use_speaker_boost':True}
}))" "$TEXT")
  curl -s -X POST \
    -H "xi-api-key: $ELEVENLABS_KEY" \
    -H "Content-Type: application/json" \
    -o "$OUTDIR/audition-$name.mp3" \
    -d "$PAYLOAD" \
    "https://api.elevenlabs.io/v1/text-to-speech/$id"
done <<< "$VOICE_LIST"

echo
echo "✓ Auditions in $OUTDIR/. Listen and pick one — note the voice ID for generate-audio.sh."
