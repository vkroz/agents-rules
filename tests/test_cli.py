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


def _init_with_rules(tmp_path, agents="[claude, cursor]"):
    """Helper: init a repo and add sample rules/skills for generate tests."""
    runner.invoke(app, ["init", str(tmp_path)])
    # Overwrite config with specified agents
    (tmp_path / ".agentpack" / "agentpack.yaml").write_text(
        f"agents: {agents}\ngitignore: true\n"
    )
    # Add a modular rule
    (tmp_path / ".agentpack" / "rules" / "coding.md").write_text(
        "---\ndescription: Coding standards\n---\n\n# Coding\n"
    )
    # Add a skill
    skill_dir = tmp_path / ".agentpack" / "skills" / "deploy"
    skill_dir.mkdir(parents=True)
    (skill_dir / "skill.md").write_text(
        "---\nname: deploy\ndescription: Deploy skill\n---\n\n# Deploy\n"
    )
    return tmp_path


def test_generate_fails_without_agentpack(tmp_path):
    result = runner.invoke(app, ["generate", str(tmp_path)])
    assert result.exit_code == 1
    assert "Not initialized" in result.output


def test_generate_claude_agents_md(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    assert (tmp_path / ".claude" / "CLAUDE.md").exists()


def test_generate_claude_modular_rules(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    assert (tmp_path / ".claude" / "rules" / "coding.md").exists()


def test_generate_claude_skills(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    assert (tmp_path / ".claude" / "skills" / "deploy.md").exists()


def test_generate_claude_agents_md_not_in_rules_dir(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    # AGENTS.md should go to CLAUDE.md, not .claude/rules/AGENTS.md
    assert not (tmp_path / ".claude" / "rules" / "AGENTS.md").exists()


def test_generate_cursor_agents_md(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    assert (tmp_path / ".cursor" / "rules" / "AGENTS.md").exists()


def test_generate_cursor_modular_rules(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    assert (tmp_path / ".cursor" / "rules" / "coding.md").exists()


def test_generate_cursor_skills(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    assert (tmp_path / ".cursor" / "rules" / "deploy.md").exists()


def test_generate_content_preserved(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    content = (tmp_path / ".claude" / "rules" / "coding.md").read_text()
    assert "Coding standards" in content


def test_generate_gitignore_updated(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    gitignore = (tmp_path / ".gitignore").read_text()
    assert ".claude/" in gitignore
    assert ".cursor/" in gitignore


def test_generate_gitignore_no_duplicates(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    runner.invoke(app, ["generate", str(tmp_path)])
    gitignore = (tmp_path / ".gitignore").read_text()
    assert gitignore.count(".claude/") == 1


def test_generate_only_claude(tmp_path):
    _init_with_rules(tmp_path, agents="[claude]")
    runner.invoke(app, ["generate", str(tmp_path)])
    assert (tmp_path / ".claude" / "CLAUDE.md").exists()
    assert not (tmp_path / ".cursor").exists()


def test_generate_only_cursor(tmp_path):
    _init_with_rules(tmp_path, agents="[cursor]")
    runner.invoke(app, ["generate", str(tmp_path)])
    assert (tmp_path / ".cursor" / "rules" / "AGENTS.md").exists()
    assert not (tmp_path / ".claude").exists()


def test_generate_defaults_to_cwd(tmp_path, monkeypatch):
    _init_with_rules(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["generate"])
    assert result.exit_code == 0
    assert (tmp_path / ".claude" / "CLAUDE.md").exists()


def test_generate_output_message(tmp_path):
    _init_with_rules(tmp_path)
    result = runner.invoke(app, ["generate", str(tmp_path)])
    assert result.exit_code == 0
    assert "Generating" in result.output
    assert "Done" in result.output


def test_sync_stub():
    result = runner.invoke(app, ["sync"])
    assert result.exit_code == 0
