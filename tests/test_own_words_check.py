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
    "turned out the breaker tripped. we sold 140 loaves anyway, which i still dont get."
)
SCISSORS_EDIT = (
    "We opened at 6 and the oven was already dead, completely dead. "
    "I called Dana because she fixed it last time. "
    "She showed up in 20 minutes with a toolbox and a coffee. "
    "We sold 140 loaves anyway, which I still don't get."
)
WRITTEN_SENTENCE = "It was a morning that tested our resilience and reminded us why community matters."


def added_words(edited):
    return [word for _, _, left_over in CHECK.check(RAW, edited) for word in left_over]


class OwnWordsCheckTests(unittest.TestCase):
    def test_cuts_typo_fixes_and_shorthand_add_nothing(self):
        self.assertEqual(added_words(SCISSORS_EDIT), [])

    def test_reordered_sentences_add_nothing(self):
        reordered = "We sold 140 loaves anyway, which I still don't get. Turned out the breaker tripped."
        self.assertEqual(added_words(reordered), [])

    def test_a_swapped_word_is_counted(self):
        self.assertEqual(added_words("We opened at 6 and the oven was already broken."), ["broken"])

    def test_a_written_sentence_is_counted(self):
        added = added_words(SCISSORS_EDIT + " " + WRITTEN_SENTENCE)
        self.assertGreaterEqual(len(added), 10)
        self.assertIn("resilience", added)

    def test_joining_two_of_the_authors_sentences_costs_only_the_joiner(self):
        joined = "I called Dana because she fixed it last time, and she showed up in 20 minutes with a toolbox and a coffee."
        self.assertEqual(added_words(joined), ["and"])

    def test_a_stray_common_word_is_not_excused(self):
        self.assertEqual(added_words("Turned out the breaker tripped at the bakery."), ["at", "the", "bakery"])

    def test_cli_exit_codes_and_cap(self):
        with tempfile.TemporaryDirectory(prefix="own-words-") as directory:
            raw_path = Path(directory) / "raw.txt"
            good_path = Path(directory) / "good.txt"
            padded_path = Path(directory) / "padded.txt"
            raw_path.write_text(RAW)
            good_path.write_text(SCISSORS_EDIT)
            padded_path.write_text(SCISSORS_EDIT + " " + WRITTEN_SENTENCE)

            def run(*arguments):
                return subprocess.run([sys.executable, str(CHECK_PATH), *arguments], capture_output=True, text=True)

            good = run(str(raw_path), str(good_path))
            self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
            self.assertIn("PASS", good.stdout)
            padded = run(str(raw_path), str(padded_path))
            self.assertEqual(padded.returncode, 1)
            self.assertIn("OVER THE CAP", padded.stdout)
            self.assertEqual(run(str(raw_path), str(padded_path), "--cap", "40").returncode, 0)
            missing = run(str(raw_path), str(Path(directory) / "missing.txt"))
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
