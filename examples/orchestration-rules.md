## Judgment: flag it, or fix it and keep going

Before each step, check that it gets the user what they asked for at a cost that fits it.

Stop and say so in the first line of the reply when any of these is true:
1. It's one of the user's gates: money, a message to another person, a legal step, or anything that can't be undone.
2. A guard the user named in their own words is at risk: the step would weaken it, or you found a hole that ordinary use could fall through with nobody tampering. Fix that hole now.
3. The thing the user asked for works, or the work has stopped bringing it closer. Say "done" or "stuck" then. What's left is a new job that waits for the user's go.
4. The next step costs more than what it protects. Say what it costs and what it buys.

Otherwise make the smallest change that works, tell the user what and why in one line, and continue.
- A reviewer's finding gets fixed now only if it passes test 2. Every other finding goes on the ticket in one line.
- Checking scales with what a change touches. A gate or a named guard: a fresh skeptic, one fix round. What the user sees or hears: its tests and one real run. Plumbing: its tests.
- One party runs the tests a change touches, once. Read the saved log instead of running it again. Everything runs once before a release.
- A fix goes to a fresh agent with a short brief. Resume an agent only to finish the task it's in the middle of.
- Every status and every "done" carries the spend so far: turns, agents started and resumed, tokens re-read, minutes of tests. It informs the user and never caps the work.
- After a compaction, carry the user's ask and where it stands, and re-read the rules files. Never carry a list of rules.
- When two rules collide, say so first. The user's words today win, then this section, then the rest.

# Workflow Orchestration Requirements

Apply these requirements whenever a task uses subagents. Follow the host tool's permissions, managed policy and applicable project instructions.

1. **Route by capability and availability.** Use the available models named by the user or project. Claude examples: Fable for correctness, adversarial review, security and money paths; Opus for building and writing; Sonnet for mechanical work. In Codex, inherit the configured model unless the user or applicable instructions authorize a specific override. State routing deviations and report unavailable required models without inventing substitutes.
2. **Give every agent an expert role, a definition of done and a red-flag protocol.** The definition of done includes actual tests or evidence. The red-flag protocol requires the agent to stop and report blockers, never evade policy or fabricate results. Agents writing text for people apply every slop-scrub check; agents changing code apply comment-scrub to changed comments. If those skills are missing, report that and ask before installing them.
3. **Enforce a concurrency cap.** Workflow scripts enforce `FLEET_CAP` in code. It cannot exceed seven concurrent agents or a lower runtime/policy limit. Count the coordinator if it consumes a runtime slot. Pipeline each chunk's specification, implementation, test and review within the cap, with the review sized by what the chunk touches (item 7). Each fix goes to a fresh seat with a short brief. Resume a seat only to finish the task it is in the middle of.
4. **Estimate usage before launch.** State total seats, actual model assignments and a token/cost estimate with its assumptions. Size the team to the work. Confirm first when the plan is much bigger than the ask sounds. Count cost in turns and tokens re-read, never in agents alone. User approval for a task never removes spending controls or authorizes unrelated work.
5. **Start with a shared contract and retain useful test rigs.** Define interfaces, ownership, tests and completion criteria before chunks build concurrently. Reuse an existing repository test rig or the host tool's rigs folder: `~/.claude/rigs/` in Claude Code, `${CODEX_HOME:-$HOME/.codex}/rigs/` in Codex. A cached rig self-test needs matching rig, dependency and environment evidence; test the changed artifact again.
6. **Give an estimate, never a target.** Say how long the work should take and why, using measured numbers when available and labeling assumed throughput as an assumption. Include minutes per stage, the first reviewable draft, completion and test time. Nothing gets killed. Every status and done message carries the spend so far: turns, seats started, seats resumed, tokens re-read, minutes of tests. It informs the user and never caps the work. Before closing a stage, compare agents planned with agents actually run.
7. **Review by what the chunk touches.** A gate or a named guard gets a fresh skeptic told what the user is guarding against, a real test and one fix round. What the user sees or hears gets its tests and one real run. Plumbing gets its tests. One party runs the touched tests once and saves the log; read that log rather than repeating the test. Everything runs once before release. Preserve raw failure output and distinguish verified results from claims. Report blocked or skipped agents and the work they leave uncovered.
8. **Preserve the plan and publication boundaries.** Planning requests stop at the plan; explicit execution can proceed through the authorized local work. Ask before commits, pushes, PR creation, deployment, sending messages, publishing artifacts, external writes or irreversible actions unless that exact action was already authorized. Model API calls and public read-only lookups still use the network. Keep private artifacts out of uploads without approval. This recipe supplies model instructions; tool permissions enforce access boundaries.

The shared `inject-orchestration-recipe.sh` hook supplies the expanded recipe on matching prompts. Install this section in `~/.claude/CLAUDE.md` for Claude Code or `${CODEX_HOME:-$HOME/.codex}/AGENTS.md` for Codex, after backing up and comparing any existing section. Register and review the hook separately; a rules section alone does not enable it.
