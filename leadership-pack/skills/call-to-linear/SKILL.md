---
name: call-to-linear
description: >
  Syncs meeting call notes from Fireflies into Linear project tasks and linked project documents. Use this skill whenever the user wants to:
  sync a call, meeting, or conversation to Linear; update Linear tasks based on a meeting; review what was
  discussed in a call and make sure Linear reflects it; consolidate call notes into project tasks; or check
  that a project's tasks are up to date after a client call. Trigger on phrases like "sync my call",
  "update Linear from the meeting", "make sure Linear has everything from my call with [name]",
  "consolidate the call into tasks", or any mention of comparing Fireflies/call content against Linear.
  Also trigger when the user asks to "turn call notes into tasks" or "make sure nothing from the call is missing
  in Linear." Also trigger when the user mentions Google Docs, SOWs, or project documents alongside a call sync.
  This skill requires both Fireflies and Linear MCP tools to be available.
---

# Call-to-Linear Sync

You are syncing the content of a Fireflies meeting transcript into a Linear project — updating existing tasks with new context, creating new tasks for items not yet tracked, handling project-level structural changes (like milestone reordering), and producing changelogs for linked documents you can't edit directly.

This is a high-leverage workflow. A single call often surfaces 5-15 action items, decisions, and context updates that would otherwise get lost. Your job is to be thorough so nothing falls through the cracks, while also being structured enough that the user can quickly review and approve your proposed changes.

## Step 1: Find the Call

The user will identify the call in one of several ways — a participant's name ("my last call with Jordan"), a meeting title ("the Analog milestone 3 call"), an email address, or just "my most recent call." Use whatever they give you to search Fireflies.

**Search strategy:**
- If given a name or email → use `fireflies_search` with the name/email as keyword. You can also use `fireflies_get_transcripts` with the `participants` filter for email-based lookups.
- If given a title → search with title keywords, scope to title
- If given "last" or "most recent" → search with relevant filters, sorted by date, limit 5
- If multiple results come back, show the user the top matches (title, date, participants) and ask which one

**Deduplication:** Fireflies sometimes creates duplicate entries for the same call (e.g., when the bot joins separately from the calendar event). If you see multiple results with the same meeting link, overlapping timestamps, or nearly identical titles on the same date — treat them as the same call. Pick the entry with the most complete summary/action items, or merge content from both if one has details the other doesn't.

Once you've identified the right call, fetch the full summary using `fireflies_get_summary`. The summary contains the short summary, keywords, and — critically — the **action items**, which are the backbone of this workflow. You generally don't need the full transcript unless the summary is thin or the user asks for deeper detail.

## Step 2: Find the Linear Project, Milestone & Linked Documents

Now figure out where in Linear these call notes belong. There are two paths:

**If the user specified a project/milestone:** Go straight there. Use `get_project` with `includeMilestones: true` and `includeResources: true` to get the project, its milestones, and any linked documents.

**If the user didn't specify:** Look at the call's title, participants, and content for clues. Search Linear projects using `list_projects` with a query based on keywords from the call. If there's a clear match (e.g., the call title mentions "Analog" and there's an "Agent Analog" project), go with it. If it's ambiguous — maybe the call touches multiple projects, or no project name is obvious — ask the user which project to sync to. Don't guess.

Once you have the project, identify the right milestone. Look at which milestones are active (not 100% complete) and match based on the call's content. If the project only has one active milestone, that's your target. If there are multiple, pick the one whose existing tasks most closely align with the call's topics, or ask.

### Step 2b: Pull Linked Documents

Many projects have linked Google Docs (SOWs, requirement docs, design specs) attached to the project description or resources. These documents represent the "documented truth" of the project, and calls often produce changes that should be reflected in them.

Check the project description and resources for Google Doc links. If you find any, fetch them using `google_drive_fetch` so you have the current documented state to compare against the call's decisions. This matters because some changes from a call are task-level (new issue, updated description) and others are document-level (the SOW says one thing, the call decided another).

If the user mentioned Google Docs or documents in their request, this step is especially important — they're expecting you to cross-reference.

## Step 3: Pull Existing Tasks

Fetch all issues in the project using `list_issues` with the project filter. You need a comprehensive view — don't limit results too aggressively. Pay attention to:

- **Task titles and descriptions** — you'll match these against call content
- **Which milestone each task belongs to** — focus on the target milestone
- **Task status** — don't modify completed/done tasks unless the call explicitly reopens something
- **Current assignees and due dates** — preserve these unless the call changes them

Build a mental map: what does Linear currently know about this project?

## Step 4: Compare & Plan Changes

This is the core of the skill. Go through the call's action items, decisions, and discussion points, and compare each one against the existing Linear tasks *and* the linked documents.

There are three levels of changes a call can produce:

### 4a: Project-Level Changes

These are structural changes that affect the project itself, not individual tasks. Examples: milestone reordering (priority swap), milestone renaming, scope changes that affect the overall project timeline, new milestones being added.

When you spot these, plan them separately — they need explicit user approval because they affect everything downstream. Use `save_milestone` for milestone reordering/renaming, and `save_project` for project-level updates.

### 4b: Task-Level Changes

For each topic from the call, determine:

1. **Does an existing task already cover this?** Look for semantic matches — the task title might not use the exact same words as the call, but "Implement F&B Integration" clearly maps to a discussion about "food ordering system." If yes → plan an **update** to that task with new context from the call.

2. **Is this a new item with no existing task?** If the call surfaced a deliverable, feature, or action item that has no home in Linear → plan a **new task**.

3. **Did the call change priorities, timelines, or scope?** If something was deprioritized, rescoped, or given a new deadline → plan an **update** to reflect that.

**When planning updates to existing tasks:**
- Add context from the call to the description — what was decided, what the approach is, specific details discussed
- Include action items with who's responsible (from the call's action items)
- Update due dates if the call established new timelines
- Don't overwrite existing description content — append or enrich it
- Preserve the task's current status unless the call explicitly changes it

**When planning new tasks:**
- Write a clear, descriptive title
- Write a detailed description including:
  - Context from the call explaining why this task exists
  - Specific deliverables discussed
  - Action items and who owns what
  - Any dependencies or blockers mentioned
  - Relevant decisions or constraints
- Set priority based on how it was discussed (urgent/blocking items = High, nice-to-haves = Medium/Low)
- Set a due date that makes sense within the milestone's timeline — stagger dates logically (foundational work first, integration/testing last)
- Assign to the user (or whoever the call designated)

### 4c: Document-Level Changes

If you fetched linked documents in Step 2b, compare the call's decisions against what those documents say. Flag any discrepancies — for example, the SOW might say "email for all follow-ups" but the call decided "SMS/WhatsApp preferred." These are changes that should be reflected in the documents, but since you typically can't edit Google Docs directly, you'll produce a changelog instead (see Step 7).

**Assigning tasks:** Default to assigning all tasks to the current user unless the call specifically assigned something to someone else who has a Linear account. Use `get_user` with "me" or the user's name to get the correct assignee ID.

**Setting deadlines:** Work backwards from the milestone's target date. Tasks with dependencies should be due before the things that depend on them. Infrastructure and foundational work comes first; testing and validation comes last. Leave a buffer before the milestone deadline for the final validation/test event.

## Step 5: Present the Plan

Before making any changes, present a clear summary to the user. Scale your approval request to the impact of the change:

**Project-level changes** (milestone swaps, scope changes): Present these first and get explicit confirmation. These are high-impact and irreversible in practice.

**Task updates and new tasks:** Present as a batch. For straightforward updates (adding call context to a description), a summary is sufficient. For anything that changes the task's scope, priority, or milestone assignment, call it out specifically.

Structure the plan like this:

**Project-level changes:**
- What's changing at the project/milestone level and why

**Updates to existing tasks:**
For each task being updated, show:
- The task identifier and current title (and new title if changing)
- What you're adding/changing and why
- New due date if applicable

**New tasks to create:**
For each new task, show:
- Proposed title
- Brief description of what it covers
- Proposed due date and milestone
- Priority level

**Document changes identified:**
If you found discrepancies between linked docs and the call, list them here so the user knows a changelog will be produced.

**Already tracked:**
Briefly note any call topics that are already fully covered in Linear (so the user knows you didn't miss them — you just determined they're already tracked).

Ask the user: "Does this look right? Want me to adjust anything before I apply these changes?"

## Step 6: Apply Changes

Once the user approves (or after incorporating their adjustments):

1. **Apply project-level changes** first — milestone reordering, renaming, etc. using `save_milestone` or `save_project`
2. **Update existing tasks** using `save_issue` — update descriptions, titles, due dates, assignees as planned
3. **Create new tasks** using `save_issue` — include all the detail from your plan
4. **Set milestone** on all new tasks to the target milestone
5. **Confirm completion** — give the user a summary of what was done with task identifiers

## Step 7: Produce Changelog for Linked Documents

If you identified document-level changes in Step 4c, produce a structured changelog as a markdown file. This serves as a bridge — the user can't expect you to edit their Google Docs directly, but they need a clear, paste-ready reference for what changed.

Organize the changelog by document section (matching the structure of the source document), and for each change include:
- Which section of the document it affects
- What the change is (add, update, remove)
- The specific text or content to add/modify
- Rationale from the call

Also include a summary table of all Linear issues created or updated during this sync, so the changelog doubles as a session record.

Save the changelog to the user's output folder.

## Important Principles

**Cross-reference everything.** The power of this workflow comes from triangulating three sources: the call transcript, the Linear project state, and the linked documents. A change might show up in the call's action items but already be tracked in Linear. Or it might be in Linear but contradicted by the call. Or the documents might say one thing while the call decided another. Check all three before deciding what to do.

**Tag the source.** When adding context to task descriptions or the changelog, note where the information came from — e.g., "Per 3/2 call with Dani:" or "From Matcha Dani call (2026-03-02):". This creates an audit trail so anyone reading the task later understands when and where a decision was made.

**Be thorough over being concise.** Task descriptions should include real detail from the call — specific decisions, approaches discussed, who said what. A task that just says "Build networking feature" is far less useful than one that explains the opt-in approach, the concierge AI concept, the phased rollout plan, and the specific action items for each person. The whole point of this skill is to capture institutional knowledge that would otherwise evaporate after the call.

**Respect what's already there.** When updating existing tasks, you're enriching them, not replacing them. If a task already has a good description, add a section with call context rather than overwriting.

**Think about task ordering.** When setting due dates for new tasks, think about dependencies. Data infrastructure should come before features that depend on that data. Testing should come after the things being tested are built.

**One task per deliverable.** Don't create a single mega-task for everything discussed in the call. Break things into discrete, actionable tasks that each represent a single deliverable or work stream. But also don't go too granular — each task should represent a meaningful chunk of work, not a single checkbox item.

**Use the call's action items as your primary source.** The Fireflies summary's action items section is gold — it's organized by person and includes timestamps. Cross-reference these against the short summary and keywords to make sure you haven't missed anything.
