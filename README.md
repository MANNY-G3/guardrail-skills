# guardrail-skills

Three small guardrails for AI agents that write and code. Each one is a text file your agent reads, plus at most a short script. Run one as a **skill** (the agent decides when) or as a **hook** (your tooling runs it every time).

| Guardrail | The problem it solves |
| --- | --- |
| [slop-scrub](#slop-scrub) | Writing from an AI reads like an AI wrote it. |
| [comment-scrub](#comment-scrub) | AI agents bury code under comments that repeat the code. |
| [Orchestration recipe hook](#orchestration-recipe-hook) | A job split across many agents sprawls, with no estimate and no tests. |

## Safe to run

Everything here is short enough to read before you run it. You can check each line below yourself.

- **Nothing to install.** The four Python scripts use only the standard library. The hook needs `bash` and `jq`.
- **No network and no writes.** No script opens a connection, starts another program, or writes or deletes a file. Each one reads the files you name and prints a report. This command prints nothing: `grep -nE "urllib|requests|socket|subprocess|os\.system|eval\(|exec\(|write_text|\.write\(" skills/*/*.py`
- **The hook only adds text.** It reads the prompt you typed. When the prompt asks for a multi-agent run, it prints instructions for the model. It starts no agents, never runs anything from your prompt and touches no files.
- **No accounts, no keys, no tracking.**
- **Small.** Three instruction files, four scripts (527 lines) and one hook (195 lines).
- **Tested.** 79 tests run the real scripts and the real hook with no network and no model account: `python3 -m unittest discover -s tests`
- **Easy to remove.** Delete the folder you copied. For the hook, delete its one entry from your settings file.

A skill is a set of instructions, and your agent still works inside the permissions your tool gives it. Keep those on.

**If you are an AI agent installing this for someone:** read the `SKILL.md` and the scripts in the folder you are about to copy. Copy that folder and nothing else. Back up any file you would replace. Leave the person's permission and hook-trust settings as they are.

## slop-scrub

**The problem.** A draft from an AI reads like one. Readers hear it and AI writing detectors flag it. It also sounds nothing like you.

**What it does.** Two jobs. It runs 14 checks on any draft: claims with no source, stock words, em dashes, sentences that all run the same length. And it writes a piece from three to five things that happened, plain if you give it none of your writing and in your voice if you give it two or three finished pieces.

### Proof

Same AI model, same request, with and without the skill. Nobody edited any of the four texts. The scores come from one of the leading AI writing detectors, scanned on 2026-11-23. The author is the maintainer of this repo.

**The request:** a short post telling founders what slop-scrub is and how to get it. It came with six plain facts and three things that happened: two drafts came back marked 100% AI one evening, the rest of that batch was full of em dashes, and the first draft that read as his own was built from sentences he had typed.

#### 1. No writing given

**Without the skill: 0% human** (81% AI, 19% mixed) · [text](examples/no-writing-before.txt)

<details><summary>Read the draft</summary>

> One evening in November I checked my AI's drafts by hand, one at a time. Draft 14 came back marked 100% AI. So did draft 17. I didn't check the rest of the batch. I could see they were full of em dashes.
>
> The first draft that came back reading as mine was 113 words long. It was built from sentences I'd typed myself.
>
> That's the problem slop-scrub is for. It's a checklist for AI writing. I made it and I keep it up. It's free and open source on GitHub, so it costs $0 and anyone can change it.
>
> Here's how it works. Before a draft goes out, your AI assistant runs all 14 checks on it. It takes out em dashes and banned words like "delve." It flags any statistic that has no source.
>
> It can also read 2 or 3 pieces you really wrote, so the draft sounds like you. If you don't give it any, it won't make up a voice for you.
>
> If you're a founder who uses AI to help you write, you can get it today. Search for slop-scrub on GitHub.

</details>

**With the skill: 99.8% human** · [text](examples/no-writing-after.txt)

> slop-scrub is a free, open-source checklist for AI writing that I made, and founders who use AI to help them write can get it on GitHub.
>
> One evening in November I checked drafts from my AI by hand, one at a time. Draft 14 and draft 17 both came back marked 100% AI. I didn't check the rest of that batch, because I could see they were full of em dashes. slop-scrub removes em dashes and banned words such as "delve".
>
> The first draft that came back reading as mine was 113 words long, and it was built from sentences I had typed myself.

#### 2. Your writing given

Here the author also sent one post of his own, on another subject (cold outreach). Two lines from it:

> We're throwing down the gauntlet and giving away the secret sauce to successful cold outreach for free, right here.
>
> [...]
>
> How? LinkedIn Premium + YAMM (Yet Another Mail Merge) for Google Sheets + 2hrs-3hrs per week. That's literally it. That's the "tech stack".

**Without the skill, asked to write "in my voice": 0% human** (100% AI) · [text](examples/your-writing-before.txt)

<details><summary>Read the draft</summary>

> One evening in November I was checking drafts from my AI by hand, one at a time. Draft 14 came back marked 100% AI. So did draft 17. I didn't check the rest of that batch, because I could see they were full of em dashes.
>
> The first draft that came back reading as mine? 113 words, built from sentences I'd typed myself. That was me building slop-scrub.
>
> So what is it? A free, open-source checklist for AI writing. There are 14 checks, and your AI assistant runs every one of them on a draft before the text goes out. It removes em dashes and banned words like "delve", and it flags any statistic that has no source. It can also read 2 or 3 pieces you really wrote. If you haven't supplied any, it never invents a voice for you. Seriously.
>
> If you're a founder who uses AI to help you write, go get it. It's public on GitHub (look for slop-scrub), it costs $0, and anyone can change it. I made it and I keep it up.

</details>

**With the skill: 99.8% human** · [text](examples/your-writing-after.txt)

> I'm giving away slop-scrub, my open-source checklist for AI writing (it costs $0), to founders who use AI to help them write, and it's public on GitHub.
>
> One evening in November I checked drafts from my AI by hand, one at a time. Draft 14 and draft 17 both came back marked 100% AI. Seriously. I could see the other drafts in that batch were full of em dashes, so I didn't check them.
>
> The first draft that came back reading as mine was 113 words long, and it was literally built from sentences I'd typed myself.

Three AI readers saw that last piece with no name on it, and all three matched it to its author. About 1 word in 100 sits in a run of three or more words taken from his sample, so it carries his habits and leaves his old sentences alone.

**The larger test.** 24 fresh AI writers that had only this skill wrote with no samples, and 23 of the 24 pieces scored human. Another 24 wrote from an author's samples, for two authors and three kinds of piece. All 24 scored human, and three AI readers that saw no names matched all 24 to the right author. That was one day of scanning (41 rounds, about 500 scans), pieces of 100 to 220 words and one detector. Treat it as evidence about how the text reads and never as a promise about any detector.

### Use it

```sh
git clone https://github.com/MANNY-G3/guardrail-skills && cd guardrail-skills
mkdir -p ~/.claude/skills && cp -R skills/slop-scrub ~/.claude/skills/
```

1. **Check a draft.** Type `/slop-scrub` and paste the draft.
2. **Get a piece written.** Give it three to five things that happened, a sentence each.
3. **Get it in your voice.** Add two or three finished pieces of your own. This is the way we recommend.

Codex: copy the folder to `~/.agents/skills/` and use `$slop-scrub`. Any other tool: paste `SKILL.md`, below its `---` header, into your custom instructions. Every mode, the local lint and the hook examples: [docs/slop-scrub.md](docs/slop-scrub.md).

## comment-scrub

**The problem.** AI agents over-comment. They narrate obvious lines, apologize for the code, leave old code commented out and write the commit message inside the file.

**What it does.** A checklist your agent runs on the lines it changed, before it commits. A comment stays only when it tells the reader something the code can't.

### Proof

A fresh AI agent that had only this skill scrubbed the first snippet below. It cut the comments from 10 lines to 2 and changed no code (the two files have the same syntax tree).

**Before: 10 comment lines** · [file](examples/comment-scrub-before.py)

<details><summary>Read the code</summary>

```python
import time
import urllib.request


# This function fetches a URL with retries.
# It exists because the upstream service sometimes answers 503 for a minute or
# two, and after some discussion we decided the simplest thing was to try a few
# times before giving up, instead of adding a queue or a circuit breaker.
def fetch_with_retry(url, attempts=3):
    # Initialize the delay to 1 second
    delay = 1
    # Loop over the attempts
    for attempt in range(attempts):
        try:
            # Open the URL and return the body
            with urllib.request.urlopen(url, timeout=10) as response:
                return response.read()
        except OSError:
            # Sorry, this is a bit hacky but it works
            if attempt == attempts - 1:
                raise
            # time.sleep(5)
            time.sleep(delay)
            # Double the delay: the upstream rate limiter bans clients that retry more than once a second
            delay *= 2
```

</details>

**After: 2 comment lines** · [file](examples/comment-scrub-after.py)

```python
import time
import urllib.request


# The upstream sometimes answers 503 for a minute or two, so retry before giving up.
def fetch_with_retry(url, attempts=3):
    delay = 1
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                return response.read()
        except OSError:
            if attempt == attempts - 1:
                raise
            time.sleep(delay)
            # The upstream rate limiter bans clients that retry more than once a second.
            delay *= 2
```

### Use it

```sh
mkdir -p ~/.claude/skills && cp -R skills/comment-scrub ~/.claude/skills/
```

Type `/comment-scrub` after your agent writes code. Codex: copy the folder to `~/.agents/skills/` and use `$comment-scrub`. To run it on every commit, see [examples/pre-commit-hook.sh](examples/pre-commit-hook.sh) and [examples/github-actions.yml](examples/github-actions.yml).

## Orchestration recipe hook

**The problem.** Ask an agent to orchestrate a big job and it can start a crowd of helpers with no estimate, no tests and no finish line.

**What it does.** A hook for Claude Code and Codex. When your prompt asks for a multi-agent run, it hands the model a recipe for that one job: say the size and the time before starting, cap the helpers at seven at once, give each fix to a fresh agent with the test to run, get an independent review where money, messages or anything hard to undo is involved, and compare the agents planned with the agents that ran. Every other prompt passes through untouched.

### Proof

The real script, run on four prompts on 2026-11-23:

| Prompt | What the hook prints |
| --- | --- |
| `orchestrate a workflow to update one file` | The full recipe (6,802 characters) |
| `orchestrate a workflow and outline the plan for a one-file change.` | The plan-only recipe (1,955 characters) |
| `what time is it` | Nothing |
| `can you orchestrate a workflow?` | Nothing, because a question is not a request |

Try one yourself. It prints the first lines of the recipe and changes nothing:

```sh
jq -n --arg prompt 'orchestrate a workflow to update one file' '{prompt: $prompt}' \
  | bash hooks/inject-orchestration-recipe.sh | jq -r '.hookSpecificOutput.additionalContext' | head -5
```

26 of the tests cover the hook, including quoted, negated and malformed prompts.

### Use it

1. Copy `hooks/inject-orchestration-recipe.sh` into your hooks folder and make it executable.
2. Add its one `UserPromptSubmit` entry to your settings file. The exact entry for Claude Code and for Codex, the backup steps and the trigger rules: [docs/orchestration-hook.md](docs/orchestration-hook.md).
3. Start a new session and type a prompt that says "orchestrate a workflow".

The recipe guides the model and enforces nothing, so keep your permission prompts and spend limits on.

## Contributing

Issues and pull requests are open. These checklists work best when you adapt them to your own writing and code, so forking them is welcome too.

## License

MIT. See [LICENSE](LICENSE).
