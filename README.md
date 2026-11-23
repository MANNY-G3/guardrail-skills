# guardrail-skills

Three small, independent guardrails for AI coding agents. Each one works two ways: as a **skill** (the agent decides when to run it) or as a **hook** (your tooling forces it to run every time, whether the agent remembers or not). Neither mode requires Claude Code specifically; see the install notes under each one.

## slop-scrub

Use the 14 checks to verify claims against their sources and find details the draft needs from its author. The checklist also catches repetitive sentences and wording that gets in the reader's way.

It also writes. Give it a few things that happened, with or without samples of your own writing, and it writes the piece. The two examples below came straight from an AI writer, and nobody edited them afterward.

### Example: no writing given

A fresh AI writer that had only this skill wrote the piece below from a short request, five plain facts and three things that happened.

**What was sent** (a test request, built from facts David S. Ferriero published in 2012 while he ran the National Archives)

> Write a short piece for our newsletter asking people to come and volunteer at the National Archives. I have no writing of mine to give you. Write it plain.
>
> - Last week a veteran rode a motorcycle from Nevada to College Park. He had been looking for 43 years for information about his platoon leader, who was killed in Vietnam. The staff found it in 30 seconds.
> - A man came to the Waltham facility with a letter from May 1946 that recommended his father for the Bronze Star. The medal had never been awarded. Walter Pierce was given his Bronze Star two days after his 100th birthday.
> - This year volunteers worked through the records of the Marine dogs that served in World War II.

**What the skill wrote** · [Copy the piece](examples/no-sample-piece.txt)

> I run the National Archives, and I'm asking you to come and volunteer at the facility near you, one of 44 around the country.
>
> Last week a veteran rode a motorcycle from Nevada to College Park. He had been looking for 43 years for information about his platoon leader, who was killed in Vietnam. The staff found it in 30 seconds.
>
> A man came to the Waltham facility with a letter from May 1946 that recommended his father for the Bronze Star, but it had never been awarded. Walter Pierce was given his Bronze Star two days after his 100th birthday.
>
> This year 295 volunteers in Washington and College Park each gave more than 100 hours. Together they gave 42,284 hours. Volunteers write descriptions of single items, write photo captions, scan files, index records and answer researchers' questions. This year volunteers worked through the records of the Marine dogs that served in World War II.

This piece scored 100% human on one of the leading AI writing detectors. In the same test, 23 of 24 pieces written this way scored human. It is in no one's voice, and the skill says so when it hands a piece like this over. Ferriero did not write it. The facts come from his posts [Celebrating Our Volunteers](https://aotus.blogs.archives.gov/2012/10/12/celebrating-our-volunteers/), [American Archives Month](https://aotus.blogs.archives.gov/2012/10/09/american-archives-month/) and [We Salute You](https://aotus.blogs.archives.gov/2012/11/08/we-salute-you/). Details: [No sample yet](#no-sample-yet).

### Example: your writing given

Here the writer also had three finished pieces by the author. None of them is a recipe, and the request was for a dessert how-to, a kind of piece he had not written. A fresh AI writer that had only this skill, the samples and the request wrote the piece below.

**The samples** are three 2012 posts by David S. Ferriero: [Staying Ahead of Sandy](https://aotus.blogs.archives.gov/2012/10/31/staying-ahead-of-sandy/), [We Salute You](https://aotus.blogs.archives.gov/2012/11/08/we-salute-you/) and [American Archives Month](https://aotus.blogs.archives.gov/2012/10/09/american-archives-month/). They are in the public domain as works of the United States government ([National Archives copyright policy](https://www.archives.gov/global-pages/privacy.html#copyright)). The first one opens:

> I hope that you and your families are well and safe after Sandy’s visit to the Northeast.
>
> The National Archives buildings were largely spared, thanks to extensive preparation based on “lessons learned” from similar weather events. I am grateful to all of our staff and especially to our facilities and emergency staff for their ongoing work in keeping personnel and records safe. None of our records were damaged as a result of Hurricane Sandy, thanks to our staffs’ careful preparation.

**What was sent** (a test request, built from his post [What Happened to Those Twinkies?](https://aotus.blogs.archives.gov/2012/11/20/what-happened-to-those-twinkies/))

> Write up my Twinkie dessert as a short how-to for the staff newsletter. Write it in my voice.

The request listed the recipe and three things that happened: a time capsule came to the National Archives with a package of Twinkies in it, the staff ate them because they would not keep, and the recipe once won him a dessert contest.

**What the skill wrote** · [Copy the piece](examples/carried-voice-piece.txt)

> Sarah's Surprise is my Twinkie dessert, a recipe I am sharing with all of our staff at the National Archives.
>
> A time capsule put together for the millennium came to us at the National Archives, and among its more than 1,300 items was a package of Twinkies. The staff who prepared the time capsule's contents for permanent keeping decided the Twinkies would not last. The Twinkies were documented as part of the time capsule, and then they were eaten.
>
> What does Sarah's Surprise take? It takes 8 Twinkies, a 20 oz. can of crushed pineapple, 1 qt. of vanilla ice cream, 2 packages of orange Jello, 1 cup of boiling water, a 7 oz. bottle of 7-Up less 1 tablespoon, and Cool Whip.
>
> Halve the Twinkies lengthwise and line a 9 by 13 dish with them, and then layer the pineapple and the softened ice cream on top. Dissolve the Jello in the boiling water and the 7-Up. When the Jello meets the 7-Up it bubbles hard! Pour the Jello over the layers and refrigerate until it sets, and then slice it and serve it with Cool Whip.
>
> And, I won the New Year's Eve Dessert Contest at the MIT Libraries with Sarah's Surprise, and still remember being embarrassed in the checkout line with the ingredients.

This piece scored 99.8% human on the same detector. Three AI readers saw it with no name on it, mixed in with pieces in a second author's voice and plain pieces in no one's. All three gave it to Ferriero, and two of the three called it natural. About 6 of every 100 words sit in runs of three or more words that also appear in his samples, so what carries over is his habits and not his old sentences: the question he answers himself, the "And," opening, the exclamation mark. Ferriero did not write this piece. Details: [Carried-voice mode](#carried-voice-mode).

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

### Writing in your voice: two ways in

**Give it your writing. This is the way we recommend.** Send two or three finished pieces of yours and three to five things that happened, a sentence each. The skill writes a plain piece around what happened and lays your voice over it: your words, your joins, your way of opening and three of the habits a reader would know you by. In the last test, 24 fresh AI writers that saw only this skill wrote 24 pieces for two authors and three kinds of piece. All 24 scored human on one of the leading AI writing detectors, and three AI readers that saw no names matched all 24 to the right author. The readers called 19 natural and 5 an impression. The pieces reused fewer than 9 of every 100 words from the samples. Details: [Carried-voice mode](#carried-voice-mode).

**Give it no writing.** Send three to five things that happened. The skill writes a plain, clean piece around them and tells you it is in no one's voice. In a matching test, 23 of 24 of those pieces scored human on the same detector. From a bare list of facts with nothing that happened, none did, so there the skill asks you what happened before it writes. Details: [No sample yet](#no-sample-yet).

Samples are worth the two minutes. Without them a piece reads like a person wrote it, and with them it reads like you wrote it. The author who gave one sample drew four of the five "impression" verdicts, so give two or three if you can.

That was one week of testing, two authors, pieces of about 100 to 220 words and one detector. Treat the numbers as evidence about how the text reads and never as a promise about any detector's verdict.

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

### Sentence-bank mode

Ask for a new piece and point the skill at pieces you already wrote. It plans the new piece for its own subject and reader, then builds it out of your sentences, each kept whole and reworked with the fewest changed words that make it true. It leaves your best-known lines alone and puts new facts in plain sentences of their own.

This mode has a short reach. It gives you a new version of a piece you have already written: one pitch reworked for a second product, last year's announcement reworked for this year's. A reader who knows the original will hear it. Ask for a kind of piece or a tone your writing does not hold, such as a calm how-to when all it has are your rants, and the skill stops and tells you what is missing. It does not pad the piece to pass its own counter.

`bank_check.py` prints, for each sentence and for the whole piece, how many words in 100 sit inside runs of three or more words from your pieces. It fails a piece under 60. It also lists the lines carried over nearly whole, the sentences that are part yours and part the editor's, and how much came from each of your pieces. The counter measures borrowed wording and never tone.

```sh
python3 skills/slop-scrub/bank_check.py piece.txt my-post.txt my-other-post.txt
python3 skills/slop-scrub/bank_check.py piece.txt VOICE.md --floor 70
python3 skills/slop-scrub/bank_check.py piece.txt post-1.txt post-2.txt post-3.txt --most-from-one 40
```

Exit status is `0` at or over the floor, `1` under it or when one piece supplies more than `--most-from-one` allows, or `2` for bad input.

### Carried-voice mode

For a different kind of piece than anything in your samples: a how-to when your samples are rants, a notice when they are thank-you posts. The skill asks for three to five things that happened, writes the plain piece around them, then lays your voice on in layers taken from your samples: your words for things, your joins, your way of opening, the shape of your sentences and three of the habits a reader would know you by. It keeps at most one short verdict of yours whole, and it adds a line of opinion only where your samples show one. It never gives you an opinion you did not hold, and it leaves the facts alone. Give it two or three of your pieces if you can, because one sample leaves little to carry. The same counter then has to come out low, because the point is your voice and not your old sentences:

```
python3 skills/slop-scrub/bank_check.py PIECE.md SAMPLE.md --at-most 15
```

Only you can say whether the result sounds like you, so it tells you what it carried and asks you to read it.

### No sample yet

With nothing you wrote to work from, the skill asks before it writes: say the piece in your own words, two minutes typed fast or dictated, and it builds the finished piece around that in anchor mode. If you would rather not, it asks for three to five things that happened, a sentence each, and writes a plain piece around them: the first line says what the piece is, the things that happened follow in plain past tense, and the always-true facts are rationed to one word in five. The piece can only be as long as the things that happened allow, so it tells you which facts it left out, that one more thing that happened makes room for more, and that the result is in no one's voice. It never makes up a thing that happened. It never invents a voice for you, and it never uses one author's samples for another author.

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
