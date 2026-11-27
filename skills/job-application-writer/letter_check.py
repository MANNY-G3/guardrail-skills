#!/usr/bin/env python3
"""Check a cover letter against the rules of the job-application-writer skill that a script can test.

Usage: letter_check.py LETTER_FILE [--source FILE ...] [--voice] [--json]
Prints one line per finding, then a one-line summary, then the rules a person still has to check by reading.
"fail" means the letter breaks a rule in SKILL.md, and "check this" points at something to look at and proves nothing.
With --source (the resume, the posting, the user's notes) it lists each number, and each name of two or more
capitalized words, that appears in none of those files.
Exit 0 when nothing fails, 1 when a rule fails, 2 on a bad command.
"""

import argparse
from decimal import Decimal
import json
from pathlib import Path
import re
import sys

FIRST_LINE_MAX_WORDS = 20
FIRST_LINE_MAX_WORDS_WITH_VOICE = 30
BODY_PARAGRAPHS_MIN = 1
BODY_PARAGRAPHS_MAX = 4
OPENING_MAX_SENTENCES = 2
LETTER_MAX_WORDS = 250
AVERAGE_SENTENCE_MAX_WORDS = 17
LONGEST_SENTENCE_MAX_WORDS = 33
SUMMING_UP_MAX_PER_100 = 2
SUMMING_UP_MAX_PER_PARAGRAPH = 1
SHORT_SENTENCE_MAX_WORDS = 12
SHORT_RUN_THAT_FAILS = 3
CLOSING_MAX_SENTENCES = 1
CLOSING_MAX_WORDS = 15
TIE_LINE_MAX_WORDS = 15
CLOSE_GUESS_MAX_WORDS = 30
SIGN_OFF_MAX_WORDS = 5
SIGN_OFF_MAX_LINES = 3

STOCK_LINES = (
    "I am writing to express my interest",
    "proven track record",
    "results-driven",
    "hit the ground running",
    "I believe I would be a great fit",
    "thank you for your time and consideration",
)
FEELING_WORDS = (
    "excited", "thrilled", "passionate", "eager", "dream job", "great fit", "perfect fit",
    "strong fit", "ideal candidate", "I believe", "I'm confident", "I am confident",
)
CLOSE_FEELING_WORDS = (
    "welcome", "glad", "happy", "love", "excited", "eager", "thrilled", "delighted", "grateful",
    "appreciate", "hope", "honored", "pleasure",
)
CHAT_SHORTHAND = ("btw", "lol", "imo", "imho", "tbh", "fyi", "idk", "omg")

FAIL, CHECK = "fail", "check"
LABELS = {FAIL: "fail", CHECK: "check this"}
RULES = {
    "greeting": ("Step 4, Shape", 'Greeting: "Dear [name],"'),
    "first-line-length": ("Step 4, Shape", f"First line: one sentence of {FIRST_LINE_MAX_WORDS} words or fewer"),
    "first-line-length-voice": ("Step 5, Case A 4", f"stays at {FIRST_LINE_MAX_WORDS_WITH_VOICE} words or fewer"),
    "first-line-person": ("Step 4, Shape", "First line: ... in the first person"),
    "body-paragraphs": ("Step 4, Shape", "Body: one to four paragraphs, one happening each"),
    "claims-sentence": ("Step 4, Claims", "Claims: ... They go in one sentence right after the first line, in the same paragraph"),
    "length": ("Step 4, Length", f"it stays under about {LETTER_MAX_WORDS} words"),
    "average-sentence": ("Step 4, Sentences 2", f"Keep the average sentence at {AVERAGE_SENTENCE_MAX_WORDS} words or fewer"),
    "longest-sentence": ("Step 4, Sentences 2", f"with none over {LONGEST_SENTENCE_MAX_WORDS}"),
    "same-opener": ("Step 4, Sentences 3", "Don't open two paragraphs in a row the same way"),
    "same-kind-opener": ("Step 4, Sentences 3", "Don't open two paragraphs in a row the same way"),
    "summing-up-rate": ("Step 4, Sentences 4", "Summing-up numbers ... stay at two per 100 words or fewer"),
    "summing-up-paragraph": ("Step 4, Sentences 4", "Summing-up numbers ... and one per paragraph"),
    "so-because": ("Step 3, 6", 'Use "so" or "because" only where the user said one thing caused the other'),
    "voice-leftovers": ("Step 5, Case A 3",
                        'Leave out hashtags, slang, chat shorthand such as "btw", all caps, emoji, dares and stacked exclamation marks'),
    "transition-opener": ("Step 4, Sentences 6", "Cut transition openers"),
    "i-also": ("Step 4, Sentences 6", 'Cut ... "I also" chains'),
    "ing-opener": ("Step 4, Sentences 6", 'Cut ... "-ing" openers such as "Using data, I..."'),
    "years-opener": ("Step 4, Sentences 7", "Don't open on a span of years"),
    "stock-line": ("Step 4, Sentences 11", "Cut stock letter lines"),
    "dash": ("Step 4, Sentences 13", "Use no em dashes and no en dashes"),
    "dash-stand-in": ("Step 4, Sentences 13", "Use no em dashes and no en dashes"),
    "ing-tail": ("Step 3, 4", 'Join the act to its result with "and" or "so", never with an "-ing" tail'),
    "posting-opener": ("Step 4, Tie lines", "Never open it on the posting's own words"),
    "closing-count": ("Step 4, Close", "Never two closing sentences"),
    "closing-guess": ("Step 4, Close", "Never two closing sentences"),
    "closing-length": ("Step 4, Close", f"at most one closing sentence of {CLOSING_MAX_WORDS} words or fewer"),
    "close-own-paragraph": ("Step 4, Close", "Close: ... in a paragraph of its own"),
    "close-fact": ("Step 4, Close", "Close: ... with no fact and no feeling in it"),
    "close-feeling": ("Step 4, Close", "Close: ... with no fact and no feeling in it"),
    "short-run": ("Step 5, 7", "Short sentences in a row read like a list of verdicts, so join one of them to its neighbor"),
    "feeling": ("Rule zero", "Add no feeling, opinion, joke or reason for applying that the user didn't give you"),
    "sign-off": ("Step 4, Shape", "Sign-off: the user's name"),
    "source-number": ("Rule zero", "Every fact in the piece comes from the user"),
    "source-name": ("Rule zero", "Every fact in the piece comes from the user"),
}
STILL_TO_CHECK = (
    "Rule zero: every fact is the user's and the same size they gave it, nothing happens that they didn't tell "
    "you about, every story shows their own part, and other people go by their role, never by name.",
    "Step 4, Body: each body paragraph opens on its happening, happenings take at least two words in three of "
    "the body, and the body ends on a happening or its tie line.",
    "Step 4, Claims: claims sit in one sentence right after the first line, or after the whole happening they "
    "belong to, never between two sentences of one happening and never after the last happening.",
    "Step 4, Sentences 1: the ration (the cap on claims and always-true sentences together). After the first line "
    "they take at most one word in five, and no two always-true sentences sit back to back.",
    "Step 4, Tie lines: a tie line is a claim about the user, so it needs the user to have done the very task the "
    "posting names themselves, at the size the posting names it, with their own words saying so. One per happening "
    f"at most, most happenings get none, and each runs {TIE_LINE_MAX_WORDS} words or fewer in words of its own.",
    "Step 4, Close: the script finds a closing sentence only by words such as let me know, I'd like to talk "
    "and thank you for, so read the end of the letter for one it missed.",
    "Step 4, the bullets-only letter: two or three short body paragraphs, each opening on the claim that answers "
    "one need, and under about 150 words.",
    "Step 4, Sentences 8 and 9: no happening polished into a tidy formula, and no present-tense habit "
    "retold as a happening.",
    "Step 4, Sentences 10 and 12: one name for each thing every time, and contractions where they sound natural.",
    "Step 5, when a sample was given: three marks at most, a full sentence apart, and no sentence and no run of "
    "four or more words copied from the sample.",
)
NO_SOURCE_NOTE = ("Rule zero: run again with --source and the resume, the posting and any notes "
                  "to list the numbers and names to check.")

MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
DAYS = "Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday"
NUMBER_WORDS = {
    "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
    "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100, "dozen": 12,
}
TENS = ("twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")
UNITS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9}
COUNT = r"(?:\d+|one|" + "|".join(NUMBER_WORDS) + r")"

WORD = re.compile(r"[^\s—–]*\w[^\s—–]*")
GREETING = re.compile(r"\s*(?:Dear|Hi|Hello|Hey|To)\b[^\n]{0,80}[,:]\s*")
SENTENCE_END = re.compile(r"[.!?]+[\"'”’)\]]*(?=\s|$)")
TITLES = {"mr", "mrs", "ms", "dr", "st", "jr", "sr", "vs", "etc"}
INITIALS = re.compile(r"(?:[a-z]\.)+[a-z]")
PARAGRAPH = re.compile(r"\S[^\n]*(?:\n(?!\s*\n)[^\n]*)*")
FIRST_PERSON = re.compile(r"\b(?:I|I['’](?:m|d|ve|ll)|[Mm]e|[Mm]y)\b")
DASH = re.compile(r"[—–]")
DASH_STAND_IN = re.compile(r"(?<=\w)(?:\s+-{1,2}\s+|--)(?=\w)")
JOINS = re.compile(r"\b(?:and|so|because|but|which|when|while|since|after|before|until|if|though|although|or)\b", re.I)
SO_OR_BECAUSE = re.compile(r"(?:(?<=,\s)|(?<=\band\s)|^|(?<=[.!?]\s))[Ss]o\b(?!\s+(?:that|much|many|far|long|well)\b)|\b[Bb]ecause\b",
                           re.M)
VOICE_LEFTOVERS = re.compile(
    r"(?<![\w&])#[A-Za-z]\w*|!{2,}|[\U0001F300-\U0001FAFF☀-➿]|\b(?:" + "|".join(CHAT_SHORTHAND) + r")\b", re.I)
SUMMING_UP = re.compile(
    rf"\d+(?:\.\d+)?\s?%|\b\d+(?:\.\d+)?\s+percent\b|\b\d+(?:\.\d+)?x\b|\b\d+\+|"
    rf"\b{COUNT}\s+(?:out\s+)?of\s+{COUNT}\b|\bup\s+to\b|\bevery\b|\bacross\b",
    re.I,
)
TRANSITION_OPENER = re.compile(
    r"(?:Early\s+on|Next|Later|Then|Also|Finally|Lastly|Most\s+recently|To\s+fix\s+that|After\s+that(?:\s+change)?|"
    r"In\s+(?:that|this|my\s+current)\s+role|Before\s+that|Beyond\s+that|On\s+top\s+of\s+that|Outside\s+of\s+that|"
    r"In\s+addition|Additionally|Furthermore|Moreover|First|Second|Third),",
    re.I,
)
NOT_PARTICIPLES = {
    "during", "according", "regarding", "including", "concerning", "excluding", "pending", "nothing",
    "something", "anything", "everything", "thing", "morning", "evening", "spring", "string", "ceiling",
    "wedding", "bring", "sing", "ring", "king", "wing", "swing", "sting", "sling",
}
ING_OPENER = re.compile(r"(?:By\s+)?([A-Za-z]+ing)\b[^,.!?\n]{0,60},\s+(?:I|we|they|she|he|my|our)\b")
ING_TAIL = re.compile(r"(\S+),\s+([a-z]+ing)\b")
GERUND_SUBJECT = re.compile(
    r"(?:\s+(?!(?:which|that|who)\b)[\w'’%$-]+){0,5}?\s+(?:is|was|are|were|has|had|means|meant|takes|took|matters|makes|made)\b")
I_ALSO = re.compile(r"\bI(?:['’](?:ve|d|m))?\s+also\b")
YEARS_OPENER = re.compile(
    r"(?:(?:Over|For|In|During|After|With)\s+(?:the\s+(?:past|last)\s+)?(?:(?:more\s+than|nearly|almost|about|over)\s+)?"
    r"(?:\d+\+?|[a-z]+)?\s*years\b|From\s+(?:[a-z]+\.?\s+)?\d{4}\s*(?:to|until|through|-)|Since\s+(?:[a-z]+\.?\s+)?\d{4}\b)",
    re.I,
)
POSTING_OPENER = re.compile(
    r"(?:(?:Your|The|This)\s+(?:job\s+)?(?:posting|post|listing|description|ad)\s+"
    r"(?:asks|says|lists|mentions|calls|wants|needs|notes|describes|highlights|stresses|emphasizes|seeks|looks|is\s+looking)"
    r"|You(?:['’]re|\s+are)\s+(?:looking|seeking|hiring))\b",
    re.I,
)
# Only words that ask the reader for contact, so a story's last line with "talk" in it isn't read as the close.
CLOSING_WORDS = re.compile(
    r"^(?:thanks|thank\s+you)\b|\bthank(?:s|\s+you)\s+for\b|\blet\s+me\s+know\b|\blook(?:ing)?\s+forward\b|"
    r"\bhear(?:ing)?\s+from\s+you\b|\b(?:chance|opportunity)\s+to\s+(?:talk|discuss|speak|chat|meet)\b|"
    r"\b(?:I['’]d|I\s+would|I['’]m|I\s+am|I['’]ll|I\s+will|be|am)\s+(?:like|love|welcome|glad|happy|eager)\s+to\s+"
    r"(?:talk|discuss|speak|chat|meet)\b|\b(?:happy|glad)\s+to\s+(?:talk|chat|discuss)\b|\b(?:reach|contact)\s+me\b|"
    r"\bget\s+in\s+touch\b|\byour\s+consideration\b|\bwelcome\s+the\s+(?:chance|opportunity)\b",
    re.I,
)
OPENER_KINDS = (
    ("a time", re.compile(
        rf"(?:(?:In|On|During|By|Since|From|Over|After|Before|Last|Early|This|That)\s+(?:(?:early|late|mid)\s+)?"
        rf"(?:\d{{4}}|{MONTHS}|{DAYS}|spring|summer|fall|autumn|winter|week|month|year|my\s+first|the\s+first|"
        rf"the\s+past|the\s+last)\b|(?:When|While|Once|After|Before)\b)", re.I)),
    ("a place", re.compile(rf"(?:At|In|With)\s+(?!(?:{MONTHS}|{DAYS})\b)[A-Z]")),
    ("the act", re.compile(r"(?:I|We)\s|I['’]ve\b")),
    ("the thing", re.compile(r"(?:The|My|Our|That|This|These|Those|A|An|Each|Every)\b")),
)

DIGITS = re.compile(r"\d{1,2}:\d{2}(?!\d)|\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")
SCALES = {"k": 1000, "thousand": 1000, "million": 1000000}
SCALE_AFTER = re.compile(r"\s?(k|thousand|million)\b", re.I)
TENS_AND_UNITS = re.compile(r"\b(" + "|".join(TENS) + r")-(" + "|".join(UNITS) + r")\b", re.I)
LOWER_WORD = re.compile(r"\b[a-z]+\b", re.I)
CONNECTORS = {"of", "and", "&", "the", "de", "la", "del", "van", "von", "du", "da"}
I_FORMS = {"i", "i'm", "i'd", "i've", "i'll"}
NAME_LEADERS = {
    "the", "a", "an", "at", "in", "on", "for", "my", "we", "our", "this", "that", "these", "those", "when",
    "after", "before", "dear", "since", "as", "with", "from", "to", "thank", "thanks", "over", "during", "while",
    "last", "next", "each", "every", "most", "some", "and", "but", "so", "then", "if", "it", "its", "it's", "here",
    "there", "what", "why", "how", "your", "you", "best", "kind", "warm", "regards", "sincerely", "cheers",
    "respectfully", "yours", "hello", "hi", "hey", "by", "of", "now", "today", "also", "both", "all", "one", "that's",
} | set(NUMBER_WORDS)
GENERIC_TAIL = {"team", "role", "position", "job", "hiring", "manager", "department"}


def words(text):
    return WORD.findall(text)


def runs_on(last_word, following):
    """True when a full stop belongs to an abbreviation, as in "Dr. Lee" or "a.m. shift"."""
    if last_word in TITLES:
        return True
    return bool(INITIALS.fullmatch(last_word)) and (following[:1].islower() or following[:1].isdigit())


def sentence_spans(text, start, end):
    spans, cursor = [], start
    for match in SENTENCE_END.finditer(text, start, end):
        last_word = re.search(r"[\w.]*$", text[cursor:match.start()]).group().lower()
        following = text[match.end():end].lstrip()[:1]
        if match.group().startswith(".") and runs_on(last_word, following):
            continue
        add_span(spans, text, cursor, match.end())
        cursor = match.end()
    add_span(spans, text, cursor, end)
    return spans


def add_span(spans, text, start, end):
    piece = text[start:end]
    if WORD.search(piece):
        lead = len(piece) - len(piece.lstrip())
        spans.append((start + lead, end, piece.strip()))


def flatten(text):
    return " ".join(text.lower().replace("’", "'").replace(".", "").split())


def plain(value):
    return format(value.normalize(), "f")


def numbers_in(text, count_one=False):
    """Return (start, written, keys) for each number, so "2,100", "2.1k" and "twenty-one" compare as values."""
    found = []
    for match in DIGITS.finditer(text):
        written = match.group()
        if ":" in written:
            found.append((match.start(), written, {written}))
            continue
        value = Decimal(written.replace(",", ""))
        keys = {plain(value)}
        scale = SCALE_AFTER.match(text, match.end())
        if scale:
            keys.add(plain(value * SCALES[scale.group(1).lower()]))
        found.append((match.start(), written, keys))
    taken = []
    for match in TENS_AND_UNITS.finditer(text):
        value = NUMBER_WORDS[match.group(1).lower()] + UNITS[match.group(2).lower()]
        found.append((match.start(), match.group(), {str(value)}))
        taken.append(match.span())
    for match in LOWER_WORD.finditer(text):
        if any(start <= match.start() < end for start, end in taken):
            continue
        word = match.group().lower()
        if word in NUMBER_WORDS:
            found.append((match.start(), match.group(), {str(NUMBER_WORDS[word])}))
        elif word == "one" and count_one:
            found.append((match.start(), match.group(), {"1"}))
    return found


def names_in(text):
    """Return (start, words) for each run of two or more capitalized words, such as an employer or a title."""
    names, run, previous_end = [], [], 0

    def finish():
        while run and run[-1][1].lower() in CONNECTORS:
            run.pop()
        while run and (run[0][1].lower().replace("’", "'") in NAME_LEADERS or run[0][1].lower() in CONNECTORS):
            run.pop(0)
        if sum(1 for _, word in run if word[:1].isupper()) >= 2:
            names.append((run[0][0], [word for _, word in run]))
        run.clear()

    for match in re.finditer(r"\S+", text):
        raw = match.group()
        if "\n" in text[previous_end:match.start()] or raw[0] in "\"“‘([":
            finish()
        previous_end = match.end()
        core = re.sub(r"['’]s$", "", raw.strip("\"'“”‘’()[]{}.,;:!?"))
        lowered = core.lower().replace("’", "'")
        if core[:1].isupper() and lowered not in I_FORMS:
            run.append((match.start(), core))
        elif lowered in CONNECTORS and run:
            run.append((match.start(), core))
        else:
            finish()
        tail = raw.rstrip("\"'”’)]")
        if tail != raw or tail[-1:] in ",;:!?" or (tail.endswith(".") and lowered not in TITLES and "." not in core):
            finish()
    finish()
    return names


def in_sources(phrase, flat_sources):
    return bool(re.search(r"(?<!\w)" + re.escape(flatten(phrase)) + r"(?!\w)", flat_sources))


def name_in_sources(name_words, flat_sources):
    if in_sources(" ".join(name_words), flat_sources):
        return True
    trimmed = list(name_words)
    while trimmed and trimmed[-1].lower() in GENERIC_TAIL:
        trimmed.pop()
    if not trimmed or (trimmed != name_words and in_sources(" ".join(trimmed), flat_sources)):
        return True
    parts, part = [], []
    for word in name_words:
        if word.lower() in ("and", "&"):
            parts.append(part)
            part = []
        elif part or word.lower() not in CONNECTORS:
            part.append(word)
    parts.append(part)
    return len(parts) > 1 and all(part and in_sources(" ".join(part), flat_sources) for part in parts)


def phrase_pattern(phrase):
    pattern = r"\s+".join(re.escape(word) for word in phrase.split())
    pattern = pattern.replace(r"I\s+am", r"I(?:\s+a|')m").replace(r"I\s+would", r"I(?:\s+woul|')d")
    return re.compile(r"(?<!\w)" + pattern.replace(r"\-", r"[-\s]") + r"(?!\w)", re.I)


def snippet(text, limit=80):
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit - 3] + "..."


def opener_kind(paragraph_text):
    for kind, pattern in OPENER_KINDS:
        if pattern.match(paragraph_text):
            return kind
    return None


def split_letter(letter, lines):
    """Return (greeting line, the lines between greeting and sign-off, sign-off lines)."""
    greeting = lines[0] if len(lines) > 1 and GREETING.fullmatch(letter, *lines[0]) else None
    middle = lines[1:] if greeting else list(lines)
    sign_off = []
    while len(middle) > 1 and len(sign_off) < SIGN_OFF_MAX_LINES:
        line = letter[slice(*middle[-1])]
        if len(words(line)) > SIGN_OFF_MAX_WORDS or re.search(r"[.!?][\"'”’)]*\s*$", line):
            break
        sign_off.insert(0, middle.pop())
    return greeting, middle, sign_off


def check(letter, sources=None, voice=False):
    """Return the findings, the measures and the rules left to a reader, for one letter."""
    findings = []

    def add(rule, level, start, detail):
        where, says = RULES[rule]
        findings.append({"line": letter.count("\n", 0, start) + 1,
                         "column": start - letter.rfind("\n", 0, start),
                         "level": level, "rule": rule, "where": where, "says": says, "text": detail})

    normalized = letter.replace("’", "'").replace("‘", "'")
    lines = [match.span() for match in re.finditer(r"[^\n]+", letter) if match.group().strip()]
    greeting, middle_lines, sign_off = split_letter(letter, lines)
    if not greeting:
        add("greeting", FAIL, lines[0][0], f'no greeting line opens the letter: "{snippet(letter[slice(*lines[0])], 40)}"')
    elif not letter[slice(*greeting)].lstrip().startswith("Dear"):
        add("greeting", FAIL, greeting[0], f'the greeting is "{letter[slice(*greeting)].strip()}"')
    if not sign_off:
        add("sign-off", CHECK, lines[-1][0], "no short last line with the user's name was found")

    middle_start, middle_end = middle_lines[0][0], middle_lines[-1][1]
    paragraphs = []
    for match in PARAGRAPH.finditer(letter, middle_start, middle_end):
        spans = sentence_spans(letter, match.start(), match.end())
        if spans:
            paragraphs.append({"start": match.start(), "end": match.end(), "sentences": spans})
    sentences = [span for paragraph in paragraphs for span in paragraph["sentences"]]
    if not sentences:
        raise ValueError("the letter has no sentences between the greeting and the sign-off, so it may be the "
                         "wrong file. Give it the finished letter as plain text.")
    counts = [len(words(span[2])) for span in sentences]
    middle_words = len(words(letter[middle_start:middle_end]))
    total_words = len(words(letter))

    first = sentences[0]
    limit = FIRST_LINE_MAX_WORDS_WITH_VOICE if voice else FIRST_LINE_MAX_WORDS
    if counts[0] > limit:
        add("first-line-length-voice" if voice else "first-line-length", FAIL, first[0],
            f'{counts[0]} words: "{snippet(first[2])}"')
    if not FIRST_PERSON.search(first[2]):
        add("first-line-person", FAIL, first[0], f'no "I", "me" or "my" in "{snippet(first[2])}"')

    closing = []
    for span in reversed(sentences[1:]):
        if not CLOSING_WORDS.search(span[2]):
            break
        closing.insert(0, span)
    closing_alone = len(paragraphs) > 1 and all(span in closing for span in paragraphs[-1]["sentences"])
    body = paragraphs[1:(len(paragraphs) - 1 if closing_alone else len(paragraphs))]

    if total_words > LETTER_MAX_WORDS:
        add("length", FAIL, 0, f"{total_words} words in the whole letter")
    opening = paragraphs[0]["sentences"]
    if len(opening) > OPENING_MAX_SENTENCES:
        add("claims-sentence", FAIL, opening[OPENING_MAX_SENTENCES][0],
            f"the first paragraph holds {len(opening)} sentences, and it takes only the first line and one sentence of claims")
    if not BODY_PARAGRAPHS_MIN <= len(body) <= BODY_PARAGRAPHS_MAX:
        add("body-paragraphs", FAIL, middle_start,
            f"{len(body)} body paragraph{'' if len(body) == 1 else 's'}, counted between the first paragraph and the close")
    average = sum(counts) / len(counts)
    if average > AVERAGE_SENTENCE_MAX_WORDS:
        add("average-sentence", FAIL, middle_start, f"the average is {average:.1f} words over {len(counts)} sentences")
    for span, count in zip(sentences, counts):
        if count > LONGEST_SENTENCE_MAX_WORDS:
            add("longest-sentence", FAIL, span[0], f'{count} words: "{snippet(span[2])}"')

    for match in DASH.finditer(letter):
        add("dash", FAIL, match.start(), f'"{snippet(letter[max(match.start() - 20, 0):match.end() + 20])}"')
    for match in DASH_STAND_IN.finditer(letter):
        add("dash-stand-in", CHECK, match.start(),
            f'a hyphen may be standing in for a dash: "{snippet(letter[max(match.start() - 20, 0):match.end() + 20])}"')

    stock_spans = []
    for line in STOCK_LINES:
        for match in phrase_pattern(line).finditer(normalized):
            stock_spans.append(match.span())
            add("stock-line", FAIL, match.start(), f'"{match.group()}"')
    flat_sources = flatten("\n".join(sources)) if sources else ""
    for word in FEELING_WORDS:
        for match in phrase_pattern(word).finditer(normalized):
            if any(start <= match.start() < end for start, end in stock_spans):
                continue
            if sources and in_sources(match.group(), flat_sources):
                continue
            stock_spans.append(match.span())
            add("feeling", CHECK, match.start(), f'"{match.group()}": keep it only if the user said it')

    for start, _, text in sentences:
        if match := TRANSITION_OPENER.match(text):
            add("transition-opener", FAIL, start, f'"{match.group()}"')
        if (match := ING_OPENER.match(text)) and match.group(1).lower() not in NOT_PARTICIPLES:
            add("ing-opener", FAIL, start, f'"{snippet(match.group(), 50)}"')
        if match := YEARS_OPENER.match(text):
            add("years-opener", FAIL, start, f'"{match.group()}"')
        if match := POSTING_OPENER.match(text):
            add("posting-opener", FAIL, start, f'"{snippet(text, 50)}"')
    for match in I_ALSO.finditer(letter, middle_start, middle_end):
        add("i-also", FAIL, match.start(), f'"{match.group()}"')
    bare_sources = " ".join(re.sub(r"[,;:]", " ", flat_sources).split())
    for match in SO_OR_BECAUSE.finditer(letter, middle_start, middle_end):
        # The joining word plus the next two words survives a tense change, as in "so my heart is" and "so my heart was".
        cause = " ".join(re.sub(r"[,;:]", " ", letter[match.start():match.end() + 60]).split()[:3])
        if sources and in_sources(cause, bare_sources):
            continue
        add("so-because", CHECK, match.start(),
            f'"{snippet(letter[match.start():match.end() + 40], 50)}" states a cause; keep it only if the user gave it')
    for match in VOICE_LEFTOVERS.finditer(letter):
        add("voice-leftovers", FAIL, match.start(), f'"{match.group()}"')
    for match in ING_TAIL.finditer(letter, middle_start, middle_end):
        before, tail = match.group(1).strip("\"'”’)").lower(), match.group(2)
        if tail in NOT_PARTICIPLES or len(tail) <= 4 or before.endswith("ing"):
            continue
        # A gerund that starts the main clause ("Because I've done it, training people is...") is a subject, not a tail.
        if GERUND_SUBJECT.match(letter, match.end(), middle_end):
            continue
        sentence_end = SENTENCE_END.search(letter, match.end(), middle_end)
        add("ing-tail", FAIL, match.start(2),
            f'", {snippet(letter[match.start(2):sentence_end.end() if sentence_end else middle_end], 60)}"')

    for previous, current in zip(paragraphs, paragraphs[1:]):
        before = WORD.search(letter, previous["start"]).group().lower().replace("’", "'").strip("\"'“”(")
        after = WORD.search(letter, current["start"]).group().lower().replace("’", "'").strip("\"'“”(")
        if before == after:
            add("same-opener", FAIL, current["start"], f'two paragraphs in a row open on "{after}"')
        elif previous in body and current in body:
            kind = opener_kind(letter[current["start"]:current["end"]])
            if kind and kind == opener_kind(letter[previous["start"]:previous["end"]]):
                add("same-kind-opener", CHECK, current["start"], f"two paragraphs in a row open on {kind}")

    summing_up = list(SUMMING_UP.finditer(letter, middle_start, middle_end))
    rate = 100 * len(summing_up) / middle_words
    if rate > SUMMING_UP_MAX_PER_100:
        found = ", ".join(f'"{match.group()}"' for match in summing_up)
        add("summing-up-rate", FAIL, middle_start, f"{len(summing_up)} in {middle_words} words is {rate:.1f} per 100: {found}")
    for paragraph in paragraphs:
        inside = [match for match in summing_up if paragraph["start"] <= match.start() < paragraph["end"]]
        if len(inside) > SUMMING_UP_MAX_PER_PARAGRAPH:
            found = ", ".join(f'"{match.group()}"' for match in inside)
            add("summing-up-paragraph", FAIL, inside[SUMMING_UP_MAX_PER_PARAGRAPH].start(), f"{len(inside)} in one paragraph: {found}")

    run = []

    def end_run():
        if len(run) >= 2:
            level = FAIL if len(run) >= SHORT_RUN_THAT_FAILS else CHECK
            joined = " ".join(f'"{snippet(span[2], 40)}"' for span in run)
            hint = "" if level == FAIL else "; join them if both make a claim"
            add("short-run", level, run[0][0], f"{len(run)} short sentences in a row with no join: {joined}{hint}")
        run.clear()

    for span, count in zip(sentences[1:], counts[1:]):
        if count <= SHORT_SENTENCE_MAX_WORDS and not JOINS.search(span[2]):
            run.append(span)
        else:
            end_run()
    end_run()

    if len(closing) > CLOSING_MAX_SENTENCES:
        quoted = " ".join(f'"{snippet(span[2], 40)}"' for span in closing)
        add("closing-count", FAIL, closing[0][0],
            f"{len(closing)} closing sentences in a row at the end, found by their closing words: {quoted}")
    for span in closing:
        if len(words(span[2])) > CLOSING_MAX_WORDS:
            add("closing-length", FAIL, span[0], f'{len(words(span[2]))} words: "{snippet(span[2])}"')
        if numbers_in(span[2]):
            add("close-fact", FAIL, span[0], f'the close holds a number: "{snippet(span[2])}"')
        for word in CLOSE_FEELING_WORDS:
            if match := re.search(r"\b" + word + r"\w*", span[2], re.I):
                add("close-feeling", CHECK, span[0], f'"{match.group()}" may be a feeling the user didn\'t give')
                break
    if closing and not closing_alone:
        add("close-own-paragraph", FAIL, closing[0][0],
            f'the closing sentence shares a paragraph with the story: "{snippet(closing[0][2], 50)}"')
    last = paragraphs[-1]
    last_text = letter[last["start"]:last["end"]]
    if (not closing and len(paragraphs) > 1 and len(last["sentences"]) >= 2
            and len(words(last_text)) <= CLOSE_GUESS_MAX_WORDS and not numbers_in(last_text)):
        add("closing-guess", CHECK, last["start"],
            "a guess from its shape: this short last paragraph has no number and may hold more than one closing sentence")

    traced = 0
    if sources:
        source_keys = set().union(*(keys for source in sources for _, _, keys in numbers_in(source, count_one=True)))
        seen = set()
        for start, written, keys in numbers_in(letter):
            if keys & source_keys:
                traced += 1
            elif written.lower() not in seen:
                seen.add(written.lower())
                add("source-number", CHECK, start, f'"{written}" is in none of the --source files')
        seen = set()
        for start, name_words in names_in(letter):
            name = " ".join(name_words)
            if name_in_sources(name_words, flat_sources):
                traced += 1
            elif flatten(name) not in seen:
                seen.add(flatten(name))
                add("source-name", CHECK, start, f'"{name}" is in none of the --source files')

    findings.sort(key=lambda finding: (finding["line"], finding["column"]))
    still_to_check = list(STILL_TO_CHECK) + ([] if sources else [NO_SOURCE_NOTE])
    measures = {"words": total_words, "body_paragraphs": len(body), "sentences": len(counts),
                "average_sentence": round(average, 1), "longest_sentence": max(counts),
                "summing_up_per_100": round(rate, 2),
                "found_in_sources": traced if sources else None}
    return {"findings": findings, "measures": measures, "still_to_check": still_to_check}


def read(path, role):
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeError:
        raise ValueError(f"{path} isn't plain UTF-8 text, so it may be a Word or PDF file. "
                         f"Save the {role} as plain text and run again.")
    except OSError as error:
        raise ValueError(f"could not read {path} ({error.strerror or error}). The path may be mistyped or the "
                         f"file not saved yet, so check the path to the {role} and run again.")
    if not text.strip():
        raise ValueError(f"{path} is empty, probably because the {role} isn't saved yet. Save it and run again.")
    return text


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("letter", type=Path, help="the cover letter, as a plain-text file")
    parser.add_argument("--source", type=Path, nargs="+", action="extend", default=[], metavar="FILE",
                        help="a file the facts must come from: the resume, the posting or the user's notes")
    parser.add_argument("--voice", action="store_true",
                        help=f"the first line is a voice opening (case A), so it may run to {FIRST_LINE_MAX_WORDS_WITH_VOICE} words")
    parser.add_argument("--json", action="store_true", help="print the findings, measures and rules left to check as JSON")
    args = parser.parse_args(argv)
    try:
        letter = read(args.letter, "letter")
        sources = [read(path, "source file") for path in args.source]
        result = check(letter, sources, args.voice)
    except ValueError as error:
        print("letter_check: " + str(error), file=sys.stderr)
        return 2
    failed = sum(finding["level"] == FAIL for finding in result["findings"])
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return int(bool(failed))
    for finding in result["findings"]:
        print("{line}:{column}: {where} [{label}] {says}: {text}".format(label=LABELS[finding["level"]], **finding))
    measures = result["measures"]
    to_check = len(result["findings"]) - failed
    summary = (f"letter_check: {failed} fail, {to_check} to check | {measures['words']} words, "
               f"{measures['body_paragraphs']} body paragraphs, sentences average {measures['average_sentence']} "
               f"words and the longest has {measures['longest_sentence']}")
    if args.source:
        summary += f" | {measures['found_in_sources']} numbers and names also appear in a source file"
    print(summary)
    print("\nStill to check by reading, because a script can't judge these:")
    for item in result["still_to_check"]:
        print("- " + item)
    return int(bool(failed))


if __name__ == "__main__":
    sys.exit(main())
