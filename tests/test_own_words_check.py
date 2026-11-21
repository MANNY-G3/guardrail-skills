import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
CHECK_PATH = REPO / "skills/slop-scrub/own_words_check.py"
SPEC = importlib.util.spec_from_file_location("own_words_check", CHECK_PATH)
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)

RAW = (
    "so the bakery thing. we opened at 6 and the oven was already dead, like completly dead. "
    "i called dana bc she fixed it last time. she showed up in 20 minutes with a toolbox and a coffee. "
    "turned out the breaker tripped. we sold 140 loaves anyway, which i still dont get. "
    "honestly i dont want a new oven or a loan from the bank this year."
)
SCISSORS_EDIT = (
    "We opened at 6 and the oven was already dead, completely dead. "
    "I called Dana because she fixed it last time. "
    "She showed up in 20 minutes with a toolbox and a coffee. "
    "We sold 140 loaves anyway, which I still don't get."
)
WRITTEN_SENTENCE = "It was a morning that tested our resilience and reminded us why community matters."


def rows_for(edited):
    return CHECK.check(RAW, edited)


def added_words(edited):
    return [word for row in rows_for(edited) for word in row["added"]]


class OwnWordsCheckTests(unittest.TestCase):
    def test_cuts_typo_fixes_and_shorthand_add_nothing(self):
        self.assertEqual(added_words(SCISSORS_EDIT), [])

    def test_reordered_sentences_add_nothing(self):
        reordered = "We sold 140 loaves anyway, which I still don't get. Turned out the breaker tripped."
        self.assertEqual(added_words(reordered), [])

    def test_a_swapped_word_is_counted(self):
        self.assertEqual(added_words("We opened at 6 and the oven was already broken."), ["broken"])

    def test_a_fixed_typo_is_listed_for_the_author(self):
        rows = rows_for("The oven was already dead, completely dead.")
        self.assertEqual(rows[0]["added"], [])
        self.assertEqual(rows[0]["respelled"], [("completly", "completely")])

    def test_a_changed_number_is_counted(self):
        self.assertEqual(added_words("We sold 190 loaves anyway, which I still don't get."), ["190"])

    def test_a_written_sentence_counts_in_full(self):
        rows = rows_for(SCISSORS_EDIT + " " + WRITTEN_SENTENCE)
        self.assertTrue(rows[-1]["written_by_editor"])
        self.assertEqual(len(rows[-1]["added"]), rows[-1]["count"])
        self.assertFalse(any(row["written_by_editor"] for row in rows[:-1]))

    def test_joining_two_of_the_authors_sentences_costs_only_the_joiner(self):
        joined = "I called Dana because she fixed it last time, and she showed up in 20 minutes with a toolbox and a coffee."
        self.assertEqual(added_words(joined), ["and"])

    def test_a_stray_common_word_is_not_excused(self):
        self.assertEqual(added_words("Turned out the breaker tripped at the bakery."), ["at", "the", "bakery"])

    def test_a_negation_cut_from_inside_a_sentence_is_caught(self):
        reversed_meaning = rows_for("Honestly I want a new oven or a loan from the bank this year.")
        self.assertEqual(reversed_meaning[0]["added"], [])
        self.assertEqual(reversed_meaning[0]["lost_negations"], ["dont"])

    def test_a_negation_in_a_clause_that_was_cut_whole_is_not_flagged(self):
        kept_tail = rows_for("We sold 140 loaves anyway.")
        self.assertEqual(kept_tail[0]["lost_negations"], [])

    def test_a_kept_tail_clause_is_not_blamed_for_negations_in_the_part_cut_whole(self):
        raw = (
            "if you dont think you can bake, i dont know what to tell you, "
            "so maybe you need to hear this: you can do all of this for 500 a year."
        )
        tail_only = CHECK.check(raw, "You can do all of this for 500 a year.")
        self.assertEqual(tail_only[0]["added"], [])
        self.assertEqual(tail_only[0]["lost_negations"], [])
        reversed_meaning = CHECK.check(raw, "If you think you can bake, I know what to tell you.")
        self.assertEqual(reversed_meaning[0]["lost_negations"], ["dont", "dont"])

    def test_cli_exit_codes_and_reasons(self):
        with tempfile.TemporaryDirectory(prefix="own-words-") as directory:
            raw_path = Path(directory) / "raw.txt"
            raw_path.write_text(RAW)

            def run(edited, *extra):
                edited_path = Path(directory) / "edited.txt"
                edited_path.write_text(edited)
                return subprocess.run(
                    [sys.executable, str(CHECK_PATH), str(raw_path), str(edited_path), *extra],
                    capture_output=True, text=True,
                )

            good = run(SCISSORS_EDIT)
            self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
            self.assertIn("PASS", good.stdout)

            padded = run(SCISSORS_EDIT + " " + WRITTEN_SENTENCE)
            self.assertEqual(padded.returncode, 1)
            self.assertIn("a sentence the author did not write", padded.stdout)
            self.assertEqual(run(SCISSORS_EDIT + " " + WRITTEN_SENTENCE, "--cap", "90").returncode, 1)

            swapped = run("We opened at 6 and the oven was already broken, totally and fully broken.")
            self.assertEqual(swapped.returncode, 1)
            self.assertIn("over the cap", swapped.stdout)
            self.assertEqual(run("We opened at 6 and the oven was already broken.", "--cap", "20").returncode, 0)

            reversed_meaning = run("Honestly I want a new oven or a loan from the bank this year.")
            self.assertEqual(reversed_meaning.returncode, 1)
            self.assertIn("CUT A NEGATION", reversed_meaning.stdout)

            missing = subprocess.run(
                [sys.executable, str(CHECK_PATH), str(raw_path), str(Path(directory) / "missing.txt")],
                capture_output=True, text=True,
            )
            self.assertEqual(missing.returncode, 2)
            self.assertIn("Could not read a file", missing.stderr)

    def test_skill_and_readme_name_the_mode_and_the_checker(self):
        for name in ("skills/slop-scrub/SKILL.md", "README.md"):
            with self.subTest(name=name):
                text = (REPO / name).read_text()
                self.assertIn("Own-words mode", text)
                self.assertIn("own_words_check.py", text)


if __name__ == "__main__":
    unittest.main()
