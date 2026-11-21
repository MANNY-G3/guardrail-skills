from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
CHECK_PATH = REPO / "skills/slop-scrub/bank_check.py"

BANK_ONE = (
    "I started keeping bees the year my knees gave out on me. "
    "Nobody warns you that a hive weighs as much as a small fridge, so plan on a second pair of hands. Fine by me. "
    "All it takes is a smoker, a veil and a neighbor who owes you a favor."
)
BANK_TWO = "To be fair to the club down in Marlow, they lent me the extractor twice. And that was that."
REWORKED = (
    "I started keeping chickens the year my knees gave out on me. "
    "Nobody warns you that a coop weighs as much as a small fridge, so plan on a second pair of hands. Fine by me. "
    "All it takes is a feeder, a fence and a neighbor who owes you a favor."
)
MODEL_WRITTEN = (
    "Backyard poultry is more approachable than most newcomers assume. "
    "With a modest budget and a little patience, daily care becomes a satisfying morning habit."
)


class BankCheckTests(unittest.TestCase):
    def run_check(self, piece, banks, *extra):
        with tempfile.TemporaryDirectory(prefix="bank-") as directory:
            piece_path = Path(directory) / "piece.txt"
            piece_path.write_text(piece)
            bank_paths = []
            for number, bank in enumerate(banks):
                bank_path = Path(directory) / f"bank{number}.txt"
                bank_path.write_text(bank)
                bank_paths.append(str(bank_path))
            return subprocess.run(
                [sys.executable, str(CHECK_PATH), str(piece_path), *bank_paths, *extra],
                capture_output=True, text=True,
            )

    def test_a_piece_reworked_from_the_bank_passes(self):
        result = self.run_check(REWORKED, [BANK_ONE])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_a_piece_in_the_models_own_words_fails(self):
        result = self.run_check(MODEL_WRITTEN, [BANK_ONE])
        self.assertEqual(result.returncode, 1)
        self.assertIn("under the floor of 60", result.stdout)

    def test_sentences_may_come_from_several_pieces_in_any_order(self):
        shuffled = "And that was that. All it takes is a feeder, a fence and a neighbor who owes you a favor. To be fair to the club down in Dover, they lent me the extractor twice."
        result = self.run_check(shuffled, [BANK_ONE, BANK_TWO])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_each_sentence_gets_its_own_share(self):
        result = self.run_check(REWORKED + " " + MODEL_WRITTEN.split(". ")[0] + ".", [BANK_ONE], "--floor", "40")
        self.assertIn("  0% author's | Backyard poultry", result.stdout)

    def test_a_raised_floor_can_fail_a_piece_that_passed(self):
        self.assertEqual(self.run_check(REWORKED, [BANK_ONE], "--floor", "95").returncode, 1)

    def test_missing_and_empty_inputs_are_bad_input(self):
        missing = subprocess.run(
            [sys.executable, str(CHECK_PATH), "/nonexistent/piece.txt", "/nonexistent/bank.txt"],
            capture_output=True, text=True,
        )
        self.assertEqual(missing.returncode, 2)
        self.assertIn("Could not read a file", missing.stderr)
        empty_bank = self.run_check(REWORKED, ["two words"])
        self.assertEqual(empty_bank.returncode, 2)
        self.assertIn("too few words", empty_bank.stderr)

    def test_skill_and_readme_name_the_mode_and_the_counter(self):
        for name in ("skills/slop-scrub/SKILL.md", "README.md"):
            with self.subTest(name=name):
                text = (REPO / name).read_text()
                self.assertIn("Sentence-bank mode", text)
                self.assertIn("bank_check.py", text)


if __name__ == "__main__":
    unittest.main()
