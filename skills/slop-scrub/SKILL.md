---
name: slop-scrub
description: Edit drafts before they leave the agent. Also triggers on "slop scrub", "check for AI-isms", "scrub this", "check this copy", "review this writing", or "run slop scrub on this". Check claims and preserve the author's voice while removing banned wording and repetitive prose.
---

# Slop Scrub

Read the draft as its copy editor and apply the checklist. Run it again after you've made the edits.

This skill runs on any text before it leaves the agent. No channel is exempt. No context makes AI-isms acceptable. Even internal notes get scrubbed if they might be forwarded.

> **Not using Claude Code?** This file works as a standalone checklist too — see the [README](../../README.md) for how to run it as a plain prompt, a git hook, or a CI check with any LLM.

## Input

The text to scrub is one of:

- Pasted directly after the `/slop-scrub` command
- The most recent draft the agent just produced (scrub it before showing the user)
- A specific file or message the user references ("scrub the LinkedIn draft I just wrote")

If no text is provided and no draft is in scope, ask the user what to scrub. Don't guess.

## The 14-item checklist

Run every item. For EACH item, report what you found. "Clean" is acceptable only if you actually checked. Do not skip items. Do not batch them. The whole point is to catch the thing you'd skip.

### 1. Word scan

Search the text for every word in this banned list. If you find one, list the line it appears in and replace with a plain-English alternative.

**Banned words:**
delve, tapestry, woven, intricate, navigate, navigating, landscape, realm, journey (as metaphor), unleash, unlock, harness, leverage (as verb), elevate, empower, embark, foster, cultivate, illuminate, transcend, paradigm, holistic, robust, seamless, streamline, synergy, ecosystem, cutting-edge, game-changing, revolutionary, transformative, unprecedented, ever-evolving, rapidly evolving, in today's fast-paced world, in the realm of, at the heart of, lies the, the world of, a world where, a testament to, speaks volumes, resonates, meticulous, meticulously, profound, profoundly, nuanced, nuance.

This list is a starting point, not a ceiling. If a word feels like AI reaching for grandeur, flag it.

### 2. Construction scan

Search for these banned sentence shapes:

- **"It's not X, it's Y"** and any variant ("This isn't X. It's Y." / "Not just X — Y.")
- **"Not only X, but also Y"** and variants such as "not just X, but Y"
- **"No X. No Y. Just Z."** triplets used for emphasis
- **Automatic groups of three** in parallel clauses, adjectives, or nouns. Keep the entries that each give the reader something they need.
- **Mid-sentence self-questions** — "And what does that mean? It means..."
- **"An X with Y and Z" catty dismissals** — "An app with a logo and a landing page"
- **Pre-loaded transitions** — "Here's the thing:", "But here's the kicker:", "What's interesting is:"
- **Dressed-up verbs** such as `serves as`, `stands as`, `acts as`, `functions as`, `boasts`, `features`, and `represents` where `is`, `are`, or `has` would mean the same thing

Rewrite any found. Replace with plain declarative sentences.

### 3. Drumroll scan

Search for pre-announcements that promise something is coming instead of just saying it:

- "Here's the wildest part:"
- "What most people don't realize:"
- "The best thing about this:"
- "But here's the kicker:"
- "Here's why this matters:"
- "The crazy thing is:"

Delete the drumroll. Keep the point. The reader doesn't need a pep band warming them up for a sentence.

### 4. Metaphor check

Is every metaphor earned (rooted in real observation) or is it concept-stacking (piling abstract nouns on top of each other to sound profound)? Cut any stacking. "The architecture of trust" is concept-stacking. "Trust is the load-bearing wall — pull it and the whole house comes down" is earned.

### 5. Sensory check

Is sensory language attached to something you can actually sense?

- "The texture of embarrassment" — cut. Embarrassment has no texture.
- "The weight of a $9,400 invoice" — fine. An invoice has weight, literally and figuratively, and the number grounds it.

If you can't physically perceive the thing the sensory word is attached to, cut it.

### 6. Quietness check

Are things described as quiet, humming, whispering, spectral, or ghostly that literally aren't? AI loves making everything quietly happen. Cut those. "The bug quietly corrupts your data" — does it actually do this without noise? If yes, fine. If you just liked the cadence, cut.

### 7. Profundity check

Read the whole piece for claims of importance without a stated consequence. If the prose calls an ordinary event a pivotal milestone or a turning point, or says it leaves a legacy, use the author's facts to say what changed and how much. Cut commentary that says a fact "highlights," "underscores," "reflects," or "shows" something when it adds no information. Keep a verb like "shows" when the sentence explains what the evidence establishes.

- "And maybe that's exactly the point." — cut.
- "Sometimes the answer was in front of us all along." — cut.
- "The real question isn't X. It's Y." — cut.

State the consequence when the author has supplied one. End on the point the reader came for.

### 8. Bartender test

Would a smart bartender — not a customer at the bar, the bartender — understand every sentence after one read? Technical terms are fine if the audience is technical. Abstract jargon stacking is never fine. If you can't pass this test, simplify until you can.

### 9. Specificity and swap test

Check every paragraph for at least one detail only the author could provide. Look for a number, name, date, place, or action in the draft, supplied notes, or approved `VOICE.md` samples. For copy about a company or product, try swapping in a competitor's name. Flag interchangeable passages.

Use supplied facts that apply to this piece. For a paragraph without a qualifying detail, flag it as `needs a real detail from the author`. Never invent a detail.

### 10. Em dash check

Zero tolerance. Search for `—` (em dash) and `–` (en dash). Replace every one with a period, comma, line break, or set of parentheses. AI uses em dashes as a tell. Humans rarely do, especially not three per paragraph.

Exception: this rule applies to OUTPUT text (content meant for human readers). It does not apply to internal instruction docs, code comments, or project-level agent instruction files.

### 11. Source check

Does every factual claim have a source, or is it clearly framed as illustrative?

- "73% of AI companies struggle with margins" — needs a source or it's fabricated.
- "Consider two customers on the same plan" — clearly hypothetical, fine.

Flag every unsourced claim. Replace vague attributions such as "experts say," "studies show," "research suggests," or "many believe" with a named source that supports the claim. Flag runs of outlet, brand, or institution names that borrow prestige without adding evidence. Cite one source for a point, and add another only if it supplies different evidence the reader needs. Cut unsupported claims or frame genuinely hypothetical examples as illustrative.

### 12. Contraction check

Check for stiff, over-expanded prose, but do not force contractions into every sentence. AI often avoids contractions even when the surrounding voice uses them. Where a contraction sounds natural for this writer and reader, use it; where the expanded form adds emphasis, fits a formal passage, or matches the author's samples, keep it. Preserve contractions already present when they fit.

Examples of common contractions include `do not` / `don't`, `cannot` / `can't`, `will not` / `won't`, `it is` / `it's`, `we are` / `we're`, and `I have` / `I've`. Check meaning and grammar before changing a form. In particular, `let us know` and `let us help you` mean _allow us_, so do not change them to `let's`.

Flag repeated uncontracted forms when they make conversational copy sound formal or unlike its author. Do not treat an isolated expanded form as an error by itself.

### 13. Staccato check

Look for adjacent runs of two or more sentences where every sentence is short (about 12 words or fewer), declarative, a complete claim on its own, parallel in shape, and unconnected to the next sentence by a word or phrase such as `because`, `so`, `which`, `when`, `but`, or `and`. The run reads like a list of verdicts.

Example to rewrite: "The same request produces a different plan tomorrow. A passing test does not carry forward." Join the claims: "The same request produces a different plan tomorrow, so a passing test doesn't carry forward."

- Three or more qualifying sentences in a row: rewrite the run.
- Two qualifying sentences in a row: flag the run for review. Rewrite it when both sentences also avoid contractions.

Join the claims with a connective that states their relationship, vary sentence length on purpose, or add a concrete example that supports the claim. One short sentence after a longer one can work when the contrast is the point.

Also flag three or more consecutive sentences of nearly equal length, including long sentences. Read the run aloud and vary the pacing if the sentences repeat the same beat.

Exempt headlines, bullets, calls to action, captions, table cells, and quoted speech from a named person.

### 14. Sales pitch, caveats, and assistant residue

- In prose outside an ad, check for sales language such as `nestled`, `vibrant`, `boasts`, `must-see`, and `world-class`. Describe the fact a reader can verify.
- Cut needless caveats such as `important to note`, `worth mentioning`, or `results may vary`. Keep qualifications that tell the reader a specific limit or condition.
- Remove assistant residue on sight. Look for `as an AI`, `I hope this helps`, `great question`, `certainly` as an opening acknowledgment, `let me know if you would like`, and `here is a revised version`.

## Own-words mode

Use this mode when the author hands you their own rough words: a voice memo transcript, a brain dump, messages typed fast, or notes. Give the author's words back, tightened. In this mode you edit with scissors and you write nothing.

You may:

- Cut words and whole sentences.
- Put the author's sentences in a better order.
- Split one of the author's sentences, or join two of them, at a natural break.
- Fix spelling and punctuation.
- Spell out shorthand the author typed.

You may not:

- Write a new sentence, a bridge, a summary line or an ending.
- Swap the author's word for a different word.
- Smooth a rough sentence into a polished one.

When two parts need a bridge, leave the gap open and tell the author which one it is.

At most 5 of every 100 words in the piece may be words the author did not type. Check that with the script beside this file, and fix the piece until it passes:

```
python3 own_words_check.py RAW_FILE EDITED_FILE --cap 5
```

Items 10 and 11 of the checklist still apply as written in this mode. Every other item becomes a flag for the author, so report what you found and change nothing.

Report the piece, the checker's output, each word you added, and each gap you left.

## Output Format

```
SLOP SCRUB REPORT
=================

VOICE: [USED: project-root VOICE.md | NOT FOUND: offer to build one from two author-selected pieces]

1. Word scan: [CLEAN | FOUND: list with line numbers]
2. Construction scan: [CLEAN | FOUND: shapes and verbs]
3. Drumroll scan: [CLEAN | FOUND: list]
4. Metaphor check: [CLEAN | FOUND: list]
5. Sensory check: [CLEAN | FOUND: list]
6. Quietness check: [CLEAN | FOUND: list]
7. Profundity check: [CLEAN | FOUND: inflated claims, empty commentary, or endings]
8. Bartender test: [PASS | FLAGGED: list]
9. Specificity and swap test: [PASS | FLAGGED: paragraph and missing detail]
10. Em dash check: [CLEAN | FOUND: count]
11. Source check: [PASS | FLAGGED: claims and attributions]
12. Contraction check: [CLEAN | FOUND: list]
13. Staccato and repeated length: [CLEAN | FLAGGED: runs]
14. Sales pitch, caveats, and assistant residue: [CLEAN | FOUND: list]

CHANGES MADE:
- [original phrase] → [replacement phrase]
- [original phrase] → [replacement phrase]

CLEANED TEXT:
[full text with all fixes applied]
```

Check and report all 14 items, even when each one is clean.

## Severity (when prioritizing fixes)

**Instant kill (rewrite immediately)**

- Any banned word
- Any em or en dash in output text
- "It's not X, it's Y" and "not only X, but also Y" constructions
- Assistant residue
- Fabricated stats without source notes
- Engagement-bait questions at the end of posts ("What do you think?")

**Strong rewrite recommended**

- Unnecessary groups of three and dressed-up verbs
- Drumrolls and pre-loaded transitions
- Staccato runs of three or more qualifying sentences, and two qualifying sentences when both are uncontracted
- Repeated rhythm across three or more sentences of similar length
- Mid-sentence self-questions
- Sensory language on abstracts
- Endings that hint at significance and unsupported claims of importance elsewhere
- Concept-stacking
- Mixed metaphors
- Sales wording in non-ad prose and vague caveats

**Flag for review**

- Forced quietness or ghostly imagery (sometimes context justifies it)
- Interchangeable passages and missing facts the reader needs
- Unnamed sources and multiple citations that serve the same purpose
- Wording the intended reader would need to read twice
- Contractions or expanded forms that sound wrong for this author
- Two short verdict-like sentences when the rewrite threshold is unmet

## Rules

- Read any project voice guide before editing. Read a project-root `VOICE.md` in full on every run and honor any words and phrases the author avoids. Use the samples to match the author's range of sentence lengths, use of contractions, choice of `I` or `we`, and punctuation within the checklist rules. Preserve their directness and vocabulary. Compare the edited copy with the full range of the approved samples.
- Keep approved samples verbatim. When `VOICE.md` is absent, edit from the supplied material, state the file's absence in the report, and offer to build one from two short pieces the author selects. Never invent a voice, details, or samples for the author.
- When a paragraph needs rebuilding, use the author's supplied facts in the order the author would tell them. A swap of synonyms leaves the paragraph's structure and claims in place.
- Use the full checklist even if the local linter reports zero findings. The editor still decides whether each sentence serves the reader.
- The strongest basis for the edit is the author's own wording, supported by their facts and approved samples. A scrub cannot guarantee a detector verdict. Never add typos, odd punctuation, invisible characters, look-alike characters, or grammar errors to change a score.
- Sweep the draft for em and en dashes again when the edits are complete.
- If the user asks you to scrub a draft and you can't find one to scrub, ask. Don't invent text to scrub.
- Never apologize for finding slop. Finding it is the job. Reporting "clean" when you didn't actually check is the failure.
