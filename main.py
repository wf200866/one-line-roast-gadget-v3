"""Single-entry publisher for the printer roast.

Concept: the printer disconnects the second you ask it to print, only to
turn around and hand you a flawless alignment page -- its tidy way of
saying the device is blameless and the operator is the bug.

Kept deliberately small: one canonical quip, a guard on its shape, and a
crash-safe write to /output/entry.txt (staging file, then rename).
"""

from __future__ import annotations

import os
import tempfile

JOKE = "My home printer goes offline the instant I hit print, then prints a flawless test page to prove the problem is me."

OUTPUT_DIR = "/output"
OUTPUT_NAME = "entry.txt"
LOW_BOUND = 1
HIGH_BOUND = 200


def _check_entry(entry: str) -> str:
    """Confirm the entry is a usable string and return it unchanged."""
    if not isinstance(entry, str) or not entry.strip():
        raise ValueError("entry must be a non-blank string")
    size = len(entry)
    if size < LOW_BOUND or size > HIGH_BOUND:
        raise ValueError(
            f"entry length {size} outside allowed range "
            f"{LOW_BOUND}..{HIGH_BOUND}"
        )
    return entry


def _ensure_output_dir(directory: str) -> None:
    """Create *directory* if needed and make it traversable."""
    os.makedirs(directory, exist_ok=True)
    os.chmod(directory, 0o755)


def _commit_atomically(destination: str, payload: str) -> None:
    """Stage *payload* next to *destination*, then swap it into place."""
    directory = os.path.dirname(destination) or "."
    fd, staged = tempfile.mkstemp(dir=directory, prefix=".entry-", suffix=".part")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as writer:
            writer.write(payload)
        os.chmod(staged, 0o644)
        os.replace(staged, destination)
        os.chmod(destination, 0o644)
    except BaseException:
        if os.path.exists(staged):
            os.unlink(staged)
        raise


def main() -> None:
    payload = _check_entry(JOKE)
    _ensure_output_dir(OUTPUT_DIR)
    target = os.path.join(OUTPUT_DIR, OUTPUT_NAME)
    _commit_atomically(target, payload)
    print(f"stored {len(payload)} chars in {target}")


if __name__ == "__main__":
    main()
