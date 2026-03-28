"""Integration tests — end-to-end workflows without external services."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from algitex import Project, Pipeline
from algitex.algo import Loop
from algitex.propact import Workflow
from algitex.tools.tickets import Tickets
from algitex.tools.analysis import HealthReport, Analyzer
from algitex.tools.proxy import Proxy, LLMResponse
from algitex.config import Config


class TestProjectWorkflow:
    """Full project lifecycle: analyze → plan → tickets → status."""

    def test_analyze_plan_status(self, tmp_path):
        p = Project(str(tmp_path))

        # Analyze (no tools installed → empty report with defaults)
        report = p.analyze(full=False)
        assert report.grade in ("A", "B", "C", "D")

        # Plan creates tickets from analysis
        plan = p.plan(sprints=1, auto_tickets=True)
        assert "tickets_created" in plan
        assert "summary" in plan

        # Status includes health + tickets + algo
        status = p.status()
        assert "health" in status
        assert "tickets" in status
        assert "algo" in status
        assert "cost_ledger" in status

    def test_add_ticket_and_board(self, tmp_path):
        p = Project(str(tmp_path))
        p.add_ticket("Feature A", priority="high", type="feature")
        p.add_ticket("Bug B", priority="critical", type="bug")
        p.add_ticket("Refactor C", priority="normal", type="refactor")

        status = p.status()
        assert status["tickets"]["open"] == 3

    def test_plan_generates_tickets_from_bad_report(self, tmp_path):
        p = Project(str(tmp_path))
        # Inject a bad report
        p._last_report = HealthReport(
            project_path=str(tmp_path),
            cc_avg=6.0,
            vallm_pass_rate=0.50,
            god_modules=["cli.py", "core.py", "utils.py"],
            god_functions=["main", "_dispatch", "_process", "_handle"],
            dup_groups=5,
            dup_lines=800,
        )
        plan = p.plan()
        # Should create tickets for: 3 god modules + 4 god functions + 1 dup + 1 vallm
        assert plan["tickets_created"] >= 8

    def test_cost_ledger_accumulates(self, tmp_path):
        p = Project(str(tmp_path))
        p.add_ticket("T1", meta={"cost_usd": 0.05})
        p.add_ticket("T2", meta={"cost_usd": 0.10})
        p.add_ticket("T3", meta={"cost_usd": 0.02})

        status = p.status()
        assert abs(status["cost_ledger"]["total_spent_usd"] - 0.17) < 0.001


class TestAlgoFullCycle:
    """Full algo loop: discover → traces → extract → report."""

    def test_full_algo_cycle(self, tmp_path):
        loop = Loop(str(tmp_path))

        # Stage 1: discover
        loop.discover()
        assert loop._state.stage >= 1

        # Add traces with patterns
        for _ in range(10):
            loop.add_trace("What is Python?", "Python is a language...", cost_usd=0.01)
        for _ in range(7):
            loop.add_trace("Format this JSON", '{"ok": true}', cost_usd=0.005)
        for i in range(3):
            loop.add_trace(f"Unique question {i}", f"Answer {i}", cost_usd=0.03)

        assert loop._state.total_requests == 20
        assert loop._state.total_cost_usd == pytest.approx(0.01 * 10 + 0.005 * 7 + 0.03 * 3)

        # Stage 2: extract
        patterns = loop.extract(min_frequency=5)
        assert len(patterns) >= 2
        assert patterns[0].frequency == 10  # "What is Python?" most frequent

        # Stage 3: generate rules (no LLM)
        rules = loop.generate_rules(use_llm=False)
        assert len(rules) >= 1

        # Report
        report = loop.report()
        assert report["patterns_found"] >= 2
        assert report["total_cost_usd"] > 0

    def test_pattern_ordering_by_savings(self, tmp_path):
        loop = Loop(str(tmp_path))

        # Pattern A: frequent but cheap (10 × $0.001 = $0.01)
        for _ in range(10):
            loop.add_trace("Cheap repeat", "Reply", cost_usd=0.001)
        # Pattern B: less frequent but expensive (5 × $0.10 = $0.50)
        for _ in range(5):
            loop.add_trace("Expensive repeat", "Reply", cost_usd=0.10)

        patterns = loop.extract(min_frequency=3)
        # Pattern B should rank first (higher total savings)
        assert patterns[0].avg_cost_usd > patterns[1].avg_cost_usd

    def test_min_frequency_filter(self, tmp_path):
        loop = Loop(str(tmp_path))
        for _ in range(4):
            loop.add_trace("Semi-frequent", "Reply", cost_usd=0.01)

        assert len(loop.extract(min_frequency=5)) == 0
        assert len(loop.extract(min_frequency=4)) == 1
        assert len(loop.extract(min_frequency=3)) == 1


class TestPropactWorkflowIntegration:
    """Multi-step workflow execution."""

    def test_multi_step_workflow(self, tmp_path):
        wf_file = tmp_path / "multi.md"
        wf_file.write_text("""# Multi-step

## Create file

```propact:shell
echo "hello" > /tmp/algitex-test-output.txt
```

## Read file

```propact:shell
cat /tmp/algitex-test-output.txt
```

## Clean up

```propact:shell
rm -f /tmp/algitex-test-output.txt
```
""")
        wf = Workflow(str(wf_file))
        result = wf.execute()
        assert result.success
        assert result.steps_done == 3
        assert result.steps_failed == 0
        assert "hello" in result.steps[1].result

    def test_stop_on_error(self, tmp_path):
        wf_file = tmp_path / "fail.md"
        wf_file.write_text("""# Fail test

## This fails

```propact:shell
exit 1
```

## This should be skipped

```propact:shell
echo "should not run"
```
""")
        wf = Workflow(str(wf_file))
        result = wf.execute(stop_on_error=True)
        assert not result.success
        assert result.steps_failed == 1
        assert result.steps[1].status == "skipped"

    def test_continue_on_error(self, tmp_path):
        wf_file = tmp_path / "continue.md"
        wf_file.write_text("""# Continue test

## Fails

```propact:shell
exit 1
```

## Still runs

```propact:shell
echo "I ran"
```
""")
        wf = Workflow(str(wf_file))
        result = wf.execute(stop_on_error=False)
        assert result.steps_failed == 1
        assert result.steps_done == 1
        assert "I ran" in result.steps[1].result

    def test_elapsed_time_tracked(self, tmp_path):
        wf_file = tmp_path / "timed.md"
        wf_file.write_text("""# Timed
```propact:shell
sleep 0.1
```
""")
        wf = Workflow(str(wf_file))
        result = wf.execute()
        assert result.steps[0].elapsed_ms >= 50  # at least 50ms
        assert result.total_elapsed_ms >= 50

    def test_workflow_title_extraction(self, tmp_path):
        wf_file = tmp_path / "titled.md"
        wf_file.write_text("# My Awesome Workflow\n```propact:shell\necho ok\n```\n")
        wf = Workflow(str(wf_file))
        wf.parse()
        status = wf.status()
        assert status["title"] == "My Awesome Workflow"


class TestPipelineIntegration:
    """Pipeline composable steps."""

    def test_analyze_and_report(self, tmp_path):
        result = (
            Pipeline(str(tmp_path))
            .analyze(full=False)
            .report()
        )
        assert len(result["steps"]) == 1
        assert result["steps"][0]["step"] == "analyze"

    def test_full_pipeline_dry(self, tmp_path):
        pipeline = Pipeline(str(tmp_path))
        pipeline.analyze(full=False)
        pipeline.create_tickets()
        result = pipeline.report()
        assert len(result["steps"]) == 2

    def test_pipeline_preserves_state(self, tmp_path):
        pipeline = Pipeline(str(tmp_path))
        pipeline.analyze(full=False)
        pipeline.create_tickets()
        result = pipeline.report()
        assert "analysis" in result["results"]


class TestProxyMock:
    """Proxy with mocked HTTP calls."""

    def test_proxy_planfile_headers(self):
        """Verify planfile-aware headers are sent."""
        proxy = Proxy()
        # We can't call without a server, but we can verify the method signature
        import inspect
        sig = inspect.signature(proxy.ask)
        params = list(sig.parameters.keys())
        assert "planfile_ref" in params
        assert "workflow_ref" in params
        proxy.close()

    def test_llm_response_dataclass(self):
        resp = LLMResponse(
            content="Hello",
            model="haiku",
            tier="cheap",
            cost_usd=0.001,
            elapsed_ms=150.0,
        )
        assert str(resp) == "Hello"
        assert resp.model == "haiku"

    def test_proxy_health_offline(self):
        """Proxy.health() returns False when proxym isn't running."""
        proxy = Proxy()
        assert proxy.health() is False
        proxy.close()

    def test_proxy_budget_offline(self):
        proxy = Proxy()
        budget = proxy.budget()
        assert "error" in budget
        proxy.close()


class TestConfigIntegration:
    def test_full_config_load_save_roundtrip(self, tmp_path):
        cfg = Config()
        cfg.proxy.default_tier = "premium"
        cfg.proxy.budget_daily_usd = 5.0
        cfg.tickets.backend = "github"
        cfg.analysis.cc_target = 2.5
        cfg.analysis.formats = ["toon", "evolution", "flow"]

        path = cfg.save(str(tmp_path / "algitex.yaml"))

        import yaml
        data = yaml.safe_load(path.read_text())
        assert data["proxy"]["default_tier"] == "premium"
        assert data["proxy"]["budget_daily_usd"] == 5.0
        assert data["tickets"]["backend"] == "github"
        assert data["analysis"]["cc_target"] == 2.5
        assert "flow" in data["analysis"]["formats"]


class TestTicketsEdgeCases:
    def test_empty_board(self, tmp_path):
        t = Tickets(str(tmp_path))
        board = t.board()
        assert all(len(v) == 0 for v in board.values())

    def test_update_nonexistent(self, tmp_path):
        t = Tickets(str(tmp_path))
        result = t.update("DLP-9999", status="done")
        assert result is None

    def test_sequential_ids(self, tmp_path):
        t = Tickets(str(tmp_path))
        for i in range(5):
            ticket = t.add(f"Task {i}")
            assert ticket.id == f"DLP-{i+1:04d}"

    def test_ticket_tags(self, tmp_path):
        t = Tickets(str(tmp_path))
        ticket = t.add("Tagged task", tags=["frontend", "urgent"])
        assert ticket.tags == ["frontend", "urgent"]

    def test_ticket_meta_persists(self, tmp_path):
        t = Tickets(str(tmp_path))
        t.add("With meta", meta={"model": "opus", "cost_usd": 0.15})

        t2 = Tickets(str(tmp_path))
        loaded = t2.list()[0]
        assert loaded.meta["model"] == "opus"
        assert loaded.meta["cost_usd"] == 0.15
