import ast
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
CHECK_PATH = Path(os.environ.get("LETTER_CHECK_PATH") or REPO / "skills/job-application-writer/letter_check.py")
SKILL = REPO / "skills/job-application-writer/SKILL.md"
SPEC = importlib.util.spec_from_file_location("letter_check", CHECK_PATH)
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)

RESUME = """ROBIN ASHGROVE
Larkspur Lane Books | Store Lead | 2021 - present
- Moved the store's special orders from a paper binder to a shared spreadsheet, lost orders fell from 12 a month to 2
- Trained 5 new booksellers on the register and the order system
Brightwater Library | Circulation Clerk | 2018 - 2021
- Rebuilt the overdue notice letter, returns within a week rose by 15%
Skills: English/Spanish
"""
POSTING = """Support Specialist
Quillmoor Software
Quillmoor makes inventory software for independent bookstores.
- Answer customer tickets by email and chat
- Help new stores set up their catalog
"""
SOURCES = [RESUME, POSTING]

GREETING = "Dear Quillmoor Software hiring team,"
FIRST_LINE = "I'm applying for the Support Specialist role at Quillmoor Software."
STORE = ("At Larkspur Lane Books I moved our special orders from a paper binder to a shared spreadsheet, "
         "and lost orders fell from 12 a month to 2.")
TIE = "That's the cleanup a new store needs when it sets up a catalog."
LIBRARY = "I rebuilt the overdue notice letter at Brightwater Library, and returns within a week rose by 15%."
TRAINING = "Five new booksellers learned the register and the order system from me at Larkspur Lane Books."
CLOSE = "I'd like to talk about the role."
SIGN_OFF = "Robin Ashgrove"


def letter(greeting=GREETING, first=FIRST_LINE, store=STORE + " " + TIE, library=LIBRARY,
           training=TRAINING, close=CLOSE, sign_off=SIGN_OFF, extra=()):
    parts = [greeting, first, store, library, training, *extra, close, sign_off]
    return "\n\n".join(part for part in parts if part)


CLEAN = letter()


def findings(text, **options):
    return CHECK.check(text, **options)["findings"]


def rules(text, **options):
    return {finding["rule"] for finding in findings(text, **options)}


class LetterCheckTests(unittest.TestCase):
    def assert_only(self, text, rule, level=None, **options):
        found = findings(text, **options)
        self.assertEqual({finding["rule"] for finding in found}, {rule}, json.dumps(found, indent=1))
        if level:
            self.assertEqual({finding["level"] for finding in found}, {level})

    def run_cli(self, text, *extra, sources=()):
        with tempfile.TemporaryDirectory(prefix="letter-") as directory:
            path = Path(directory) / "letter.txt"
            path.write_text(text)
            source_paths = []
            for number, source in enumerate(sources):
                source_path = Path(directory) / f"source{number}.txt"
                source_path.write_text(source)
                source_paths.append(str(source_path))
            arguments = [str(path)] + (["--source", *source_paths] if source_paths else []) + list(extra)
            return subprocess.run([sys.executable, str(CHECK_PATH), *arguments], capture_output=True, text=True)

    def test_the_clean_letter_passes_everything(self):
        self.assertEqual(findings(CLEAN), [])
        self.assertEqual(findings(CLEAN, sources=SOURCES), [])
        measures = CHECK.check(CLEAN)["measures"]
        self.assertEqual(measures["body_paragraphs"], 3)
        self.assertLessEqual(measures["average_sentence"], CHECK.AVERAGE_SENTENCE_MAX_WORDS)

    def test_greeting(self):
        self.assert_only(letter(greeting=None), "greeting", "fail")
        self.assert_only(letter(greeting="Hi Quillmoor Software team,"), "greeting", "fail")

    def test_first_line_length_and_the_voice_allowance(self):
        long_first = ("I'm applying for the Support Specialist role at Quillmoor Software, which makes "
                      "inventory software for bookstores like the one I run.")
        self.assert_only(letter(first=long_first), "first-line-length", "fail")
        self.assertEqual(findings(letter(first=long_first), voice=True), [])

    def test_first_line_in_the_first_person(self):
        first = "This is an application for the Support Specialist role at Quillmoor Software."
        self.assert_only(letter(first=first), "first-line-person", "fail")

    def test_body_paragraphs_one_to_four(self):
        self.assertEqual(findings(letter(library=None, training=None)), [], "one happening is enough to write from")
        self.assert_only(letter(store=None, library=None, training=None), "body-paragraphs", "fail")
        extra = ("Customer emails came to me at Larkspur Lane Books, and I answered about 30 a week.",
                 "Brightwater Library put me on the circulation desk from 2018 to 2021, and I learned the hold system.")
        self.assert_only(letter(extra=extra), "body-paragraphs", "fail")

    def test_claims_go_in_one_sentence_after_the_first_line(self):
        claims = " I've run the front desk at Larkspur Lane Books since 2021."
        self.assertEqual(findings(letter(first=FIRST_LINE + claims)), [])
        self.assert_only(letter(first=FIRST_LINE + claims + " I trained 5 new booksellers there."), "claims-sentence", "fail")

    def test_total_length(self):
        filler = " I shelved the new arrivals on the front table and checked them against the order list." * 12
        self.assert_only(letter(training=TRAINING + filler), "length", "fail")

    def test_average_sentence(self):
        training = ("Five new booksellers learned the register and the order system from me at Larkspur Lane Books, "
                    "and they used both on their own shifts after their first month there.")
        self.assert_only(letter(training=training), "average-sentence", "fail")

    def test_longest_sentence(self):
        store = ("At Larkspur Lane Books I moved our special orders from a paper binder to a shared spreadsheet "
                 "that the whole staff could open on any shift, and lost orders fell from 12 a month to 2. " + TIE)
        self.assert_only(letter(store=store), "longest-sentence", "fail")

    def test_two_paragraphs_in_a_row_open_on_the_same_word(self):
        training = "I trained 5 new booksellers on the register and the order system at Larkspur Lane Books."
        self.assert_only(letter(training=training), "same-opener", "fail")

    def test_two_paragraphs_in_a_row_open_on_the_same_kind_of_opener(self):
        library = "The overdue notice letter I rebuilt at Brightwater Library lifted returns within a week by 15%."
        training = "Our five new booksellers at Larkspur Lane Books learned the register and the order system from me."
        self.assert_only(letter(library=library, training=training), "same-kind-opener", "check")

    def test_summing_up_numbers_per_100_words(self):
        store = STORE + " That's the cleanup every new store needs when it sets up a catalog."
        training = ("Five new booksellers learned every part of the register and the order system "
                    "from me at Larkspur Lane Books.")
        self.assert_only(letter(store=store, training=training), "summing-up-rate", "fail")

    def test_summing_up_numbers_per_paragraph(self):
        library = ("I rebuilt the overdue notice letter at Brightwater Library, and returns within a week "
                   "rose by 15% across the system.")
        extra = ("Customer emails came to me at Larkspur Lane Books, and I answered about 30 a week.",)
        self.assert_only(letter(library=library, extra=extra), "summing-up-paragraph", "fail")

    def test_you_and_your_have_no_cap(self):
        store = STORE + " That's the cleanup your new stores need when they set up your catalog."
        self.assertEqual(findings(letter(store=store)), [])

    def test_so_and_because_state_a_cause_the_user_must_give(self):
        library = "I rebuilt the overdue notice letter at Brightwater Library, so returns within a week rose by 15%."
        self.assert_only(letter(library=library), "so-because", "check")
        notes = "My notes: I rebuilt the overdue notice letter, so returns within a week went up."
        self.assertEqual(rules(letter(library=library), sources=SOURCES + [notes]), set())
        self.assertEqual(rules(letter(library=LIBRARY.replace("rose by", "rose so much, by"))), set(),
                         '"so much" is not a cause')

    def test_voice_habits_a_letter_leaves_out(self):
        for leftover in ("btw", "#bookstores", "!!", "\U0001F4DA"):
            with self.subTest(leftover=leftover):
                self.assert_only(letter(training=TRAINING[:-1] + " " + leftover + "."), "voice-leftovers", "fail")

    def test_transition_openers(self):
        self.assert_only(letter(training="Additionally, f" + TRAINING[1:]), "transition-opener", "fail")
        self.assert_only(letter(training="In that role, f" + TRAINING[1:]), "transition-opener", "fail")

    def test_i_also_chains(self):
        training = ("Five new booksellers learned the register from me, and I also showed them the order system "
                    "at Larkspur Lane Books.")
        self.assert_only(letter(training=training), "i-also", "fail")
        self.assert_only(letter(training=training.replace("I also", "I've also")), "i-also", "fail")

    def test_ing_openers(self):
        self.assert_only(letter(training="Using the order system, I trained five new booksellers at Larkspur Lane Books."),
                         "ing-opener", "fail")
        during = "During the holidays, five new booksellers learned the register and the order system from me."
        self.assertEqual(rules(letter(training=during)), set())

    def test_ing_tail_after_a_comma(self):
        library = "I rebuilt the overdue notice letter at Brightwater Library, lifting returns within a week by 15%."
        self.assert_only(letter(library=library), "ing-tail", "fail")
        after_a_percent = LIBRARY[:-1] + ", saving the staff a round of calls."
        self.assert_only(letter(library=after_a_percent), "ing-tail", "fail")
        for fine in (
            "Because I ran the desk at Brightwater Library, training new clerks was part of my week.",
            "At Brightwater Library my desk work covered scheduling, training and filing for the branch.",
            "I rebuilt the overdue notice letter at Brightwater Library, including the second reminder.",
        ):
            with self.subTest(fine=fine):
                self.assertNotIn("ing-tail", rules(letter(library=fine)))

    def test_span_of_years_openers(self):
        library = ("Over three years at Brightwater Library I rebuilt the overdue notice letter, "
                   "and returns within a week rose by 15%.")
        self.assert_only(letter(library=library), "years-opener", "fail")
        library = ("From 2018 to 2021 at Brightwater Library I rebuilt the overdue notice letter, "
                   "and returns within a week rose by 15%.")
        self.assert_only(letter(library=library), "years-opener", "fail")

    def test_stock_letter_lines(self):
        self.assert_only(letter(close="I'd hit the ground running at Quillmoor."), "stock-line", "fail")
        for line in CHECK.STOCK_LINES:
            with self.subTest(line=line):
                self.assertIn("stock-line", rules(letter(training=TRAINING + " " + line + " is my aim.")))
        self.assertIn("stock-line", rules(letter(first="I'm writing to express my interest in the Support Specialist role.")))

    def test_every_stock_line_the_skill_lists_is_checked(self):
        item = re.search(r"Cut stock letter lines:(.*)", SKILL.read_text())
        self.assertTrue(item, "SKILL.md no longer has its 'Cut stock letter lines' item")
        listed = re.findall(r'"([^"]+)"', item[1])
        self.assertGreaterEqual(len(listed), 5)
        self.assertEqual({line.lower() for line in listed}, {line.lower() for line in CHECK.STOCK_LINES})

    def test_em_and_en_dashes(self):
        self.assert_only(letter(store=STORE.replace(", and lost", " — lost") + " " + TIE), "dash", "fail")
        self.assert_only(letter(store=STORE.replace(", and lost", " – lost") + " " + TIE), "dash", "fail")
        self.assert_only(letter(store=STORE.replace(", and lost", " - lost") + " " + TIE), "dash-stand-in", "check")
        self.assertEqual(rules(letter(store=STORE.replace("shared", "shared, sign-up") + " " + TIE)), set())

    def test_tie_line_opening_on_the_postings_words(self):
        store = STORE + " Your posting asks for someone who can help new stores set up a catalog."
        self.assert_only(letter(store=store), "posting-opener", "fail")

    def test_two_closing_sentences(self):
        close = ("Thank you for reading, and for the time it takes to sort these letters. "
                 "I'd like to talk about the role when it suits the team.")
        self.assert_only(letter(close=close), "closing-count", "fail")

    def test_a_long_closing_sentence(self):
        self.assert_only(letter(close="I'd like to talk about how my order system work would carry over to Quillmoor Software."),
                         "closing-length", "fail")

    def test_the_close_sits_in_a_paragraph_of_its_own(self):
        self.assert_only(letter(training=TRAINING + " " + CLOSE, close=None), "close-own-paragraph", "fail")
        story_end = TRAINING + " The owner asked me to talk the new staff through the order system."
        self.assertEqual(findings(letter(training=story_end, close=None)), [], "a story's last line is not a close")

    def test_the_close_holds_no_fact_and_no_feeling(self):
        self.assert_only(letter(close="I'd like to talk about the 5 booksellers I trained."), "close-fact", "fail")
        self.assert_only(letter(close="I'd welcome the chance to talk about the role."), "close-feeling", "check")
        self.assertEqual(findings(letter(close="Please let me know if you'd like to talk.")), [])

    def test_a_short_last_paragraph_is_flagged_as_a_guess(self):
        close = "I learn new systems fast, and I like the work. It would mean a lot to me, and I hope it shows."
        self.assert_only(letter(close=close), "closing-guess", "check")
        self.assertIn("a guess", findings(letter(close=close))[0]["text"])

    def test_short_sentences_in_a_row(self):
        store = "At Larkspur Lane Books I moved special orders into a spreadsheet. Lost orders fell from 12 a month to 2. "
        self.assert_only(letter(store=store + TIE), "short-run", "check")
        self.assert_only(letter(store=store + "Nobody missed the binder. " + TIE), "short-run", "fail")
        joined = "At Larkspur Lane Books I moved special orders into a spreadsheet. Lost orders fell from 12 to 2, and that's the cleanup a new store needs."
        self.assertEqual(rules(letter(store=joined)), set(), "the first line never starts a run")

    def test_feelings_the_user_did_not_give(self):
        first = "I'm excited to apply for the Support Specialist role at Quillmoor Software."
        self.assert_only(letter(first=first), "feeling", "check")
        notes = "My notes: I'm excited about this one because I shop at stores that use Quillmoor."
        self.assertEqual(rules(letter(first=first), sources=SOURCES + [notes]), set())

    def test_sign_off(self):
        self.assert_only(letter(sign_off=None), "sign-off", "check")

    def test_numbers_missing_from_the_sources(self):
        self.assert_only(letter(store=STORE.replace("12 a month", "14 a month") + " " + TIE), "source-number", "check",
                         sources=SOURCES)
        self.assert_only(letter(training="Six" + TRAINING[4:]), "source-number", "check", sources=SOURCES)
        self.assertEqual(rules(letter(store=STORE.replace("12 a month", "14 a month") + " " + TIE)), set(),
                         "without --source nothing is compared")

    def test_number_forms_compare_as_values(self):
        keys = [keys for _, _, keys in CHECK.numbers_in("$2.1k, 2,100, twenty-one, 4:10, a five-step form")]
        self.assertEqual(keys, [{"2.1", "2100"}, {"2100"}, {"4:10"}, {"21"}, {"5"}])
        self.assertEqual(CHECK.numbers_in("one of them"), [])

    def test_names_missing_from_the_sources(self):
        library = LIBRARY.replace("Brightwater Library", "Brightwater County Library")
        self.assert_only(letter(library=library), "source-name", "check", sources=SOURCES)
        bilingual = TRAINING[:-1] + ", and I help customers in English and Spanish."
        self.assertEqual(rules(letter(greeting="Dear Hiring Manager,", training=bilingual), sources=SOURCES), set())
        both = ["Larkspur", "Lane", "Books", "and", "the", "Brightwater", "Library"]
        self.assertTrue(CHECK.name_in_sources(both, CHECK.flatten(RESUME)), "a 'the' added after 'and' still matches")

    def test_rules_left_to_a_reader_are_listed_once_at_the_end(self):
        result = self.run_cli(CLEAN)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        tail = result.stdout.split("Still to check by reading", 1)
        self.assertEqual(len(tail), 2)
        self.assertTrue(tail[0].strip().splitlines()[-1].startswith("letter_check: 0 fail, 0 to check"))
        self.assertIn("ration", tail[1])
        self.assertIn("--source", tail[1])
        with_sources = self.run_cli(CLEAN, sources=SOURCES)
        self.assertNotIn("run again with --source", with_sources.stdout)
        self.assertIn("also appear in a source file", with_sources.stdout)
        self.assertIsNone(re.search(r"made[- ]up|invented|fabricat|no false|all facts", with_sources.stdout, re.I))

    def test_cli_exit_codes_and_reasons(self):
        self.assertEqual(self.run_cli(CLEAN).returncode, 0)
        failing = self.run_cli(letter(greeting=None))
        self.assertEqual(failing.returncode, 1)
        self.assertRegex(failing.stdout, r"^1:1: Step 4, Shape \[fail\] Greeting")
        checks_only = self.run_cli(letter(sign_off=None))
        self.assertEqual(checks_only.returncode, 0)
        self.assertIn("[check this]", checks_only.stdout)
        as_json = self.run_cli(letter(greeting=None), "--json")
        self.assertEqual(as_json.returncode, 1)
        self.assertEqual(json.loads(as_json.stdout)["findings"][0]["rule"], "greeting")
        self.assertEqual(self.run_cli("   \n").returncode, 2)
        self.assertIn("is empty", self.run_cli("   \n").stderr)
        self.assertEqual(self.run_cli(CLEAN, "--no-such-option").returncode, 2)
        missing = subprocess.run([sys.executable, str(CHECK_PATH), "/nonexistent/letter.txt"], capture_output=True, text=True)
        self.assertEqual(missing.returncode, 2)
        self.assertIn("could not read", missing.stderr)
        self.assertIn("check the path", missing.stderr)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "letter.txt"
            path.write_text(CLEAN)
            no_source = subprocess.run([sys.executable, str(CHECK_PATH), str(path), "--source", str(path.with_name("resume.txt"))],
                                       capture_output=True, text=True)
            self.assertEqual(no_source.returncode, 2)
            path.write_bytes(b"\xff\xfe\x00")
            binary = subprocess.run([sys.executable, str(CHECK_PATH), str(path)], capture_output=True, text=True)
            self.assertEqual(binary.returncode, 2)
            self.assertIn("plain text", binary.stderr)

    def test_the_skills_own_good_examples_raise_no_fail(self):
        skill = SKILL.read_text()
        examples = ("I'm applying for the Billing Operations Lead role at Contoso.",
                    "At Northwind I merged three billing spreadsheets into one",
                    "One evening I checked the drafts by hand, and two of them came back flagged",
                    "The vendor sign-up form I rebuilt",
                    "I moved our billing onto a new payment processor, and failed payments fell by 40%",
                    "That's the same cleanup the posting lists first.",
                    "Please let me know if you'd like to talk.")
        for example in examples:
            self.assertIn(example, skill)
        text = "\n\n".join(("Dear Contoso hiring team,", examples[0] + " " + examples[1] + ".", examples[2] + ".",
                            examples[3] + " went from 14 steps to 5.", examples[4] + ". " + examples[5], examples[6],
                            SIGN_OFF))
        self.assertEqual([f for f in findings(text) if f["level"] == "fail"], [])
        self.assertEqual(CHECK.check(text)["measures"]["body_paragraphs"], 3)

    def test_each_rule_is_named_in_the_skills_own_words(self):
        skill = " ".join(SKILL.read_text().replace("**", "").split())
        for rule, (where, says) in CHECK.RULES.items():
            for piece in says.split(" ... "):
                with self.subTest(rule=rule, piece=piece):
                    self.assertIn(piece, skill)

    def test_the_script_is_safe_to_run(self):
        source = CHECK_PATH.read_text()
        self.assertIsNone(re.search(r"urllib|requests|socket|subprocess|os\.system|eval\(|exec\(|write_text|\.write\(", source))
        tree = ast.parse(source)
        imported = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        imported |= {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertLessEqual(imported, set(sys.stdlib_module_names))
        called = {getattr(node.func, "id", None) or getattr(node.func, "attr", None)
                  for node in ast.walk(tree) if isinstance(node, ast.Call)}
        self.assertFalse(called & {"open", "write_text", "write_bytes", "mkdir", "touch", "unlink", "rmdir", "rename"})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "letter.txt"
            path.write_text(CLEAN)
            before = sorted(Path(directory).rglob("*"))
            subprocess.run([sys.executable, str(CHECK_PATH), str(path), "--source", str(path), "--json"],
                           cwd=directory, capture_output=True, text=True)
            self.assertEqual(sorted(Path(directory).rglob("*")), before)

    def test_negative_control_detects_a_removed_check(self):
        source = CHECK_PATH.read_text()
        self.assertIn('DASH = re.compile(r"[—–]")', source)
        with tempfile.TemporaryDirectory() as directory:
            mutated = Path(directory) / "letter_check.py"
            mutated.write_text(source.replace('DASH = re.compile(r"[—–]")', 'DASH = re.compile(r"nevermatchthis")'))
            environment = os.environ.copy()
            environment["LETTER_CHECK_PATH"] = str(mutated)
            result = subprocess.run([
                sys.executable, "-m", "unittest", "test_letter_check.LetterCheckTests.test_em_and_en_dashes", "-v",
            ], cwd=REPO / "tests", env=environment, capture_output=True, text=True)
        raw = result.stdout + result.stderr
        self.assertEqual(result.returncode, 1, raw)
        self.assertIn("FAILED", raw)


if __name__ == "__main__":
    unittest.main()
