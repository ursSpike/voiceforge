# PUSH PROTOCOL — ship-check owns this

## Policy

- No automatic commits or pushes.
- No background process stages files periodically.
- No second “extras repo” during the event. Moving files now risks breaking runtime paths and history.
- Scratch/design references remain untouched and unstaged. Archive them after the event with a reviewed
  manifest.
- Stage an explicit allowlist only.
- Every push requires Spike’s one-word approval: `push`.

## Protected Paths

Do not stage changes to these unless the task explicitly names them and an audit approves the diff:

- `eval/label_manifest.json`
- `eval/labels_spike.csv`
- `eval/label_snapshot.json`
- `out/judge_results.json`
- `out/calls.json`
- `out/analytics.json`
- `out/demo_report_data.json`
- `rubric.yaml`

## Before Commit

```bash
git status --short
git diff --check
git diff --stat
git diff -- <explicit paths>
```

Then:

1. Reject unrelated notebook or scratch changes.
2. Search the intended diff for secrets, tokens, authorization headers, `.env` values, phone numbers,
   and personal data.
3. Run the smallest relevant tests plus:

```bash
.venv/bin/python pipeline/test_live_isolation.py
.venv/bin/python pipeline/preflight.py --offline
```

4. Stage explicit paths:

```bash
git add path/one path/two
git diff --cached --check
git diff --cached --stat
```

5. Show Spike the staged paths, test results, and commit message. Wait for `push`.

## Commit Attribution

Claude Code’s user-level setting (`~/.claude/settings.json`) disables generated commit/PR attribution
going forward, including fresh directories. This is a repository-owner preference, not a history
rewrite. Do not alter existing commits or authorship.

## After The Event

Create a sibling archive such as `/Users/varsh/voiceforge-extras` only after:

1. generating a move manifest;
2. proving no runtime/build path references each candidate;
3. using `git mv` for tracked files;
4. rebuilding `/` and `/platform`;
5. running preflight.

Until then, cleanliness means **selective staging**, not moving files.
