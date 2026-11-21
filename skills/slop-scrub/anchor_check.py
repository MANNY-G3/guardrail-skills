#!/usr/bin/env python3
"""Count how much of a finished piece is the author's own words, for anchor mode.

Usage: anchor_check.py RAW PIECE [--cap 25]
New sentences are allowed in this mode. They count in full against the cap.
Exit 0 when the piece passes, 1 when it does not, 2 on bad input.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from own_words_check import check  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("raw", type=Path)
    parser.add_argument("piece", type=Path)
    parser.add_argument("--cap", type=float, default=25.0, help="most words of the editor's allowed, per 100 words")
    args = parser.parse_args()
    try:
        rows = check(args.raw.read_text(), args.piece.read_text())
    except OSError as error:
        print(f"Could not read a file: {error}. Check both paths and run again.", file=sys.stderr)
        return 2
    total = sum(row["count"] for row in rows)
    if not total:
        print("The piece has no words in it. Give it the finished piece.", file=sys.stderr)
        return 2
    for row in rows:
        if row["written_by_editor"]:
            note = "YOURS, whole sentence"
        elif row["added"]:
            note = "author's, you added: " + ", ".join(row["added"])
        else:
            note = "author's"
        if row["lost_negations"]:
            note += "; CUT A NEGATION (" + ", ".join(row["lost_negations"]) + "), check the meaning"
        print(f"{row['count']:3d} words | {note} | {row['sentence'][:70]}")
    added = sum(len(row["added"]) for row in rows)
    share = 100 * added / total
    failures = []
    if share > args.cap:
        failures.append(f"your share is over the cap of {args.cap:g} per 100")
    if any(row["lost_negations"] for row in rows):
        failures.append("a negation was cut from inside a kept sentence")
    edges_yours = sum(1 for row in (rows[0], rows[-1]) if row["written_by_editor"])
    verdict = "PASS" if not failures else "FAIL: " + "; ".join(failures)
    print(f"\n{total} words, {added} yours, {share:.1f} per 100 (cap {args.cap:g}); first or last sentence yours: {edges_yours} of 2: {verdict}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
