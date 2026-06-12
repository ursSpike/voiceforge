#!/usr/bin/env python3
"""
Grounded Outcome Probe (Agent 2 — jun13_eval, ISOLATED investigation).

INVESTIGATION ONLY. This NEVER touches the production outcome field. It proposes an ADDITIVE
`outcome_evidence` contract derived from the PUBLIC SOURCE TRUTH of two dataset families, and
compares it against (a) the existing keyword task_completion HEURISTIC and (b) the human labels.

Two grounded families on the 46-call manifest (44 public; the 2 frozen bolna/hero are NOT public-
source-grounded and stay `unknown`):

  SpokenWOZ (swz_*) — raw cached at data/spokenwoz/data.json. We use the dialogue's:
    * goal.info / goal.book  (the user's constraints)
    * FINAL system-turn `metadata` belief state (constraint PRESERVED in tracked state)
    * per-system-turn `dialog_act`  *-inform acts (requested info SUPPLIED by agent)
    * `booking-book` dialog acts + booked payload (booking CONFIRMED where required)
  Code-Mixed-Dialog (cmd_hi_*) — raw cached at data/code_mixed_dialog/dialog-dstc2-dev.txt,
  mapped via normalized metadata.source_dialog_index. We use the hidden backend trace:
    * `api_call <args>` lines  (constraints represented in the backend query)
    * `api_call no result`     (KB miss)
    * `R_<slot>` KB rows        (the selected entity + its attributes)
    * the spoken system response (was requested info actually voiced; recovery after a miss)

Each signal is computed only when its source evidence exists; otherwise it is `unknown`
(never guessed). The call-level grounded verdict is a CONSERVATIVE roll-up:
    success  — required constraints grounded AND (booking confirmed where required) AND
               terminal resolution reached, with no contradiction
    fail     — a hard grounding failure (unrecovered KB miss with no offer, requested info
               never supplied, or required booking absent)
    unknown  — insufficient source evidence to decide

Run:  .venv/bin/python experiments/jun13_eval/grounded/grounded_probe.py
Writes: grounded_probe.json (machine output) next to this file.
The companion grounded_probe.md is hand-written from this script's output.

READ-ONLY w.r.t. everything outside experiments/jun13_eval/grounded/.
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]            # .../voiceforge
HERE = Path(__file__).resolve().parent
NORM = ROOT / "data" / "normalized"
SWZ_RAW = ROOT / "data" / "spokenwoz" / "data.json"
CMD_RAW = ROOT / "data" / "code_mixed_dialog" / "dialog-dstc2-dev.txt"
MANIFEST = ROOT / "eval" / "label_manifest.json"
LABELS = ROOT / "eval" / "labels_spike.csv"
SWZ_CACHE = HERE / "_swz_raw"                          # per-dialogue extracts (built on demand)

UNKNOWN = "unknown"


# ----------------------------------------------------------------------------- source loaders
def load_manifest():
    return json.loads(MANIFEST.read_text())["order"]


def load_labels():
    out = {}
    for r in csv.DictReader(LABELS.open()):
        out[r["call_id"]] = r["primary_label"]
    return out


def load_normalized(cid):
    return json.loads((NORM / f"{cid}.json").read_text())


def _brace_match(data, start):
    """Return end index (exclusive) of the JSON object beginning at data[start]=='{'."""
    depth = 0
    instr = False
    esc = False
    k = start
    while k < len(data):
        c = data[k]
        if esc:
            esc = False
        elif c == "\\":
            esc = True
        elif c == '"':
            instr = not instr
        elif not instr:
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return k + 1
        k += 1
    raise ValueError("unbalanced braces")


def ensure_swz_cache(swz_ids):
    """Extract just the needed dialogues from the 246MB raw file into a small local cache.
    Raw-streams once; does NOT modify the source. Idempotent."""
    SWZ_CACHE.mkdir(parents=True, exist_ok=True)
    missing = [i for i in swz_ids if not (SWZ_CACHE / f"{i}.json").exists()]
    if not missing:
        return
    data = SWZ_RAW.read_text()
    for mul in missing:
        key = f'"{mul}": '
        i = data.find(key)
        if i < 0:
            continue
        j = i + len(key)
        end = _brace_match(data, j)
        (SWZ_CACHE / f"{mul}.json").write_text(data[j:end])


def load_swz(mul):
    return json.loads((SWZ_CACHE / f"{mul}.json").read_text())


def load_cmd_blocks():
    raw = CMD_RAW.read_text()
    return [b for b in raw.split("\n\n") if b.strip()]


# ----------------------------------------------------------------------------- SpokenWOZ probe
# slot-name aliases: goal uses camelCase/spaced; belief `semi` uses lowercase nospace; acts vary.
def _norm_slot(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _belief_value(meta, dom, slot):
    """Look up a tracked value in a turn's metadata belief state for dom.slot (semi or book)."""
    dd = (meta or {}).get(dom, {})
    nslot = _norm_slot(slot)
    for bucket in ("semi", "book"):
        for k, v in (dd.get(bucket) or {}).items():
            if _norm_slot(k) == nslot and v not in ("", [], None):
                return v
    return None


def _final_belief(log):
    for t in reversed(log):
        if t.get("metadata"):
            return t["metadata"]
    return {}


def _system_inform_slots(log):
    """All (domain, slot) pairs the system informed via *-inform / *-recommend dialog acts."""
    informed = set()
    for t in log:
        if t.get("tag") != "system":
            continue
        for act, pairs in (t.get("dialog_act") or {}).items():
            dom = act.split("-")[0]
            kind = act.split("-", 1)[1] if "-" in act else ""
            if kind in ("inform", "recommend", "offerbooked", "offerbook"):
                for slot, _val in pairs:
                    informed.add((dom, _norm_slot(slot)))
    return informed


def _booking_confirmed(log):
    """Booking is CONFIRMED if any of these source forms appears:
      (a) a `booking-book` act with a payload,
      (b) a non-empty `booked` list in any belief state, OR
      (c) a `*-ack` act carrying committed book* slots (book/people/day/time/stay) — the system
          acknowledging the reservation details (e.g. restaurant-ack [bookpeople, booktime, bookday]).
    A `booking-request` (asking for details, value '?') is NOT a confirmation."""
    for t in log:
        for act, pairs in (t.get("dialog_act") or {}).items():
            if act == "booking-book" and pairs and pairs != [["none", "none"]]:
                return True
            if act.endswith("-ack"):
                for slot, val in pairs:
                    if slot.lower().startswith("book") and val not in ("?", "", "none"):
                        return True
        meta = t.get("metadata") or {}
        for dom, dd in meta.items():
            if (dd.get("book") or {}).get("booked"):
                return True
    return False


def _terminal_resolution(log):
    """Did the dialogue reach a clean close — general-bye / thanks exchange at the tail?"""
    tail_acts = set()
    for t in log[-4:]:
        tail_acts |= set(t.get("dialog_act", {}).keys())
    return bool(tail_acts & {"general-bye", "general-thanks", "general-welcome"})


def probe_swz(cid, mul):
    d = load_swz(mul)
    goal = d.get("goal", {})
    log = d.get("log", [])
    final = _final_belief(log)
    informed = _system_inform_slots(log)

    # Required info/book constraints, requested (reqt) slots
    info_constraints = []     # (dom, slot, val)
    book_constraints = []     # (dom, slot, val)
    reqt_slots = []           # (dom, slot)
    for dom, g in goal.items():
        if not isinstance(g, dict) or not g:
            continue
        for slot, val in (g.get("info") or {}).items():
            info_constraints.append((dom, slot, str(val)))
        for slot, val in (g.get("book") or {}).items():
            book_constraints.append((dom, slot, str(val)))
        for slot in (g.get("reqt") or []):
            reqt_slots.append((dom, slot))

    sig = {}

    # SIGNAL 1: constraint supplied by user  (proxy: goal declares info constraints at all)
    sig["constraint_supplied"] = bool(info_constraints) if (info_constraints or book_constraints) else UNKNOWN

    # SIGNAL 2: constraint preserved in tracked state
    if info_constraints:
        preserved = []
        for dom, slot, val in info_constraints:
            tracked = _belief_value(final, dom, slot)
            ok = tracked is not None and _norm_slot(str(tracked)) == _norm_slot(val) if tracked is not None else False
            # allow prefix match for truncated belief (e.g. idnumber)
            if not ok and tracked is not None:
                a, b = _norm_slot(str(tracked)), _norm_slot(val)
                ok = a.startswith(b) or b.startswith(a)
            preserved.append({"dom": dom, "slot": slot, "goal": val,
                              "tracked": tracked, "ok": bool(ok)})
        sig["constraint_preserved"] = preserved
        sig["constraint_preserved_frac"] = round(sum(p["ok"] for p in preserved) / len(preserved), 3)
    else:
        sig["constraint_preserved"] = UNKNOWN
        sig["constraint_preserved_frac"] = UNKNOWN

    # SIGNAL 3: requested info supplied by agent
    if reqt_slots:
        supplied = []
        for dom, slot in reqt_slots:
            ok = (dom, _norm_slot(slot)) in informed
            supplied.append({"dom": dom, "slot": slot, "informed": ok})
        sig["reqt_supplied"] = supplied
        sig["reqt_supplied_frac"] = round(sum(s["informed"] for s in supplied) / len(supplied), 3)
    else:
        sig["reqt_supplied"] = UNKNOWN
        sig["reqt_supplied_frac"] = UNKNOWN

    # SIGNAL 4: booking confirmed where required
    if book_constraints:
        sig["booking_required"] = True
        sig["booking_confirmed"] = _booking_confirmed(log)
    else:
        sig["booking_required"] = False
        sig["booking_confirmed"] = UNKNOWN

    # SIGNAL 5: terminal resolution
    sig["terminal_resolution"] = _terminal_resolution(log) if log else UNKNOWN

    # ----- conservative roll-up
    verdict, why = _swz_verdict(sig)
    return {"family": "spokenwoz", "raw_id": mul,
            "evidence": {
                "goal_info": info_constraints,
                "goal_book": book_constraints,
                "goal_reqt": reqt_slots,
                "n_turns": len(log),
            },
            "signals": sig, "verdict": verdict, "verdict_reason": why}


def _swz_verdict(sig):
    cp = sig["constraint_preserved_frac"]
    rq = sig["reqt_supplied_frac"]
    # Hard fail conditions
    if sig["booking_required"] and sig["booking_confirmed"] is False:
        return "fail", "required booking never confirmed in trace"
    if rq != UNKNOWN and rq == 0.0:
        return "fail", "agent never supplied any requested info slot"
    if cp != UNKNOWN and cp < 0.5:
        return "fail", f"only {cp} of user constraints preserved in tracked state"
    # Success conditions
    cons_ok = (cp == UNKNOWN) or (cp >= 0.75)
    reqt_ok = (rq == UNKNOWN) or (rq >= 0.5)
    book_ok = (not sig["booking_required"]) or (sig["booking_confirmed"] is True)
    term_ok = sig["terminal_resolution"] in (True, UNKNOWN)
    if cons_ok and reqt_ok and book_ok and term_ok:
        return "success", "constraints preserved, requested info supplied, booking ok, clean close"
    return UNKNOWN, "partial grounding; insufficient to assert success or fail"


# ----------------------------------------------------------------------------- Code-Mixed probe
API_RE = re.compile(r"\bapi_call\s+(.+)")
KB_RE = re.compile(r"^(\S+)\s+R_(\w+)\s+(.+)$")


def parse_cmd_block(block):
    """Return structured turns: user utterances, system spoken responses, api_calls, kb rows."""
    user_turns, sys_spoken, api_calls, no_results, kb_rows = [], [], [], 0, []
    for ln in block.split("\n"):
        ln = ln.rstrip()
        if not ln:
            continue
        # strip leading turn number
        m = re.match(r"^\d+\s(.*)$", ln)
        body = m.group(1) if m else ln
        if "\t" in body:
            u, s = body.split("\t", 1)
            u = u.strip()
            s = s.strip()
            if u and u != "<SILENCE>":
                user_turns.append(u)
            am = API_RE.match(s)
            if am:
                api_calls.append(am.group(1).strip())
            elif s:
                sys_spoken.append(s)
        else:
            # bare line: api_call no result, api_call ..., or an R_ KB row
            if body.strip() == "api_call no result":
                no_results += 1
            elif API_RE.match(body):
                api_calls.append(API_RE.match(body).group(1).strip())
            else:
                km = KB_RE.match(body)
                if km:
                    kb_rows.append({"entity": km.group(1), "slot": km.group(2), "value": km.group(3)})
    return user_turns, sys_spoken, api_calls, no_results, kb_rows


# DSTC2 facet vocab (cuisine/area/price). Borrowed from the production heuristic's vocab so the
# comparison is apples-to-apples on the SAME tokens, but here used to read the BACKEND trace, not
# to keyword-match free text.
AREAS = {"north", "south", "east", "west", "centre", "center"}
PRICES = {"cheap", "moderate", "expensive"}
CUISINES = {"chinese", "thai", "indian", "italian", "french", "british", "european", "asian",
            "asian_oriental", "international", "korean", "lebanese", "spanish", "turkish",
            "vietnamese", "portuguese", "mediterranean", "gastropub", "seafood", "japanese",
            "persian", "african", "catalan", "jamaican", "cuban", "moroccan", "modern",
            "fusion", "steakhouse", "barbeque", "vegetarian", "venetian", "polynesian",
            "north_american", "world", "tuscan", "creative", "scottish", "kosher",
            "traditional", "crossover", "halal", "unusual", "swedish", "australasian",
            "afghan", "basque", "belgian", "brazilian", "canapes", "caribbean", "christmas",
            "corsica", "danish", "eritrean", "english", "german", "greek", "hungarian",
            "indonesian", "irish", "malaysian", "mexican", "polish", "romanian", "russian",
            "singaporean", "south_african", "swiss", "thai_and_chinese", "welsh", "austrian"}


def probe_cmd(cid):
    n = load_normalized(cid)
    idx = n["metadata"]["source_dialog_index"]
    block = CMD_BLOCKS[idx]
    user_turns, sys_spoken, api_calls, no_results, kb_rows = parse_cmd_block(block)

    sig = {}

    # SIGNAL 1: requested constraints represented in the api_call
    # Collect facets the user asked for (from user utterances) vs facets present in api_call args.
    user_text = " ".join(user_turns).lower()
    asked = set()
    for tok in re.findall(r"[a-z_]+", user_text):
        if tok in AREAS:
            asked.add(("area", "north" if tok in ("north",) else tok))
        if tok in PRICES:
            asked.add(("price", tok))
        if tok in CUISINES:
            asked.add(("cuisine", tok))
    api_text = " ".join(api_calls).lower()
    if api_calls:
        # of the distinct facet VALUES the user named, how many appear in some api_call?
        named_vals = {v for _k, v in asked}
        if named_vals:
            rep = {v: (v in api_text) for v in named_vals}
            sig["constraints_in_api_call"] = rep
            sig["constraints_in_api_call_frac"] = round(sum(rep.values()) / len(rep), 3)
        else:
            sig["constraints_in_api_call"] = UNKNOWN
            sig["constraints_in_api_call_frac"] = UNKNOWN
    else:
        sig["constraints_in_api_call"] = UNKNOWN
        sig["constraints_in_api_call_frac"] = UNKNOWN

    # SIGNAL 2: a selected entity is consistent with KB attributes.
    # The KB may return MANY candidates; the agent picks ONE and voices it. The "selected" entity
    # is therefore the KB entity whose delex token appears in the spoken responses (NOT merely the
    # first row). Fall back to first row only if none is voiced.
    entities = sorted({r["entity"] for r in kb_rows})
    spoken = " ".join(sys_spoken).lower()
    voiced_entities = [e for e in entities if e in spoken]
    selected = voiced_entities[0] if voiced_entities else (entities[0] if entities else None)
    sig["selected_entity"] = selected
    sig["kb_candidate_count"] = len(entities)
    sig["kb_attributes"] = {r["slot"]: r["value"] for r in kb_rows if r["entity"] == selected}
    if entities:
        sig["entity_voiced"] = bool(voiced_entities)
    else:
        sig["entity_voiced"] = UNKNOWN

    # SIGNAL 3: requested info actually spoken
    # The user asks for phone/address/postcode/price; the system should voice the delex slot token
    # or the literal value. Map ask -> expected token.
    ask_map = {"phone": ["phone", "_phone"], "address": ["address", "_address"],
               "post": ["post", "post_code", "_post_code", "postcode"],
               "price": ["price", "cheap", "moderate", "expensive", "range"]}
    requests = []
    for ut in user_turns:
        u = ut.lower()
        for key, toks in ask_map.items():
            if key in u or (key == "post" and "post" in u):
                requests.append(key)
    requests = list(dict.fromkeys(requests))
    spoken = " ".join(sys_spoken).lower()
    if requests:
        supplied = {}
        for key in requests:
            toks = ask_map[key]
            supplied[key] = any(t in spoken for t in toks)
        sig["info_requests"] = supplied
        sig["info_requests_frac"] = round(sum(supplied.values()) / len(supplied), 3)
    else:
        sig["info_requests"] = UNKNOWN
        sig["info_requests_frac"] = UNKNOWN

    # SIGNAL 4: no-result recovery
    if no_results:
        # recovery = at least one entity surfaced AFTER a no-result, i.e. an entity exists at all
        sig["no_result_count"] = no_results
        sig["no_result_recovered"] = bool(entities)
    else:
        sig["no_result_count"] = 0
        sig["no_result_recovered"] = UNKNOWN

    # SIGNAL 5: agent claims contradicting the backend trace
    # Check: if the spoken response asserts a facet (area/price/cuisine) about the selected entity,
    # does it match the KB row for that entity? (delex tokens are exact, so a mismatch is real.)
    contradiction = False
    contra_detail = []
    if selected:
        e = selected
        attrs = {r["slot"]: r["value"].lower() for r in kb_rows if r["entity"] == e}
        # cuisine
        for fac, vocab, kbslot in [("cuisine", CUISINES, "cuisine"), ("area", AREAS, "location"),
                                   ("price", PRICES, "price")]:
            kbval = attrs.get(kbslot)
            if not kbval:
                continue
            spoken_facets = {t for t in re.findall(r"[a-z_]+", spoken) if t in vocab}
            # If the agent voiced a facet of this type that differs from KB -> contradiction
            wrong = {f for f in spoken_facets if f != kbval and f not in (e,)}
            # only count if the KB value's own token is NOT also voiced (i.e. it really stated a wrong one)
            if wrong and kbval not in spoken_facets:
                contradiction = True
                contra_detail.append({"facet": fac, "kb": kbval, "voiced": sorted(wrong)})
    sig["agent_contradicts_backend"] = contradiction
    sig["contradiction_detail"] = contra_detail

    verdict, why = _cmd_verdict(sig)
    return {"family": "code_mixed_dialog", "raw_id": f"dialog#{idx}",
            "evidence": {
                "user_turns": user_turns,
                "api_calls": api_calls,
                "no_results": no_results,
                "kb_entities": entities,
                "sys_spoken_tail": sys_spoken[-3:],
            },
            "signals": sig, "verdict": verdict, "verdict_reason": why}


def _cmd_verdict(sig):
    # Hard fails
    if sig["agent_contradicts_backend"]:
        return "fail", f"agent claim contradicts KB trace: {sig['contradiction_detail']}"
    if sig["no_result_count"] and sig["no_result_recovered"] is False:
        return "fail", "KB returned no result and no alternative entity ever surfaced"
    if sig["info_requests_frac"] not in (UNKNOWN,) and sig["info_requests_frac"] == 0.0:
        return "fail", "user requested info the agent never voiced"
    cia = sig["constraints_in_api_call_frac"]
    if cia not in (UNKNOWN,) and cia < 0.5:
        return "fail", f"only {cia} of user-named constraints reached the backend api_call"
    # Success: an entity was found+voiced, requested info supplied, constraints honored, no contradiction
    entity_ok = sig["entity_voiced"] in (True, UNKNOWN)
    info_ok = sig["info_requests_frac"] in (UNKNOWN,) or sig["info_requests_frac"] >= 0.5
    cia_ok = cia in (UNKNOWN,) or cia >= 0.5
    recov_ok = sig["no_result_recovered"] in (True, UNKNOWN)
    if sig["selected_entity"] and entity_ok and info_ok and cia_ok and recov_ok:
        return "success", "entity found+voiced, constraints reached backend, requested info supplied, no contradiction"
    if sig["selected_entity"] is None and sig["no_result_count"] == 0:
        return UNKNOWN, "no api_call / no KB entity / no miss — nothing groundable in trace"
    return UNKNOWN, "partial grounding; insufficient to assert success or fail"


# ----------------------------------------------------------------------------- keyword baseline
def keyword_verdict(cid):
    sys.path.insert(0, str(ROOT / "pipeline"))
    from score import build_outcome  # READ-ONLY import of production heuristic
    out, frac, ncap, ntot = build_outcome(load_normalized(cid))
    return ("success" if out["task_completed"] else "fail"), f"{ncap}/{ntot} fields, frac={round(frac,2)}"


# ----------------------------------------------------------------------------- driver
CMD_BLOCKS = None


def main():
    global CMD_BLOCKS
    order = load_manifest()
    labels = load_labels()
    swz_ids = [c.split("swz_")[1] for c in order if c.startswith("swz_")]
    ensure_swz_cache(swz_ids)
    CMD_BLOCKS = load_cmd_blocks()

    results = []
    for cid in order:
        hum = labels.get(cid)
        if cid.startswith("swz_"):
            probe = probe_swz(cid, cid.split("swz_")[1])
            family = "spokenwoz"
        elif cid.startswith("cmd_hi_"):
            probe = probe_cmd(cid)
            family = "code_mixed_dialog"
        else:
            probe = {"family": "non_public", "raw_id": None, "evidence": {},
                     "signals": {}, "verdict": UNKNOWN,
                     "verdict_reason": "not a public-source dataset family (frozen bolna/hero) — no source ground truth"}
            family = "non_public"
        kw_verdict, kw_detail = keyword_verdict(cid)
        results.append({
            "call_id": cid,
            "family": family,
            "human_label": hum,
            "keyword_verdict": kw_verdict,
            "keyword_detail": kw_detail,
            "grounded_verdict": probe["verdict"],
            "grounded_reason": probe["verdict_reason"],
            "grounded_raw_id": probe["raw_id"],
            "evidence": probe["evidence"],
            "signals": probe["signals"],
        })

    # ---- coverage report: fraction of the 44 public manifest calls each signal is computable for
    public = [r for r in results if r["family"] in ("spokenwoz", "code_mixed_dialog")]
    n_public = len(public)
    signal_defs = {
        "spokenwoz": ["constraint_supplied", "constraint_preserved_frac", "reqt_supplied_frac",
                      "booking_confirmed", "terminal_resolution"],
        "code_mixed_dialog": ["constraints_in_api_call_frac", "entity_voiced", "info_requests_frac",
                              "no_result_recovered", "agent_contradicts_backend"],
    }
    # Two signals are CONDITIONAL (apply only to a subset): booking_confirmed applies only to calls
    # that REQUIRE a booking; no_result_recovered applies only to calls that hit a KB miss. For these
    # we report APPLICABLE coverage (computable / applicable), since a non-applicable call correctly
    # returns `unknown` and must NOT be counted as a parse gap. The STOP-flag fires on applicable
    # coverage, which is the true parse-coverage of the source-grounded rule.
    def applicable(fam, s, r):
        if fam == "spokenwoz" and s == "booking_confirmed":
            return r["signals"].get("booking_required") is True
        if fam == "code_mixed_dialog" and s == "no_result_recovered":
            return bool(r["signals"].get("no_result_count"))
        return True

    coverage = {}
    for fam, sigs in signal_defs.items():
        fam_rows = [r for r in public if r["family"] == fam]
        for s in sigs:
            app_rows = [r for r in fam_rows if applicable(fam, s, r)]
            computable = sum(1 for r in app_rows if r["signals"].get(s) not in (None, UNKNOWN))
            conditional = len(app_rows) != len(fam_rows)
            coverage[f"{fam}.{s}"] = {
                "computable": computable,
                "applicable": len(app_rows),
                "of_all_family": len(fam_rows),
                "applicable_coverage": round(computable / len(app_rows), 3) if app_rows else 1.0,
                "conditional": conditional,
            }

    # ---- agreement: grounded vs human, keyword vs human, on BINARY human labels among public calls
    def agree(field):
        a = t = 0
        rows = []
        for r in public:
            if r["human_label"] not in ("success", "fail"):
                continue
            if r[field] not in ("success", "fail"):
                continue   # grounded unknown not counted as agree/disagree
            t += 1
            if r[field] == r["human_label"]:
                a += 1
            else:
                rows.append(r["call_id"])
        return a, t, rows

    kw_a, kw_t, kw_dis = agree("keyword_verdict")
    gr_a, gr_t, gr_dis = agree("grounded_verdict")

    grounded_unknown = [r["call_id"] for r in results if r["grounded_verdict"] == UNKNOWN]

    out = {
        "meta": {
            "n_total_manifest": len(order),
            "n_public": n_public,
            "n_swz": sum(1 for r in public if r["family"] == "spokenwoz"),
            "n_cmd": sum(1 for r in public if r["family"] == "code_mixed_dialog"),
            "keyword_baseline_note": "reproduces production build_outcome (frac>=0.7)",
        },
        "coverage": coverage,
        "agreement_vs_human_binary": {
            "keyword": {"agree": kw_a, "of": kw_t, "disagreements": kw_dis},
            "grounded": {"agree": gr_a, "of": gr_t, "disagreements": gr_dis,
                         "note": "grounded `unknown` excluded from the denominator (never guessed)"},
        },
        "grounded_unknown_calls": grounded_unknown,
        "results": results,
    }
    (HERE / "grounded_probe.json").write_text(json.dumps(out, indent=2))

    # console summary
    print(f"public calls: {n_public} (swz {out['meta']['n_swz']} / cmd {out['meta']['n_cmd']})")
    print(f"keyword vs human (binary): {kw_a}/{kw_t}")
    print(f"grounded vs human (binary, unknown excluded): {gr_a}/{gr_t}")
    print(f"grounded unknown count: {len(grounded_unknown)} -> {grounded_unknown}")
    print("\nAPPLICABLE COVERAGE (parse-coverage among calls where the rule applies; STOP-flag any <0.80):")
    stops = []
    for k, v in coverage.items():
        flag = "  <-- STOP <0.80" if v["applicable_coverage"] < 0.80 else ""
        if flag:
            stops.append(k)
        cond = " [conditional]" if v["conditional"] else ""
        print(f"  {k:48s} {v['computable']}/{v['applicable']} = {v['applicable_coverage']}{cond}{flag}")
    print(f"\nSTOP-conditions hit: {stops if stops else 'NONE'}")
    print("wrote grounded_probe.json")


if __name__ == "__main__":
    main()
