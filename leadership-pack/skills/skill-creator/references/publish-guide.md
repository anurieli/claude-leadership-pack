# Publishing to the Skills Repository

After a skill is finalized (user is happy, evals pass, description is optimized), publish it to the shared skills repository so it's available across all machines via the plugin system.

## Repository Details

- **Repo:** `anurieli/claude-leadership-pack` on GitHub
- **Skills directory:** `skills/` (auto-discovered by the plugin system)
- **Commands directory:** `commands/` (must be registered in `.claude-plugin/plugin.json`)
- **README:** `README.md` at repo root — contains the skill directory that documents every skill

## Step-by-Step

### 1. Clone the repo

```bash
git clone https://github.com/anurieli/claude-leadership-pack.git /tmp/claude-leadership-pack-publish
```

If the clone already exists at that path, pull latest instead:

```bash
cd /tmp/claude-leadership-pack-publish && git pull
```

### 2. Copy the skill into the repo

Copy the finalized skill folder into `skills/`:

```bash
cp -r /path/to/my-new-skill /tmp/claude-leadership-pack-publish/skills/my-new-skill
```

The skill directory must contain at minimum a `SKILL.md` with proper frontmatter (name, description). Any bundled resources (scripts/, references/, assets/) come along.

### 3. Register commands (if applicable)

If the skill includes slash commands (standalone `.md` files meant to be invoked with `/command-name`), add them to `.claude-plugin/plugin.json` in the `"commands"` array:

```json
{
  "commands": [
    "./commands/existing-command.md",
    "./commands/new-command.md"
  ]
}
```

Skills placed in `skills/` are auto-discovered — no `plugin.json` change needed for skills.

### 4. Update the README

Open `README.md` and add a new entry to the **Skill Directory** section (or **Command Directory** if it's a command). Follow this exact format:

#### For skills:

```markdown
### skill-name

**What it does:** One paragraph explaining the skill's purpose and what it produces.

**When to use it:** Natural language triggers — what the user would say to invoke this. Include example phrases.

**How it works:**
1. Step one
2. Step two
3. Step three
(Keep it concise — 4-8 steps covering the main workflow)

**Requirements:**
| Requirement | How to set up |
|---|---|
| Service/Tool Name | Brief setup instructions including what API key is needed |

(If no external requirements, write: **Requirements:** None — this is a self-contained skill.)

**Note:** (Optional) Any customization notes, caveats, or things the user should know about adapting this skill.
```

#### For commands:

```markdown
### /command-name

**What it does:** One sentence explaining what the command does.

**When to use it:** When/why you'd run this command.

**Requirements:** What's needed (or "None").
```

### 5. Update the "Which Skills Work Out of the Box" list

In the **Handling Dependencies** section of the README, there's a list of skills/commands with zero external dependencies. If the new skill has no MCP or API key requirements, add it to that list. If it does have requirements, don't add it.

### 6. Commit and push

```bash
cd /tmp/claude-leadership-pack-publish
git add skills/my-new-skill/
git add README.md
git add .claude-plugin/plugin.json  # only if commands were added
git commit -m "Add my-new-skill: brief description of what it does"
git push
```

### 7. Tell the user to reload

After pushing, tell the user:

> The skill has been published to the repository. Run `/reload-plugins` to pull the latest version, or tell Claude: "Reload plugins to pull the latest skills."

## Determining Requirements

When writing the Requirements table for the README entry, check the skill's SKILL.md for:

- **MCP tool references** — any `fireflies_*`, `notion-*`, `linear_*`, `slack_*`, `google_drive_*` or similar tool calls mean that MCP server is required
- **API key references** — environment variables like `OPENAI_API_KEY`, `LINEAR_API_KEY`, etc.
- **CLI tools** — references to `claude`, `npm`, `python`, `node`, etc.
- **Python scripts** — if the skill bundles scripts in `scripts/`, Python 3 is a requirement
- **Project structure assumptions** — if the skill assumes a specific framework (Next.js, Convex, etc.), note it

If the skill uses the `compatibility` field in its SKILL.md frontmatter, pull requirements from there. If it doesn't have one, consider adding it.
