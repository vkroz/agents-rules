"""Tests for the CLI."""

from typer.testing import CliRunner

from agent_pack.cli import app

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_init_creates_directory_structure(tmp_path):
    result = runner.invoke(app, ["init", str(tmp_path)])
    assert result.exit_code == 0

    ap_dir = tmp_path / ".agentpack"
    assert ap_dir.is_dir()
    assert (ap_dir / "rules").is_dir()
    assert (ap_dir / "skills").is_dir()


def test_init_creates_config_file(tmp_path):
    runner.invoke(app, ["init", str(tmp_path)])

    config = (tmp_path / ".agentpack" / "agentpack.yaml").read_text()
    assert "agents:" in config
    assert "claude" in config
    assert "cursor" in config
    assert "gitignore: true" in config


def test_init_creates_starter_agents_md(tmp_path):
    runner.invoke(app, ["init", str(tmp_path)])

    agents_md = (tmp_path / ".agentpack" / "rules" / "AGENTS.md").read_text()
    assert "description:" in agents_md
    assert "alwaysApply: true" in agents_md
    assert "# Project Instructions" in agents_md


def test_init_fails_if_already_initialized(tmp_path):
    runner.invoke(app, ["init", str(tmp_path)])

    result = runner.invoke(app, ["init", str(tmp_path)])
    assert result.exit_code == 1
    assert "Already initialized" in result.output


def test_init_output_message(tmp_path):
    result = runner.invoke(app, ["init", str(tmp_path)])
    assert "Initialized" in result.output
    assert "agentpack.yaml" in result.output
    assert "AGENTS.md" in result.output
    assert "agentpack generate" in result.output


def test_init_defaults_to_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert (tmp_path / ".agentpack" / "agentpack.yaml").exists()


def test_generate_stub():
    result = runner.invoke(app, ["generate"])
    assert result.exit_code == 0


def test_sync_stub():
    result = runner.invoke(app, ["sync"])
    assert result.exit_code == 0
