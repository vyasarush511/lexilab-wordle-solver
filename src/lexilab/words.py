from __future__ import annotations

from importlib import resources

from lexilab.feedback import validate_word


DEFAULT_WORD_LIST = "allowed_words.txt"


def _load_packaged_words(filename: str = DEFAULT_WORD_LIST) -> list[str]:
    data_file = resources.files("lexilab").joinpath("data", filename)
    return data_file.read_text(encoding="utf-8").splitlines()


def load_words(path: str | None = None) -> list[str]:
    if path is None:
        raw_words = _load_packaged_words()
    else:
        with open(path, encoding="utf-8") as word_file:
            raw_words = word_file.readlines()

    words: list[str] = []
    seen: set[str] = set()
    for line in raw_words:
        stripped = line.strip().lower()
        if not stripped or stripped.startswith("#"):
            continue
        word = validate_word(stripped)
        if word in seen:
            continue
        seen.add(word)
        words.append(word)
    return words
