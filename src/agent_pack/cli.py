"""CLI entry point for agentpack."""

from typing import Optional

import typer

from agent_pack import __version__

app = typer.Typer(help="AI agent configuration manager.")


def version_callback(value: bool):
    if value:
        print(f"agentpack {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True,
        help="Show version and exit.",
    ),
):
    """AI agent configuration manager."""
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


@app.command()
def init():
    """Bootstrap the agent-pack/ directory structure."""
    print("agentpack init: not yet implemented")


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
