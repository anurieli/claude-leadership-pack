# Linear Push Guide

When the user wants to push the generated project plan into Linear, follow this sequence using the Linear MCP tools.

## Pre-flight

1. **Confirm the team** — ask the user which Linear team this project belongs to. Use `list_teams` if they're unsure.
2. **Check for existing labels** — use `list_issue_labels` to see what labels already exist. Only create labels that don't exist yet using `create_issue_label`.

## Push Sequence

### 1. Create the Project

Use `save_project` with:
- `name`: The project name from the generated plan
- `team`: The confirmed team name or ID
- `description`: The full project description from Step 1 of the plan
- `state`: "planned" (or "started" if kickoff is today)

Save the returned project ID — you'll need it for milestones.

### 2. Create Milestones

Every milestone must have a hard target date. If the kickoff date isn't known, ask the user before creating milestones — don't create them without dates.

For each milestone (in order), use `save_milestone` with:
- `project`: The project ID from step 1
- `name`: Milestone name
- `description`: Exit criteria only (no dates in the description — the date lives in `targetDate`)
- `targetDate`: **Required.** ISO format date calculated from kickoff + week range in the proposal (e.g., `2026-04-01`). For Integration QA: 1 week after the final dev milestone. For Deployment & Handoff: 1–2 weeks after QA.

### 3. Create Tasks (Parent Issues) — Split by Discipline

Tasks are split by engineering discipline (Backend, Frontend, AI) within each milestone. Create all tasks for a milestone before moving to the next.

For each task, use `create_issue` with:
- `team`: The confirmed team
- `title`: The task name (format: "[Feature Area] — [Discipline]")
- `description`: The full task description (What this is, Why it matters, Depends on, Key Deliverable, Relevant Docs)
- `project`: The project ID
- `milestone`: The milestone name or ID
- `labels`: Always include the discipline label (`backend`, `frontend`, or `ai`) plus any other relevant labels
- `state`: "backlog" for future milestones, "triage" for M0
- `blockedBy` / `blocks`: If a task depends on another task from a different discipline (e.g., Frontend blocked by Backend), set the relationship here using issue IDs. Create the upstream task first.

Save each returned issue ID — you'll need them as parent IDs for subtasks and for cross-discipline dependency wiring.

### 4. Create Subtasks (Child Issues) with Dependencies

Dependencies are first-class citizens in Linear — they show up as blocking relationships in the UI, not as text in descriptions. This means you must create subtasks in **dependency order**: upstream subtasks first so you have their IDs, then downstream subtasks that reference them.

For each subtask, use `create_issue` with:
- `team`: The confirmed team
- `title`: The subtask name (action-verb format)
- `description`: The full subtask description (What to Build, Acceptance Criteria, Relevant Docs, Testing Notes)
- `parentId`: The parent task's issue ID
- `labels`: Apply relevant labels
- `state`: "backlog"
- `blockedBy`: Array of issue IDs that must be completed before this subtask can start. Set this on creation — don't add it as an afterthought.
- `blocks`: Array of issue IDs that this subtask is blocking (use when you create the upstream subtask first and already know what it will block)

**Creation order matters.** Walk through each Task's subtasks and sort them so that subtasks with no dependencies are created first. Then create the dependent subtasks, referencing the IDs of the ones you just created. This way every `blockedBy` reference points to a real issue ID.

### 5. Add PM Notification Comments

For **every** milestone (not just selected ones), use `create_comment` on the milestone's first task with the notification template:

```
🔔 PM ACTION REQUIRED
Status: [Ready for QA / Milestone Complete / Blocked]
What's done: [1–2 sentences]
What you need to do: [Specific action for the PM]
Blocking anything: [Yes/No — and if yes, what]
```

Add this as a comment template that developers can copy when they're ready.

## Rate Limiting

Linear MCP calls should be paced. If creating many issues:
- Create parent tasks first (all of them), collect IDs
- Then create subtasks in dependency order within each task, setting `blockedBy`/`blocks` at creation time
- Labels go on at creation time too — don't defer them

## Error Handling

If a label doesn't exist and `create_issue_label` fails, skip the label and note it for the user. Don't let a missing label block the entire push.

If the team doesn't have a matching workflow state (e.g., no "backlog" state), use `list_issue_statuses` to find the closest match.
