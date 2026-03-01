# agentpack User Guide

agentpack manages AI agent configurations across multiple tools. Write rules once in a vendor-neutral format; agentpack compiles them into tool-specific files (`CLAUDE.md`, `.cursor/rules/`, etc.).

## Installation

```bash
# Install from GitHub
uv tool install git+https://github.com/numio-ai/agent-pack

# For development
git clone https://github.com/numio-ai/agent-pack.git
cd agent-pack
uv sync
uv run agentpack --version
```

## Quick Start

```bash
cd my-project
agentpack init       # creates .agentpack/ with starter config
# edit rules in .agentpack/rules/
agentpack generate   # produces tool-specific output files
```

## Commands

| Command | Description |
|---------|-------------|
| `agentpack init` | Bootstrap `.agentpack/` in the current repo |
| `agentpack generate` | Compile canonical rules into tool-specific configs |
| `agentpack sync [<remote>]` | Pull shared rules from a remote git repo |

`<remote>` is a name from `agentpack.yaml` or a full git URL. If omitted, syncs all configured remotes.

## Configuration: `agentpack.yaml`

```yaml
agents: [claude, cursor]    # Target tools for generation
gitignore: true              # Auto-add generated files to .gitignore
remotes:
  community: https://github.com/agentpack/agent-pack-community
  my-org: git@github.com:my-org/agent-pack-shared.git
```

| Field | Required | Description |
|-------|----------|-------------|
| `agents` | Yes | Target tools: `claude`, `cursor` |
| `gitignore` | No | Auto-add generated files to `.gitignore`. Default: `true`. |
| `remotes` | No | Named remote repos for `agentpack sync`. Keys are names; values are git URLs (HTTPS or SSH). |

## Directory Layout

```
.agentpack/
  agentpack.yaml
  rules/
    AGENTS.md           # Main project instructions
    *.md                # Modular rules
  skills/
    <name>/
      skill.md          # One directory per skill
```

## Rule Format

```markdown
---
description: "What this rule does"
paths: ["src/api/**/*.ts"]   # optional: file patterns that trigger this rule
alwaysApply: false            # optional: if true, always active
---

Rule content in markdown.
```

## Skill Format

```markdown
---
name: deploy
description: "What this skill does"
claude:
    allowed-tools: Read, Grep
cursor:
    compatibility: network access
---

Skill content in markdown.
```

## Generated Output

Given `agents: [claude, cursor]`, `agentpack generate` produces:

| Source | Claude output | Cursor output |
|--------|--------------|---------------|
| `.agentpack/rules/CLAUDE.md` | `CLAUDE.md` (root) | `AGENTS.md` (root, cursor-only) |
| `.agentpack/rules/*.md` | `.claude/rules/*.md` | `.cursor/rules/*.md` |
| `.agentpack/skills/<name>/skill.md` | `.claude/skills/<name>.md` | `.cursor/rules/<name>.md` |
