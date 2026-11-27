# guardrail-skills

Four small guardrails for AI agents that write and code. Each one is a text file your agent reads, plus at most a short script. Run one as a **skill** (the agent decides when) or as a **hook** (your tooling runs it every time).

| Guardrail | The problem it solves |
| --- | --- |
| [slop-scrub](#slop-scrub) | A draft from your AI sounds nothing like you. |
| [job-application-writer](#job-application-writer) | A cover letter your AI writes from your resume reads like an AI wrote it. |
| [comment-scrub](#comment-scrub) | AI agents bury code under comments that repeat the code. |
| [Orchestration recipe hook](#orchestration-recipe-hook) | A job split across many agents sprawls, with no estimate and no tests. |

## Safe to run

- **Zero dependencies, local only:** five Python standard-library scripts (1,205 lines), one `bash`/`jq` hook (203 lines), and four instruction files. No network calls, file writes, accounts, or keys.
- **Tested offline:** 124 tests cover the scripts and hook (`python3 -m unittest discover -s tests`).

## slop-scrub

The whole point of this skill is to help you take your writing and have your AI use your voice at scale, without it sounding like slop.

**The problem.** You ask your AI for a draft and it sounds nothing like you. It can read like an AI wrote it, and readers hear that.

**What it does.** Two jobs. It runs 14 checks on any draft: claims with no source, stock words, em dashes, sentences that all run the same length. And it writes a piece from three to five things that happened, plain if you give it none of your writing and in your voice if you give it two or three finished pieces.

### Proof

Same AI model, same request, with and without the skill. Nobody edited any of the four texts. AI writing detectors can flag a draft that reads like an AI wrote it, so each text has a score from one of the leading ones, scanned on 2026-11-23. The author is the maintainer of this repo.

**The request:** a short post telling founders what slop-scrub is and how to get it. It came with six plain facts and three things that happened.

The drafts without the skill were each written once. Each piece with the skill is the highest-scoring of several written the same way in the larger test below, so read it as the best case. Of the 8 written from this request with no samples, 7 scored human, and all 4 written with one post of the author's did too. A comparison like this can also come out the other way, with the draft written without the skill scoring higher.

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

<details><summary>Read the piece</summary>

> slop-scrub is a free, open-source checklist for AI writing that I made, and founders who use AI to help them write can get it on GitHub.
>
> One evening in November I checked drafts from my AI by hand, one at a time. Draft 14 and draft 17 both came back marked 100% AI. I didn't check the rest of that batch, because I could see they were full of em dashes. slop-scrub removes em dashes and banned words such as "delve".
>
> The first draft that came back reading as mine was 113 words long, and it was built from sentences I had typed myself.

</details>

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

<details><summary>Read the piece</summary>

> I'm giving away slop-scrub, my open-source checklist for AI writing (it costs $0), to founders who use AI to help them write, and it's public on GitHub.
>
> One evening in November I checked drafts from my AI by hand, one at a time. Draft 14 and draft 17 both came back marked 100% AI. Seriously. I could see the other drafts in that batch were full of em dashes, so I didn't check them.
>
> The first draft that came back reading as mine was 113 words long, and it was literally built from sentences I'd typed myself.

</details>

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

**Results depend on the writing you give it.** They also vary by model, request and detector, and no score is a promise. Test it on one of your own drafts and judge the result yourself before you rely on it. If an install step fails, stop and delete what you copied.

## job-application-writer

Give your AI your resume and the job posting. It asks what happened behind a line or two of your resume, then writes the cover letter from what you did, at the size you did it. **The problem.** A cover letter your AI writes reads like an AI wrote it. In the tests, all 24 letters written from a resume and a posting alone did, in every style tried. So did 4 of 4 written with no skill from requests that held the person's own story. **What it does.** It asks for your story first and builds the letter on it. Every fact stays yours: numbers stay exact, "helped" never becomes "led", and a skill your resume doesn't show never goes in. It also tailors your resume to one posting, and it works with a writing sample of yours, even three short posts on another subject, or with none.

### Proof

With this version's final text, 8 of 9 pieces by fresh AI writers (new sessions that saw only a request and the skill) passed on one of the leading AI writing detectors, where a pass means the human share beat the AI share plus the mixed share. Letters with the person's story and no writing sample passed 2 of 3 (95.7% and 84.2%, while the third read 0.0% human). Letters with three short posts on another subject as the sample passed 3 of 3, and so did tailored resumes, all at 100.0%. The text before its last fix passed 18 of 19, and the version before that passed 12 of 12 letters (lowest 97.9%). A fact check of that 18-of-19 round found nothing made up and no one else's work handed to the user. One letter did make the user's part bigger: he had recommended one volunteer, his first, and the letter called it "the volunteer recruiting this role calls for". That letter and one other claimed a fit with the job that the request didn't back. Both tailored copies of one resume dropped the user's own line about two years as a manager, on a posting that asks for three or more. Those findings led to tighter rules on when a letter may say a story fits the job and on which resume lines to drop. A fact check of the final round's 9 pieces then found nothing made up, nothing made bigger and no fit claimed. Both resumes on that request kept the two-years line word for word. The cost was that two letters said less about the job than before. One story, told mostly as a scene with little the person did in it, passed 3 times and failed 2 times across the rounds, so a story that says little of your own part can go either way. The job seekers and postings were made up, and each story was a real person's published writing, word for word, from United States government staff blogs. It was one detector on one night. No story typed fast by a user and no job seeker's own resume has been tried, and no hiring manager has judged a letter. Every letter written from a resume alone, which is what "write it now" gives, read as machine-written. No score is promised, so read every line before you send it. Here are [an example request](examples/job-application-request.md) and [the skill's whole reply](examples/job-application-reply.txt), unedited, from the text before its last fix. Its letter claims no fit with the job and read 100.0% human on one scan. The story in the request is real: a United States Fish and Wildlife Service story, ["2024 Waterfowl Banding Operations: Saskatchewan 2"](https://www.fws.gov/story/2024-09/2024-waterfowl-banding-operations-saskatchewan-2), used word for word. The job seeker, resume and posting are made up. Every round and count: [docs/job-application-writer.md](docs/job-application-writer.md).

### Use it

Copy the folder with `mkdir -p ~/.claude/skills && cp -R skills/job-application-writer ~/.claude/skills/`, type `/job-application-writer`, and paste your resume, the posting and anything you've already written about the work. With a resume and a posting alone, it asks about one or two lines on your resume and waits. It asks what was going on and who was there, what your own part was, what happened next with the numbers, and why you want this job. Answer in two minutes, typed fast or spoken, or say "write it now" for a short letter from your resume alone. Check the letter with `python3 skills/job-application-writer/letter_check.py letter.txt --source resume.txt posting.txt`. To tailor your resume, ask for it, and the skill chooses, orders and trims your own bullets with your wording and layout kept. It lists each changed bullet beside the one it came from, and each thing the posting asks for that your resume doesn't show. Codex: copy the folder to `~/.agents/skills/` and use `$job-application-writer`. Any other tool: paste `SKILL.md`, below its `---` header, into your custom instructions.

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

**Results depend on the code you give it.** It's a checklist your agent follows, so it can miss a comment or cut one you'd keep. Read the diff before you commit.

## Orchestration recipe hook

**The problem.** Ask an agent to orchestrate a big job and it can start a crowd of helpers with no estimate, no tests and no finish line.

**What it does.** A hook for Claude Code and Codex. When your prompt asks for a multi-agent run, it hands the model a recipe for that one job: say the size and the time before starting, cap the helpers at seven at once, give each fix to a fresh agent with the test to run, get an independent review where money, messages or anything hard to undo is involved, and compare the agents planned with the agents that ran. Every other prompt passes through untouched.

### Proof

The real script, run on four prompts on 2026-11-26:

| Prompt | What the hook prints |
| --- | --- |
| `orchestrate a workflow to update one file` | The full recipe (7,376 characters) |
| `orchestrate a workflow and outline the plan for a one-file change.` | The plan-only recipe (2,566 characters) |
| `what time is it` | Nothing |
| `can you orchestrate a workflow?` | Nothing, because a question is not a request |

Try one yourself. It prints the first lines of the recipe and changes nothing:

```sh
jq -n --arg prompt 'orchestrate a workflow to update one file' '{prompt: $prompt}' \
  | bash hooks/inject-orchestration-recipe.sh | jq -r '.hookSpecificOutput.additionalContext' | head -5
```

28 of the tests cover the hook, including quoted, negated and malformed prompts.

### Use it

1. Copy `hooks/inject-orchestration-recipe.sh` into your hooks folder and make it executable.
2. Add its one `UserPromptSubmit` entry to your settings file. The exact entry for Claude Code and for Codex, the backup steps and the trigger rules: [docs/orchestration-hook.md](docs/orchestration-hook.md).
3. Start a new session and type a prompt that says "orchestrate a workflow".

The recipe guides the model and enforces nothing, so keep your permission prompts and spend limits on.

**Results depend on the job you give it, and multi-agent runs can use a lot of tokens.** You're responsible for your own usage. Try it on a small job first, and if an install step fails, stop and undo it.

## Contributing

Issues and pull requests are open. These checklists work best when you adapt them to your own writing and code, so forking them is welcome too.

## License

MIT. See [LICENSE](LICENSE).
