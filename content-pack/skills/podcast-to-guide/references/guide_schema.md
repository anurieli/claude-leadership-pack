# Guide Schema

The structured guide is a JSON object passed to `render_pdf.py`. Same structure also drives the markdown file. Be ruthless: skip empty sections rather than padding.

## Schema

```json
{
  "title": "Episode title (used on cover, large)",
  "subtitle": "One-line description, optional",
  "source_label": "AI DAILY BRIEF",
  "episode_date": "2026-05-01",
  "channel": "The AI Daily Brief",
  "duration_label": "24 min",
  "source_url": "https://open.spotify.com/episode/...",
  "youtube_url": "https://www.youtube.com/watch?v=...",
  "tldr": [
    "3-5 sentences. Each one a complete thought, not a fragment.",
    "Tells a busy reader what happened in this episode.",
    "Avoid filler like 'in this episode...' — get straight to the substance."
  ],
  "stories": [
    {
      "headline": "Title-cased story headline. Concrete, not vague.",
      "why_it_matters": "1-2 sentences. The shift, the implication, the bet. Aimed at a builder.",
      "details": [
        "Specific facts: numbers, names, dates, model versions.",
        "Quotes or paraphrases of NLW's analysis if it adds value.",
        "Skip details that just restate the headline."
      ]
    }
  ],
  "tools_mentioned": [
    {"name": "Tool/Company/Model", "note": "What it does or why it came up. One short clause."}
  ],
  "builder_takeaways": [
    "Action-oriented. 'Try X', 'Watch for Y', 'Stop doing Z'.",
    "Tied to something concrete the listener can do this week."
  ],
  "quotes": [
    {"text": "The actual line, no ellipsis abuse.", "speaker": "NLW"}
  ]
}
```

## Quality bar (do not ship below this)

- **TL;DR**: A reader should know whether to listen or skip after reading just this.
- **Stories**: Concrete. If you find yourself writing "discusses the importance of...", delete it.
- **Builder takeaways**: Verbs first. Each takeaway should pass the test "could I act on this tomorrow?"
- **Tools**: Capture every named product/model/company. This is the highest-utility extract for a builder skimming archives later.
- **Quotes**: Only include if the wording itself is the value. Paraphrasing is fine elsewhere.

## What to omit

- Generic intros/outros.
- Sponsor reads.
- Listener-callout boilerplate.
- "As I always say" preamble unless followed by a genuine framework.

## Style rules

- No em dashes. Use periods, commas, colons, semicolons.
- No marketing fluff in the markdown file (it's internal). The PDF is more polished but not promotional.
- Keep lines tight. Bullet points are not paragraphs.
