# slop-scrub: the full guide

The short version, with examples and results, is in the [README](../README.md#slop-scrub). This page holds every mode, the local lint and the install notes. Run the commands from the top folder of the repo.

**The banned-word list is a starting point, not a ruling.** You'll disagree with parts of it, and you should. `leverage` and `robust` have honest uses. Open `skills/slop-scrub/SKILL.md`, edit the list in item 1, and make it yours. Forking it into something opinionated about *your* writing is the intended use, not a misuse.

**Install as a skill**

Copy the entire `skills/slop-scrub/` folder, including `slop_lint.py`.

- **Claude Code.** For personal use, copy it to `~/.claude/skills/slop-scrub/` and run `/slop-scrub`. [Claude Code skills](https://code.claude.com/docs/en/skills)
- **Codex.** Copy it to `~/.agents/skills/slop-scrub/` for personal use or to `.agents/skills/slop-scrub/` in the project. Invoke it with `$slop-scrub` or select it from `/skills`. [Codex skills](https://learn.chatgpt.com/docs/build-skills)
- **Other tools.** Paste the text below the `---` frontmatter in `SKILL.md` into your system prompt or custom instructions.

Put two or three short samples approved by the author in the root voice guide (`VOICE.md`) with a reader description and any words or phrases the author avoids. The strongest basis for the edit is the author's own wording, supported by their facts and approved samples. The checklist cannot guarantee a detector verdict. [Voice guide template](../examples/VOICE.md.template)

When the project has no voice guide, work from the person's original draft and notes, flagging any detail they still need to supply.

### Local lint

Give the linter a UTF-8 file or pipe text into standard input. Use `--json` for structured results.

```sh
python3 skills/slop-scrub/slop_lint.py draft.txt
python3 skills/slop-scrub/slop_lint.py --json < draft.txt
```

Exit status is `0` for a clean scan, `1` for findings, or `2` for bad input. Beyond banned words and em dashes, the linter flags stacked multi-clause sentences, participial summary tails, transition-opener scaffolding, and parallel paragraph openers or closers as review items. Run the full checklist after the scan, since the linter cannot assess author voice or whether the claims are supported.

### Writing in your voice: two ways in

**Give it your writing. This is the way we recommend.** Send two or three finished pieces of yours and three to five things that happened, a sentence each. The skill writes a plain piece around what happened and lays your voice over it: your words, your joins, your way of opening and three of the habits a reader would know you by. In the last test, 24 fresh AI writers that saw only this skill wrote 24 pieces for two authors and three kinds of piece. All 24 scored human on one of the leading AI writing detectors, and three AI readers that saw no names matched all 24 to the right author. The readers called 19 natural and 5 an impression. The pieces reused fewer than 9 of every 100 words from the samples. Details: [Carried-voice mode](#carried-voice-mode).

**Give it no writing.** Send three to five things that happened. The skill writes a plain, clean piece around them and tells you it is in no one's voice. In a matching test, 23 of 24 of those pieces scored human on the same detector. From a bare list of facts with nothing that happened, none did, so there the skill asks you what happened before it writes. Details: [No sample yet](#no-sample-yet).

Samples are worth the two minutes. Without them a piece reads like a person wrote it, and with them it reads like you wrote it. The author who gave one sample drew four of the five "impression" verdicts, so give two or three if you can.

That was one day of scanning (41 rounds, about 500 scans), two authors, pieces of about 100 to 220 words and one detector. Treat the numbers as evidence about how the text reads and never as a promise about any detector's verdict.

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

With nothing you wrote to work from, the skill asks before it writes: say the piece in your own words, two minutes typed fast or dictated, and it builds the finished piece around that in anchor mode. For persuasive business pieces such as cover letters, cold outreach emails, executive memos, or thought-leadership threads, that short spoken dump is the default first step before drafting. If you would rather not, it asks for three to five things that happened, a sentence each, and writes a plain piece around them: the first line says what the piece is, the things that happened follow in plain past tense, and the always-true facts are rationed to one word in five. The piece can only be as long as the things that happened allow, so it tells you which facts it left out, that one more thing that happened makes room for more, and that the result is in no one's voice. It never makes up a thing that happened. It never invents a voice for you, and it never uses one author's samples for another author.

**As a hook:** see [`examples/pre-commit-hook.sh`](../examples/pre-commit-hook.sh) or [`examples/github-actions.yml`](../examples/github-actions.yml) for how to force it to run on every commit or PR instead of waiting for the agent to remember.
