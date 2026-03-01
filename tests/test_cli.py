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


def test_init_creates_starter_claude_md(tmp_path):
    runner.invoke(app, ["init", str(tmp_path)])

    claude_md = (tmp_path / ".agentpack" / "rules" / "CLAUDE.md").read_text()
    assert "description:" in claude_md
    assert "alwaysApply: true" in claude_md
    assert "# Project Instructions" in claude_md


def test_init_fails_if_already_initialized(tmp_path):
    runner.invoke(app, ["init", str(tmp_path)])

    result = runner.invoke(app, ["init", str(tmp_path)])
    assert result.exit_code == 1
    assert "Already initialized" in result.output


def test_init_output_message(tmp_path):
    result = runner.invoke(app, ["init", str(tmp_path)])
    assert "Initialized" in result.output
    assert "agentpack.yaml" in result.output
    assert "CLAUDE.md" in result.output
    assert "agentpack generate" in result.output


def test_init_defaults_to_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert (tmp_path / ".agentpack" / "agentpack.yaml").exists()


# ---------------------------------------------------------------------------
# Generate helpers
# ---------------------------------------------------------------------------


def _init_with_rules(tmp_path, agents="[claude, cursor]"):
    """Helper: init a repo and add sample rules/skills for generate tests."""
    runner.invoke(app, ["init", str(tmp_path)])
    (tmp_path / ".agentpack" / "agentpack.yaml").write_text(
        f"agents: {agents}\ngitignore: true\n"
    )
    (tmp_path / ".agentpack" / "rules" / "coding.md").write_text(
        "---\ndescription: Coding standards\n---\n\n# Coding\n"
    )
    skill_dir = tmp_path / ".agentpack" / "skills" / "deploy"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: deploy\ndescription: Deploy skill\n---\n\n# Deploy\n"
    )
    return tmp_path


# ---------------------------------------------------------------------------
# Generate — basic output
# ---------------------------------------------------------------------------


def test_generate_fails_without_agentpack(tmp_path):
    result = runner.invoke(app, ["generate", str(tmp_path)])
    assert result.exit_code == 1
    assert "Not initialized" in result.output


def test_generate_claude_agents_md(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    assert (tmp_path / "CLAUDE.md").exists()


def test_generate_claude_modular_rules(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    assert (tmp_path / ".claude" / "rules" / "coding.md").exists()


def test_generate_claude_skills(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    assert (tmp_path / ".claude" / "skills" / "deploy" / "SKILL.md").exists()


def test_generate_claude_agents_md_not_in_rules_dir(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    assert not (tmp_path / ".claude" / "rules" / "CLAUDE.md").exists()


def test_generate_cursor_agents_md_not_in_rules_dir(tmp_path):
    """CLAUDE.md must never be placed inside .cursor/rules/ regardless of agents config."""
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    assert not (tmp_path / ".cursor" / "rules" / "CLAUDE.md").exists()


def test_generate_cursor_modular_rules(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    assert (tmp_path / ".cursor" / "rules" / "coding.md").exists()


def test_generate_cursor_no_skills_when_claude_configured(tmp_path):
    """When both agents are configured, cursor reads skills from .claude/skills/."""
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    assert not (tmp_path / ".cursor" / "skills").exists()


def test_generate_cursor_skills_when_cursor_only(tmp_path):
    _init_with_rules(tmp_path, agents="[cursor]")
    runner.invoke(app, ["generate", str(tmp_path)])
    assert (tmp_path / ".cursor" / "skills" / "deploy" / "SKILL.md").exists()


def test_generate_claude_md_at_root_not_in_claude_dir(tmp_path):
    """CLAUDE.md must be at project root, not inside .claude/."""
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    assert not (tmp_path / ".claude" / "CLAUDE.md").exists()


def test_generate_agents_md_at_root_cursor_only(tmp_path):
    """cursor-only config produces AGENTS.md at project root."""
    _init_with_rules(tmp_path, agents="[cursor]")
    runner.invoke(app, ["generate", str(tmp_path)])
    assert (tmp_path / "AGENTS.md").exists()


def test_generate_no_agents_md_when_claude_present(tmp_path):
    """AGENTS.md is not generated when claude is in the agents list."""
    _init_with_rules(tmp_path)  # [claude, cursor]
    runner.invoke(app, ["generate", str(tmp_path)])
    assert not (tmp_path / "AGENTS.md").exists()


def test_generate_agents_md_has_html_marker(tmp_path):
    _init_with_rules(tmp_path, agents="[cursor]")
    runner.invoke(app, ["generate", str(tmp_path)])
    content = (tmp_path / "AGENTS.md").read_text()
    assert content.startswith("<!-- GENERATED BY agentpack.")
    assert ".agentpack/rules/CLAUDE.md" in content


def test_generate_agents_md_strips_frontmatter(tmp_path):
    _init_with_rules(tmp_path, agents="[cursor]")
    runner.invoke(app, ["generate", str(tmp_path)])
    content = (tmp_path / "AGENTS.md").read_text()
    assert "---" not in content
    assert "alwaysApply" not in content


def test_generate_agents_md_skips_user_defined(tmp_path):
    """User-defined AGENTS.md at project root is not overwritten."""
    _init_with_rules(tmp_path, agents="[cursor]")
    (tmp_path / "AGENTS.md").write_text("# My own AGENTS.md\n")
    result = runner.invoke(app, ["generate", str(tmp_path)])
    assert "WARN" in result.output
    assert "skipping" in result.output
    assert (tmp_path / "AGENTS.md").read_text() == "# My own AGENTS.md\n"


def test_generate_agents_md_force_overwrites_user_defined(tmp_path):
    _init_with_rules(tmp_path, agents="[cursor]")
    (tmp_path / "AGENTS.md").write_text("# My own AGENTS.md\n")
    result = runner.invoke(app, ["generate", "--force", str(tmp_path)])
    assert "WARN" not in result.output
    assert "GENERATED BY agentpack" in (tmp_path / "AGENTS.md").read_text()


def test_generate_claude_md_skips_user_defined(tmp_path):
    """User-defined CLAUDE.md at project root is not overwritten."""
    _init_with_rules(tmp_path)
    (tmp_path / "CLAUDE.md").write_text("# My own CLAUDE.md\n")
    result = runner.invoke(app, ["generate", str(tmp_path)])
    assert "WARN" in result.output
    assert "skipping" in result.output
    assert (tmp_path / "CLAUDE.md").read_text() == "# My own CLAUDE.md\n"


def test_generate_gitignore_claude_md_entry(tmp_path):
    _init_with_rules(tmp_path, agents="[claude]")
    runner.invoke(app, ["generate", str(tmp_path)])
    gitignore = (tmp_path / ".gitignore").read_text()
    assert "CLAUDE.md" in gitignore


def test_generate_gitignore_agents_md_cursor_only(tmp_path):
    _init_with_rules(tmp_path, agents="[cursor]")
    runner.invoke(app, ["generate", str(tmp_path)])
    gitignore = (tmp_path / ".gitignore").read_text()
    assert "AGENTS.md" in gitignore
    assert "CLAUDE.md" not in gitignore


def test_generate_gitignore_no_agents_md_when_claude_present(tmp_path):
    """AGENTS.md must not appear in .gitignore when claude is also configured."""
    _init_with_rules(tmp_path)  # [claude, cursor]
    runner.invoke(app, ["generate", str(tmp_path)])
    gitignore = (tmp_path / ".gitignore").read_text()
    assert "AGENTS.md" not in gitignore


def test_generate_cleanup_removes_stale_claude_md(tmp_path):
    """Switching from [claude] to [cursor] removes the previously generated CLAUDE.md."""
    _init_with_rules(tmp_path, agents="[claude]")
    runner.invoke(app, ["generate", str(tmp_path)])
    assert (tmp_path / "CLAUDE.md").exists()

    (tmp_path / ".agentpack" / "agentpack.yaml").write_text("agents: [cursor]\ngitignore: true\n")
    runner.invoke(app, ["generate", str(tmp_path)])

    assert not (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / "AGENTS.md").exists()


def test_generate_cleanup_removes_stale_agents_md(tmp_path):
    """Switching from [cursor] to [claude] removes the previously generated AGENTS.md."""
    _init_with_rules(tmp_path, agents="[cursor]")
    runner.invoke(app, ["generate", str(tmp_path)])
    assert (tmp_path / "AGENTS.md").exists()

    (tmp_path / ".agentpack" / "agentpack.yaml").write_text("agents: [claude]\ngitignore: true\n")
    runner.invoke(app, ["generate", str(tmp_path)])

    assert not (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / "CLAUDE.md").exists()


def test_generate_content_preserved(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    content = (tmp_path / ".claude" / "rules" / "coding.md").read_text()
    assert "Coding standards" in content


def test_generate_gitignore_updated(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    gitignore = (tmp_path / ".gitignore").read_text()
    assert "CLAUDE.md" in gitignore
    assert ".claude/" in gitignore
    assert ".cursor/" in gitignore


def test_generate_gitignore_no_duplicates(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    runner.invoke(app, ["generate", str(tmp_path)])
    gitignore = (tmp_path / ".gitignore").read_text()
    assert gitignore.count("CLAUDE.md") == 1
    assert gitignore.count(".claude/") == 1


def test_generate_only_claude(tmp_path):
    _init_with_rules(tmp_path, agents="[claude]")
    runner.invoke(app, ["generate", str(tmp_path)])
    assert (tmp_path / "CLAUDE.md").exists()
    assert not (tmp_path / ".cursor").exists()


def test_generate_only_cursor(tmp_path):
    _init_with_rules(tmp_path, agents="[cursor]")
    runner.invoke(app, ["generate", str(tmp_path)])
    assert (tmp_path / "AGENTS.md").exists()
    assert not (tmp_path / ".claude").exists()


def test_generate_defaults_to_cwd(tmp_path, monkeypatch):
    _init_with_rules(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["generate"])
    assert result.exit_code == 0
    assert (tmp_path / "CLAUDE.md").exists()


def test_generate_output_message(tmp_path):
    _init_with_rules(tmp_path)
    result = runner.invoke(app, ["generate", str(tmp_path)])
    assert result.exit_code == 0
    assert "Generating" in result.output
    assert "Done" in result.output


# ---------------------------------------------------------------------------
# Generated file markers
# ---------------------------------------------------------------------------


def test_generate_claude_md_has_html_marker(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    content = (tmp_path / "CLAUDE.md").read_text()
    assert content.startswith("<!-- GENERATED BY agentpack.")
    assert ".agentpack/rules/CLAUDE.md" in content


def test_generate_claude_md_strips_frontmatter(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    content = (tmp_path / "CLAUDE.md").read_text()
    assert "---" not in content
    assert "alwaysApply" not in content


def test_generate_rules_have_yaml_marker(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    content = (tmp_path / ".claude" / "rules" / "coding.md").read_text()
    assert content.startswith("---\n# GENERATED BY agentpack.")
    assert ".agentpack/rules/coding.md" in content


def test_generate_skills_have_yaml_marker(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    content = (tmp_path / ".claude" / "skills" / "deploy" / "SKILL.md").read_text()
    assert "# GENERATED BY agentpack." in content
    assert ".agentpack/skills/deploy/SKILL.md" in content


def test_generate_cursor_rules_have_yaml_marker(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    content = (tmp_path / ".cursor" / "rules" / "coding.md").read_text()
    assert "# GENERATED BY agentpack." in content
    assert ".agentpack/rules/coding.md" in content


# ---------------------------------------------------------------------------
# Overwrite protection
# ---------------------------------------------------------------------------


def test_generate_skips_modified_file(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    target = tmp_path / "CLAUDE.md"
    target.write_text("# My custom rules\n")
    result = runner.invoke(app, ["generate", str(tmp_path)])
    assert "WARN" in result.output
    assert "skipping" in result.output
    assert target.read_text() == "# My custom rules\n"


def test_generate_force_overwrites_modified_file(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    target = tmp_path / "CLAUDE.md"
    target.write_text("# My custom rules\n")
    result = runner.invoke(app, ["generate", "--force", str(tmp_path)])
    assert "WARN" not in result.output
    assert "GENERATED BY agentpack" in target.read_text()


def test_generate_overwrites_marker_file(tmp_path):
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    result = runner.invoke(app, ["generate", str(tmp_path)])
    assert result.exit_code == 0
    assert "WARN" not in result.output


# ---------------------------------------------------------------------------
# Supplementary directories
# ---------------------------------------------------------------------------


def test_generate_copies_supplementary_dirs(tmp_path):
    _init_with_rules(tmp_path)
    scripts_dir = tmp_path / ".agentpack" / "skills" / "deploy" / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "run.sh").write_text("#!/bin/bash\necho deploy")
    runner.invoke(app, ["generate", str(tmp_path)])
    out_script = tmp_path / ".claude" / "skills" / "deploy" / "scripts" / "run.sh"
    assert out_script.exists()
    assert "echo deploy" in out_script.read_text()


def test_generate_copies_supplementary_dirs_cursor_only(tmp_path):
    _init_with_rules(tmp_path, agents="[cursor]")
    refs_dir = tmp_path / ".agentpack" / "skills" / "deploy" / "references"
    refs_dir.mkdir()
    (refs_dir / "guide.md").write_text("# Guide")
    runner.invoke(app, ["generate", str(tmp_path)])
    out = tmp_path / ".cursor" / "skills" / "deploy" / "references" / "guide.md"
    assert out.exists()


# ---------------------------------------------------------------------------
# Cleanup of stale generated files
# ---------------------------------------------------------------------------


def test_generate_removes_stale_rule_on_rename(tmp_path):
    """Renaming a source rule removes the old generated file on next generate."""
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    old_rule = tmp_path / ".claude" / "rules" / "coding.md"
    assert old_rule.exists()

    (tmp_path / ".agentpack" / "rules" / "coding.md").rename(
        tmp_path / ".agentpack" / "rules" / "coding-renamed.md"
    )
    runner.invoke(app, ["generate", str(tmp_path)])

    assert not old_rule.exists()
    assert (tmp_path / ".claude" / "rules" / "coding-renamed.md").exists()


def test_generate_removes_stale_cursor_rule_on_rename(tmp_path):
    """Renaming a source rule removes the old cursor-generated file on next generate."""
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    old_rule = tmp_path / ".cursor" / "rules" / "coding.md"
    assert old_rule.exists()

    (tmp_path / ".agentpack" / "rules" / "coding.md").rename(
        tmp_path / ".agentpack" / "rules" / "coding-renamed.md"
    )
    runner.invoke(app, ["generate", str(tmp_path)])

    assert not old_rule.exists()
    assert (tmp_path / ".cursor" / "rules" / "coding-renamed.md").exists()


def test_generate_removes_stale_skill_on_rename(tmp_path):
    """Renaming a skill source removes the old generated SKILL.md on next generate."""
    _init_with_rules(tmp_path, agents="[cursor]")
    runner.invoke(app, ["generate", str(tmp_path)])
    old_skill = tmp_path / ".cursor" / "skills" / "deploy" / "SKILL.md"
    assert old_skill.exists()

    (tmp_path / ".agentpack" / "skills" / "deploy").rename(
        tmp_path / ".agentpack" / "skills" / "deploy-v2"
    )
    runner.invoke(app, ["generate", str(tmp_path)])

    assert not old_skill.exists()
    assert (tmp_path / ".cursor" / "skills" / "deploy-v2" / "SKILL.md").exists()


def test_generate_cleanup_preserves_user_files(tmp_path):
    """Cleanup only removes marker files; user files without a marker are preserved."""
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    user_file = tmp_path / ".claude" / "rules" / "my-custom.md"
    user_file.write_text("# My Custom Rule\n")

    runner.invoke(app, ["generate", str(tmp_path)])

    assert user_file.exists()


def test_generate_cleanup_removes_deleted_source_rule(tmp_path):
    """Deleting a source rule removes its generated output on next generate."""
    _init_with_rules(tmp_path)
    runner.invoke(app, ["generate", str(tmp_path)])
    generated = tmp_path / ".claude" / "rules" / "coding.md"
    assert generated.exists()

    (tmp_path / ".agentpack" / "rules" / "coding.md").unlink()
    runner.invoke(app, ["generate", str(tmp_path)])

    assert not generated.exists()


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------


def test_generate_case_insensitive_skill_md(tmp_path):
    """_find_skill_md matches skill.md case-insensitively."""
    _init_with_rules(tmp_path)
    skill_dir = tmp_path / ".agentpack" / "skills" / "review"
    skill_dir.mkdir(parents=True)
    (skill_dir / "skill.md").write_text(
        "---\nname: review\ndescription: Review\n---\n\n# Review\n"
    )
    runner.invoke(app, ["generate", str(tmp_path)])
    assert (tmp_path / ".claude" / "skills" / "review" / "SKILL.md").exists()


def test_sync_stub():
    result = runner.invoke(app, ["sync"])
    assert result.exit_code == 0
