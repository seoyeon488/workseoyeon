"""Aggregate suite JSON rows: mean ± sd per (budget, arm). Usage: agg.py suite.json out.md [out.tsv]"""
import json, statistics, sys
from collections import defaultdict
d = json.load(open(sys.argv[1], encoding="utf-8"))
rows = d["rows"]
ARMS = ["no_action", "random", "patient_independent", "cost_first", "dcvc", "dcvc-no_bundles", "dcvc-no_dcv",
        "dcvc-no_recovery", "dcvc-no_evidence_routing"]
cols = [("CE", lambda r: r["system_confirmed_eligible"]), ("VE", lambda r: r["verified_eligible"]),
        ("FE", lambda r: r["false_eligible"]), ("CI", lambda r: r["system_confirmed_ineligible"]),
        ("VI", lambda r: r["verified_ineligible"]), ("FI", lambda r: r["false_ineligible"]),
        ("unver", lambda r: r["confirmed_unverified"]),
        ("Cov", lambda r: r["coverage"]), ("Unres", lambda r: r["unresolved"]), ("wait", lambda r: r["waiting"]),
        ("noact", lambda r: r["unresolved_no_action"]), ("min", lambda r: r["assumed_cost_minutes"]),
        ("act", lambda r: r["actions"]), ("zero", lambda r: r["fairness"]["zero_allocation"]),
        ("gini", lambda r: r["fairness"]["allocation_gini"])]
g = defaultdict(list)
for r in rows:
    g[(r["budget_minutes"], r["arm"])].append(r)


def fmt(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return "-"
    m = statistics.fmean(vals)
    s = statistics.stdev(vals) if len(vals) > 1 else 0.0
    f = (lambda x: f"{x:.3f}") if any(isinstance(v, float) and v != int(v) for v in vals) or abs(m) < 1 and m != 0 else (lambda x: f"{x:.2f}".rstrip("0").rstrip("."))
    return f(m) if s < 1e-9 else f"{f(m)}±{f(s)}"


lines = ["| 예산 | 팔 | n | " + " | ".join(c for c, _ in cols) + " | 해시(고유 수) |",
         "|" + "---|" * (len(cols) + 4)]
tsv = ["budget\tarm\tn\t" + "\t".join(c for c, _ in cols) + "\thashes"]
for b in sorted({k[0] for k in g}):
    for arm in ARMS:
        rs = g.get((b, arm))
        if not rs:
            continue
        hs = sorted({r["result_hash"][:10] for r in rs})
        vals = [fmt([f(r) for r in rs]) for _, f in cols]
        lines.append(f"| {b:g} | {arm} | {len(rs)} | " + " | ".join(vals) + f" | {len(hs)} |")
        tsv.append(f"{b:g}\t{arm}\t{len(rs)}\t" + "\t".join(vals) + "\t" + ",".join(hs))
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(lines) + "\n")
if len(sys.argv) > 3:
    open(sys.argv[3], "w", encoding="utf-8").write("\n".join(tsv) + "\n")
# identical-hash check dcvc vs no_dcv
same = defaultdict(lambda: [0, 0])
for (b, arm), rs in g.items():
    if arm != "dcvc":
        continue
    for r in rs:
        key = (r["cohort_index"], r["seed"])
        for ab in ("dcvc-no_dcv", "dcvc-no_recovery", "dcvc-no_bundles", "dcvc-no_evidence_routing"):
            o = [x for x in g.get((b, ab), []) if (x["cohort_index"], x["seed"]) == key]
            if o:
                same[(b, ab)][1] += 1
                same[(b, ab)][0] += o[0]["result_hash"] == r["result_hash"]
print("\n".join(lines))
print("hash-identical to dcvc:", {f"{b:g}/{ab}": f"{s}/{n}" for (b, ab), (s, n) in sorted(same.items())})
