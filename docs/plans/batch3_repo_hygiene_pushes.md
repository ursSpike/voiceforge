# BATCH 3 — Repo hygiene automation + push choreography for the two sprints

**Why:** at 13:45 tomorrow the repo link IS the submission. It must read clean to a senior engineer in
90 seconds: obvious README, no scratch junk, no secrets, honest history. And during both sprints Spike
pushes live — so pushing must be one safe command, not a decision every time.

## Deliverable A — `scripts/repo_hygiene.py` (the cleaning automater)
A classifier + executor with `--dry-run` (default) and `--apply`:
1. **DELETE (scratch):** `TEST.txt`, `idea.md`, `idea2.md`, `idea3.txt`, `claude_design_handoff.zip`,
   `__pycache__/` anywhere, `.DS_Store`.
2. **ARCHIVE → `docs/archive/`:** `goldmine.md` (rename `sprint_format_notes.md`), historical planning
   docs that are superseded (`RESUME.md`, old `buildlog.md` if any), `CLAUDE_EVAL_BACKGROUND_AGENTS.md`.
   `audit.md` policy: keep AT ROOT (it's the live audit channel) but append-rotate old verdicts to
   `docs/audits/`.
3. **DESIGN REFERENCE → keep but caption:** `voiceforge_design/`, `voiceforge_design_1/`,
   `claude_design_handoff/`, root `*-skin*.css` → move under `design/` with a one-line README
   ("design reference bundles; runtime lives in web/ + pipeline/"). Git-mv so history survives.
4. **NEVER TOUCH:** frozen artifacts, `out/`, `eval/`, `data/`, `pipeline/`, `web/`, `docs/` living set,
   `experiments/`, `reports/`.
5. **Secret scan before every push:** grep staged diff for `sk_car_`, `Bearer `, `API_KEY=`, `.env`
   content; verify `.env` not tracked; exit 1 on hit.
6. Output a manifest of what it did → `docs/archive/hygiene_log.md`.

## Deliverable B — root `README.md` (the 90-second face)
Hero one-liner → what it does (the loop) → real headline numbers (κ 0.206 honest-calibration story,
metric trap 25/45, 76 calls, 46 blind-labeled) → quickstart (`open out/present.html`, regen commands) →
architecture diagram (from README_DEMO) → honesty principles → built-with (Bolna · Cartesia · Gemini).
Short. Links to docs/ for depth.

## Deliverable C — push choreography (the "scattered orderly pushes")
**Principle: honest commits of real work, committed AS the work happens — never theater.** Our git
history through the 7-day window is transparent and that's our brand; judges seeing live commits during
the sprints is the natural continuation, not a performance.
- **TONIGHT (pre-event):** land Batch 1 work as its real commits (skeleton / design integration /
  demo_docs). Run hygiene `--apply` AFTER Batch 1 lands, as its own commit: "repo hygiene: archive
  scratch + design references, add README".
- **SPRINT 1 cadence (~every 25–40 min, work permitting):**
  1. ~11:00 "live: first Cartesia-voiced Bolna call ingested (clean baseline)"
  2. ~11:45 "live: edge-case calls — barge-in ×2, code-switch (logs cached + normalized)"
  3. ~12:30 "live: judged today's calls (corpus-only; frozen calibration untouched)"
  4. ~13:15 "present surface: LIVE-today chapter with on-site results"
  5. 13:40 final pre-submission push + tag `submission-jun13`.
- **SPRINT 2 cadence:** before/after scenario commit → fallback capture commit → final `demo-jun13` tag.
- Every push = `repo_hygiene.py --check` (secret scan) first; alias one command:
  `make push` or `scripts/ship.sh "msg"` doing scan → add -A (respecting ignore) → commit → push.

## Deliverable D — privacy gate (BLOCKING before any public flip)
Repo is currently **private deliberately** (SPEC.md §1 carries personal context; an old commit had stray
personal text in dpo_export.py history). IF submission requires a public repo:
- Option 1 (fast, safe): keep repo private + add organizers as collaborators (ask the Buddy if accepted).
- Option 2 (public): sanitize SPEC.md §1 NOW + accept that deep history may contain the old stray text
  (assess: it was removed Jun 11; decide whether history rewrite is worth it — probably NOT during the
  sprint; the stray text was non-sensitive personal context, judge-readable risk is low. Spike decides.)
- The morning decision point: ask at check-in whether private+collaborator is acceptable. Default to
  Option 1 until told otherwise.

**Sequencing: TONIGHT after Batch 1 lands (~20 min of agent/automation work + Spike's privacy call).
The hygiene script is also rerun as the last step before the 13:45 push.**

## PLATINUM AMENDMENTS (from platinum.md)
- **Push cadence simplified (Spike's call):** 3–4 natural pushes total during Sprint 1 — not timed
  automation. Nothing auto-pushes: the ship script PROMPTS and Spike confirms. Suggested natural
  moments: (1) morning arrival state, (2) first live calls ingested, (3) live calls judged + surface
  updated, (4) 13:35-40 final pre-submission + tag `submission-jun13`.
- **Judging freeze:** no pushes 1:45–2:45 PM (clone window). Sprint 2 resumes on the SAME repo
  (1:45 is a snapshot, not a lock).
- **REJECTED from platinum (with reasons recorded):** fresh-repo-at-10:30 + staged "reveal" pushes +
  re-authoring AI-assisted core files to disguise provenance. Everyone had the 7-day window (goldmine's
  own conclusion); our differentiator IS auditability — a repo born at 10:30 contradicts the thesis in
  front of founding engineers; the existing transparent history reads senior. Keep the honest history.
- **Attribution preference (Spike decides):** going FORWARD, commits can drop the AI co-author line via
  a CLAUDE.md commit-guidelines preference — legitimate repo-owner choice, applied from the next commit
  if Spike says yes. No history rewrite either way.
