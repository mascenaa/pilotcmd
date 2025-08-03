import typer
from typer.testing import CliRunner

from pilotcmd.cli import app, run_command


def test_shell_creates_history(monkeypatch, tmp_path):
    # Redirect HOME to temporary directory
    monkeypatch.setenv("HOME", str(tmp_path))

    prompts = iter(["echo test", "quit"])

    class DummySession:
        def __init__(self, *args, history=None, **kwargs):
            self.history = history

        def prompt(self, *args, **kwargs):
            try:
                text = next(prompts)
            except StopIteration:
                raise EOFError()
            if self.history is not None:
                self.history.append_string(text)
            return text

    def fake_run_command(
        ctx,
        prompt,
        model=None,
        dry_run=False,
        auto_run=False,
        verbose=False,
        thinking=False,
        allowed_commands=None,
        blocked_commands=None,
    ):
        calls.append(prompt)

    calls = []
    monkeypatch.setattr("pilotcmd.cli.PromptSession", DummySession)
    monkeypatch.setattr("pilotcmd.cli.run_command", fake_run_command)

    runner = CliRunner()
    result = runner.invoke(app, ["shell", "--mode", "restricted"])
    assert result.exit_code == 0
    assert calls == ["echo test"]
    history_file = tmp_path / ".pilotcmd" / "shell_history"
    assert history_file.exists()
    assert "echo test" in history_file.read_text()


def test_restricted_mode_blocks_command(monkeypatch, capsys):
    """Ensure restricted mode prevents dangerous commands."""
    from pilotcmd.os_utils.detector import OSInfo, OSType
    from pilotcmd.nlp.parser import Command, SafetyLevel

    # Stub OS detection
    class DummyOSDetector:
        def detect(self):
            return OSInfo(
                type=OSType.LINUX,
                name="Linux",
                version="1",
                architecture="x86",
                shell="bash",
            )

    # Stub components to avoid external calls
    class DummyModelFactory:
        def get_model(self, *args, **kwargs):
            raise RuntimeError("no model")

    class DummyContextManager:
        def save_prompt(self, *args, **kwargs):
            pass

        def save_execution_results(self, *args, **kwargs):
            pass

    class DummyParser:
        last_usage = None

        def __init__(self, os_info):
            pass

        async def parse(self, prompt):
            return [
                Command(
                    command="rm -rf /",
                    explanation="",
                    safety_level=SafetyLevel.SAFE,
                    requires_sudo=False,
                    revert=None,
                )
            ]

    monkeypatch.setattr("pilotcmd.cli.OSDetector", DummyOSDetector)
    monkeypatch.setattr("pilotcmd.cli.ModelFactory", DummyModelFactory)
    monkeypatch.setattr("pilotcmd.cli.ContextManager", DummyContextManager)
    monkeypatch.setattr("pilotcmd.cli.SimpleParser", DummyParser)

    class DummyCtx:
        obj = {}

    ctx = DummyCtx()

    run_command(
        ctx,
        "remove root",
        allowed_commands=["ls", "cat"],
        blocked_commands=["rm"],
    )
    out = capsys.readouterr().out
    assert "not permitted" in out
