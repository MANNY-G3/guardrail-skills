"""Measure saved scrub outputs without models, network calls or detector scores."""

import argparse
import importlib.util
import json
from pathlib import Path
import re


REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("slop_lint", REPO / "skills/slop-scrub/slop_lint.py")
LINT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LINT)
AI = REPO / "tests/fixtures/ai"
HUMAN = REPO / "tests/fixtures/human"


def words(text):
    return re.findall(r"\b\w+(?:['’]\w+)*\b", text)


def word_edits(before, after):
    a, b = words(before), words(after)
    row = list(range(len(b) + 1))
    for i, left in enumerate(a, 1):
        next_row = [i]
        for j, right in enumerate(b, 1):
            next_row.append(min(row[j] + 1, next_row[j - 1] + 1,
                                row[j - 1] + (left != right)))
        row = next_row
    return {"original_words": len(a), "edited_words": len(b), "word_edits": row[-1],
            "share_changed": row[-1] / len(a) if a else 0}


def evaluate(ai_dir=AI):
    drafts = []
    ai_dir = Path(ai_dir)
    for raw in sorted(ai_dir.glob("*.txt")):
        facts = json.loads(raw.with_suffix(".facts.json").read_text())
        versions = {"before": raw.read_text(),
                    "old": (ai_dir / "old" / raw.name).read_text(),
                    "new": (ai_dir / "new" / raw.name).read_text()}
        record = {"file": raw.name, "versions": {}}
        for version, text in versions.items():
            findings = LINT.lint(text)
            numbers = re.findall(r"\b\d[\d,.]*\b", text)
            allowed_numbers = {str(number) for number in facts["allowed_numbers"]}
            record["versions"][version] = {
                "words": len(words(text)), "hits": len(findings),
                "kill_hits": sum(f["severity"] == "kill" for f in findings),
                "numbers_outside_facts": [n for n in numbers if n not in allowed_numbers],
                "findings": findings,
            }
        record["new_has_fewer_hits"] = record["versions"]["new"]["hits"] < record["versions"]["old"]["hits"]
        record["new_improves_raw"] = record["versions"]["new"]["hits"] < record["versions"]["before"]["hits"]
        drafts.append(record)
    controls = []
    for after in sorted((HUMAN / "new").glob("*.txt")):
        before_text = (HUMAN / after.name).read_text().split("\n", 1)[1]
        after_text = after.read_text()
        controls.append({"file": after.name, **word_edits(before_text, after_text),
                         "kill_hits": sum(f["severity"] == "kill" for f in LINT.lint(after_text))})
    improvements = sum(draft["new_has_fewer_hits"] for draft in drafts)
    return {
        "metric": "Mechanical lint findings",
        "name_audit": "Names require a separate human review against each fact file",
        "drafts": drafts, "human_controls": controls,
        "drafts_with_fewer_hits": improvements,
        "drafts_improved_from_raw": sum(draft["new_improves_raw"] for draft in drafts),
        "five_of_six_bar_met": len(drafts) == 6 and improvements >= 5,
        "new_zero_kill_bar_met": len(drafts) == 6 and all(
            d["versions"]["new"]["kill_hits"] == 0 for d in drafts),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ai-dir", type=Path, default=AI)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.ai_dir), ensure_ascii=False, indent=2))
