#!/usr/bin/env python3
"""Code-Mixed-Dialog (Hindi-English) ingest adapter — Batch 2R Phase B.

Turns the cached bAbI/DSTC2 Hindi split into VoiceForge call_logs in data/normalized/. The source is
TEXT-ONLY (no timestamps), so every turn is timed null and the call is `stress_profile: unmeasured`
(the nullable-timing contract — never a fabricated ms). Restaurant-reservation domain, romanized Hinglish.

bAbI format: each non-blank line is `N <user>\\t<system>`; blank lines separate dialogues.
  - lines with NO tab are KB rows (`<rest> R_slot val`) or `api_call no result` -> backend, skipped.
  - `<SILENCE>` user parts are not user utterances -> skipped.
  - `api_call ...` system parts are backend actions, not speech -> skipped.
We keep only real user/agent natural-language utterances, merge consecutive same-speaker turns, and
count VoiceForge utterance-turns on THAT cleaned transcript. Selection is deterministic (file order),
deduped by transcript, capped at <=20 turns. Every call is validate_call()'d before it is written.

    .venv/bin/python pipeline/ingest_cmd.py [--n 24] [--max-turns 20] [--min-turns 4]
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
SRC = ROOT / "data" / "code_mixed_dialog"
OUT = ROOT / "data" / "normalized"

REPO = "https://github.com/sumanbanerjee1/Code-Mixed-Dialog"
COMMIT = "9df1d4dc800548a883f8bc1a9ce4116c77aebc02"


def parse_dialogs(raw):
    """Split the split file into dialogues (lists of raw lines)."""
    dialogs, cur = [], []
    for ln in raw.split("\n"):
        if ln.strip() == "":
            if cur:
                dialogs.append(cur); cur = []
            continue
        cur.append(ln)
    if cur:
        dialogs.append(cur)
    return dialogs


def clean_turns(lines):
    """bAbI lines -> cleaned [(speaker, text)] utterances (KB/api_call/SILENCE removed, same-speaker merged)."""
    utt = []
    for ln in lines:
        body = ln.split(" ", 1)[1] if " " in ln else ln
        if "\t" not in body:
            continue   # KB row or 'api_call no result' -> backend, not speech
        user, system = body.split("\t", 1)
        user, system = user.strip(), system.strip()
        if user and user != "<SILENCE>":
            utt.append(("user", user))
        if system and not system.startswith("api_call"):
            utt.append(("agent", system))
    # merge consecutive same-speaker turns into one
    merged = []
    for spk, text in utt:
        if merged and merged[-1][0] == spk:
            merged[-1] = (spk, (merged[-1][1] + " " + text).strip())
        else:
            merged.append((spk, text))
    return [{"turn_id": f"t{i + 1}", "speaker": spk, "text": text, "start_ms": None, "end_ms": None}
            for i, (spk, text) in enumerate(merged)]


def build_call(idx, turns, split):
    return {
        "call_id": f"cmd_hi_{idx:04d}",
        "source": "code_mixed_dialog",
        "language": "hi-en",
        "stress_profile": "unmeasured",
        "workflow_type": "restaurant_reservation",
        "turns": turns,
        "audio_path": None,
        "metadata": {
            "timing_observed": False,
            "source_dataset": "Code-Mixed-Dialog",
            "source_repo": REPO,
            "source_commit": COMMIT,
            "source_split": split,
            "source_dialog_index": idx,
            "license": "Apache-2.0 (repo LICENSE); CC BY 4.0 on the arXiv paper",
            "translation_status": "translated (human, from English DSTC2)",
            "domain": "DSTC2 restaurant reservation",
            "utterance_turns": len(turns),
            "selection_rule": "deterministic file-order; 4<=utterance_turns<=20; deduped by transcript",
        },
    }


def main():
    from normalize import validate_call
    from signals import timing_mode
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=24)
    ap.add_argument("--max-turns", type=int, default=20)
    ap.add_argument("--min-turns", type=int, default=4)
    ap.add_argument("--split", default="dev")
    args = ap.parse_args()

    raw = (SRC / f"dialog-dstc2-{args.split}.txt").read_text(encoding="utf-8")
    dialogs = parse_dialogs(raw)
    print(f"source: {len(dialogs)} dialogues in {args.split} split @ {COMMIT[:8]}")

    OUT.mkdir(parents=True, exist_ok=True)
    selected, seen_transcripts, counts = [], set(), []
    for idx, lines in enumerate(dialogs):
        turns = clean_turns(lines)
        n = len(turns)
        if not (args.min_turns <= n <= args.max_turns):
            continue
        sig = tuple(t["text"] for t in turns)
        if sig in seen_transcripts:        # no duplicate transcripts (also guards parallel-dialogue dupes)
            continue
        seen_transcripts.add(sig)
        call = build_call(idx, turns, args.split)
        validate_call(call)                # boundary-validate BEFORE writing (Codex)
        assert timing_mode(call["turns"]) == "unmeasured", "cmd call must be all-null timing"
        selected.append(call); counts.append(n)
        if len(selected) == args.n:
            break

    for call in selected:
        (OUT / f"{call['call_id']}.json").write_text(json.dumps(call, indent=2) + "\n")

    counts.sort()
    print(f"wrote {len(selected)} cmd_hi_* call_logs to data/normalized/ "
          f"(utterance-turns: min {counts[0]} / median {counts[len(counts)//2]} / max {counts[-1]})")
    print(f"  call_ids: {selected[0]['call_id']} … {selected[-1]['call_id']}")
    # show one cleaned transcript for eyeballing
    s = selected[0]
    print(f"\n  sample {s['call_id']} ({len(s['turns'])} turns):")
    for t in s["turns"][:8]:
        print(f"    {t['speaker']:5} | {t['text'][:70]}")
    if len(selected) != args.n:
        print(f"\n  WARNING: only {len(selected)} of {args.n} requested (raise --split trn or relax filters)")


if __name__ == "__main__":
    main()
