from typer.testing import CliRunner

from pilotcmd.cli import app


def test_explain_shows_revert(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))

    runner = CliRunner()
    result = runner.invoke(app, ["explain", "create directory"])
    assert result.exit_code == 0
    assert "Revert:" in result.stdout
