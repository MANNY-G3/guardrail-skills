import json
import re
import unittest

from evaluate_scrubs import AI, HUMAN, REPO, evaluate, word_edits


class ScrubFixtureTests(unittest.TestCase):
    def test_raw_drafts_have_fact_lists_and_requested_lengths(self):
        paths = []
        for batch in (AI, AI / "challenge"):
            batch_paths = sorted(batch.glob("*.txt"))
            self.assertEqual(len(batch_paths), 6)
            paths.extend(batch_paths)
        for path in paths:
            with self.subTest(path=path.name):
                facts = json.loads(path.with_suffix(".facts.json").read_text())
                self.assertIn("AI-generated", facts["origin"])
                self.assertTrue(facts["facts"])
                self.assertGreaterEqual(len(path.read_text().split()), 150)
                self.assertLessEqual(len(path.read_text().split()), 350)
                allowed = {str(number) for number in facts["allowed_numbers"]}
                for version in (path, path.parent / "old" / path.name, path.parent / "new" / path.name):
                    numbers = re.findall(r"\b\d[\d,.]*\b", version.read_text())
                    self.assertTrue(all(n in allowed for n in numbers))

    def test_new_scrubs_have_no_kill_findings(self):
        for batch in (AI, AI / "challenge"):
            report = evaluate(batch)
            self.assertEqual(len(report["drafts"]), 6)
            for draft in report["drafts"]:
                with self.subTest(batch=batch.name, draft=draft["file"]):
                    self.assertEqual(draft["versions"]["new"]["kill_hits"], 0)
                    self.assertEqual(draft["versions"]["new"]["numbers_outside_facts"], [])
            self.assertEqual(report["metric"], "Mechanical lint findings")

    def test_two_human_controls_and_edit_metric(self):
        report = evaluate()
        self.assertEqual(len(report["human_controls"]), 2)
        for control in report["human_controls"]:
            with self.subTest(control=control["file"]):
                self.assertEqual(control["kill_hits"], 0)
                self.assertTrue((HUMAN / control["file"]).is_file())
        for before, after, edits in (("A red book", "A blue book", 1),
                                     ("A red book", "A book", 1),
                                     ("A book", "A red book", 1),
                                     ("A book", "A book", 0)):
            with self.subTest(before=before, after=after):
                self.assertEqual(word_edits(before, after)["word_edits"], edits)

    def test_readme_examples_match_the_saved_texts(self):
        readme = (REPO / "README.md").read_text()
        quotes, current = [], []
        for line in readme.splitlines() + [""]:
            if line.startswith(">"):
                current.append(re.sub(r"^> ?", "", line))
            elif current:
                quotes.append("\n".join(current).strip())
                current = []
        for name in ("no-writing-before.txt", "no-writing-after.txt",
                     "your-writing-before.txt", "your-writing-after.txt"):
            with self.subTest(name=name):
                self.assertIn((REPO / "examples" / name).read_text().strip(), quotes)
                self.assertIn("(examples/" + name + ")", readme)
        for name in ("comment-scrub-before.py", "comment-scrub-after.py"):
            with self.subTest(name=name):
                code = (REPO / "examples" / name).read_text().strip()
                self.assertIn("```python\n" + code + "\n```", readme)

    def test_readme_keeps_problem_proof_use_and_stays_short(self):
        readme = (REPO / "README.md").read_text()
        self.assertLessEqual(len(readme.splitlines()), 250)
        self.assertIn("## Safe to run", readme)
        for heading in ("## slop-scrub", "## comment-scrub", "## Orchestration recipe hook"):
            with self.subTest(heading=heading):
                section = readme.split(heading + "\n", 1)[1].split("\n## ", 1)[0]
                marks = [section.find(mark) for mark in ("**The problem.**", "### Proof", "### Use it")]
                self.assertNotIn(-1, marks)
                self.assertEqual(marks, sorted(marks))


if __name__ == "__main__":
    unittest.main()
