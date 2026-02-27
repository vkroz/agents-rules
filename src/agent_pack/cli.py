"""CLI entry point for agentpack."""

from pathlib import Path
from typing import Optional

import typer
import yaml

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


def _load_config(ap_dir: Path) -> dict:
    config_path = ap_dir / "agentpack.yaml"
    if not config_path.exists():
        typer.echo(f"Config not found: {config_path}", err=True)
        raise typer.Exit(code=1)
    with open(config_path) as f:
        return yaml.safe_load(f) or {}


def _find_skill_md(skill_dir: Path) -> Optional[Path]:
    """Return the skill markdown file in a skill directory (case-insensitive match for skill.md)."""
    for f in skill_dir.iterdir():
        if f.is_file() and f.name.lower() == "skill.md":
            return f
    return None


def _generate_claude(root: Path, ap_dir: Path) -> None:
    rules_dir = ap_dir / "rules"
    skills_dir = ap_dir / "skills"

    # AGENTS.md → .claude/CLAUDE.md
    agents_md = rules_dir / "AGENTS.md"
    if agents_md.exists():
        out = root / ".claude" / "CLAUDE.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(agents_md.read_text())
        typer.echo(f"  {out.relative_to(root)}")

    # Other rules → .claude/rules/*.md
    for rule_file in sorted(rules_dir.glob("*.md")):
        if rule_file.name == "AGENTS.md":
            continue
        out = root / ".claude" / "rules" / rule_file.name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rule_file.read_text())
        typer.echo(f"  {out.relative_to(root)}")

    # Skills → .claude/skills/<name>.md
    if skills_dir.exists():
        for skill_dir in sorted(d for d in skills_dir.iterdir() if d.is_dir()):
            skill_md = _find_skill_md(skill_dir)
            if skill_md:
                out = root / ".claude" / "skills" / f"{skill_dir.name}.md"
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(skill_md.read_text())
                typer.echo(f"  {out.relative_to(root)}")


def _generate_cursor(root: Path, ap_dir: Path) -> None:
    rules_dir = ap_dir / "rules"
    skills_dir = ap_dir / "skills"

    # All rules → .cursor/rules/*.md (AGENTS.md keeps its name)
    for rule_file in sorted(rules_dir.glob("*.md")):
        out = root / ".cursor" / "rules" / rule_file.name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rule_file.read_text())
        typer.echo(f"  {out.relative_to(root)}")

    # Skills → .cursor/rules/<name>.md
    if skills_dir.exists():
        for skill_dir in sorted(d for d in skills_dir.iterdir() if d.is_dir()):
            skill_md = _find_skill_md(skill_dir)
            if skill_md:
                out = root / ".cursor" / "rules" / f"{skill_dir.name}.md"
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(skill_md.read_text())
                typer.echo(f"  {out.relative_to(root)}")


def _update_gitignore(root: Path, agents: list) -> None:
    gitignore = root / ".gitignore"
    entries = []
    if "claude" in agents:
        entries.append(".claude/")
    if "cursor" in agents:
        entries.append(".cursor/")

    existing = gitignore.read_text() if gitignore.exists() else ""
    lines = existing.splitlines()

    added = []
    for entry in entries:
        if entry not in lines:
            lines.append(entry)
            added.append(entry)

    if added:
        gitignore.write_text("\n".join(lines) + "\n")
        for e in added:
            typer.echo(f"  .gitignore: added {e}")


@app.command()
def generate(
    path: Optional[Path] = typer.Argument(
        None,
        help="Target directory. Defaults to current directory.",
    ),
):
    """Compile canonical rulesets into tool-specific configs."""
    root = (path or Path.cwd()).resolve()
    ap_dir = root / AGENTPACK_DIR

    if not ap_dir.exists():
        typer.echo("Not initialized. Run `agentpack init` first.", err=True)
        raise typer.Exit(code=1)

    config = _load_config(ap_dir)
    agents = config.get("agents", [])
    use_gitignore = config.get("gitignore", True)

    if not agents:
        typer.echo("No agents configured in agentpack.yaml", err=True)
        raise typer.Exit(code=1)

    typer.echo("Generating...")

    if "claude" in agents:
        typer.echo("Claude:")
        _generate_claude(root, ap_dir)

    if "cursor" in agents:
        typer.echo("Cursor:")
        _generate_cursor(root, ap_dir)

    if use_gitignore:
        _update_gitignore(root, agents)

    typer.echo("Done.")


@app.command()
def sync(
    remote: Optional[str] = typer.Argument(None, help="Remote repository URL."),
):
    """Pull shared configurations from a remote repository."""
    print("agentpack sync: not yet implemented")
