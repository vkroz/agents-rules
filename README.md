# agentpack

A tool to manage AI coding agents configuration.

## Why agentpack

The primary goal is consistent AI coding-agent configuration management across organizations, teams, projects, and repositories.

`agentpack` helps centralize and distribute shared rules, while still allowing repo-level customization.

Multi-tool vendor-neutral configuration is a secondary benefit:
- Write canonical rules and skills once in `.agentpack/`
- Compile to tool-specific outputs for Claude Code and Cursor

## Installation

```bash
uv tool install git+https://github.com/numio-ai/agent-pack
```

## Quick start

```bash
cd my-project
agentpack init       # creates .agentpack/ with starter config
# edit rules in .agentpack/rules/
agentpack generate   # produces tool-specific output files
```

## Core commands

- `agentpack init` - Bootstrap `.agentpack/` in the current repo
- `agentpack generate` - Compile canonical artifacts into tool-specific configs
- `agentpack sync [<remote>]` - Pull shared rules from configured remotes or a git URL

## Hierarchical inheritance

Hierarchical inheritance is a core concept in `agentpack`: rules are designed to compose across levels such as global -> org -> project -> repo -> user.

## Generated output

Given `agents: [claude, cursor]`:
- `.agentpack/rules/AGENTS.md` -> `.claude/CLAUDE.md` and `.cursor/rules/AGENTS.md`
- `.agentpack/rules/*.md` -> `.claude/rules/*.md` and `.cursor/rules/*.md`
- `.agentpack/skills/<name>/skill.md` -> `.claude/skills/<name>.md` and `.cursor/rules/<name>.md`

## Documentation

For more details, see `docs/user-guide.md`.

## Contributing

Contributions are welcome. Please read the [contributing guidelines](CONTRIBUTING.md) for more information.
