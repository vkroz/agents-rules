# agentpack Functional Specification

## Problem Statement

AI-assisted development tools (Claude Code, Cursor, GitHub Copilot, etc.) each use their own configuration format for agent behavior rules. Teams and individuals working across multiple tools face:

1. **Fragmentation** — rules are duplicated in `CLAUDE.md`, `.cursor/rules/`, `AGENTS.md`, each with different syntax
2. **Drift** — changes in one tool's config are not reflected in others
3. **No hierarchy** — no way to define global/org/project/repo rules that compose predictably
4. **No sharing** — no mechanism to distribute and reuse rule sets across repos or organizations

## Objective

A CLI tool that compiles vendor-neutral canonical rulesets into tool-specific configuration files, with hierarchical inheritance and remote sync.

## V1 Scope

### Artifact Types

- **Rules** — [Claude memory](https://code.claude.com/docs/en/memory), [Cursor rules](https://cursor.com/docs/context/rules)
- **Skills** — [open standard](https://agentskills.io), [Claude skills](https://code.claude.com/docs/en/skills), [Cursor skills](https://cursor.com/docs/context/skills)

### Target Tools

- Claude Code
- Cursor

### Hierarchy Model

agentpack resolves rules by merging sources across multiple levels:

```
user       →  ~/.config/agentpack/          # Per-user overrides
repo       →  ./.agentpack/                 # Repo-level rules
project    →  (inherited from parent repo)   # Multi-repo project
org        →  (synced from org remote)       # Organization defaults
global     →  (synced from public remote)    # Community defaults
```

V1 implements repo-level and remote sync (org/global). Full hierarchy resolution is a future goal.

### Commands

**Install**

Install agentpack from Homebrew, PyPI, or directly from GitHub sources.

**Init** (`agentpack init`)

- Create `.agentpack/` directory with a minimal `agentpack.yaml` config
- Place default starter rules as examples

**Generate** (`agentpack generate`)

Compile canonical artifacts from `.agentpack/` into tool-specific configuration files (e.g., `.claude/CLAUDE.md`, `.cursor/rules/*.md`).

- Read `agentpack.yaml` for target tools and settings
- Read all canonical artifacts from `.agentpack/rules/`, `.agentpack/skills/`, etc.
- For each target tool, produce output in the expected format and location
- Optionally update `.gitignore` with generated file paths

**Sync** (`agentpack sync [<remote>]`)

Merge shared rules from a remote git repo into the local `.agentpack/` directory.

- `<remote>` is either a name defined in `agentpack.yaml` under `remotes:`, or a full git URL
- If `<remote>` is omitted, syncs all remotes defined in `agentpack.yaml`
- On first run, clone the remote repo into `~/.cache/agentpack/remotes/<remote-name>/`
- On subsequent runs, pull updates to the cached clone
- Merge remote rules from the cache into local `.agentpack/`
- Conflict resolution: local rules override remote rules with the same filename

## Configuration

**Directory layout:**
```
.agentpack/
  agentpack.yaml        # Project configuration
  rules/                # Canonical rule files
    AGENTS.md           # Main project instructions
    *.md                # Modular rules
  skills/               # Skill definitions
    <name>/             # One directory per skill
      skill.md
```

### Configuration: `agentpack.yaml`

```yaml
agents: [claude, cursor]    # Target agents for generation
gitignore: true              # Auto-manage .gitignore entries
remotes:
  community: https://github.com/agentpack/agent-pack-community
  my-org: git@github.com:my-org/agent-pack-shared.git
```

| Field | Required | Description |
|-------|----------|-------------|
| `agents` | Yes | Target tools for generation. Supported values: `claude`, `cursor`. |
| `gitignore` | No | Auto-add generated files to `.gitignore`. Default: `true`. |
| `remotes` | No | Named remote repos for `agentpack sync`. Keys are short names used as the cache directory name (`~/.cache/agentpack/remotes/<name>/`) and as the argument to `agentpack sync <name>`. Values are git URLs (HTTPS or SSH). |

### Rules Format

Rules are markdown files with YAML frontmatter. The syntax follows the [Claude memory format](https://code.claude.com/docs/en/memory). See also [Cursor rules](https://cursor.com/docs/context/rules). Cursor natively detects and applies Claude-format rules without any modification required.

| Rules type | Location | Purpose | Mapping to tool-specific files |
|-----------|----------|---------|--------------------------------|
| Main project instructions | `.agentpack/rules/AGENTS.md` | Memory for the current project. | `.claude/CLAUDE.md`, `.cursor/rules/AGENTS.md` |
| Modular rules | `.agentpack/rules/*.md` | Rules for the current project. | `.claude/rules/*.md`, `.cursor/rules/*.md` |

```markdown
---
description: "Rule description"
paths: ["src/api/**/*.ts"]
alwaysApply: true
---
```

Each rule is a markdown file with frontmatter metadata and content. The frontmatter metadata controls how the rule is applied.

| Field | Required | Description |
|-------|----------|-------------|
| description | Yes | What the rule does and when to use it. Agent uses this to decide when to apply the rule. Rules without a `paths` field are loaded unconditionally and apply to all files. See [path-specific rules](https://code.claude.com/docs/en/memory#path-specific-rules). |
| paths | No | File patterns that trigger this rule. Example: `["*.py", "tests/**"]`. |
| alwaysApply | No | If true, the rule is always active (default: false). |


### Skill Format

Each skill is a directory under `.agentpack/skills/` containing a `skill.md` file. The directory name is the skill identifier and must match the `name` field in the frontmatter.

```
.agentpack/skills/
  deploy/
    skill.md
  review/
    skill.md
```

`skill.md` frontmatter:

```markdown
---
name: deploy
description: "Skill description"
claude:
    allowed-tools: Read, Grep
cursor:
    compatibility: system packages, network access, etc.
---
```

**Common fields:**
| Field | Required | Description |
|-------|----------|-------------|
| name | Yes | Skill identifier. Lowercase letters, numbers, and hyphens only. Must match the parent directory name. |
| description | No | What the skill does and when to use it. Agent uses this to decide when to apply the skill. If omitted, the first paragraph of the skill content is used. |

**Claude-specific fields** (under `claude:` block):
| Field | Required | Description |
|-------|----------|-------------|
| argument-hint | No | Hint shown during autocomplete to indicate expected arguments. Example: `[issue-number]` or `[filename] [format]`. |
| user-invocable | No | Set to false to hide from the `/` menu. Use for background knowledge users shouldn't invoke directly. Default: true. |
| allowed-tools | No | Tools Claude can use without asking permission when this skill is active. |
| model | No | Model to use when this skill is active. |
| context | No | Set to `fork` to run in a forked subagent context. |
| agent | No | Which subagent type to use when `context: fork` is set. |
| hooks | No | Hooks scoped to this skill's lifecycle. See Hooks in skills and agents for configuration format. |
| disable-model-invocation | No | When true, the skill is only included when explicitly invoked via `/skill-name`. The agent will not automatically apply it based on context. |

**Cursor-specific fields** (under `cursor:` block):
| Field | Required | Description |
|-------|----------|-------------|
| license | No | License name or reference to a bundled license file. |
| compatibility | No | Environment requirements (system packages, network access, etc.). |
| metadata | No | Arbitrary key-value mapping for additional metadata. |


## Out of Scope

### Next Version

- **Subagents** — [Claude sub-agents](https://code.claude.com/docs/en/sub-agents), [Cursor subagents](https://cursor.com/docs/context/subagents#custom-subagents)
- **Agent Teams** — [Claude agent-teams](https://code.claude.com/docs/en/agent-teams)

### Future

- **Reverse-sync** — propagating edits made directly to generated files (e.g., `CLAUDE.md`) back to canonical rules. This is a known friction point with no clean solution yet.
- **Additional targets** — GitHub Copilot (`AGENTS.md`), Windsurf, other tools
- **Full hierarchy resolution** — automatic merging across user/project/org/global levels
- **GUI / web interface**
- **Rule versioning and changelogs**
- **Rule validation and linting**
