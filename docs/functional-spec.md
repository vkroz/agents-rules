# agent-pack Functional Specification

## Problem Statement

AI-assisted development tools (Claude Code, Cursor, GitHub Copilot, etc.) each use their own configuration format for agent behavior rules. Teams and individuals working across multiple tools face:

1. **Fragmentation** — rules are duplicated in `CLAUDE.md`, `.cursor/rules/`, `AGENTS.md`, each with different syntax
2. **Drift** — changes in one tool's config are not reflected in others
3. **No hierarchy** — no way to define global/org/project/repo rules that compose predictably
4. **No sharing** — no mechanism to distribute and reuse rule sets across repos or organizations

## Objective

A CLI tool that compiles vendor-neutral canonical rulesets into tool-specific configuration files, with hierarchical inheritance and remote sync.

## V1 Scope

### Target Agents

V1 supports two generation targets:

| Agent | Config Location | Format |
|-------|----------------|--------|
| Claude Code | `CLAUDE.md` (repo root) | Single concatenated markdown file |
| Cursor | `.cursor/rules/*.mdc` | Individual `.mdc` files per rule |

### Functional Requirements

**F1: Init** (`agentpack init`)
- Create `agent-pack/` directory with `agent-pack.yaml`, `rules/`, `commands/` subdirectories
- Optionally detect existing tool-specific configs and offer to import them into canonical format

**F2: Generate** (`agentpack generate`)
- Read `agent-pack.yaml` for target agents and settings
- Read all canonical rules from `agent-pack/rules/` and `agent-pack/commands/`
- For each target agent, produce output in the expected format and location:
  - **Claude**: concatenate all `alwaysApply: true` rules into a single `CLAUDE.md`
  - **Cursor**: emit each rule as an individual `.mdc` file in `.cursor/rules/`, preserving frontmatter as Cursor metadata
- Respect `nested_depth` — generate configs in subdirectories up to N levels deep
- Optionally update `.gitignore` with generated file paths

**F3: Sync** (`agentpack sync <remote>`)
- Clone/pull a remote git repo containing shared canonical rules
- Merge remote rules into local `agent-pack/` directory
- Conflict resolution: local rules override remote rules with the same filename

### Canonical Format

Rules are markdown files with YAML frontmatter:

```markdown
---
description: "Rule description"
alwaysApply: true
globs: ["*.py"]
---

# Rule content in markdown
```

**Frontmatter fields:**
- `description` (string, required) — one-line summary
- `alwaysApply` (bool, optional, default `false`) — always include in generated output
- `globs` (list of strings, optional) — file patterns that trigger this rule

**Directory layout:**
```
agent-pack/
  agent-pack.yaml        # Project configuration
  rules/                 # Canonical rule files
    *.md
  commands/              # Slash-command definitions
    *.md
```

### Configuration: `agent-pack.yaml`

```yaml
agents: [claude, cursor]    # Target agents for generation
nested_depth: 2              # Subdirectory depth for config generation
gitignore: true              # Auto-manage .gitignore entries
```

### Hierarchy Model

Configurations resolve in priority order (highest wins):

```
user       →  ~/.config/agent-pack/          # Per-user overrides
repo       →  ./agent-pack/                  # Repo-level rules
project    →  (inherited from parent repo)    # Multi-repo project
org        →  (synced from org remote)        # Organization defaults
global     →  (synced from public remote)     # Community defaults
```

V1 implements **repo** and **sync** (org/global via remote). Full hierarchy resolution is a future goal.

## Out of Scope (Future)

- **Reverse-sync** — propagating edits made directly to generated files (e.g., `CLAUDE.md`) back to canonical rules. This is a known friction point with no clean solution yet.
- **Additional targets** — GitHub Copilot (`AGENTS.md`), Windsurf, other tools
- **Full hierarchy resolution** — automatic merging across user/project/org/global levels
- **GUI / web interface**
- **Rule versioning and changelogs**
- **Rule validation and linting**
