import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
LINT_PATH = Path(os.environ.get("SLOP_LINT_PATH") or REPO / "skills/slop-scrub/slop_lint.py")
SKILL = REPO / "skills/slop-scrub/SKILL.md"
SPEC = importlib.util.spec_from_file_location("slop_lint", LINT_PATH)
LINT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LINT)


class SlopLintTests(unittest.TestCase):
    def assert_pattern(self, pattern, positives, negatives):
        for text in positives:
            with self.subTest(positive=text):
                matches = [f for f in LINT.lint(text, SKILL) if f["pattern"] == pattern]
                self.assertTrue(matches, pattern + " missed: " + text)
                self.assertTrue(all(isinstance(f["item"], int) for f in matches))
        for text in negatives:
            with self.subTest(negative=text):
                self.assertFalse([f for f in LINT.lint(text, SKILL) if f["pattern"] == pattern])

    def test_every_banned_word_is_read_from_the_skill_and_caught(self):
        words = LINT.banned_words(SKILL)
        self.assertGreater(len(words), 40)
        for word in words:
            with self.subTest(word=word):
                findings = LINT.lint("The draft says " + word + " here.", SKILL)
                self.assertTrue(any(f["item"] == 1 and f["severity"] == "kill" for f in findings))
        with tempfile.TemporaryDirectory() as directory:
            skill = Path(directory) / "SKILL.md"
            skill.write_text(SKILL.read_text().replace("**Banned words:**\n", "**Banned words:**\nplantedword, "))
            self.assertTrue(LINT.lint("A plantedword appears.", skill))

    def test_dashes(self):
        self.assert_pattern("fancy-dash", ["A—B.", "A–B."], ["A-B.", "A, B."])

    def test_negative_parallel(self):
        self.assert_pattern("negative-parallel", [
            "Not just a tool, but a partner.", "Not only a file, but also a record.",
            "This isn't a tool. It is a partner.", "It's not a tool, it's a partner.",
        ], ["The file is ready, but the folder is empty.", "Only the owner can approve it."])

    def test_construction_shapes(self):
        self.assert_pattern("no-no-just", ["No files. No folders. Just work.", "No calls. No waits. Just results."],
                            ["There are no files in the folder."])
        self.assert_pattern("self-question", ["What does that mean? It means work.", "And what does that mean? That means time."],
                            ["What does that file contain?"])
        self.assert_pattern("preloaded-transition", ["Here's the thing: it works.", "But here's the kicker: it failed."],
                            ["Here's the file you asked for."])
        self.assert_pattern("three-part-list", ["It is fast, flexible, and cheap.", "They offer pens, books and paper."],
                            ["They offer pens and paper."])
        self.assert_pattern("dismissive-with", ["An app with a logo and a page.", "A company with a name and a website."],
                            ["An app with offline access."])
        self.assert_pattern("drumroll", ["Here's why this matters: the file is gone.", "The crazy thing is: it works."],
                            ["Here's why the file is gone."])

    def test_dressed_up_verbs(self):
        self.assert_pattern("dressed-up-verb", [
            "It serves as a reminder.", "The page functions as a portal.",
            "The app features a calendar.", "The hall boasts a balcony.",
            "It stands as a marker.", "It acts as a bridge.", "It represents a shift.",
        ], ["She serves soup.", "The features are listed below.", "These features saved me time."])

    def test_unnamed_authorities(self):
        self.assert_pattern("unnamed-authority", [
            "Experts say the change helps.", "Studies show a difference.",
            "Research suggests it works.", "Many believe the claim.",
        ], ["NASA studies show a difference.", "Studies show a difference, according to NASA.",
            "Research by Patel suggests a difference."])

    def test_caveats(self):
        self.assert_pattern("unneeded-caveat", [
            "It is important to note that the file exists.", "It is worth mentioning that I agree.",
            "While results may vary, try it.",
        ], ["It is important to label the switch.", "The results vary with temperature."])

    def test_assistant_residue(self):
        self.assert_pattern("assistant-residue", [
            "As an AI, I cannot attend.", "I hope this helps.", "Great question!",
            "Certainly, I can do that.", "Let me know if you would like another version.",
            "Here is a revised version of the note.",
        ], ["Please let us know when you arrive.", "Her question was about the file."])

    def test_staccato_and_same_length_runs(self):
        self.assert_pattern("staccato-run", [
            "The file changed. The test failed. The build stopped.",
            "The note is ready. The reply is late.",
        ], ["The file changed, so the test failed.", "- The file changed.\n- The test failed.\n- The build stopped."])
        self.assert_pattern("same-length-run", [
            "I put the file here. You left the book there. We read the note together.",
            "I moved the notes into the folder after the meeting ended on Monday morning. "
            "She sent the files to the client before the office closed on Friday evening. "
            "We checked the totals against the invoice before the report went out that afternoon.",
        ], ["I checked. The invoice had arrived after lunch, so I called the supplier to ask about the missing boxes. It took an hour.",
            "- I put the file here.\n- You left the book there.\n- We read the note together."])

    def test_item_13_structural_checks(self):
        self.assert_pattern("stacked-clause", [
            "I reviewed the billing logs on Tuesday morning and pulled every duplicate line item "
            "out of the monthly statement, which showed where the import script failed, so I fixed "
            "the parser right away and then reprocessed the whole batch before noon.",
        ], [
            "I reviewed the billing logs on Tuesday morning and pulled every duplicate line item out.",
            "Our regional branches tracked daily bread and butter inventory totals in a shared workbook "
            "every afternoon from April through October and then checked the numbers on Friday morning "
            "before anyone sent out the weekly summary.",
            "- I reviewed the billing logs on Tuesday morning and pulled every duplicate line item "
            "out of the monthly statement, which showed where the import script failed, so I fixed "
            "the parser right away and then reprocessed the whole batch before noon.",
        ])
        self.assert_pattern("participial-tail", [
            "I rebuilt the vendor intake queue last spring, cutting approval errors by 30%.",
            "Our team updated the checkout page in May, covering the changes we shipped.",
            "I cleaned up the invoice queue last quarter, cutting invoice errors across twelve branch offices by 30% and saving four hours a week.",
        ], [
            "I rebuilt the vendor intake queue last spring and cut approval errors by 30%.",
            "- Rebuilt the vendor intake queue, cutting approval errors by 30%.",
        ])
        self.assert_pattern("transition-opener", [
            "Early on, nobody checked the regional queue.",
            "In addition, we updated the schedule on Thursday.",
            "To fix that, we moved the nightly job to noon.",
            "Using data to group accounts, I called the smaller branches first.",
            "By grouping accounts by region, we cut setup time.",
        ], [
            "On Tuesday morning, nobody checked the regional queue.",
            "By Tuesday, I finished the monthly close check.",
            "By then, he left the branch office.",
            "# Early on, nobody checked the queue.",
        ])
        self.assert_pattern("parallel-paragraph-opener", [
            "From 2021 to 2024 at Acme I ran weekly billing checks for five branches.\n\n"
            "From 2018 to 2021 at Northwind I handled regional onboarding across twelve stores.",
            "I'm sure the weekly audit caught every duplicate line in April.\n\n"
            "I’m sure the monthly billing export fixed the remaining totals in May.",
            "Your posting asks for someone who has shipped billing integrations at scale.\n\n"
            "Your posting asks for an operator who knows how finance teams close the books.",
        ], [
            "At Acme I ran weekly billing checks for five branches from 2021 to 2024.\n\n"
            "Before that I handled regional onboarding across twelve stores at Northwind.",
            "From 2021 to 2024 at Acme I ran weekly billing checks.\n\n"
            "## Next section\n\n"
            "From 2018 to 2021 at Northwind I handled regional onboarding.",
        ])
        self.assert_pattern("parallel-paragraph-closer", [
            "In May our team migrated the legacy reporting jobs before the quarterly audit wrapped up last week.\n\n"
            "In June another team rewrote the invoice export pipeline after the vendor integration wrapped up last week.",
        ], [
            "In May our team migrated the legacy reporting jobs before the quarterly audit.\n\n"
            "In June another team rewrote the invoice export pipeline after the vendor release.",
        ])

    def test_human_controls_have_no_kill_findings(self):
        controls = sorted((REPO / "tests/fixtures/human").glob("*.txt"))
        self.assertGreaterEqual(len(controls), 3)
        self.assertLessEqual(len(controls), 5)
        for path in controls:
            with self.subTest(path=path.name):
                header, body = path.read_text().split("\n", 1)
                self.assertIn("https://", header)
                self.assertIn("License:", header)
                self.assertGreater(len(body.split()), 60)
                self.assertFalse([f for f in LINT.lint(body, SKILL) if f["severity"] == "kill"])

    def test_cli_stdin_file_json_and_exit_codes(self):
        for text, code in (("The invoice arrived on Monday.", 0), ("Great question!", 1), ("", 2)):
            with self.subTest(text=text):
                result = subprocess.run([sys.executable, str(LINT_PATH), "--json"], input=text,
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, code, result.stderr)
                if code != 2:
                    self.assertIsInstance(json.loads(result.stdout), list)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "prose.txt"
            path.write_text("As an AI, I can't join.")
            result = subprocess.run([sys.executable, str(LINT_PATH), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn("item 14", result.stdout)
            path.write_bytes(b"\xff")
            result = subprocess.run([sys.executable, str(LINT_PATH), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            result = subprocess.run([sys.executable, str(LINT_PATH), str(path.with_name("missing.txt"))], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)

    def test_negative_control_detects_removed_pattern(self):
        source = LINT_PATH.read_text()
        self.assertIn(r"as\s+an\s+AI\b", source)
        with tempfile.TemporaryDirectory() as directory:
            mutated = Path(directory) / "slop_lint.py"
            mutated.write_text(source.replace(r"as\s+an\s+AI\b", "nevermatchthisphrase"))
            environment = os.environ.copy()
            environment["SLOP_LINT_PATH"] = str(mutated)
            result = subprocess.run([
                sys.executable, "-m", "unittest", "test_slop_lint.SlopLintTests.test_assistant_residue", "-v",
            ], cwd=REPO / "tests", env=environment, capture_output=True, text=True)
        raw = result.stdout + result.stderr
        evidence = os.environ.get("SLOP_LINT_TEST_EVIDENCE")
        if evidence:
            Path(evidence).write_text(raw)
        self.assertEqual(result.returncode, 1, raw)
        self.assertIn("assistant-residue missed: As an AI", raw)


if __name__ == "__main__":
    unittest.main()
