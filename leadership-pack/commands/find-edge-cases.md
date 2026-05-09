You are a production reliability engineer. Your job is to find edge cases that could break the feature, build, or tweak we just worked on in this conversation before it hits real users.

## Step 1: Identify the Recent Change

Look at the CURRENT CONVERSATION CONTEXT to understand what feature, fix, or tweak was just built or modified. You already have the full context of what we just did -- use it. Do NOT rely on git commits; the work may not even be committed yet.

If the conversation context is unclear or too broad, read the most recently modified files to fill in the gaps:
- Use `git diff` (staged + unstaged) and `git diff HEAD` to see uncommitted work.
- Only fall back to `git log` if there is truly no conversation context.

Summarize in 1-2 sentences what the change is before proceeding.

## Step 2: Map the Data Flow & Trust Boundaries

For the identified change, trace the complete data flow:
- **Inputs**: What user-provided data enters the system? (forms, file uploads, API params, webhook payloads, URL params, SMS messages)
- **Processing**: What transformations, lookups, or external calls happen?
- **Storage**: What gets written to the database? What are the uniqueness constraints?
- **Outputs**: What goes back to the user or to external services?
- **Trust boundaries**: Where does data cross from untrusted (user/external) to trusted (internal)?

## Step 3: Systematically Find Edge Cases

Go through EVERY category below and list specific, concrete edge cases for the recent change. Do NOT skip categories -- if a category doesn't apply, say so explicitly.

### A. Human Input Errors
- Empty/blank/whitespace-only fields that are assumed to have values
- Duplicate values where uniqueness is assumed (e.g., duplicate phone numbers, duplicate emails, duplicate names)
- Missing required fields that aren't validated (e.g., no phone number, no email)
- Malformed data (e.g., phone numbers with letters, emails without @, URLs without protocol)
- Unexpected formats (e.g., international phone numbers, names with special characters/emoji, RTL text)
- Extremely long inputs (e.g., 10,000 character names, massive file uploads)
- Extremely short inputs (e.g., single character, single pixel image)
- Copy-paste artifacts (e.g., invisible unicode characters, smart quotes, extra whitespace, BOM)
- Encoding issues (e.g., UTF-8 vs Latin-1, emoji in text fields)
- Boundary values (e.g., 0, -1, MAX_INT, empty arrays, null vs undefined)

### B. File Upload & Processing Errors
- Wrong file type (e.g., PDF disguised as image, corrupted file, zero-byte file)
- Extremely large files that exceed memory or timeout limits
- Files with malicious content (e.g., zip bombs, SVG with scripts, EXIF injection)
- Unsupported formats (e.g., HEIC, WebP, TIFF where only JPEG/PNG expected)
- Concurrent uploads that race against each other
- Upload interrupted midway -- is partial state cleaned up?
- Filenames with special characters (spaces, unicode, path traversal attempts)

### C. Concurrency & Race Conditions
- Two users modifying the same record simultaneously
- Double-click / double-submit on buttons
- Browser back button after a submission
- Multiple tabs open with the same form
- Webhook arriving before the triggering action completes
- Batch operations where one item fails -- does it roll back or leave partial state?

### D. External Service Failures
- AWS Rekognition: timeout, rate limit, service outage, unexpected response format
- Twilio: delivery failure, invalid phone number, rate limit, webhook replay
- Google Sheets: API quota exceeded, sheet deleted/renamed, column reordered, permission revoked
- Google Drive: file moved/deleted, sharing permissions changed, large folder
- OpenRouter/LLM: timeout, malformed response, token limit exceeded, model unavailable
- S3/CloudFront: upload failure, permission denied, bucket policy change
- Redis/rate limiter: connection failure, stale data
- Convex: function timeout (especially actions), storage limits

### E. Infrastructure & Environment Failures
- Network timeout mid-operation (what state is left behind?)
- Database write succeeds but subsequent action fails -- is there inconsistency?
- Serverless cold start causing timeouts on first request
- Memory limits exceeded during image processing or large batch operations
- Cron job runs twice (idempotency)
- Deployment during active processing -- do in-flight jobs recover?

### F. Authorization & Security Edge Cases
- User accesses resource after their session expires mid-operation
- User with "viewer" role attempts mutation through direct API call
- Cross-event data leakage (attendee from event A sees photos from event B)
- Webhook endpoint called without valid signature/auth
- Escalated conversation accessed by non-admin
- Gallery link shared with someone who shouldn't have access
- PII in error messages or logs

### G. State & Lifecycle Edge Cases
- Operating on a deleted event/attendee/photo (stale UI reference)
- Event status transitions that skip states (e.g., upcoming -> completed, skipping live)
- Re-processing something that was already processed (idempotency)
- Undoing an action after dependent actions have occurred
- Data migration on records created before a schema change

### H. Scale & Performance Edge Cases
- Event with 10,000+ attendees -- does the sheet sync hold up?
- Hundreds of photos uploaded simultaneously
- Thousands of SMS messages in a burst
- Gallery with 500+ photos -- does it load?
- Search/filter on large datasets
- Knowledge base with very large documents

### I. Integration & Sync Edge Cases
- Google Sheet column headers changed or reordered after initial sync
- Sheet has merged cells, hidden rows, or formulas instead of values
- Twilio phone number reassigned or deactivated
- Gallery domain DNS not propagated yet
- Timezone changes after attendees already synced (daylight saving edge)

## Step 4: Output a Prioritized Report

Present findings as a structured report:

### Critical (Will break in production)
List edge cases that WILL cause errors, data loss, or security issues with normal usage patterns.

### High (Likely to encounter)
List edge cases that real users are likely to hit and that will cause degraded experience.

### Medium (Could happen)
List edge cases that are plausible but less common, would cause confusion or minor issues.

### Low (Defensive hardening)
List edge cases that are unlikely but worth hardening against for robustness.

For EACH edge case, include:
1. **What**: A specific, concrete scenario (not vague)
2. **Where**: The exact file(s) and function(s) affected
3. **Impact**: What breaks -- error message, data corruption, silent failure, security hole?
4. **Fix suggestion**: A one-liner on how to address it

## Step 5: Quick Wins

List the top 5 fixes I should make RIGHT NOW before shipping, sorted by effort (easiest first). For each, describe the exact change needed.

## Step 6: Append to Edge-Cases-TODO.md

After presenting the report, append ALL discovered edge cases to `Edge-Cases-TODO.md` in the project root. This file is a running log across sessions -- never overwrite existing content, only append.

If the file doesn't exist yet, create it with the header below. If it already exists, read it first, then append a new section.

Use this exact format:

```
# Edge Cases TODO

## [Date] - [Short description of the feature/change]

### Critical
- [ ] [Related feature/process] - [Brief but descriptive edge case]
- [ ] [Related feature/process] - [Brief but descriptive edge case]

### High
- [ ] [Related feature/process] - [Brief but descriptive edge case]

### Medium
- [ ] [Related feature/process] - [Brief but descriptive edge case]

### Low
- [ ] [Related feature/process] - [Brief but descriptive edge case]
```

Rules for the TODO file:
- Each item is a checkbox (`- [ ]`) so I can check them off as I fix them.
- Each item starts with the related feature/process in brackets, then a dash, then the edge case description. Keep it brief but specific enough to act on without re-reading the full report.
- Group by severity (Critical > High > Medium > Low).
- Use today's date and a short label for the section header.
- Do NOT duplicate edge cases that already exist in the file from previous runs.
