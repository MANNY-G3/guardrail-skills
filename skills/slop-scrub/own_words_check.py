#!/usr/bin/env python3
"""Count the words in an edited piece that the author did not type.

Usage: own_words_check.py RAW EDITED [--cap 5]
Exit 0 when the piece passes, 1 when it does not, 2 on bad input.
"""

import argparse
import functools
import re
import sys
from pathlib import Path

SHORTHAND = {"bc": "because", "idk": "i dont know", "u": "you", "ur": "your"}
NEGATIONS = {
    "not", "no", "never", "without", "nothing", "nobody", "none", "neither", "nor", "aint",
    "dont", "cant", "wont", "didnt", "doesnt", "isnt", "arent", "wasnt", "werent",
    "couldnt", "wouldnt", "shouldnt",
}
WORD = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)*")


def words(text):
    found = []
    for typed in WORD.findall(text.lower().replace("’", "'")):
        plain = typed.replace("'", "")
        found.extend(SHORTHAND.get(plain, plain).split())
    return found


def sentences(text):
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", text) if WORD.search(part.lower())]


def edit_distance(left, right):
    row = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        next_row = [i]
        for j, b in enumerate(right, 1):
            next_row.append(min(row[j] + 1, next_row[j - 1] + 1, row[j - 1] + (a != b)))
        row = next_row
    return row[-1]


@functools.lru_cache(maxsize=None)
def same_word(edited, typed):
    if edited == typed:
        return True
    # Numbers and negations carry the meaning, so a near miss there is a different word.
    if any(character.isdigit() for character in edited + typed) or edited in NEGATIONS or typed in NEGATIONS:
        return False
    # A fixed typo counts as the author's word; short words must match exactly.
    return min(len(edited), len(typed)) >= 4 and edit_distance(edited, typed) <= 2


def align(edited_words, source_words):
    """Return the edited words with no match and the (edited, source) positions that matched."""
    # Order matters: cutting words from a sentence keeps the rest in the author's order.
    rows, cols = len(edited_words), len(source_words)
    longest = [[0] * (cols + 1) for _ in range(rows + 1)]
    for i in range(rows - 1, -1, -1):
        for j in range(cols - 1, -1, -1):
            if same_word(edited_words[i], source_words[j]):
                longest[i][j] = longest[i + 1][j + 1] + 1
            else:
                longest[i][j] = max(longest[i + 1][j], longest[i][j + 1])
    left_over, kept, i, j = [], [], 0, 0
    while i < rows and j < cols:
        if same_word(edited_words[i], source_words[j]):
            kept.append((i, j))
            i, j = i + 1, j + 1
        elif longest[i + 1][j] >= longest[i][j + 1]:
            left_over.append(edited_words[i])
            i += 1
        else:
            j += 1
    return left_over + edited_words[i:], kept


def tightest_alignment(edited_words, source_words):
    """Align twice, from the front and from the back, and keep the match that spans less of the source."""
    # A kept tail clause can open with a word that also sits early in the author's sentence; matching from the back keeps that word from stretching the span.
    added, kept = align(edited_words, source_words)
    added_back, kept_back = align(edited_words[::-1], source_words[::-1])
    last_edited, last_source = len(edited_words) - 1, len(source_words) - 1
    kept_back = sorted((last_edited - i, last_source - j) for i, j in kept_back)

    def span(pairs):
        positions = [position for _, position in pairs]
        return max(positions) - min(positions) if positions else 0

    if span(kept_back) < span(kept):
        return added_back[::-1], kept_back
    return added, kept


def check(raw_text, edited_text):
    sources = [words(sentence) for sentence in sentences(raw_text)]
    rows = []
    for sentence in sentences(edited_text):
        edited_words = words(sentence)
        closest = sorted(sources, key=lambda source: len(align(edited_words, source)[0]))[:4]
        source = closest[0] if closest else []
        added, kept = align(edited_words, source)
        # A join of two of the author's sentences is allowed; a stray common word is not excused.
        joins = [first + second for first in closest for second in closest if first is not second]
        if joins:
            best_join = min(joins, key=lambda joined: len(align(edited_words, joined)[0]))
            join_added, join_kept = align(edited_words, best_join)
            if len(added) - len(join_added) >= 3:
                source, added, kept = best_join, join_added, join_kept
        added, kept = tightest_alignment(edited_words, source)
        written_by_editor = len(added) * 2 >= len(edited_words)
        if written_by_editor:
            added = list(edited_words)
        kept_positions = {position for _, position in kept}
        lost_negations = []
        if kept_positions and not written_by_editor:
            # A negation cut from between words that were kept can reverse what the author said.
            lost_negations = [
                source[position]
                for position in range(min(kept_positions), max(kept_positions) + 1)
                if source[position] in NEGATIONS and position not in kept_positions
            ]
        rows.append({
            "sentence": sentence,
            "count": len(edited_words),
            "added": added,
            "written_by_editor": written_by_editor,
            "lost_negations": lost_negations,
            "respelled": [(source[j], edited_words[i]) for i, j in kept if source[j] != edited_words[i]],
        })
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("raw", type=Path)
    parser.add_argument("edited", type=Path)
    parser.add_argument("--cap", type=float, default=5.0, help="most added words allowed, per 100 words")
    args = parser.parse_args()
    try:
        rows = check(args.raw.read_text(), args.edited.read_text())
    except OSError as error:
        print(f"Could not read a file: {error}. Check both paths and run again.", file=sys.stderr)
        return 2
    total = sum(row["count"] for row in rows)
    if not total:
        print("The edited file has no words in it. Give it the finished piece.", file=sys.stderr)
        return 2
    for row in rows:
        notes = []
        if row["written_by_editor"]:
            notes.append("NEW SENTENCE, not the author's")
        elif row["added"]:
            notes.append("added: " + ", ".join(row["added"]))
        if row["lost_negations"]:
            notes.append("CUT A NEGATION (" + ", ".join(row["lost_negations"]) + "), check the meaning")
        if row["respelled"]:
            notes.append("spelling changed: " + ", ".join(f"{typed} to {edited}" for typed, edited in row["respelled"]))
        summary = "; ".join(notes) or "all the author's words"
        print(f"{row['count']:3d} words | {summary} | {row['sentence'][:70]}")
    added = sum(len(row["added"]) for row in rows)
    share = 100 * added / total
    failures = []
    if share > args.cap:
        failures.append(f"over the cap of {args.cap:g} added words per 100")
    if any(row["written_by_editor"] for row in rows):
        failures.append("it holds a sentence the author did not write")
    if any(row["lost_negations"] for row in rows):
        failures.append("a negation was cut from inside a sentence")
    verdict = "PASS" if not failures else "FAIL: " + "; ".join(failures)
    print(f"\n{total} words, {added} added by the editor, {share:.1f} per 100 (cap {args.cap:g}): {verdict}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
