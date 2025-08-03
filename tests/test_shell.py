import typer
from typer.testing import CliRunner

from pilotcmd.cli import app


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
    ):
        calls.append(prompt)

    calls = []
    monkeypatch.setattr("pilotcmd.cli.PromptSession", DummySession)
    monkeypatch.setattr("pilotcmd.cli.run_command", fake_run_command)

    runner = CliRunner()
    result = runner.invoke(app, ["shell"])
    assert result.exit_code == 0
    assert calls == ["echo test"]
    history_file = tmp_path / ".pilotcmd" / "shell_history"
    assert history_file.exists()
    assert "echo test" in history_file.read_text()
