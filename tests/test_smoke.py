"""Project-specific CLI integration tests."""

import json

import pytest

from app.cli import main


def test_cli_help_lists_crop_and_agricultural_commands(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    output = capsys.readouterr().out
    assert "advice" in output
    assert "crops" in output
    assert "records" in output
    assert "weather" in output
    assert "feedback" in output


def test_feedback_command_persists_structured_jsonl(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)

    main(["feedback", "--crop", "Wheat", "--rating", "5", "--comment", "Useful field guidance"])

    assert "Recorded 5-star feedback" in capsys.readouterr().out
    feedback_path = tmp_path / "data" / "farmer_feedback.jsonl"
    rows = [json.loads(line) for line in feedback_path.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1
    assert rows[0]["crop"] == "Wheat"
    assert rows[0]["rating"] == 5
    assert rows[0]["comment"] == "Useful field guidance"
