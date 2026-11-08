"""Scratch driver (not in repo): run suite ARMS on the NSCLC eval set (PR #43, 240 pairs) through WP6 runner.run
with the external pair GT. Same loader as ctrec.sim.__main__.load_cohorts. Usage: wp6_eval_arms.py BUDGETS SEEDS OUT.json"""
import json, subprocess, sys, time, types
import ctrec
from ctrec.sim import __main__ as M, runner
from ctrec.sim.suite import ARMS, initial_open
from ctrec.engine.bundles import SourceCatalog
from ctrec.engine.contracts import EffortBudget, PairStatus

budgets = [int(x) for x in sys.argv[1].split(",")]
seeds = [int(x) for x in sys.argv[2].split(",")]
out_path = sys.argv[3]
arms_only = sys.argv[4].split(",") if len(sys.argv) > 4 else None
a = types.SimpleNamespace(generator="data/nsclc/eval/inputs/generator_config.json", scenario="nsclc-eval-v1",
                          map="data/nsclc/eval/inputs/source_map.json", trials_dir="data/nsclc/trials",
                          replicate="0", include_draft=False)
co = M.load_cohorts(a)[0]
labels, gt_kind = M.load_gt(__import__("pathlib").Path("data/nsclc/eval/pair_gt.csv"))
from collections import Counter
print("ctrec", ctrec.__file__, "HEAD", subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip())
print("pairs", len(labels), Counter(labels.values()))
cat = SourceCatalog()
init = initial_open(co)
rows = []
for b in budgets:
    bud = EffortBudget(coordinator_minutes=b, clinician_minutes=60, horizon_steps=10)
    for seed in seeds:
        for arm, pid, cfg in ARMS:
            if arms_only and arm not in arms_only:
                continue
            t = time.time()
            spec = runner.build_spec(f"eval-{arm}-{b}-{seed}", pid, co, bud, seed, dict(cfg), cat)
            r = runner.run(spec, co, cat, labels=labels, gt_kind=gt_kind)
            pairs = r.final.pairs()
            lab = lambda p: labels.get(p.pair.key, "unlabeled")
            st = Counter(p.status.value for p in pairs)
            ce = [p for p in pairs if p.status == PairStatus.CONFIRMED_ELIGIBLE]
            ci = [p for p in pairs if p.status == PairStatus.CONFIRMED_INELIGIBLE]
            ex = [p for p in pairs if p.status == PairStatus.EXPERT_REVIEW]
            un = [p for p in pairs if p.status not in (PairStatus.CONFIRMED_ELIGIBLE, PairStatus.CONFIRMED_INELIGIBLE)]
            wait = [p for p in un if p.pair.key in r.remaining_pairs or p.status == PairStatus.EXPERT_REVIEW]
            m = r.metrics
            needing = [x for x, k in init.items() if k]
            zero = sum(1 for x in needing if r.per_patient[x]["coordinator_minutes"] <= 0)
            row = {"arm": arm, "budget": b, "seed": seed, "result_hash": r.result_hash,
                   "CE": len(ce), "CE_gt_eligible": sum(lab(p) == "eligible" for p in ce),
                   "CE_gt_ineligible(FE)": sum(lab(p) == "ineligible" for p in ce),
                   "CE_gt_other": sum(lab(p) not in ("eligible", "ineligible") for p in ce),
                   "CI": len(ci), "CI_gt_ineligible": sum(lab(p) == "ineligible" for p in ci),
                   "CI_gt_eligible_or_pending(FI)": sum(lab(p) in ("eligible", "eligible_pending_expert") for p in ci),
                   "CI_gt_unlabeled": sum(lab(p) == "unlabeled" for p in ci),
                   "EXPERT_REVIEW": len(ex), "expert_ready_correct": m["correct_expert_ready"],
                   "correct_resolved": m["correct_eligible_resolved"],
                   "coverage": round((len(ce) + len(ci)) / len(pairs), 4),
                   "unresolved": len(un), "waiting": len(wait), "unresolved_no_action": len(un) - len(wait),
                   "status_final": dict(st), "actions": sum(m["actions_executed"].values()),
                   "assumed_cost_minutes": m["active_minutes"]["coordinator"],
                   "patients_needing": len(needing), "zero_allocation": zero, "gini": m["allocation_gini"],
                   "termination": m["termination"], "secs": round(time.time() - t, 1)}
            rows.append(row)
            print(json.dumps(row, ensure_ascii=False), flush=True)
json.dump({"head": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(),
           "ctrec": ctrec.__file__, "gt_kind": gt_kind, "rows": rows}, open(out_path, "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
