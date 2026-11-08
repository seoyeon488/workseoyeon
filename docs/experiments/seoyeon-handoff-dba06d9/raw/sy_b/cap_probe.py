"""Scratch DIAGNOSTIC (not in repo, not an official arm): re-run suite arms with a per-round per-patient execution
capacity in the sim dispatch (EngineLoop.dispatch capacity=K; sim default is unlimited, runner.py:187) and a longer
horizon, so that the plan is re-proposed after outcomes and the DCV filter can act.
Usage: cap_probe.py COHORT(nsclc|gen0) BUDGETS K HORIZON OUT.json [arms comma]"""
import json, subprocess, sys
import ctrec
from ctrec.engine import loop as L
from ctrec.engine.bundles import SourceCatalog
from ctrec.engine.contracts import EffortBudget
from ctrec.sim import runner
from ctrec.sim.suite import ARMS, pair_metrics, initial_open

cohort_name, budgets, K, H, outp = sys.argv[1], [int(x) for x in sys.argv[2].split(",")], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
arms = sys.argv[6].split(",") if len(sys.argv) > 6 else ["dcvc", "dcvc-no_dcv", "dcvc-no_bundles", "dcvc-no_evidence_routing", "random"]
orig = L.EngineLoop.dispatch
L.EngineLoop.dispatch = staticmethod(lambda plan, can_execute=lambda a: True, capacity=None:
                                     orig(plan, can_execute, lambda alias: K))
if cohort_name == "nsclc":
    from ctrec.sim import nsclc_pilot
    sc = nsclc_pilot.suite_cohort()
else:
    from ctrec.sim.suite import load_generator
    sc = load_generator("data/cohort/generator_config.json", "neph-k3-catalog-source", [int(cohort_name[3:])],
                        "data/cohort/source_map.json")[0]
co, cat = sc.cohort, SourceCatalog()
init = initial_open(co)
rows = []
for b in budgets:
    bud = EffortBudget(coordinator_minutes=b, clinician_minutes=60, horizon_steps=H)
    for arm, pid, cfg in ARMS:
        if arm not in arms:
            continue
        spec = runner.build_spec(f"cap{K}-{arm}-{b}-1", pid, co, bud, 1, dict(cfg), cat)
        r = runner.run(spec, co, cat)
        m = pair_metrics(r, sc.labels, init)
        row = {"arm": arm, "budget": b, "K": K, "horizon": H, "CI": m["system_confirmed_ineligible"],
               "CE": m["system_confirmed_eligible"], "VI": m["verified_ineligible"], "FI": m["false_ineligible"],
               "unresolved": m["unresolved"], "noact": m["unresolved_no_action"], "actions": m["actions"],
               "cost": m["assumed_cost_minutes"], "zero": m["fairness"]["zero_allocation"],
               "gini": m["fairness"]["allocation_gini"], "rounds": r.metrics["rounds"],
               "termination": m["termination"], "hash": r.result_hash}
        rows.append(row)
        print(json.dumps(row), flush=True)
json.dump({"head": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(), "ctrec": ctrec.__file__,
           "diagnostic": True, "rows": rows}, open(outp, "w"), indent=1)
