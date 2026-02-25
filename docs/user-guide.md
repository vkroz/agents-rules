# agent-pack User Guide

## What is agent-pack?

agent-pack manages AI agent configurations across multiple tools. You write rules once in a vendor-neutral format, and agent-pack compiles them into tool-specific config files (`CLAUDE.md`, `.cursor/rules/`, etc.).

## Installation

```bash
# Install from GitHub
uv tool install git+https://github.com/vkroz/agent-pack

# Or install from a local clone for development
git clone https://github.com/agenture-org/agent-pack.git
cd agent-pack
uv sync
uv run agentpack --version
```

## Quick Start

```bash
# Bootstrap in your repo
cd my-project
agentpack init

# Edit your rules in agent-pack/
# Then generate tool-specific configs
agentpack generate
```

## CLI Commands

### `agentpack init`

Creates the `agent-pack/` directory structure in the current repo:

```
agent-pack/
  agent-pack.yaml       # Configuration
  rules/
    my-rule.md           # Your canonical rules
  commands/
    my-command.md        # Slash-command definitions
```

### `agentpack generate`

Reads `agent-pack/agent-pack.yaml` and canonical rules, produces tool-specific output files. Generated files are placed alongside `agent-pack/` in a `.generated-agent-pack/` directory, then copied to the locations each tool expects.

Example: with `agents: [claude, cursor]`, running `agentpack generate` produces:
- `CLAUDE.md` at the repo root
- `.cursor/rules/*.mdc` files

### `agentpack sync`

Pulls shared configurations from remote git repositories into your local `agent-pack/` directory.

```bash
# Sync from a public rules repo
agentpack sync https://github.com/agenture-org/agent-pack-community

# Sync from an org-private repo
agentpack sync git@github.com:my-org/agent-pack-shared.git
```

## Configuration: `agent-pack.yaml`

```yaml
# Which tools to generate configs for
agents: [claude, cursor]

# How many directory levels deep to generate nested configs
nested_depth: 2

# Add generated files to .gitignore
gitignore: true
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `agents` | list | `[claude]` | Target tools: `claude`, `cursor` |
| `nested_depth` | int | `1` | Directory depth for nested config generation |
| `gitignore` | bool | `true` | Auto-add generated files to `.gitignore` |

## Canonical Rule Format

Rules are markdown files with a YAML frontmatter header, stored in `agent-pack/rules/`.

```markdown
---
description: Short description of what this rule does
alwaysApply: true
---

# Rule Title

Your rule content in markdown.
```

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | string | yes | One-line summary, used by tools that support rule metadata |
| `alwaysApply` | bool | no | If `true`, rule is always active (default: `false`) |
| `globs` | list | no | File patterns that trigger this rule (e.g., `["*.py", "tests/**"]`) |

### Commands

Commands are markdown files in `agent-pack/commands/` that define slash-command workflows for agents. Same format as rules.

## Example

Given this structure:

```
my-project/
  agent-pack/
    agent-pack.yaml
    rules/
      code-style.md
      testing.md
    commands/
      review.md
```

With `agent-pack.yaml`:
```yaml
agents: [claude, cursor]
nested_depth: 1
gitignore: true
```

Running `agentpack generate` produces:

```
my-project/
  CLAUDE.md                          # Combined rules for Claude Code
  .cursor/
    rules/
      code-style.mdc                 # Individual rule files for Cursor
      testing.mdc
  .gitignore                         # Updated with generated file paths
```
