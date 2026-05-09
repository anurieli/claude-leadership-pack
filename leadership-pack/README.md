# Claude Leadership Pack

Shared Claude Code skills and commands for project management, internal comms, skill creation, and autonomous development workflows.

---

## Setup

Open Claude Code and paste this:

```
Set up the claude-leadership-pack plugin. Do the following:

1. Read ~/.claude/settings.json (create it if it doesn't exist)
2. Add this entry to the "extraKnownMarketplaces" object (create the object if it doesn't exist):

   "claude-leadership-pack": {
     "source": {
       "source": "github",
       "repo": "anurieli/claude-leadership-pack"
     }
   }

3. Write the updated settings.json
4. Run: /plugin install leadership-pack@claude-leadership-pack
```

That's it. Claude does everything.

### Updating

When new skills are pushed to this repo, tell Claude:

```
Reload plugins to pull the latest skills. Run: /reload-plugins
```

---

## Skill Directory

### create-workflow

**What it does:** A workflow composer that takes a goal, discovers which existing skills can serve it, builds any missing skills, and packages everything into the right container — usually an agent definition (`.claude/agents/`) that bundles skills together via the `skills` frontmatter field. Think of it as a staffing agency: you describe the role, it recruits existing capabilities and trains new ones for the gaps, then hands back a ready-to-work agent.

**When to use it:** When you want to automate a multi-step process, create a new agent, or compose multiple skills into a single workflow. Say things like "I want to automate what happens after client calls", "create a workflow for onboarding new clients", "build me an agent that handles deploy tracking", or "I keep doing X manually."

**How it works:**
1. Asks about your goal — the end result, not the implementation
2. Breaks it into a workflow sketch (ordered capability steps)
3. Scans local skills, local agents, and the npx ecosystem for matches
4. Presents a discovery report mapping each step to existing or missing capabilities
5. For gaps: classifies them (template, integration, logic, script) and builds lightweight skills
6. Packages the result — either tells you "you already have this", creates a new skill, or generates an agent definition with `skills: [...]` that wires everything together

**Requirements:** None — works with whatever skills and MCP servers you already have configured. The more skills installed, the more it can compose.

---

### call-to-linear

**What it does:** Syncs meeting call notes from Fireflies into a Linear project. It fetches the call transcript/summary, cross-references it against existing Linear tasks and linked project documents, then creates new tasks, updates existing ones, and produces changelogs for documents that need updating.

**When to use it:** After a client call, standup, or any meeting where action items, decisions, or scope changes came up that need to be reflected in Linear. Say things like "sync my call with Jordan to Linear", "update Linear from the meeting", or "make sure nothing from the call is missing."

**How it works:**
1. Searches Fireflies for the call (by participant name, title, or "most recent")
2. Fetches the full summary and action items
3. Finds the matching Linear project and milestone
4. Pulls linked Google Docs (SOWs, specs) for cross-referencing
5. Compares call content against existing tasks and documents
6. Presents a change plan (project-level, task-level, document-level changes)
7. After approval, applies all changes to Linear
8. Produces a changelog for any linked documents that need manual updates

**Requirements:**
| Requirement | How to set up |
|---|---|
| Fireflies MCP | Add the Fireflies MCP server to your Claude Code config. Requires a Fireflies API key. |
| Linear MCP | Add the Linear MCP server to your Claude Code config. Requires a Linear API key. |
| Google Drive MCP *(optional)* | Only needed if your Linear projects have linked Google Docs. Add the Google Drive MCP server. |

---

### internal-comms

**What it does:** Helps write internal communications using your company's preferred formats. Covers 3P updates (Progress/Plans/Problems), company newsletters, FAQ responses, status reports, leadership updates, project updates, and incident reports.

**When to use it:** When asked to write any kind of internal communication. Say things like "write a 3P update", "draft a company newsletter", or "write a status report."

**How it works:**
1. Identifies the communication type from your request
2. Loads the matching guideline/template from the `examples/` directory
3. Follows the format, tone, and content-gathering instructions specific to that type

**Requirements:** None — this is a self-contained skill with bundled templates.

---

### linear-project-generator

**What it does:** Takes project documents (proposals, PRDs, SOWs, behavior guides) and generates a complete Linear project hierarchy — project description, milestones with hard dates, discipline-split tasks (Backend/Frontend/AI), and atomic subtasks with acceptance criteria.

**When to use it:** At project kickoff when you have a proposal, PRD, or SOW and need to turn it into a structured, trackable Linear project. Say things like "turn this proposal into a Linear project", "set up the project in Linear", or "break this SOW down into tasks."

**How it works:**
1. Reads and cross-references all provided project documents
2. Generates a project description with tech stack, contacts, and key docs
3. Creates milestones with target dates and exit criteria
4. Splits work into discipline-specific tasks (Backend, Frontend, AI)
5. Generates atomic subtasks with acceptance criteria, testing notes, and doc references
6. Sets up dependency graphs using Linear's `blockedBy`/`blocks` relationships
7. Applies labels and PM notification triggers
8. Optionally pushes everything directly to Linear

**Requirements:**
| Requirement | How to set up |
|---|---|
| Linear MCP | Add the Linear MCP server to your Claude Code config. Requires a Linear API key. |

**Note:** This skill is configured for Cut The Edge inc.'s workflow (milestones include Integration QA and Deployment & Handoff, tasks split by engineering discipline). Modify `SKILL.md` if your project structure differs.

---

### schedule

**What it does:** Creates scheduled or recurring tasks from the current session. Distills what you just did into a repeatable prompt that can run autonomously on a cron schedule.

**When to use it:** When you want to automate something you just did — "schedule this to run every morning", "make this a weekly task", or "turn this into a recurring job."

**How it works:**
1. Analyzes the current session to identify the core task
2. Drafts a self-contained prompt (no references to the current conversation)
3. Chooses a descriptive task name in kebab-case
4. Determines scheduling (one-off vs. recurring with cron expression)
5. Creates the scheduled task using Claude Code's built-in scheduling

**Requirements:** None — uses Claude Code's built-in `create_scheduled_task` tool. Cron expressions use local machine timezone.

---

### skill-creator

**What it does:** A meta-skill for creating, testing, and iterating on new skills. Handles the full lifecycle: capturing intent, writing the SKILL.md, generating test cases, running evaluations (with and without the skill), presenting results in a browser-based viewer, and iterating based on feedback. Also includes description optimization for better skill triggering.

**When to use it:** When you want to create a new skill from scratch, improve an existing one, run evaluations, or optimize a skill's trigger description. Say "create a skill for X", "improve this skill", "run evals on this skill", or "optimize the description."

**How it works:**
1. Captures intent through interview (what, when, output format)
2. Writes a SKILL.md draft following best practices
3. Generates test prompts and runs them (with-skill vs. baseline)
4. Launches a browser-based evaluation viewer for human review
5. Runs quantitative benchmarks (pass rate, timing, tokens)
6. Iterates based on feedback until satisfied
7. Optionally optimizes the description for better triggering accuracy

**Requirements:**
| Requirement | How to set up |
|---|---|
| Python 3 | Must be installed. Used for eval viewer, benchmarking, and packaging scripts. |
| `claude` CLI | Must be installed and authenticated. Used for description optimization (`run_loop.py`). |

---

## Command Directory

### /design-system-creation-prompt

**What it does:** Generates a comprehensive design system and style guide for a project — color palette, typography hierarchy, component patterns, animation standards, and responsive rules, all wired through CSS variables and Tailwind utilities.

**When to use it:** When starting a new frontend project or standardizing an existing one's visual identity.

**Requirements:** None — outputs a design system specification. Assumes Tailwind CSS v4+.

---

### /find-edge-cases

**What it does:** Acts as a production reliability engineer. Systematically finds edge cases across 9 categories (human input errors, file uploads, concurrency, external services, infrastructure, auth, state lifecycle, scale, integrations) and outputs a prioritized report with fix suggestions. Appends findings to `Edge-Cases-TODO.md`.

**When to use it:** After building or modifying a feature, before shipping to production.

**Requirements:** None — works on whatever codebase is in the current directory.

---

### /fix

**What it does:** Runs `npm run dev`, finds errors, fixes them in a loop until the dev server runs clean, then commits and pushes.

**When to use it:** Quick "just make it work" command for Node.js projects.

**Requirements:** Node.js project with `npm run dev` configured.

---

### /teach

**What it does:** Post-session technical deep dive. Reviews all code changes from the current session and creates a comprehensive learning breakdown — syntax patterns, framework concepts, data structures, architecture decisions, and line-by-line code walkthroughs.

**When to use it:** After a coding session when you want to understand what was built at a deeper level.

**Requirements:** None — analyzes the current session's work.

---

### /up-next

**What it does:** Orchestrates a full task cycle: gets the next task from the task manager, hands it to strategy and architecture agents for planning, creates an execution plan, runs it, evaluates completion, updates PRD and CLAUDE.md, then loops to the next task.

**When to use it:** For autonomous development loops across a project's task backlog.

**Requirements:**
| Requirement | How to set up |
|---|---|
| Agent teams | Requires `taskmaster-manager`, `product-strategy-advisor`, `react-component-architect`, and `section-executor` agent types configured. |

---

### /update-claude-md

**What it does:** Reviews recent code changes and updates the project's CLAUDE.md to reflect new patterns, conventions, dependencies, and architecture decisions.

**When to use it:** After completing a feature or significant code change.

**Requirements:** A CLAUDE.md file in the project.

---

### /update-prd

**What it does:** Reviews the README and updates it with relevant information about architecture, components, React patterns, and styling norms.

**When to use it:** After implementing changes that affect the project's documented architecture.

**Requirements:** A README.md in the project.

---

### /upload-article

**What it does:** Uploads a blog article with full SEO and Generative Engine Optimization (GEO). Handles content analysis, metadata generation, GEO optimization (TL;DR blocks, FAQ schema, answer-first structure), placeholder image generation, cross-linking with existing articles, and build verification.

**When to use it:** When publishing a new blog post to the platform.

**Requirements:** This command is specific to the LargeBusinessLoans.com project structure. Modify for your own blog platform.

---

## Handling Dependencies

### The Problem

Claude Code's plugin system doesn't auto-install MCP servers or API keys. When a skill needs an external service (Fireflies, Linear, Notion, etc.), you have to set it up yourself. If a required MCP isn't connected, the skill will fail when it tries to call those tools.

### How to Set Up MCP Servers

Each skill that needs external services lists its requirements in the tables above. The general process:

1. **Get an API key** from the service (Fireflies, Linear, Notion, OpenAI, etc.)
2. **Add the MCP server** to your Claude Code configuration (project-level `.mcp.json` or user-level `~/.claude/mcp.json`)
3. **Restart Claude Code** to pick up the new MCP server

Example MCP config entry (in `.mcp.json`):

```json
{
  "mcpServers": {
    "linear": {
      "command": "npx",
      "args": ["-y", "@linear/mcp-server"],
      "env": {
        "LINEAR_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Which Skills Work Out of the Box

These skills and commands have **zero external dependencies** — they work immediately after plugin installation:

- `internal-comms` — bundled templates
- `schedule` — uses built-in Claude Code tools
- `skill-creator` — needs Python and `claude` CLI (usually already present)
- `/design-system-creation-prompt`
- `/find-edge-cases`
- `/fix` (needs a Node.js project)
- `/teach`
- `/update-claude-md`
- `/update-prd`

### Best Practices

- **Check before you start:** If you're unsure whether an MCP is connected, ask Claude: "Do you have access to Linear/Fireflies/Notion tools?"
- **API keys in env, not in code:** Never put API keys in MCP config files that get committed. Use environment variables or a `.env` file that's gitignored.
- **One MCP at a time:** If setting up multiple MCPs, add and verify them one at a time to isolate issues.

---

## Legacy Install (Script)

If you prefer symlinks over the plugin system:

```bash
git clone https://github.com/anurieli/claude-leadership-pack.git ~/claude-leadership-pack
cd ~/claude-leadership-pack && ./install.sh
```

Update: `cd ~/claude-leadership-pack && git pull && ./install.sh`
Uninstall: `cd ~/claude-leadership-pack && ./uninstall.sh`
