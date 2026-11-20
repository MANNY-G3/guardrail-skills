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

    def test_readme_example_matches_saved_raw_and_scrubbed_bodies(self):
        readme = (REPO / "README.md").read_text()
        before = readme.split("**Before: unedited AI draft**", 1)[1].split("**After: the new checklist**", 1)[0]
        after = readme.split("**After: the new checklist**", 1)[1].split("The edit keeps", 1)[0]
        for excerpt, path in ((before, AI / "challenge/blog-intro.txt"),
                              (after, REPO / "examples/slop-scrub-after.txt")):
            with self.subTest(path=path):
                body = "\n".join(re.sub(r"^> ?", "", line) for line in excerpt.splitlines()
                                 if line.startswith(">"))
                self.assertEqual(body.strip(), path.read_text().strip())
                if path.name == "slop-scrub-after.txt":
                    self.assertGreaterEqual(len(body.strip()), 250)

    def test_readme_human_example_matches_saved_opening_paragraphs(self):
        readme = (REPO / "README.md").read_text()
        before = readme.split("**Before (human original)**", 1)[1].split("**After (current checklist)**", 1)[0]
        after = readme.split("**After (current checklist)**", 1)[1].split("The edit moves", 1)[0]
        for excerpt, name in ((before, "slop-scrub-human-before.txt"),
                              (after, "slop-scrub-human-after.txt")):
            with self.subTest(name=name):
                body = "\n".join(re.sub(r"^> ?", "", line) for line in excerpt.splitlines()
                                 if line.startswith(">"))
                saved = (REPO / "examples" / name).read_text().strip()
                self.assertEqual(body.strip(), saved.split("\n\n", 1)[0])
                self.assertIn("(examples/" + name + ")", excerpt)


if __name__ == "__main__":
    unittest.main()
