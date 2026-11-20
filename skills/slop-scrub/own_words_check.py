#!/usr/bin/env python3
"""Count the words in an edited piece that the author did not type.

Usage: own_words_check.py RAW EDITED [--cap 5]
Exit 0 when the share of added words is at or under the cap, 1 when over, 2 on bad input.
"""

import argparse
import functools
import re
import sys
from pathlib import Path

SHORTHAND = {"bc": "because", "idk": "i dont know", "u": "you", "ur": "your"}
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
    # A fixed typo counts as the author's word; short words must match exactly.
    return min(len(edited), len(typed)) >= 4 and edit_distance(edited, typed) <= 2


def unmatched(edited_words, source_words):
    # Order matters: cutting words from a sentence keeps the rest in the author's order.
    rows, cols = len(edited_words), len(source_words)
    longest = [[0] * (cols + 1) for _ in range(rows + 1)]
    for i in range(rows - 1, -1, -1):
        for j in range(cols - 1, -1, -1):
            if same_word(edited_words[i], source_words[j]):
                longest[i][j] = longest[i + 1][j + 1] + 1
            else:
                longest[i][j] = max(longest[i + 1][j], longest[i][j + 1])
    left_over, i, j = [], 0, 0
    while i < rows and j < cols:
        if same_word(edited_words[i], source_words[j]):
            i, j = i + 1, j + 1
        elif longest[i + 1][j] >= longest[i][j + 1]:
            left_over.append(edited_words[i])
            i += 1
        else:
            j += 1
    return left_over + edited_words[i:]


def check(raw_text, edited_text):
    sources = [words(sentence) for sentence in sentences(raw_text)]
    rows = []
    for sentence in sentences(edited_text):
        edited_words = words(sentence)
        closest = sorted(sources, key=lambda source: len(unmatched(edited_words, source)))[:4]
        left_over = unmatched(edited_words, closest[0]) if closest else edited_words
        # A join of two of the author's sentences is allowed; a stray common word is not excused.
        joins = [unmatched(edited_words, first + second) for first in closest for second in closest if first is not second]
        best_join = min(joins, key=len, default=left_over)
        if len(left_over) - len(best_join) >= 3:
            left_over = best_join
        rows.append((sentence, len(edited_words), left_over))
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
    total = sum(count for _, count, _ in rows)
    added = sum(len(left_over) for _, _, left_over in rows)
    if not total:
        print("The edited file has no words in it. Give it the finished piece.", file=sys.stderr)
        return 2
    for sentence, count, left_over in rows:
        note = "all the author's words" if not left_over else "added: " + ", ".join(left_over)
        print(f"{count:3d} words | {note} | {sentence[:70]}")
    share = 100 * added / total
    verdict = "PASS" if share <= args.cap else "OVER THE CAP"
    print(f"\n{total} words, {added} added by the editor, {share:.1f} per 100 (cap {args.cap:g}): {verdict}")
    return 0 if share <= args.cap else 1


if __name__ == "__main__":
    sys.exit(main())
