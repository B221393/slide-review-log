import pytest

from slide_review_log.__main__ import build_parser, main


def test_parser_prog():
    assert build_parser().prog == "slide-review-log"


def test_help_exits():
    with pytest.raises(SystemExit) as exit_info:
        main(["--help"])
    assert exit_info.value.code == 0


def test_feedback_carries_across_revisions(tmp_path, capsys):
    db = ["--db", str(tmp_path / "review.sqlite3")]
    assert main(db + [
        "add", "--deck", "demo", "--version", "v1", "--slide", "4",
        "--date", "2026-01-10", "Add units",
    ]) == 0
    assert capsys.readouterr().out == "Added #1\n"
    assert main(db + ["list", "--deck", "other"]) == 0
    assert capsys.readouterr().out == ""
    assert main(db + ["list", "--deck", "demo"]) == 0
    assert capsys.readouterr().out == "#1 2026-01-10 v1 p4 [open] Add units\n"
    assert main(db + ["resolve", "1", "--version", "v2"]) == 0
    assert capsys.readouterr().out == "Resolved #1 in v2\n"
    assert main(db + ["list", "--deck", "demo"]) == 0
    assert capsys.readouterr().out == ""
    assert main(db + ["list", "--deck", "demo", "--all"]) == 0
    assert capsys.readouterr().out == "#1 2026-01-10 v1 p4 [resolved in v2] Add units\n"
