from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
CHECK_PATH = REPO / "skills/slop-scrub/anchor_check.py"

RAW = (
    "so the bakery thing. we opened at 6 and the oven was already dead, like completly dead. "
    "i called dana bc she fixed it last time. she showed up in 20 minutes with a toolbox and a coffee. "
    "turned out the breaker tripped. we sold 140 loaves anyway, which i still dont get. "
    "honestly i dont want a new oven or a loan from the bank this year."
)
AUTHOR_BODY = (
    "We opened at 6 and the oven was already dead, completely dead. "
    "I called Dana because she fixed it last time. "
    "She showed up in 20 minutes with a toolbox and a coffee. "
    "We sold 140 loaves anyway, which I still don't get."
)
ONE_PLAIN_FACT = "The bakery is on Mill Street."
THREE_ADDED_SENTENCES = (
    "The bakery is on Mill Street. It has traded there for eleven years. "
    "The oven is a deck oven that the first owner bought second-hand."
)


class AnchorCheckTests(unittest.TestCase):
    def run_check(self, piece, *extra):
        with tempfile.TemporaryDirectory(prefix="anchor-") as directory:
            raw_path = Path(directory) / "raw.txt"
            piece_path = Path(directory) / "piece.txt"
            raw_path.write_text(RAW)
            piece_path.write_text(piece)
            return subprocess.run(
                [sys.executable, str(CHECK_PATH), str(raw_path), str(piece_path), *extra],
                capture_output=True, text=True,
            )

    def test_one_added_fact_passes_and_is_marked_as_the_editors(self):
        result = self.run_check(AUTHOR_BODY + "\n\n" + ONE_PLAIN_FACT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("YOURS, whole sentence", result.stdout)
        self.assertIn("PASS", result.stdout)

    def test_too_many_added_sentences_fail_the_cap(self):
        result = self.run_check(AUTHOR_BODY + "\n\n" + THREE_ADDED_SENTENCES)
        self.assertEqual(result.returncode, 1)
        self.assertIn("over the cap of 25", result.stdout)

    def test_a_higher_cap_lets_the_same_piece_pass(self):
        result = self.run_check(AUTHOR_BODY + "\n\n" + THREE_ADDED_SENTENCES, "--cap", "60")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_negation_cut_from_the_authors_sentence_fails(self):
        result = self.run_check(AUTHOR_BODY + " Honestly I want a new oven or a loan from the bank this year.")
        self.assertEqual(result.returncode, 1)
        self.assertIn("CUT A NEGATION", result.stdout)

    def test_the_last_line_says_whether_the_piece_opens_or_closes_on_the_editor(self):
        result = self.run_check(ONE_PLAIN_FACT + "\n\n" + AUTHOR_BODY)
        self.assertIn("first or last sentence yours: 1 of 2", result.stdout)

    def test_a_missing_file_is_bad_input(self):
        result = subprocess.run(
            [sys.executable, str(CHECK_PATH), "/nonexistent/raw.txt", "/nonexistent/piece.txt"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("Could not read a file", result.stderr)

    def test_skill_and_guide_name_the_mode_and_the_counter(self):
        for name in ("skills/slop-scrub/SKILL.md", "docs/slop-scrub.md"):
            with self.subTest(name=name):
                text = (REPO / name).read_text()
                self.assertIn("Anchor mode", text)
                self.assertIn("anchor_check.py", text)


if __name__ == "__main__":
    unittest.main()
