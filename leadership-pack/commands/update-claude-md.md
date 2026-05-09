# /update-claude-md

## Purpose

Run this command after completing a new code implementation to ensure the CLAUDE.md file stays current and accurately reflects the codebase.

## Instructions for Claude

When this command is invoked:

1. **Review Recent Changes**
   - Examine all files modified or created in the current session
   - Identify new patterns, conventions, or architectural decisions introduced
   - Note any new dependencies, build steps, or environment requirements

2. **Analyze the Tagged CLAUDE.md File**
   - Read the existing CLAUDE.md file provided in context
   - Identify sections that need updates based on the implementation work

3. **Update the Following Sections as Needed**

   | Section | What to Check/Update |
   |---------|---------------------|
   | **Project Overview** | Add new features or capabilities implemented |
   | **Directory Structure** | Add new files, folders, or modules created |
   | **Coding Standards** | Document any new patterns or conventions established |
   | **Build/Test Instructions** | Add new commands, scripts, or testing procedures |
   | **Dependencies** | List new packages, libraries, or tools added |
   | **Architecture/Context** | Explain significant design decisions made |
   | **Known Issues/Limitations** | Document any caveats or TODOs discovered |

4. **Output Requirements**
   - Provide the complete updated CLAUDE.md content
   - Clearly indicate what was added or changed and why
   - Keep additions concise and actionable
   - Follow existing formatting conventions in the file

5. **Quality Checklist**
   - [ ] No sensitive data (credentials, API keys) included
   - [ ] Examples are concrete and accurate
   - [ ] Commands are copy-paste ready
   - [ ] New patterns align with existing conventions
   - [ ] Outdated information removed or corrected

## Usage

```
/update-claude-md

[Paste or tag your CLAUDE.md file here]
```

## Example Invocation

```
/update-claude-md

@CLAUDE.md

Just implemented:
- New authentication module in src/auth/
- Added JWT token validation
- Created user session middleware
```

---

*This command helps maintain a living, accurate CLAUDE.md that evolves with your codebase.*