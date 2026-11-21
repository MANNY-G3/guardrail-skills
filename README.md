# guardrail-skills

Three small, independent guardrails for AI coding agents. Each one works two ways: as a **skill** (the agent decides when to run it) or as a **hook** (your tooling forces it to run every time, whether the agent remembers or not). Neither mode requires Claude Code specifically; see the install notes under each one.

## slop-scrub

Use the 14 checks to verify claims against their sources and find details the draft needs from its author. The checklist also catches repetitive sentences and wording that gets in the reader's way.

### Example: an unedited AI draft

A fresh AI writer produced this first draft from fictional project notes, without loading either checklist. The draft was frozen before the scrub runs. Both edits used the same notes, with no voice sample.

- [Raw draft](tests/fixtures/ai/challenge/blog-intro.txt)
- [Supplied facts](tests/fixtures/ai/challenge/blog-intro.facts.json)

The notes describe Nora Ellis coordinating 12 volunteers at Portside Archive in Charleston. They inventoried 640 boxes over 2 Saturdays, found 37 duplicate labels, spent 18 hours relabeling, and photographed every shelf.

**Before: unedited AI draft**

> There is something satisfying about making a collection easier to navigate, especially when the work is shared. At Portside Archive in Charleston, Nora Ellis coordinated a volunteer cataloguing project that brought that idea into focus. The inventory covered 640 boxes, with 12 volunteers working across 2 Saturdays. Along the way, the team found 37 duplicate box labels, took 18 hours in total to relabel them, and photographed every shelf.
>
> Those details offer a vivid picture of the care behind an inventory. A label is a small thing, but it is also a point of reference for anyone trying to understand where a box belongs. Photographs add another way to see the shelves, while the time spent relabeling shows the patient attention involved in making the records clearer.
>
> What stands out is the collective nature of the effort: volunteers giving their attention to the boxes, the labels, and the shelves as parts of the same project. It is an encouraging reminder that cataloguing is made up of tangible, deliberate actions. This project offers a chance to reflect on those actions and on the people who bring their care to the work.

**After: the new checklist**

> Volunteers found 37 duplicate box labels while inventorying 640 boxes at Portside Archive in Charleston. Relabeling took 18 hours in all.
>
> Nora Ellis coordinated the cataloguing project with 12 volunteers over 2 Saturdays, and the team photographed every shelf.

The edit keeps every supplied name and number while cutting claims about care and collective effort that add no fact. It replaces general commentary with the work the team did. This README version has 39 words and 261 characters, with mechanical findings falling from 2 to zero. It restores the cataloguing-project context from the notes; the saved benchmark retains the independent editor's 37-word output. These counts describe the local lint, not a detector verdict. [Copy the after text](examples/slop-scrub-after.txt) or inspect the [saved comparison](tests/fixtures/ai/challenge/evaluation.json).

### Example from a human author

David S. Ferriero's October 12, 2012 post “Celebrating Our Volunteers” is in the public domain as a work of the United States government. [Original post](https://aotus.blogs.archives.gov/2012/10/12/celebrating-our-volunteers/) · [National Archives copyright policy](https://www.archives.gov/global-pages/privacy.html#copyright)

**Before (human original)** · [Full original](examples/slop-scrub-human-before.txt)

> This week we had an opportunity to honor volunteers who contributed more than 100 hours of their time to the National Archives this year in our Washington and College Park locations—295 volunteers who contributed 42,284 hours! These amazing numbers demonstrate their love of history and the work that we do.

**After (current checklist)** · [Full edit](examples/slop-scrub-human-after.txt)

> This week we honored volunteers at our Washington and College Park locations who each gave more than 100 hours to the National Archives this year. The 295 volunteers contributed 42,284 hours in all. We’re grateful for their love of history and for the time they gave to our work.

The edit moves Ferriero's count of 295 volunteers and 42,284 hours into its own sentence and keeps his “we” and “our” as he thanks the volunteers. The editor worked from the passage without a separate voice sample.

**The banned-word list is a starting point, not a ruling.** You'll disagree with parts of it, and you should. `leverage` and `robust` have honest uses. Open `skills/slop-scrub/SKILL.md`, edit the list in item 1, and make it yours. Forking it into something opinionated about *your* writing is the intended use, not a misuse.

**Install as a skill**

Copy the entire `skills/slop-scrub/` folder, including `slop_lint.py`.

- **Claude Code.** For personal use, copy it to `~/.claude/skills/slop-scrub/` and run `/slop-scrub`. [Claude Code skills](https://code.claude.com/docs/en/skills)
- **Codex.** Copy it to `~/.agents/skills/slop-scrub/` for personal use or to `.agents/skills/slop-scrub/` in the project. Invoke it with `$slop-scrub` or select it from `/skills`. [Codex skills](https://learn.chatgpt.com/docs/build-skills)
- **Other tools.** Paste the text below the `---` frontmatter in `SKILL.md` into your system prompt or custom instructions.

Put two or three short samples approved by the author in the root voice guide (`VOICE.md`) with a reader description and any words or phrases the author avoids. The strongest basis for the edit is the author's own wording, supported by their facts and approved samples. The checklist cannot guarantee a detector verdict. [Voice guide template](examples/VOICE.md.template)

When the project has no voice guide, work from the person's original draft and notes, flagging any detail they still need to supply.

### Local lint

Give the linter a UTF-8 file or pipe text into standard input. Use `--json` for structured results.

```sh
python3 skills/slop-scrub/slop_lint.py draft.txt
python3 skills/slop-scrub/slop_lint.py --json < draft.txt
```

Exit status is `0` for a clean scan, `1` for findings, or `2` for bad input. Run the full checklist after the scan, since the linter cannot assess author voice or whether the claims are supported.

### Own-words mode

Give the skill your own rough words, such as a voice memo transcript, a brain dump or notes typed fast, and it edits with scissors. It cuts and reorders your sentences and fixes typos. It spells out shorthand, and it writes no new sentence, so the piece that comes back is made of sentences you wrote.

`own_words_check.py` counts the words in the edited piece that you did not type, and it fails the piece when more than 5 in 100 are new. It also fails a piece that holds a sentence you did not write, or one where a "not" or a "never" was cut from inside your sentence. Changed numbers count as new words, and every spelling fix is listed so you can see a swapped word.

```sh
python3 skills/slop-scrub/own_words_check.py raw.txt edited.txt
python3 skills/slop-scrub/own_words_check.py raw.txt edited.txt --cap 10
```

Exit status is `0` at or under the cap, `1` over it, or `2` for bad input.

### Anchor mode

Give the skill your own words plus a few facts and ask for a finished piece, or give it a piece you already wrote and ask for a new cut for a different reader. Your sentences stay as the body, kept together in whole paragraphs. The skill may add up to 25 words in every 100, and only plain ones: a fact you supplied, a number, a name, a short link between two of your points. It adds no summing-up and no commentary.

`anchor_check.py` prints which sentences are yours and which the editor added, and it fails the piece when the editor's share is over the cap or when a "not" or a "never" was cut from inside one of your sentences.

```sh
python3 skills/slop-scrub/anchor_check.py raw.txt piece.txt
python3 skills/slop-scrub/anchor_check.py raw.txt piece.txt --cap 15
```

Exit status is `0` at or under the cap, `1` over it, or `2` for bad input.

**As a hook:** see [`examples/pre-commit-hook.sh`](examples/pre-commit-hook.sh) or [`examples/github-actions.yml`](examples/github-actions.yml) for how to force it to run on every commit or PR instead of waiting for the agent to remember.

---

## comment-scrub

**What it is:** a checklist that catches code comments that restate the code, apologize for bad code, or bury a commit-message narrative in the source. Ships with `COMMENTS.md`, the underlying comment-hygiene standard it enforces.

**Why it was built:** AI agents tend to over-comment: narrating obvious lines, writing multi-paragraph "why this exists" essays inline, leaving commented-out code behind. The fix isn't "write fewer comments" as a vague instruction, it's a specific, repeatable check.

**Why it's useful:** code that reads clean, where every comment that survives is actually earning its place instead of restating what the code already says.

**Install as a skill**

Copy the entire `skills/comment-scrub/` folder so both `SKILL.md` and `COMMENTS.md` are available.

- **Claude Code.** For personal use, copy it to `~/.claude/skills/comment-scrub/` and run `/comment-scrub`.
- **Codex.** Copy it to `~/.agents/skills/comment-scrub/` for personal use or to `.agents/skills/comment-scrub/` in the project. Invoke it with `$comment-scrub` or select it from `/skills`.
- **Other tools.** Paste the `SKILL.md` body into your instructions and include `COMMENTS.md` if your tool supports a second reference file.

**As a hook:** same two examples as slop-scrub, this is the one you actually want on every commit. See [`examples/pre-commit-hook.sh`](examples/pre-commit-hook.sh).

---

## inject-orchestration-recipe.sh

A `UserPromptSubmit` hook for **Claude Code and Codex**. Both runtimes accept a JSON object with a `prompt` string on stdin and the `hookSpecificOutput.additionalContext` response below. The same script works in either tool; configuration and hook-trust steps differ.

The hook provides planning or execution instructions for the current job only. The time estimate tells the user how long the job is likely to take. Work continues within the user's authorization if the estimate runs over and ends when the requested result works. At each update and at completion, report how many turns you've used and how many seats you've started or resumed. Include tokens reread and minutes spent testing.

Give each fix to a fresh agent with a brief describing the finding and the files it affects. Include the test to run. Ask for independent review when a chunk touches a safeguard the user named or involves money, legal steps, messages to others, or another action that's hard to undo. Exercise changes the user will see or hear. Run focused tests for each chunk, inspect the saved logs, and keep any reusable test rig. Compare the agents planned with the agents that ran before closing each stage.

The recipe is model context. Agent limits and approval boundaries still depend on the agent following it and the runtime enforcing its permissions. This script neither launches agents nor intercepts pushes, deployments, or external writes. Keep your permission controls and spend-cap hooks enabled. Cloud model requests also use the network; a local workflow is not an offline workflow.

**Requirements:** Bash 3.2 or newer, `jq`, and standard `cat`, `grep`, and `tr` commands. Review the script before enabling it. Stop if managed policy disallows user hooks; do not change policy or bypass hook trust.

**Before installing:** back up each existing destination to the same name plus `.bak-orchestration`; never overwrite an existing backup. Resolve symlinks and preserve both the link and its target. Keep backups and machine-specific settings out of source control. These examples show entries to merge into your configuration, not replacement files. If installation or validation fails, stop, restore only this install's changes from the backups, and report the actual error output.

**Install (Claude Code):** copy the script to `~/.claude/hooks/inject-orchestration-recipe.sh`, make it executable, and merge this entry into `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [{ "type": "command", "command": "bash \"$HOME/.claude/hooks/inject-orchestration-recipe.sh\"" }] }
    ]
  }
}
```

Preserve all other settings and hooks. If this command is already registered, update its script without adding another registration. Validate the result with `jq empty ~/.claude/settings.json`. Check `/hooks` in Claude Code, then start a fresh session for the smoke test.

**Install (Codex):** copy the same script to `${CODEX_HOME:-$HOME/.codex}/hooks/inject-orchestration-recipe.sh`, make it executable, and merge this entry into `${CODEX_HOME:-$HOME/.codex}/hooks.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [{
          "type": "command",
          "command": "bash \"${CODEX_HOME:-$HOME/.codex}/hooks/inject-orchestration-recipe.sh\"",
          "additionalContextLimit": 8000
        }]
      }
    ]
  }
}
```

Preserve existing hooks, including spend controls. Codex also supports inline `[hooks]` configuration; use one representation per configuration layer to avoid duplicates. Validate `hooks.json` with `jq empty`, then open `/hooks` in the CLI or Settings > Hooks in the app to review and trust the new hook. Registration alone does not activate an untrusted hook. Do not edit stored trust hashes or use trust-bypass flags as an installation step.

Codex documents `additionalContextLimit` as an approximate token threshold with a default of 2,500 tokens. Set a positive integer for a limit or `0` for unlimited inline context. For output above the threshold, Codex saves the full output to disk and shows a preview. This example sets a conservative 8,000-token budget with room for recipe edits. [Codex hooks](https://learn.chatgpt.com/docs/hooks)

The current execution and plan recipes measure 6,802 and 1,955 ASCII characters, respectively. The test deliberately applies the budget to characters as a stricter size check. Those counts cannot establish whether Codex would have saved the execution recipe to disk with the former 5,000-token setting.

**Standing rules:** [examples/orchestration-rules.md](examples/orchestration-rules.md) contains the companion section. In Claude Code, append it to `~/.claude/CLAUDE.md`; in Codex, use `${CODEX_HOME:-$HOME/.codex}/AGENTS.md`. If the section exists, compare and merge it rather than appending a duplicate. Claude examples name Fable, Opus and Sonnet; Codex uses its available models and inherits the configured model unless an override is authorized. Stop and report missing required models instead of inventing names or changing account settings.

The recipe reuses an existing repository test rig or a tool-specific rigs folder. Create `~/.claude/rigs/` or `${CODEX_HOME:-$HOME/.codex}/rigs/` only if needed. The writing and comment checks use this repository's independent skills; installing the hook does not download or install those skills.

**Plan versus execution:**

| Prompt | Hook output |
| --- | --- |
| `orchestrate a workflow to update one file` | Full recipe |
| `orchestrate a workflow and outline the plan for a one-file change.` | Plan-only recipe |
| `orchestrate a workflow and outline a plan to build a tool` | Plan-only recipe |
| `plan and execute an uc workflow` | Full recipe |
| `orchestrate a workflow, do not execute` | Plan-only recipe |
| `what time is it` | No output |
| `can you orchestrate a workflow?` | No output |
| `Explain the phrase "orchestrate a workflow".` | No output |

The aliases `uc workflow` and `ultracode workflow` are personal shorthand you can change. Matches are case-insensitive and accept whitespace between words. Questions ending in `?`, quoted examples, code spans/blocks and negated triggers are skipped. Planning language defaults to the plan-only recipe, even when it describes building or shipping. An explicit `plan and execute` or `plan then run` selects execution; `plan only`, negated execution and the runtime's `permission_mode: "plan"` keep the plan-only variant. These are conservative text heuristics, not a natural-language permission parser. Existing user instructions and runtime policy remain authoritative.

Empty or missing prompts produce no output. Malformed JSON, non-object events, multiple JSON documents, wrong prompt types and missing `jq` produce an error on stderr and exit 2. In either tool, exit 2 from `UserPromptSubmit` blocks the prompt. A hook that never starts or is skipped cannot inject instructions; do not assume it provides an enforcement boundary.

**Test locally:**

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The suite invokes the actual hook under `/bin/bash`, checks stdout/stderr and the JSON schema, and runs a mutated-script negative control to prove a missing recipe requirement fails an assertion. It uses no model account, network or external writes. To test an installed copy directly:

```sh
H="$HOME/.claude/hooks/inject-orchestration-recipe.sh" # or the Codex hook path
jq -n --arg prompt 'orchestrate a workflow and outline the plan for a one-file change.' \
  '{prompt: $prompt}' | /bin/bash "$H"
```

Then start a fresh session in each tool and enter that same plan-only prompt. Confirm the hook is loaded and trusted and the model stops at the plan. Direct script tests establish the hook's response; a live session establishes runtime loading and model behavior. Report an authentication or trust blocker separately rather than claiming a live test passed.

Keep apostrophes out of the recipe heredocs while they remain inside command substitutions: macOS Bash 3.2 can fail to parse that construction. Rerun the suite after any edit.

Hook contracts and Codex trust/context settings: [Claude Code hooks](https://code.claude.com/docs/en/hooks), [Codex hooks](https://learn.chatgpt.com/docs/hooks).

---

## Contributing

Issues and pull requests are open. Bug reports, focused improvements, and additions to the banned-word list are welcome. These checklists work best when you adapt them to your writing and code, so forking them for your own rules is welcome too.

---

## License

MIT. See [LICENSE](LICENSE).
