import builtins

from lexilab.cli import _assist


def test_assist_updates_from_feedback(monkeypatch, capsys) -> None:
    feedback = iter(["GYY..", "GGGGG"])
    monkeypatch.setattr(builtins, "input", lambda _: next(feedback))

    _assist(["cigar", "crane", "slate"], first_guess="crane", max_turns=6)

    output = capsys.readouterr().out
    assert "1. Try: crane" in output
    assert "crane -> GYY.. leaves 1 candidates" in output
    assert "2. Try: cigar" in output
    assert "Solved in 2 guesses." in output
