# job-application-writer: the full record

The short version is in the [README](../README.md#job-application-writer). This page holds what each round of tests tried and found, every count, what the tests don't cover, and how to run the checker and its tests. Run the commands from the top folder of the repo.

## How the tests worked

- **The detector.** Every piece was scanned on one of the leading AI writing detectors, from the night of 2026-11-26 into the early hours of 2026-11-27. It gives each text a human share, an AI share and a mixed share. A piece **passes** when its human share is higher than its AI share plus its mixed share. The numbers on this page are human shares.
- **Fresh writers.** A fresh writer is a new AI session that saw only one request, plus the skill folder when the test gave it one. It saw no notes from earlier rounds.
- **Requests.** Each request is a message from a made-up job seeker: a resume, a job posting, and in some requests an account of the work or three short posts on another subject. The job seekers and the postings were made up, and so were the resumes, except the published sample resumes named below.
- **Accounts.** An account is a person's own telling of their work. Every account in rounds 2 to 4 was a real person's published writing, copied word for word from United States government staff blogs. Rounds 2 and 3 used the same eight accounts, by seven authors, and round 4 used four of them.

## The first version, and why it failed

**Round 1.** Fresh writers wrote 14 pieces from a resume and a posting: 10 with the first version of the skill and 4 with no skill. That was 10 letters and 4 tailored resumes. All 14 read 0.0% human. The pieces with no skill did no better, so the skill didn't cause the failure, and it didn't prevent it either.

**The diagnosis.** 24 letters from a resume and a posting alone, counting round 1's 10, read 0.0% human every time. The 14 new ones tried, among other things, the bullets retold in time order, the resume's own wording kept, one long loose paragraph, a formal register, the posting's lines answered one by one, a voice sample laid on and a different greeting. One had made-up detail added as a check (the skill forbids made-up detail), and it read 0.0% too.

What did move a letter was the material. The same greeting, first line and sign-off around a real person's account read 100.0%. Two resume results added to that letter in a paragraph of their own dropped it to 0.0%. A resume bullet is a result summed up afterward, and every bullet retold as a sentence read as machine-written.

**Writing the rules.** The rule writer then built 35 letters on six accounts, and 25 passed. Six of the ten misses were every letter on one short account an AI had worded. The other four set resume claims after the last story, set a claim between two sentences of one story, set two unrelated resume results in a row, or opened in the user's voice with the close joined on.

Where the resume claims sat mattered most. A paragraph of claims after the last story cost one letter its pass (0.0%). With those claims moved up to sit right after the first line, and nothing else changed, the same letter read 79.3%. On two other letters the same move was worth 14 and 5 points.

## Round 2: the second version, on real accounts

Fresh writers had the second version and eight requests, each with a real account. All 12 letters scanned passed, from 97.9% to 100.0%. Four letters written from the same requests with no skill all failed: three read 100.0% AI and one 99.9% mixed. The round stopped before four more letters with the skill were scanned.

## Round 3: before the last fix

Fresh writers had the skill's text as it stood then. Its checker had the same rules as now, and only three lines of the checker's reading list have changed since. They wrote 19 pieces, and 18 passed. The fact check below led to tighter rules on tie lines and on choosing resume lines, and round 4 tested them.

- **Letters with an account and no writing sample:** 5 of 6 passed. One read 0.0% human, and the others read 68.9% to 100.0%. The miss and the lowest pass came from the same request, written by two different writers.
- **Letters with an account and three short posts on another subject as the sample:** 6 of 6 passed, from 93.7% to 100.0%.
- **Resumes tailored to a made-up posting:** 7 of 7 passed, all at 100.0%. They were tailored from five sample resumes a United States government agency published.

**The example in this repo.** The request in [examples/job-application-request.md](../examples/job-application-request.md) holds a real account: a United States Fish and Wildlife Service story, ["2024 Waterfowl Banding Operations: Saskatchewan 2"](https://www.fws.gov/story/2024-09/2024-waterfowl-banding-operations-saskatchewan-2), used word for word. The job seeker, the resume and the posting are made up. [examples/job-application-reply.txt](../examples/job-application-reply.txt) is the skill's whole reply, unedited, written with the text before its last fix. Its letter has no tie line. The checker found 0 fails and 0 things to check in its letter, and the letter read 100.0% human when scanned once on 2026-11-27.

<details><summary>Read the letter</summary>

> Dear Gulfmarsh Land Trust hiring team,
>
> I'm applying for the Director of Land Stewardship role at Gulfmarsh Land Trust. I have 13 years in wetland habitat and waterfowl work, and at the South Texas Refuge Complex I plan water levels, plantings and prescribed burns with refuge staff.
>
> In August 2024 I was on a waterfowl banding detail in Saskatchewan, with a crew of 4. On our drives between trap sites, there was time for reflection. I thought about how vastly different this work was from my day-to-day job. It came full circle for me to see thousands of ducks on their breeding grounds. They would not be so numerous and healthy without the habitat we provided at the South Texas Refuge Complex, about 2,000 miles away, and other refuges like ours. I came out of this experience with numerous cuts, bruises, achy joints and muscles, but also mentally refreshed and stronger than ever. I had a renewed sense of purpose. I knew I personally contributed to an integral link in the chain of conservation.
>
> Please let me know if you'd like to talk.
>
> Renata Szabo-Quill

</details>

After the letter, the reply says where each line came from and asks six questions it couldn't answer from the request, such as why the person wants this job.

## Fact check of round 3

An AI reviewer read all 19 round 3 pieces against their requests, letters sentence by sentence and resumes line by line, and ran the checker on each one.

- **Made up: 0.** Every number, name, date and title in all 19 pieces is in its request.
- **Another person's act told as the user's: 0.**
- **Made bigger: 1 letter.** The user had recommended one volunteer, his first, and his resume says "Recommend volunteers to the survey". The letter said "That's the volunteer recruiting this role calls for", for a posting that asks to "Recruit and train volunteers and student workers". The reviewer graded it mild.
- **A fit claimed that the request didn't back: 2 letters,** that one and one more. The other says "That patrol is the kind of winter cabin trip the posting lists first." The posting's first duty is to plan and lead winter trips, and the story never says he led the patrol. Both lines are tie lines, the skill's name for a short sentence that links one story to the job.
- **Copied from the writing sample: 0** of the 6 letters that had one.
- **Resumes:** 0 of 7 changed a number, date, degree, employer or title, and 0 of 7 added a skill, tool or keyword the resume doesn't support. Both tailored copies of one resume dropped the user's own line "Two years' experience as a manager", on a posting that asks for "3 or more years". The job dates stayed, so a reader now counts about eight years where her own summary said two. The skill allowed dropping a line then, so no rule caught it.

The reviewer's read of what let these through: the tie-line rule leaves the call to the writer and has no test for the user's own part or for size, and the checker can't judge tie lines. The resume drop sits where "drop the ones that don't" meets "when two things the user gave you disagree, use neither and ask", on a request that asked for the resume alone.

What changed after it: a tie line now counts as a claim about the user, so the size of the verb binds it, and it goes in only when the user did the very task the posting names, at that size, in their own words. A resume line that says how long, how much or at what level stays in whenever the posting sets a bar on that same thing, and a bar the user falls short of goes on the list of questions. Round 4 tested these rules.

The same reviewer, an AI and not a hiring manager, also gave each letter a 90-second hiring read. It asked of each one whether it would keep reading and whether the applicant would be glad they sent it. The answers were 4 yes, 8 mixed (2 of those leaning no) and 0 no. Most letters are one story, with the fit left to the second sentence, and the three letters for director jobs undersell people with 13 and 24 years behind them.

## Round 4: the final text

Fresh writers had the rules in `skills/job-application-writer/` as they are now, on four of the same accounts and two of the same sample resumes. They wrote 9 pieces, and 8 passed.

- **Letters with an account and no writing sample:** 2 of 3 passed, at 95.7% and 84.2%. The third read 0.0% human, with 37.0% mixed.
- **Letters with an account and three short posts as the sample:** 3 of 3 passed, all at 100.0%.
- **Tailored resumes:** 3 of 3 passed, all at 100.0%.

**Fact check of round 4.** An AI reviewer read all 9 pieces against their requests, the same way as in round 3. It found 0 made up, 0 made bigger, 0 borrowed, 0 fits claimed and 0 copied from a writing sample. No letter has a tie line. Both resumes on the request that lost its two-years line in round 3 keep it word for word, and no dropped line makes a resume say more than the user said. Two letters state as fact something their request only implies: that the first volunteer he recommended was a former teacher of his. The reviewer passed both, because it doesn't make him bigger, and a real user would be there to confirm a line like that.

**The cost.** Two letters say less about the job than their round 3 versions. One lost the user's own line joining her stories to the job, and the other lost the trail crew he led, though the job supervises instructors. The reviewer saw the change and didn't test its cause. Its 90-second hiring read came to 2 yes, 4 mixed (1 of those leaning no) and 0 no.

**The weak spot.** Letters on one account, a first overnight winter patrol told mostly as a scene, passed 3 times and failed 2 times with fresh writers. That was a pass in round 2, a fail and a pass in round 3, and a pass and a fail in round 4. Every other request passed every time from round 2 on. An account that says little of what the person did themselves can go either way.

## Resumes

- **Typed by people, untouched:** six read 100.0% human. Five were sample resumes a United States government agency published, and one was a work-history letter from 1859.
- **Written by an AI:** five read 0.0% human. Four of them were round 1's tailored resumes, and the fifth was a made-up resume as a request pasted it.
- **How far tailoring can go:** the rule writer tailored two of the agency samples five ways. Choosing, ordering and cutting bullets read 100.0% both times. Adding a summary line built from the person's own phrases read 100.0%, and so did rewording every bullet lightly. Rewording every bullet heavily with the layout kept read 97.2%. A full rewrite with a new summary, new section names and merged bullets read 0.0% human (100.0% mixed). That's why the skill's resume step keeps your wording and your layout.

## All the counts

| Test | Who wrote it | Pieces | Passed | Human share |
| --- | --- | --- | --- | --- |
| Round 1: letters (10) and resumes (4) from a resume and a posting | Fresh writers, first version (10) or no skill (4) | 14 | 0 | 0.0 every time |
| Letters from a resume and a posting alone, in many styles (includes round 1's 10 letters) | Fresh writers and the rule writer | 24 | 0 | 0.0 every time |
| Letters on six real accounts | The rule writer | 35 | 25 | not listed here |
| Round 2: letters on eight real accounts | Fresh writers, second version | 12 | 12 | 97.9 to 100.0 |
| Round 2: the same requests | Fresh writers, no skill | 4 | 0 | 0.0 every time |
| Round 3: letters with an account, no writing sample | Fresh writers, before the last fix | 6 | 5 | 0.0 once, the rest 68.9 to 100.0 |
| Round 3: letters with an account and three short posts | Fresh writers, before the last fix | 6 | 6 | 93.7 to 100.0 |
| Round 3: tailored resumes | Fresh writers, before the last fix | 7 | 7 | 100.0 every time |
| Round 4: letters with an account, no writing sample | Fresh writers, final text | 3 | 2 | 0.0 once, the others 95.7 and 84.2 |
| Round 4: letters with an account and three short posts | Fresh writers, final text | 3 | 3 | 100.0 every time |
| Round 4: tailored resumes | Fresh writers, final text | 3 | 3 | 100.0 every time |
| Resumes typed by people, untouched | People | 6 | 6 | 100.0 every time |
| Resumes an AI wrote (includes round 1's 4) | AI | 5 | 0 | 0.0 every time |

## What the tests don't cover

- **One detector, one night.** Another detector, or this one on another day, may read the same text differently.
- **Polished accounts only.** Every account was published writing. No account typed fast or spoken by a user has been tried.
- **No job seeker's own resume.** The resumes people typed were published samples, so the detector may have seen them before.
- **No hiring manager** has judged a letter.
- **Tie lines and dropped lines.** Two of 12 round 3 letters claimed a fit the request didn't back, and one resume dropped a line that showed the user short of a requirement. After the rules were tightened, round 4's 6 letters had no tie line and its 3 resumes kept every such line. That's 9 pieces, and no script catches either problem, so read each tie line and each dropped line against what you did.
- **An account with little of your own part in it.** Letters on one account told mostly as a scene passed 3 times and failed 2 times. Tell what you did yourself, with the numbers, when the skill asks.
- **Few writers per request.** Each request in rounds 2 to 4 was written by one or two writers in each round.
- **A letter from bullets alone.** When you say "write it now" with no account, the skill writes a short letter from your resume. Every letter like that in the tests read as machine-written.
- **No score is a promise.** The skill never adds typos, odd characters or broken grammar to change one, and neither should you.

## The checker

`letter_check.py` tests the letter rules a script can count. It needs only Python 3, makes no network calls and writes no files.

```sh
python3 skills/job-application-writer/letter_check.py letter.txt --source resume.txt posting.txt notes.txt
python3 skills/job-application-writer/letter_check.py letter.txt --source resume.txt posting.txt --voice
python3 skills/job-application-writer/letter_check.py letter.txt --json
```

- A line marked `fail` breaks a rule in `SKILL.md`. Fix it and run the checker again.
- A line marked `check this` points at something to read, such as a number or a name that's in none of the `--source` files. It proves nothing on its own.
- `--voice` lets the first line run to 30 words, for a letter whose opening uses your own way of opening.
- The report ends with the rules a script can't judge, so read the letter for those.

Exit status is `0` when nothing fails, `1` when a rule fails, or `2` for bad input. A clean run never proves the facts are true.

## Run the tests

```sh
python3 -m unittest discover -s tests
python3 -m unittest tests.test_letter_check
```

The first runs every test in the repo, and the second runs the checker's 42 alone. The detector scans aren't in this repo. To test the skill yourself, write a letter with it and scan the letter on a detector you trust.
