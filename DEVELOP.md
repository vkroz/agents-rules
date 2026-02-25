# Development Operations Guide

`agent-pack` is a Python CLI tool for managing AI agent configurations across multiple tools (Claude Code, Cursor, etc.). It compiles vendor-neutral rulesets into tool-specific config files.

## Prerequisites

- Python 3.11+
- `uv` package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Setup

```bash
git clone https://github.com/vkroz/agent-pack.git
cd agent-pack
uv sync                    # creates .venv, installs all deps
uv run agentpack --help    # verify CLI works
```

## Development Workflow

### Run the CLI

```bash
uv run agentpack --help          # via uv (recommended during dev)
uv run agentpack init            # run a subcommand

uv tool install -e .             # install globally in dev mode
agentpack --help                 # then use directly
```

### Test

```bash
uv run pytest                    # all tests
uv run pytest -v                 # verbose
uv run pytest tests/test_cli.py  # single file
uv run pytest --cov=src          # with coverage (if configured)
```

### Lint & Format

```bash
uv run ruff check .              # lint
uv run ruff check --fix .        # auto-fix lint issues
uv run ruff format --check .     # check formatting
uv run ruff format .             # auto-format
```

### CI one-liner

```bash
uv sync && uv run pytest && uv run ruff check . && uv run ruff format --check .
```

## Troubleshooting

### Diagnose a broken CLI

When `uv run agentpack` fails, run these commands in order to isolate the problem:

```bash
# 1. Is the script entrypoint registered?
#    Look for "agentpack" under [project.scripts] in pyproject.toml
grep -A1 '\[project.scripts\]' pyproject.toml

# 2. Can Python find and import the package?
uv run python -c "import agent_pack; print(agent_pack.__version__)"

# 3. Can Python import the CLI module?
uv run python -c "from agent_pack.cli import app; print('OK')"

# 4. Does the module entrypoint work?
uv run python -m agent_pack --help

# 5. Force rebuild + reinstall the package
uv sync --reinstall
uv run agentpack --help
```

Common root causes:
- **`Failed to spawn: agentpack`** — script name in `[project.scripts]` doesn't match the command you're running.
- **`ModuleNotFoundError`** — an import path in `cli.py` or `__main__.py` references a module that doesn't exist (e.g. stale rename).
- **`ImportError` on a symbol** — the entrypoint in `pyproject.toml` or `__main__.py` references a name not exported by the module.

### Reset environment

```bash
rm -rf .venv/
uv sync
uv run pytest              # verify clean state
```

### Update dependencies

```bash
uv sync --upgrade           # all deps
uv add package-name@latest  # specific package
uv add --dev pytest@latest  # dev dependency
```

## Build & Deploy

### Build

```bash
rm -rf dist/
uv build
```

### Publish

```bash
uv publish --repository testpypi   # test PyPI first
uv publish                          # production PyPI
```

### Homebrew Formula

Example formula for a tap repository:

```ruby
class AgentPack < Formula
  desc "CLI tool for managing AI agent configurations"
  homepage "https://github.com/vkroz/agent-pack"
  url "https://files.pythonhosted.org/packages/source/a/agent-pack/agent-pack-0.1.0.tar.gz"
  sha256 "YOUR_SHA256_HERE"
  license "MIT"
  depends_on "python@3.11"
  depends_on "uv"
  def install
    system "uv", "pip", "install", *std_pip_args, "."
  end
  test do
    system "#{bin}/agentpack", "--help"
  end
end
```

## Configuration

| Setting | Value | Source |
|---|---|---|
| Python version | 3.11+ | `pyproject.toml` |
| Linter/formatter | Ruff (E, F, I rules) | `pyproject.toml [tool.ruff]` |
| Test framework | pytest | `pyproject.toml [tool.pytest]` |
| Build backend | hatchling | `pyproject.toml [build-system]` |
| IDE workspace | `agent-pack.code-workspace` | repo root |

## Version Management

- Version lives in `pyproject.toml` → `[project.version]` and `src/agent_pack/__init__.py`
- Follow semver (MAJOR.MINOR.PATCH)
- Tag releases: `git tag v0.1.0 && git push --tags`

---

See also: `pyproject.toml` · `README.md` · `CLAUDE.md` · `docs/`
