"""Smoke tests for the CLI."""

from typer.testing import CliRunner

from agent_pack.cli import app

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_init_stub():
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0


def test_generate_stub():
    result = runner.invoke(app, ["generate"])
    assert result.exit_code == 0


def test_sync_stub():
    result = runner.invoke(app, ["sync"])
    assert result.exit_code == 0
