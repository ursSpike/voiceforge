# TODAY — Jun 13. The only file you drive the day from.

TIME | CHECK | COMMAND | RESULT | NEXT
---|---|---|---|---
before leaving | demo_docs reads ≤6:30 | open docs/demo_docs.md, read aloud | ? | pack, go
on arrival | preflight green | `.venv/bin/python pipeline/preflight.py` | ? | start booth Buddy chat
10:30 | Buddy: interruption telemetry? private-repo OK? | ask | ? | gates call #5 + repo decision
~10:45 | live call #1 clean booking made + logs saved | dial Bolna agent | ? | paste exec id to coordinator
~10:50 | call #1 ingested + judged | `.venv/bin/python pipeline/ingest_live.py --execution <id> && .venv/bin/python pipeline/judge_live.py` | ? | glance /platform LIVE-TODAY
~11:05 | live call #2 Hinglish | dial + save logs | ? | paste exec id
~11:20 | call #2 ingested+judged | (same command, new id) | ? | glance /platform
~11:35 | live call #3 ambiguous+repair | dial + save | ? | paste exec id
~11:50 | call #3 ingested+judged | (same) | ? | glance /platform
~12:05 | live call #4 changed-slot | dial + save | ? | paste exec id
~12:20 | call #4 ingested+judged | (same) | ? | (call #5 barge-in ONLY if Buddy confirmed telemetry)
~12:40 | isolation holds (live didn't touch frozen) | `.venv/bin/python pipeline/test_live_isolation.py` | ? | proceed to submission prep
13:30 | submission text ready | open submission draft | ? | paste at 13:45
13:40 | final push + tag | confirm push to coordinator | ? | `git tag submission-jun13`
13:45 | SUBMIT (repo URL + desc + demo URL/loom) | submission portal | ? | STOP pushing till 14:45
13:45–14:45 | judging freeze — NO pushes | rehearse Q&A (spar) | ? | wait for Top-10
15:00–16:30 | (if Top 10) before/after + capture + rehearse ×2 | per master plan Phase 4 | ? | final demo-jun13 tag
16:40+ | present: / for story → /platform for live call → close → Q&A | — | ? | done

---
SAFE FALLBACK (always works, offline): `open out/dashboard.html`
LIVE COMMAND (memorize): `.venv/bin/python pipeline/ingest_live.py --execution <id> && .venv/bin/python pipeline/judge_live.py`
NEVER: edit eval/ or out/ by hand · `git add -A` · push 13:45–14:45 · call live calls "calibrated"
