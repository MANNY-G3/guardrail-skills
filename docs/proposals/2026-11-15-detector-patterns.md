# Prose checks for author facts and voice

## Scope

Extend slop-scrub to 14 checks and update the author voice template. Add a local linter for patterns a script can identify, while keeping the full checklist as the editing standard.

## Pattern mapping

Use the following observations as prompts for editing. A match alone cannot establish who wrote a passage. [Wikipedia's writing guide](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) describes related patterns and their limits.

| Observation | Change to the checklist |
| --- | --- |
| Claims that inflate an ordinary event into a turning point | In item 7, give the scale or consequence when the author supplies one. |
| Outlets, brands, or institutions named for prestige | In item 11, cite a source that supports the claim. Keep a second source only if it adds evidence the reader needs. |
| Commentary that repeats a fact in more abstract words | Apply item 7 throughout the piece. Cut commentary that never says what the evidence establishes. |
| Promotional wording in factual prose | In item 14, replace sales language outside ads with a fact the reader can verify. |
| Vague attributions presented as evidence | In item 11, name the source or drop the claim. |
| Formal verbs for simple descriptions | In item 2, prefer a plain verb when the meaning stays the same. |
| A paired construction that tries to make its second half sound bigger | In item 2, say what the reader needs to know directly. |
| Lists padded to reach three entries | In item 2, keep the entries that each serve a purpose. Apply the check to adjectives and nouns as well as clauses. |
| Qualifications without a condition the reader can use | In item 14, cut the caveat or name the condition that limits the claim. |
| Assistant phrases left inside the draft | In item 14, remove the assistant's opening, handoff, or sign-off from the draft. |

Item 9 asks for a detail only the author could provide in every paragraph. Rebuild a paragraph from the author's facts in the order the author would tell them. Flag the paragraph if the author hasn't supplied a detail.

Item 13 checks pacing in runs of three or more sentences of similar length. Read the run aloud before comparing it with the author's samples.

Edit sentence rhythm for the reader and author. These checks assess prose rather than determine authorship.

## Omissions

- Keep the existing banned list rather than importing another word table. Authors can adapt the list to their own writing.
- Reject synonym cycling as a repair strategy. Rebuild a paragraph from the author's facts when swapping words would leave the same gaps. Wikipedia's guide gives historical context for synonym cycling and cautions that syntax alone can mislead, including when reading older human writing. Its page carries a CC BY-SA 4.0 notice. This proposal draws on those cautions in original wording. [Wikipedia signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- Keep the tool focused on local editorial checks. No external scoring service is part of this change.

The linked writing guide was read on November 19, 2026.

## Acceptance checks

- Keep every existing banned word and the rule against em and en dashes in output. Report all 14 checks.
- Read the project-root `VOICE.md` in full when it exists. Preserve the author's range of sentence lengths and use of contractions. Follow their choice of pronoun and punctuation within the checklist rules. The template uses placeholders for the optional list of words and phrases the author avoids.
- Run the linter on the README example. Its frozen AI draft should produce findings, and the edit should pass while retaining the supplied project facts.
- Test clean input and inputs that produce findings or errors. Keep those checks local, with no network calls or credentials.
- Include authentic passages from before 2022 as controls when comparing drafts blind. Record what the comparison used and what it observed. A detector label alone cannot settle authorship or guarantee a verdict on future drafts.

## Local comparison

The six revisions made with the earlier checklist each returned zero findings from the linter. That baseline leaves no room to meet the acceptance target of fewer mechanical findings on five of six drafts. Record editorial observations separately.

After the owner asked for a stronger before-and-after demonstration, a fresh writer produced six more unedited drafts from richer fictional fact sheets. Each channel had a requested tone, recorded in `tests/fixtures/ai/challenge/generation.json`. The coordinator saved the raw hashes before measuring the drafts, and fresh editors applied the old and new checklists independently.

In that second batch, raw findings totaled 5 across four drafts. The old checklist left 1 finding and the new checklist left zero. The new checklist improved on the old in one of six drafts, so the original five-of-six target was still missed. Both batches remain in the repository; the exercise does not establish a detector score or general advantage.

The independent edit reduced the second batch's blog introduction from 190 words to 37 while preserving the supplied names and numeric values. Its mechanical findings fell from 2 to zero. The README uses a 39-word version with the cataloguing-project context restored from the notes; the benchmark body stays unchanged. The two historical controls from the first run remain unchanged.
