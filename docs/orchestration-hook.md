# Orchestration recipe hook: install and reference

The short version, with a test you can run, is in the [README](../README.md#orchestration-recipe-hook). This page holds the exact settings entries, the backup steps and the trigger rules.

A `UserPromptSubmit` hook for **Claude Code and Codex**. Both runtimes accept a JSON object with a `prompt` string on stdin and the `hookSpecificOutput.additionalContext` response below. The same script works in either tool; configuration and hook-trust steps differ.

The hook provides planning or execution instructions for the current job only. The time estimate tells the user how long the job is likely to take. Work continues within the user's authorization if the estimate runs over and ends when the requested result works. At each update and at completion, report how many turns you've used and how many seats you've started or resumed. Include tokens reread and minutes spent testing.

Give each fix to a fresh agent with a brief describing the finding and the files it affects. Include the test to run. Ask for independent review when a chunk touches a safeguard the user named or involves money, legal steps, messages to others, or another action that's hard to undo. Exercise changes the user will see or hear. Run focused tests for each chunk, inspect the saved logs, and keep any reusable test rig. Compare the agents planned with the agents that ran before closing each stage.

The recipe is model context. Agent limits and approval boundaries still depend on the agent following it and the runtime enforcing its permissions. This script neither launches agents nor intercepts pushes, deployments, or external writes. Keep your permission controls and spend-cap hooks enabled. Cloud model requests also use the network; a local workflow is not an offline workflow.

**Requirements:** Bash 3.2 or newer, `jq`, and standard `cat`, `grep`, and `tr` commands. Review the script before enabling it. Stop if managed policy disallows user hooks; do not change policy or skip hook trust.

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

Preserve existing hooks, including spend controls. Codex also supports inline `[hooks]` configuration; use one representation per configuration layer to avoid duplicates. Validate `hooks.json` with `jq empty`, then open `/hooks` in the CLI or Settings > Hooks in the app to review and trust the new hook. Registration alone does not activate an untrusted hook. Do not edit stored trust hashes or use flags that skip hook trust as an installation step.

Codex documents `additionalContextLimit` as an approximate token threshold with a default of 2,500 tokens. Set a positive integer for a limit or `0` for unlimited inline context. For output above the threshold, Codex saves the full output to disk and shows a preview. This example sets a conservative 8,000-token budget with room for recipe edits. [Codex hooks](https://learn.chatgpt.com/docs/hooks)

The current execution and plan recipes measure 6,802 and 1,955 ASCII characters, respectively. The test deliberately applies the budget to characters as a stricter size check. Those counts cannot establish whether Codex would have saved the execution recipe to disk with the former 5,000-token setting.

**Standing rules:** [examples/orchestration-rules.md](../examples/orchestration-rules.md) contains the companion section. In Claude Code, append it to `~/.claude/CLAUDE.md`; in Codex, use `${CODEX_HOME:-$HOME/.codex}/AGENTS.md`. If the section exists, compare and merge it rather than appending a duplicate. Claude examples name Fable, Opus and Sonnet; Codex uses its available models and inherits the configured model unless an override is authorized. Stop and report missing required models instead of inventing names or changing account settings.

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
