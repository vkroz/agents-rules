"""CLI entry point for agentpack."""

from pathlib import Path
from typing import Optional

import typer

from agent_pack import __version__

app = typer.Typer(help="AI agent configuration manager.")

AGENTPACK_DIR = ".agentpack"

DEFAULT_CONFIG = """\
agents: [claude, cursor]
gitignore: true
"""

DEFAULT_AGENTS_MD = """\
---
description: Main project instructions for AI agents
alwaysApply: true
---

# Project Instructions

<!-- Add your project-specific instructions here.
     This file maps to .claude/CLAUDE.md and .cursor/rules/AGENTS.md
     when you run `agentpack generate`. -->
"""


def version_callback(value: bool):
    if value:
        print(f"agentpack {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
):
    """AI agent configuration manager."""
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


@app.command()
def init(
    path: Optional[Path] = typer.Argument(
        None,
        help="Target directory. Defaults to current directory.",
    ),
):
    """Bootstrap .agentpack/ directory structure with starter config."""
    root = (path or Path.cwd()).resolve()
    ap_dir = root / AGENTPACK_DIR

    if ap_dir.exists():
        typer.echo(f"Already initialized: {ap_dir}", err=True)
        raise typer.Exit(code=1)

    rules_dir = ap_dir / "rules"
    skills_dir = ap_dir / "skills"

    rules_dir.mkdir(parents=True)
    skills_dir.mkdir(parents=True)

    (ap_dir / "agentpack.yaml").write_text(DEFAULT_CONFIG)
    (rules_dir / "AGENTS.md").write_text(DEFAULT_AGENTS_MD)

    typer.echo(f"Initialized {ap_dir}")
    typer.echo("  agentpack.yaml   — project configuration")
    typer.echo("  rules/AGENTS.md  — starter project instructions")
    typer.echo("\nNext: edit your rules, then run `agentpack generate`.")


@app.command()
def generate():
    """Compile canonical rulesets into tool-specific configs."""
    print("agentpack generate: not yet implemented")


@app.command()
def sync(
    remote: Optional[str] = typer.Argument(None, help="Remote repository URL."),
):
    """Pull shared configurations from a remote repository."""
    print("agentpack sync: not yet implemented")
