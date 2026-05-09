# Script

## Pacing target

~70–75 words for 30s at 2.4 words/sec. Adjust for chosen template.

## Voice direction

- Voice: TODO (audition first — `scripts/audition-voices.sh "<hook>"`)
- Tone: TODO (read aloud test, contractions, varied sentence length)
- Use V3 emotion tags at sentence starts: `[excited]`, `[serious]`, `[upbeat]`, `[warm]`, `[confident]`, `[uplifting]`
- TTS substitutions: see `references/voices.json` (API → A P I, "live" → "Built on", etc.)

## Hook grounding

Before writing, read `.build/assets/extracted/visible-text.txt` and `.build/assets/extracted/tokens.json`. The hero's H1, sub-headline, and pull-quotes ARE the thesis. Open with the site's actual argument, paraphrased. Generic SaaS-promo openers ("most companies approach X the same way", "tired of Y?", "what if Z?") are a fail signal — rewrite.

## Structure

Hook (site's thesis) → Stakes (what's at risk) → Brand answer → Proof/paths → CTA.

## Narration

[excited] TODO: opening hook line — paraphrased from the site's actual H1.
[serious] TODO: stakes — what happens if you ignore this?
[confident] TODO: brand's answer — what they do.
[upbeat] TODO: proof point — specific number, named customer, or unique mechanism.
[uplifting] TODO: closing CTA — what to do next, where to go.
