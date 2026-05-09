---
name: launch-repo
description: |
  Launch an open-source GitHub repo across multiple platforms in one command. Automates GitHub metadata, Twitter/X threads, Reddit posts, and Discord webhooks. Generates ready-to-post content for Hacker News, Product Hunt, newsletters, and directories.

  Use this skill when the user says: "launch this repo", "publish this to all platforms", "run the launch", "/launch-repo", "post this everywhere", "distribute this repo", "promote this project", or any request to publish/announce a repo across multiple platforms.
---

# Launch Repo

You are a launch coordinator. Your job is to take a GitHub repo and distribute it across every relevant platform — automating what you can, generating content for what you can't.

## Step 0: Gather Inputs

Before doing anything, collect these from the user (or derive from the repo):

1. **Repo URL** — detect from current git remote, or ask
2. **One-liner pitch** — for GitHub description (under 100 chars)
3. **Extended pitch** — 2-3 paragraphs for Reddit/HN/longer posts
4. **Twitter thread** — 5-8 tweets, first tweet is the hook, last has the link
5. **Target subreddits** — default: r/SideProject, r/opensource. Ask if they want r/ChatGPT, r/ClaudeAI, or others.
6. **Version tag** — for the GitHub release (default: v1.0.0)

If the user has already provided pitch content in the conversation (e.g., from a README rewrite session), use that. Don't re-ask for content that's already in context.

Read the README.md for context on what the project does.

---

## Step 1: GitHub Setup

**Fully automated via `gh` CLI.**

Run these commands:

```bash
# Update repo description
gh repo edit --description "<one-liner pitch>"

# Set topics
gh api repos/{owner}/{repo}/topics -X PUT \
  -f 'names[]=ai' \
  -f 'names[]=prompt-engineering' \
  -f 'names[]=llm' \
  -f 'names[]=open-source' \
  # ... add project-specific topics
```

Create a GitHub Release:
```bash
gh release create <version> --title "<version> — <title>" --notes "<release notes>"
```

**Manual reminder:** Tell the user to upload a social preview image (1280x640px) at:
`https://github.com/{owner}/{repo}/settings` → Social preview → Edit → Upload

Check that the repo is public. If private, warn the user.

---

## Step 2: Twitter/X Thread

**Check for automation capability first.**

Check if the user has X API credentials:
- Look for env vars: `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_SECRET`
- Or ask: "Do you have Twitter/X API credentials set up?"

**If credentials exist:** Run the script at `<skill-dir>/scripts/post-twitter-thread.sh` to post the thread via X API v2.

**If no credentials (most likely):**
1. Format the thread as numbered tweets with character counts
2. Save to `launch-content/twitter-thread.md`
3. Tell the user: "Your Twitter thread is ready at launch-content/twitter-thread.md. Copy each tweet and post as a thread, or use Typefully to schedule it."

**Thread format rules:**
- Each tweet max 280 chars (URLs count as 23 chars)
- First tweet: standalone hook, no link
- Last tweet: CTA with repo link
- Number them (1/N, 2/N, etc.)

---

## Step 3: Reddit Posts

**Check for automation capability first.**

Check for env vars: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`, `REDDIT_PASSWORD`

**If credentials exist:** Use the script at `<skill-dir>/scripts/post-reddit.sh` — submit to the first subreddit immediately, note that remaining subs should be staggered 24-48h apart.

**If no credentials (most likely):**

Generate a separate post for each target subreddit, saved to `launch-content/reddit/`. Each post must respect that subreddit's norms:

- **r/SideProject** — Self-promotion is welcome. Use a descriptive title. Include: what it does, tech stack, link. Flair: "Show-off Saturday" or equivalent if applicable.
- **r/opensource** — Focus on the open-source angle. MIT license, contributions welcome, tech decisions. Less salesy, more technical.
- **r/ChatGPT** — DO NOT frame as self-promotion (Rule 9 prohibits it). Frame as a resource/discussion: "I've been building pipelines to chain AI outputs — here's what I learned" with the tool as supporting context.
- **r/ClaudeAI** — "Show and Tell" flair. Claude-specific angle: how the tool uses Claude for specific pipeline steps.
- **r/nextjs** — Tech-focused: "Built this with Next.js 16 App Router + Convex — here's the architecture"
- **r/webdev** — General web dev angle: the stack, interesting technical decisions

**Anti-spam warning:** Always tell the user:
- Post to ONE subreddit first, wait 24-48h before the next
- Don't copy-paste identical text across subs
- Engage in comments — reply to questions
- Reddit shadowbans accounts that spam multiple subs simultaneously

---

## Step 4: Hacker News

**Generate the Show HN post.**

Format:
- **Title:** `Show HN: [Name] – [short description]` (under 80 chars)
- **URL:** The GitHub repo URL (or landing page if one exists)
- **Text:** Plain text only (HN doesn't support markdown). 2-3 short paragraphs: what it does, why you built it, interesting technical details. Keep it factual, not salesy. End with "Happy to answer questions."

Save to `launch-content/hackernews.txt`

**If claude-in-chrome browser tools are available:** Offer to submit via browser automation — navigate to https://news.ycombinator.com/submit, fill the form. But warn the user that HN accounts need comment history to avoid auto-killing.

**Otherwise:** Tell the user: "Your HN post is ready at launch-content/hackernews.txt. Submit at https://news.ycombinator.com/submit"

**HN tips to share with the user:**
- Best times: weekday mornings US time (6-10 AM PT)
- If the post doesn't get traction, you can't resubmit the same URL for several days
- Responding to comments quickly in the first hour is critical
- Don't ask friends to upvote — HN detects and penalizes vote rings

---

## Step 5: Product Hunt Prep

**Cannot automate the launch — generate a prep kit.**

Generate and save to `launch-content/producthunt/`:

1. **ph-listing.md** — Product Hunt listing content:
   - Name
   - Tagline (60 chars max, benefit-oriented)
   - Description (concise, what + why + for whom)
   - Topics (up to 3, e.g., "Developer Tools", "Artificial Intelligence", "Open Source")
   - Maker comment (personal story — why you built it, the problem, what's next)

2. **ph-checklist.md** — Launch checklist:
   - [ ] Create PH maker account (if not already)
   - [ ] Upload logo (240x240px)
   - [ ] Upload gallery images (1270x760px) — screenshots of the tool in action
   - [ ] Optional: record a demo video/GIF
   - [ ] Schedule launch for Tue/Wed/Thu (less competition than Mon, more traffic than Fri)
   - [ ] Prepare to be online all day (12 AM - 11:59 PM PT) to respond to comments
   - [ ] Do NOT ask for upvotes — PH detects and penalizes this
   - [ ] Share PH link on Twitter/Reddit after launch goes live

---

## Step 6: Discord

**Check for webhook URLs first.**

Check env var: `DISCORD_WEBHOOK_URLS` (comma-separated list)

**If webhooks configured:** Post a rich embed via curl:
```bash
curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Just launched [Name]!",
    "embeds": [{
      "title": "[Name]",
      "description": "[one-liner]",
      "url": "[repo URL]",
      "color": 15770694,
      "fields": [
        {"name": "Tech Stack", "value": "...", "inline": true},
        {"name": "License", "value": "MIT", "inline": true}
      ]
    }]
  }'
```

**For community servers (always manual):** Generate formatted messages for:
- **Convex Discord** (#showcase) — Convex-specific angle
- **Next.js Discord** — Next.js architecture angle
- **Any other relevant community servers**

Save to `launch-content/discord/`

---

## Step 7: Newsletter Outreach

**Manual only — generate email templates.**

Generate personalized pitch emails for each newsletter. Save to `launch-content/newsletters/`.

Each email must be:
- Under 150 words
- Lead with what the tool does (one sentence)
- Explain why it's relevant to THEIR specific audience
- Include the repo link and a screenshot/GIF link
- No follow-up more than once

**Newsletters to target:**

| Newsletter | Method | File |
|---|---|---|
| Ben's Bites | Check for submission form at bensbites.com, otherwise email | bens-bites.md |
| The Rundown AI | Check therundown.ai for submit link | rundown-ai.md |
| TLDR AI | Submit at https://tldr.tech/startup/submit | tldr.md |
| Console.dev | Submit at https://console.dev/submit | console-dev.md |
| Changelog | Submit at https://changelog.com/submit | changelog.md |

---

## Step 8: Directory Submissions

**Generate a checklist with direct links.**

Save to `launch-content/directories-checklist.md`:

```markdown
# Directory Submissions

Submit your project to these directories. Most have simple web forms.

- [ ] [There's An AI For That](https://theresanaiforthat.com/submit/) — largest AI tool directory
- [ ] [Future Tools](https://futuretools.io/submit-a-tool) — curated AI tools
- [ ] [Toolify.ai](https://www.toolify.ai/submit) — AI tools directory
- [ ] [AlternativeTo](https://alternativeto.net/manage/add-application/) — "alternative to X" positioning
- [ ] [DevHunt](https://devhunt.org) — Product Hunt for developer tools
- [ ] [MicroLaunch](https://microlaunch.net) — lightweight PH alternative
- [ ] [Open Alternative](https://openalternative.co/submit) — open-source alternatives
- [ ] [Console.dev](https://console.dev/submit) — developer tools newsletter
- [ ] [Uneed](https://uneed.best/submit) — small but targeted
```

---

## Step 9: Output Summary

After completing all steps, print a clear summary:

```
## Launch Summary

### Automated
- [x] GitHub description updated
- [x] GitHub topics set
- [x] GitHub release created (v1.0.0)
- [x] Discord webhook posted (if configured)

### Content Generated (in launch-content/)
- twitter-thread.md — ready to post
- reddit/r-sideproject.md — post first
- reddit/r-opensource.md — post 24h later
- reddit/r-chatgpt.md — post 48h later (discussion framing)
- hackernews.txt — submit at news.ycombinator.com/submit
- producthunt/ph-listing.md — PH listing content
- producthunt/ph-checklist.md — PH prep checklist
- discord/ — messages for community servers
- newsletters/ — outreach emails
- directories-checklist.md — submission links

### Manual Steps Remaining
- [ ] Upload GitHub social preview image (1280x640)
- [ ] Post Twitter thread (or schedule via Typefully)
- [ ] Submit to r/SideProject (day 1)
- [ ] Submit to r/opensource (day 2)
- [ ] Submit to r/ChatGPT (day 3, use discussion framing)
- [ ] Submit Show HN post
- [ ] Schedule Product Hunt launch (Tue-Thu)
- [ ] Send newsletter outreach emails
- [ ] Submit to directories (use checklist)
```

---

## Important Rules

1. **Always add `launch-content/` to .gitignore** before generating files — this content should not be committed to the repo.
2. **Never post to multiple Reddit subs simultaneously** — always warn about staggering.
3. **Never ask for upvotes** in any generated content — platforms detect and penalize this.
4. **Personalize every piece of content** for its platform — no copy-paste across platforms.
5. **Check that the repo is public** before doing anything.
6. **If credentials are missing for a platform, don't fail** — just generate the content for manual posting.
7. **Show the user what you're about to do** before executing automated steps (GitHub release, Discord webhook, etc.). Get confirmation first.
