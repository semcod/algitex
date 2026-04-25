"""Tests for algitex CLI commands."""

import json
import pytest
from click.testing import CliRunner

from algitex.cli import app

runner = CliRunner()


class TestCLIBasic:
    def test_help(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Progressive algorithmization" in result.stdout

    def test_tools(self):
        result = runner.invoke(app, ["tools"])
        assert result.exit_code == 0
        assert "proxym" in result.stdout
        assert "vallm" in result.stdout
        assert "code2llm" in result.stdout

    def test_init(self, tmp_path):
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        assert "algitex initialized" in result.stdout
        assert (tmp_path / "algitex.yaml").exists()
        assert (tmp_path / ".algitex").is_dir()

    def test_init_creates_yaml(self, tmp_path):
        runner.invoke(app, ["init", str(tmp_path)])
        import yaml
        data = yaml.safe_load((tmp_path / "algitex.yaml").read_text())
        assert "proxy" in data
        assert "tickets" in data
        assert "analysis" in data


class TestCLITickets:
    def test_ticket_add(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["ticket", "add", "Fix the router"])
        assert result.exit_code == 0
        assert "DLP-0001" in result.stdout

    def test_ticket_add_with_priority(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, [
            "ticket", "add", "Critical bug",
            "--priority", "critical",
            "--type", "bug",
        ])
        assert result.exit_code == 0
        assert "DLP-0001" in result.stdout

    def test_ticket_list_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["ticket", "list"])
        assert result.exit_code == 0
        assert "No tickets" in result.stdout

    def test_ticket_list_with_data(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner.invoke(app, ["ticket", "add", "Task one"])
        runner.invoke(app, ["ticket", "add", "Task two"])
        result = runner.invoke(app, ["ticket", "list"])
        assert result.exit_code == 0
        assert "DLP-0001" in result.stdout
        assert "DLP-0002" in result.stdout

    def test_ticket_board(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner.invoke(app, ["ticket", "add", "Open task"])
        result = runner.invoke(app, ["ticket", "board"])
        assert result.exit_code == 0
        assert "OPEN" in result.stdout


class TestCLIAlgo:
    def test_algo_help(self):
        result = runner.invoke(app, ["algo", "--help"])
        assert result.exit_code == 0
        assert "discover" in result.stdout
        assert "extract" in result.stdout
        assert "rules" in result.stdout
        assert "report" in result.stdout

    def test_algo_discover(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["algo", "discover", "--path", str(tmp_path)])
        assert result.exit_code == 0
        assert "Discovery mode active" in result.stdout

    def test_algo_extract_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["algo", "extract", "--path", str(tmp_path)])
        assert result.exit_code == 0
        assert "No patterns found" in result.stdout

    def test_algo_report(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["algo", "report", "--path", str(tmp_path)])
        assert result.exit_code == 0
        assert "stage" in result.stdout.lower()


class TestCLIWorkflow:
    def test_workflow_help(self):
        result = runner.invoke(app, ["workflow", "--help"])
        assert result.exit_code == 0
        assert "run" in result.stdout
        assert "validate" in result.stdout

    def test_workflow_validate_good(self, tmp_path):
        wf = tmp_path / "good.md"
        wf.write_text("# Test\n```propact:shell\necho hi\n```\n")
        result = runner.invoke(app, ["workflow", "validate", str(wf)])
        assert result.exit_code == 0
        assert "Valid" in result.stdout

    def test_workflow_validate_bad(self, tmp_path):
        wf = tmp_path / "bad.md"
        wf.write_text("# Test\n```propact:rest\n\n```\n")
        result = runner.invoke(app, ["workflow", "validate", str(wf)])
        assert result.exit_code == 0
        assert "error" in result.stdout.lower()

    def test_workflow_run_shell(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        wf = tmp_path / "run.md"
        wf.write_text("# Run\n```propact:shell\necho hello\n```\n")
        result = runner.invoke(app, ["workflow", "run", str(wf)])
        assert result.exit_code == 0
        assert "complete" in result.stdout.lower()

    def test_workflow_run_dry(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        wf = tmp_path / "dry.md"
        wf.write_text("# Dry\n```propact:shell\nrm -rf /\n```\n")
        result = runner.invoke(app, ["workflow", "run", str(wf), "--dry-run"])
        assert result.exit_code == 0


class TestCLIAnalyze:
    def test_analyze(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["analyze", "--path", str(tmp_path), "--quick"])
        assert result.exit_code == 0
        assert "Health Report" in result.stdout

    def test_plan(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["plan", "--path", str(tmp_path)])
        assert result.exit_code == 0
        assert "Sprint Plan" in result.stdout
