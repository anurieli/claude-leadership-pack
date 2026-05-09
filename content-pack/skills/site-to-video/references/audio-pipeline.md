# Audio Pipeline (ElevenLabs V3 + Music + SFX)

**Audio drives the video, not the reverse.** Generate audio FIRST, get its actual duration with `ffprobe`, then size the composition to fit. If the VO is 38.8s, the composition is `38.8 + 1–1.5s tail = 40s`. Music and beats follow.

Voice catalog and TTS substitutions live in `voices.json` (sibling file). Read that for IDs, default settings, V3 emotion-tag semantics, and pronunciation gotchas.

## Voice generation (curl)

```bash
curl -s -X POST \
  -H "xi-api-key: $ELEVENLABS_KEY" \
  -H "Content-Type: application/json" \
  -o narration.mp3 \
  -d '{
    "text": "[excited] Every post you publish kicks off a flood of comments. [serious] Most reply tools fire back the same line every time. ...",
    "model_id": "eleven_v3",
    "voice_settings": {
      "stability": 0.4,
      "similarity_boost": 0.75,
      "style": 0.5,
      "use_speaker_boost": true
    }
  }' \
  https://api.elevenlabs.io/v1/text-to-speech/<VOICE_ID>
```

**Always audition 2–3 voices on the first sentence before committing.** Use `scripts/audition-voices.sh "<hook sentence>"` to generate samples from Brian, Bill, Liam, Mark in parallel.

## Convert to WAV and measure

HyperFrames composition needs the actual duration. Always do this before sizing the timeline.

```bash
ffmpeg -y -i narration.mp3 -ar 48000 -ac 2 narration.wav
ffprobe -v error -show_entries format=duration -of csv=p=0 narration.wav
# → 38.832
# composition data-duration = 40 (38.832 + ~1.2s tail)
```

## Music — ElevenLabs Music API

```bash
curl -s -X POST \
  -H "xi-api-key: $ELEVENLABS_KEY" \
  -H "Content-Type: application/json" \
  -o music.mp3 \
  -d '{
    "prompt": "Upbeat modern app trailer instrumental. 105 BPM. Driving pulsing synth bass, crisp clap percussion, bright melodic plucky synth lead, optimistic and energetic. Apple product reveal meets Stripe announcement vibe. Builds steadily. NO vocals.",
    "music_length_ms": 40000
  }' \
  https://api.elevenlabs.io/v1/music
```

**Prompt anatomy:** `[genre] [tempo] [instrumentation] [mood] [reference] [arc] [NO vocals]`.

Match music duration to narration + 1–2s tail. Music longer than composition is wasteful but harmless; shorter is a hard fail.

**Always duck music to `data-volume="0.10"` to `0.15`.** Full-volume music competes with VO and ruins comprehension.

## Sound Effects — ElevenLabs SFX API

Min duration **0.5s** (anything less returns 400). Generate 6–10 hits per video.

| Moment | SFX prompt |
|---|---|
| Scene entrance | "soft paper rustle, single quick brush of paper, clean and quiet" |
| Terminal typing | "soft mechanical typewriter clicks, sequence of 5 keystrokes, gentle wooden tone" |
| Arrow draw | "subtle short upward swoosh whoosh, soft air movement, very brief" |
| Auto-send confirm | "three soft confirmation ticks in quick succession, like checkmarks landing" |
| UI tap | "single confident finger tap on glass touchscreen, clean" |
| Stat slam | "soft warm low impact thud, like a felt hammer on wood, no boom" |
| Outro logo lock | "single warm soft analog chime, like a meditation bell tail, gentle bright resolve" |

```bash
curl -s -X POST \
  -H "xi-api-key: $ELEVENLABS_KEY" \
  -H "Content-Type: application/json" \
  -o sfx/tap.mp3 \
  -d '{"text":"single confident finger tap on glass touchscreen, soft and clean, brief","duration_seconds":0.5,"prompt_influence":0.6}' \
  https://api.elevenlabs.io/v1/sound-generation
```

**Reuse the same SFX file at multiple timeline moments** by creating multiple `<audio>` elements with **different `data-track-index` values**. The engine forbids overlapping audio on the same track.

## Word-level transcription

```bash
hyperframes transcribe narration.wav --model small.en --language en
# → transcript.json: [{ text, start, end }, ...]
```

## Compute beat boundaries from sentence ends

```python
import json
t = json.load(open('transcript.json'))
sentences = []
i = 0; n = len(t)
while i < n:
    start = t[i]['start']; j = i
    while j < n and not t[j]['text'].endswith(('.', '!', '?')): j += 1
    if j < n:
        sentences.append({'start': start, 'end': t[j]['end'],
                          'text': ' '.join(t[k]['text'] for k in range(i, j+1))})
        i = j + 1
    else: break
```

Group sentences into 5–7 beats. **Beat boundaries land on word onsets** (the `.start` of the first word of the next sentence). This is what makes hard cuts feel intentional.

## SRT generation (for the deliverable)

After rendering, generate `final.srt` from `transcript.json`:

```python
import json
def fmt(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int((s%1)*1000):03d}"
words = json.load(open('.build/transcript.json'))
# group ~7 words per cue
with open('final.srt', 'w') as f:
    for i in range(0, len(words), 7):
        chunk = words[i:i+7]
        f.write(f"{i//7+1}\n{fmt(chunk[0]['start'])} --> {fmt(chunk[-1]['end'])}\n"
                f"{' '.join(w['text'] for w in chunk)}\n\n")
```
