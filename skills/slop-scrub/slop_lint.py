#!/usr/bin/env python3
"""Find mechanical checklist matches in UTF-8 prose. Context still needs an editor."""

import argparse
import json
from pathlib import Path
import re
import sys


SKILL = Path(__file__).with_name("SKILL.md")
WORD = re.compile(r"\b[\w]+(?:['’][\w]+)*\b")
FLAGS = re.I
PATTERNS = (
    (10, "kill", "fancy-dash", r"[—–]"),
    (2, "kill", "negative-parallel", r"\b(?:not\s+(?:just|only)\b[^.!?\n]{1,100}\bbut\b(?:\s+also\b)?|(?:it|this|that)(?:\s+(?:is\s+not|isn['’]t)|['’]s\s+not)\b[^.!?\n]{1,100}[,.;]\s*(?:it|this|that)(?:\s+is\b|['’]s\b))"),
    (2, "strong", "no-no-just", r"\bno\s+[^.!?\n]{1,50}[.!]\s*no\s+[^.!?\n]{1,50}[.!]\s*just\b"),
    (2, "strong", "self-question", r"\bwhat\s+does\s+that\s+mean\?\s*(?:it|that)\s+means\b"),
    (2, "strong", "preloaded-transition", r"\b(?:here['’]s\s+the\s+thing|but\s+here['’]s\s+the\s+kicker|what['’]s\s+interesting\s+is)\s*:"),
    (2, "review", "three-part-list", r"\b[\w-]+(?:\s+[\w-]+){0,2},\s+[\w-]+(?:\s+[\w-]+){0,2},?\s+and\s+[\w-]+\b"),
    (2, "review", "dismissive-with", r"\ban?\s+[\w-]+\s+with\s+(?:a\s+)?[\w-]+\s+and\s+(?:a\s+)?[\w-]+\b"),
    (3, "strong", "drumroll", r"\b(?:here['’]s\s+(?:the\s+wildest\s+part|why\s+this\s+matters)|what\s+most\s+people\s+don['’]t\s+realize|the\s+(?:best\s+thing\s+about\s+this|crazy\s+thing\s+is))\s*:"),
    (2, "strong", "dressed-up-verb", r"\b(?:serves|stands|acts|functions)\s+as\b|\bboasts\s+(?:a|an|the|\d+)\b|\bfeatures\s+(?:a|an|the|\d+)\b|\brepresents\s+(?:a|an|the)\b"),
    (11, "review", "unnamed-authority", r"\b(?:experts\s+(?:say|argue)|studies\s+show|research\s+suggests|many\s+believe)\b"),
    (14, "strong", "unneeded-caveat", r"\b(?:it\s+is\s+(?:important\s+to\s+note|worth\s+mentioning)|while\s+results\s+may\s+vary)\b"),
    (14, "kill", "assistant-residue", r"\b(?:as\s+an\s+AI\b|I\s+hope\s+this\s+helps\b|great\s+question\b|certainly\s*[,!:]|let\s+me\s+know\s+if\s+you\s+would\s+like\b|here\s+is\s+a\s+revised\s+version\b)"),
)


def banned_words(skill=SKILL):
    """Read item 1, stripping its contextual annotations without duplicating the list."""
    source = Path(skill).read_text(encoding="utf-8")
    item = re.search(r"^### 1\. .*?\n(.*?)(?=^### 2\.)", source, re.M | re.S)
    if not item:
        raise ValueError("SKILL.md is missing checklist item 1")
    words = re.search(r"\*\*Banned words:\*\*\s*\n([^\n]+)", item[1])
    if not words:
        raise ValueError("SKILL.md item 1 is missing its banned-word list")
    return [re.sub(r"\s*\([^)]*\)", "", word).strip().rstrip(".")
            for word in words[1].split(",") if word.strip()]


def sentence_spans(text):
    return [(m.start(), m.end(), m.group())
            for m in re.finditer(r"[^.!?\n]+(?:[.!?]+|$)", text) if WORD.search(m.group())]


def named_source(text, start, end):
    left = max(text.rfind(mark, 0, start) for mark in ".!?\n") + 1
    right = min((p for mark in ".!?\n" if (p := text.find(mark, end)) >= 0),
                default=len(text))
    sentence = text[left:right]
    return bool(re.search(
        r"https?://|\b(?:according to|by|from|at)\s+[A-Z][\w-]+|"
        r"\b[A-Z]{2,}\s+(?:studies|research)|\([A-Z][\w-]+,?\s+\d{4}\)",
        sentence,
    ))


def lint(text, skill=SKILL):
    """Return item, severity, pattern, line, column and text for each potential match."""
    findings = []

    def add(item, severity, pattern, start, end):
        findings.append({"item": item, "severity": severity, "pattern": pattern,
                         "line": text.count("\n", 0, start) + 1,
                         "column": start - text.rfind("\n", 0, start),
                         "text": text[start:end].strip()})

    normalized = text.replace("’", "'")
    for word in banned_words(skill):
        expression = r"(?<!\w)" + r"\s+".join(re.escape(w) for w in word.split()) + r"(?!\w)"
        for match in re.finditer(expression, normalized, FLAGS):
            add(1, "kill", "banned-word", *match.span())
    for item, severity, name, expression in PATTERNS:
        for match in re.finditer(expression, text, FLAGS):
            if name == "unnamed-authority" and named_source(text, *match.span()):
                continue
            add(item, severity, name, *match.span())

    paragraphs = re.finditer(r"\S[^\n]*(?:\n(?!\s*\n)[^\n]*)*", text)
    for paragraph in paragraphs:
        for block in re.split(r"\n(?=\s*(?:[-*+>]\s|\d+[.)]\s|#|\|))", paragraph.group()):
            if re.match(r"\s*(?:[-*+>]\s|\d+[.)]\s|#|\|)", block):
                continue
            offset = paragraph.start() + paragraph.group().find(block)
            spans = sentence_spans(block)
            lengths = [len(WORD.findall(sentence)) for _, _, sentence in spans]
            for index in range(len(spans) - 2):
                window = lengths[index:index + 3]
                if min(window) and max(window) - min(window) <= max(2, round(sum(window) / 3 * .1)):
                    add(13, "strong", "same-length-run", offset + spans[index][0],
                        offset + spans[index + 2][1])
            short_run = []

            def flush():
                if len(short_run) >= 2:
                    severity = "strong" if len(short_run) >= 3 else "review"
                    add(13, severity, "staccato-run", offset + short_run[0][0],
                        offset + short_run[-1][1])
                short_run.clear()

            for span, length in zip(spans, lengths):
                sentence = span[2].strip()
                if (length <= 12 and sentence.endswith(".") and not
                        re.search(r"\b(?:because|so|which|when|but|and)\b", sentence, FLAGS)):
                    short_run.append(span)
                else:
                    flush()
            flush()
    return sorted(findings, key=lambda finding: (finding["line"], finding["column"], finding["item"]))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", help="UTF-8 file; omit or use - for stdin")
    parser.add_argument("--json", action="store_true", help="print a JSON finding array")
    args = parser.parse_args(argv)
    try:
        text = sys.stdin.read() if args.file in (None, "-") else Path(args.file).read_text(encoding="utf-8")
        if not text.strip():
            raise ValueError("input is empty")
        findings = lint(text)
    except (OSError, UnicodeError, ValueError) as error:
        print("slop-lint: " + str(error), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        for finding in findings:
            print("{line}:{column}: item {item} [{severity}] {pattern}: {text}".format(**finding))
        if not findings:
            print("Clean mechanical scan; judgment checks still need an editor.")
    return int(bool(findings))


if __name__ == "__main__":
    sys.exit(main())
