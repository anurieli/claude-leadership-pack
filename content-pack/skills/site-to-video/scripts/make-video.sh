#!/usr/bin/env bash
# Scaffold a new site-to-video project: capture site + copy starter template.
#
# Usage: make-video.sh <URL> [project-name] [template]
#   template: saas-30s (default) | launch-teaser-15s | portrait-reel
#
# After this runs, edit .build/SCRIPT.md and then run scripts/generate-audio.sh.
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <URL> [project-name] [template]" >&2
  exit 1
fi

URL="$1"
NAME="${2:-$(echo "$URL" | sed -E 's|https?://||; s|/.*||; s|\.|-|g')}"
TEMPLATE="${3:-saas-30s}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE_DIR="$SKILL_DIR/templates/$TEMPLATE"

# Default project parent: ~/Downloads/. Override with SITE_TO_VIDEO_DIR.
PARENT="${SITE_TO_VIDEO_DIR:-$HOME/Downloads}"
mkdir -p "$PARENT"
cd "$PARENT"

if [[ ! -d "$TEMPLATE_DIR" ]]; then
  echo "Unknown template: $TEMPLATE" >&2
  echo "Available: $(ls "$SKILL_DIR/templates/")" >&2
  exit 1
fi

if [[ -e "$NAME" ]]; then
  echo "Project '$NAME' already exists. Pick a different name or remove it." >&2
  exit 1
fi

mkdir -p "$NAME/.build/audio/sfx"
cp -r "$TEMPLATE_DIR/." "$NAME/.build/"
cd "$NAME"

HF=$(command -v hyperframes || echo "npx --yes hyperframes@latest")
echo "→ Capturing $URL ..."
$HF capture "$URL" --output .build/assets

echo
echo "✓ Project scaffolded at $(pwd)"
echo "  Template: $TEMPLATE"
echo "  Captured: .build/assets/"
echo
echo "Next steps:"
echo "  1. Read .build/assets/extracted/visible-text.txt to ground the hook"
echo "  2. Edit .build/SCRIPT.md (V3 emotion tags + TTS substitutions)"
echo "  3. scripts/audition-voices.sh \"<your hook sentence>\""
echo "  4. scripts/generate-audio.sh"
echo "  5. Build .build/index.html scenes from the storyboard"
echo "  6. hyperframes render --output final.mp4 --fps 30 --quality high"
