#!/usr/bin/env python3
"""Measure how much of a new piece is built from the author's own wording, for sentence-bank mode.

Usage: bank_check.py PIECE BANK_FILE [BANK_FILE ...] [--floor 60] [--run 3]
A word counts as the author's when it sits inside a run of RUN or more words found in a bank file.
Exit 0 when the share is at or over the floor, 1 when it is under, 2 on bad input.
"""

import argparse
import re
import sys
from pathlib import Path

WORD = re.compile(r"[a-z0-9$~']+")


def words(text):
    return WORD.findall(text.lower().replace("’", "'"))


def sentences(text):
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", text) if WORD.search(part.lower())]


def covered_flags(piece_words, runs, run):
    flags = [False] * len(piece_words)
    for start in range(len(piece_words) - run + 1):
        if tuple(piece_words[start:start + run]) in runs:
            for position in range(start, start + run):
                flags[position] = True
    return flags


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("piece", type=Path)
    parser.add_argument("bank", type=Path, nargs="+")
    parser.add_argument("--floor", type=float, default=60.0, help="least share of the author's wording, per 100 words")
    parser.add_argument("--run", type=int, default=3, help="shortest run of words that counts as the author's")
    args = parser.parse_args()
    try:
        piece_text = args.piece.read_text()
        bank_words = [words(path.read_text()) for path in args.bank]
    except OSError as error:
        print(f"Could not read a file: {error}. Check the paths and run again.", file=sys.stderr)
        return 2
    piece_words = words(piece_text)
    if not piece_words:
        print("The piece has no words in it. Give it the finished piece.", file=sys.stderr)
        return 2
    runs = set()
    for source in bank_words:
        runs.update(tuple(source[start:start + args.run]) for start in range(len(source) - args.run + 1))
    if not runs:
        print("The bank files hold too few words to match against. Give it the author's finished pieces.", file=sys.stderr)
        return 2

    for sentence in sentences(piece_text):
        sentence_words = words(sentence)
        flags = covered_flags(sentence_words, runs, args.run)
        share = 100 * sum(flags) / len(sentence_words)
        print(f"{share:5.0f}% author's | {sentence[:80]}")
    flags = covered_flags(piece_words, runs, args.run)
    share = 100 * sum(flags) / len(piece_words)
    verdict = "PASS" if share >= args.floor else f"FAIL: under the floor of {args.floor:g}"
    print(f"\n{len(piece_words)} words, {share:.1f} per 100 inside runs of {args.run} or more from the bank (floor {args.floor:g}): {verdict}")
    return 0 if share >= args.floor else 1


if __name__ == "__main__":
    sys.exit(main())
