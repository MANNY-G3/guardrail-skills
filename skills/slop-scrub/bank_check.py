#!/usr/bin/env python3
"""Measure how much of a new piece is built from the author's own wording, for sentence-bank and carried-voice modes.

Usage: bank_check.py PIECE BANK_FILE [BANK_FILE ...] [--floor 60] [--run 3] [--most-from-one N] [--at-most N]
A word counts as the author's when it sits inside a run of RUN or more words found in a bank file.
After the sentence table it lists the lines carried over nearly whole, the sentences that mix the
author's wording with the editor's, and the share that comes from each bank file.
Sentence-bank mode wants the share high (--floor). Carried-voice mode wants it low (--at-most): that option
replaces the floor and leaves out the list of mixed sentences, because there a mix is what the mode asks for.
Exit 0 on a pass, 1 on a fail (under the floor, over --at-most, or one file over --most-from-one), 2 on bad input.
"""

import argparse
import re
import sys
from pathlib import Path

WORD = re.compile(r"(?:[a-z]\.){2,}|[$~]*\d+(?:[.,]\d+)+|[a-z0-9$~']+")
TITLE = re.compile(r"\b(?:mr|mrs|ms|dr)\.$", re.IGNORECASE)
MONTH = re.compile(r"\b(?:jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\.$", re.IGNORECASE)
INITIALS = re.compile(r"\b(?:[a-z]\.){2,}$", re.IGNORECASE)
NEARLY_WHOLE = 90
MIXED_LOW, MIXED_HIGH = 25, 70


def words(text):
    return WORD.findall(text.lower().replace("’", "'"))


def sentence_runs_on(previous, following):
    """True when the full stop that ends `previous` belongs to an abbreviation, as in "Feb. 21st" or "9 a.m. sharp"."""
    if TITLE.search(previous):
        return True
    if MONTH.search(previous):
        return following[:1].isdigit()
    if INITIALS.search(previous):
        return following[:1].islower() or following[:1].isdigit()
    return False


def sentences(text):
    out = []
    for line in text.splitlines():
        in_line = []
        for part in re.split(r"(?<=[.!?])\s+", line):
            part = part.strip()
            if not WORD.search(part.lower()):
                continue
            if in_line and sentence_runs_on(in_line[-1], part):
                in_line[-1] = f"{in_line[-1]} {part}"
            else:
                in_line.append(part)
        out.extend(in_line)
    return out


def runs_in(source_words, run):
    return {tuple(source_words[start:start + run]) for start in range(len(source_words) - run + 1)}


def covered_flags(piece_words, runs, run):
    flags = [False] * len(piece_words)
    for start in range(len(piece_words) - run + 1):
        if tuple(piece_words[start:start + run]) in runs:
            for position in range(start, start + run):
                flags[position] = True
    return flags


def per_100(flags):
    return 100 * sum(flags) / len(flags) if flags else 0.0


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("piece", type=Path)
    parser.add_argument("bank", type=Path, nargs="+")
    parser.add_argument("--floor", type=float, default=60.0, help="least share of the author's wording, per 100 words")
    parser.add_argument("--run", type=int, default=3, help="shortest run of words that counts as the author's")
    parser.add_argument("--most-from-one", type=float, default=None, help="most that any one bank file may supply, per 100 words")
    parser.add_argument("--at-most", type=float, default=None, help="carried-voice mode: most of the piece that may be the author's wording, per 100 words")
    args = parser.parse_args()
    try:
        piece_text = args.piece.read_text()
        bank_texts = [path.read_text() for path in args.bank]
    except OSError as error:
        print(f"Could not read a file: {error}. Check the paths and run again.", file=sys.stderr)
        return 2
    piece_sentences = sentences(piece_text)
    sentence_words = [words(sentence) for sentence in piece_sentences]
    piece_words = [word for group in sentence_words for word in group]
    if not piece_words:
        print("The piece has no words in it. Give it the finished piece.", file=sys.stderr)
        return 2
    runs_by_file = [runs_in(words(text), args.run) for text in bank_texts]
    runs = set().union(*runs_by_file)
    if not runs:
        print("The bank files hold too few words to match against. Give it the author's finished pieces.", file=sys.stderr)
        return 2
    whole_bank_sentences = {tuple(words(sentence)) for text in bank_texts for sentence in sentences(text)}

    flags = covered_flags(piece_words, runs, args.run)
    nearly_whole, mixed = [], []
    position = 0
    for sentence, group in zip(piece_sentences, sentence_words):
        span = slice(position, position + len(group))
        position += len(group)
        if len(group) < args.run and tuple(group) in whole_bank_sentences:
            flags[span] = [True] * len(group)
        alone = covered_flags(group, runs, args.run)
        if len(group) < args.run and tuple(group) in whole_bank_sentences:
            alone = [True] * len(group)
        share = per_100(alone)
        print(f"{share:5.0f}% author's | {sentence[:80]}")
        if share >= NEARLY_WHOLE and len(group) >= 5:
            nearly_whole.append(sentence)
        elif MIXED_LOW <= share < MIXED_HIGH and len(group) >= 6:
            mixed.append(sentence)

    if nearly_whole:
        print(f"\nCarried over nearly whole ({len(nearly_whole)}). A reader who knows the author will recognize these, so do not reuse them soon:")
        for sentence in nearly_whole:
            print(f"  - {sentence[:100]}")
    if mixed and args.at_most is None:
        print(f"\nSentences that are part the author's and part yours ({len(mixed)}). A swapped name or number is fine. A clause of yours written into their sentence is not: move it into a sentence of its own.")
        for sentence in mixed:
            print(f"  - {sentence[:100]}")
    over_cap = None
    if len(args.bank) > 1:
        print("\nBy bank file, per 100 words of the piece:")
        for path, file_runs in zip(args.bank, runs_by_file):
            from_file = per_100(covered_flags(piece_words, file_runs, args.run))
            print(f"  {from_file:5.1f}  {path.name}")
            if args.most_from_one is not None and from_file > args.most_from_one and over_cap is None:
                over_cap = (path.name, from_file)

    share = per_100(flags)
    if args.at_most is not None:
        limit = f"at most {args.at_most:g}"
        verdict = "PASS" if share <= args.at_most else f"FAIL: over the most allowed in carried-voice mode ({args.at_most:g})"
    elif share < args.floor:
        limit = f"floor {args.floor:g}"
        verdict = f"FAIL: under the floor of {args.floor:g}"
    elif over_cap:
        limit = f"floor {args.floor:g}"
        verdict = f"FAIL: {over_cap[0]} supplies {over_cap[1]:.1f} per 100, over the most allowed from one piece ({args.most_from_one:g})"
    else:
        limit = f"floor {args.floor:g}"
        verdict = "PASS"
    print(f"\n{len(piece_words)} words, {share:.1f} per 100 inside runs of {args.run} or more from the bank ({limit}): {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
