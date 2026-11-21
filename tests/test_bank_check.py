from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
CHECK_PATH = REPO / "skills/slop-scrub/bank_check.py"

BANK_ONE = (
    "The bar for baking good bread at home has never been lower. "
    "Everyone wants to tell you that it's hard, so you should buy their mixer. Nonsense. "
    "The only things you need are a cast iron pot and a free afternoon."
)
BANK_TWO = "For the record, no shade to the bakery down the road, they earn their keep. That's literally it."
REWORKED = (
    "The bar for fixing your own bike has never been lower. "
    "Everyone wants to tell you that it's hard, so you should buy their stand. Nonsense. "
    "The only things you need are a set of hex keys and a free afternoon."
)
MODEL_WRITTEN = (
    "Bicycle maintenance is more approachable than most riders assume. "
    "With a modest toolkit and a little patience, routine repairs become a satisfying weekend habit."
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
        shuffled = "That's literally it. The only things you need are a set of hex keys and a free afternoon. For the record, no shade to the shop down the road, they earn their keep."
        result = self.run_check(shuffled, [BANK_ONE, BANK_TWO])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_each_sentence_gets_its_own_share(self):
        result = self.run_check(REWORKED + " " + MODEL_WRITTEN.split(". ")[0] + ".", [BANK_ONE], "--floor", "40")
        self.assertIn("  0% author's | Bicycle maintenance", result.stdout)

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
