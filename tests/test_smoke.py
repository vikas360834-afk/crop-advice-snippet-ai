"""Integration tests for the JSON-backed store and command-line startup."""

from app.storage import Store


def test_json_store_round_trips_values_and_defaults(tmp_path):
    store = Store(str(tmp_path / "app.json"))
    store.put("hello", {"n": 1})
    assert store.get("hello") == {"n": 1}
    assert store.get("missing", "fallback") == "fallback"
    assert store.all() == {"hello": {"n": 1}}


def test_cli_hello_command_runs(capsys):
    from app.cli import main

    main(["hello"])
    assert "is ready" in capsys.readouterr().out
