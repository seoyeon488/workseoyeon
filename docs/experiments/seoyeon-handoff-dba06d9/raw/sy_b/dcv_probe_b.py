"""Scratch diagnostic probe (not in repo, not an official arm).
For a cohort/budget/seed and an arm config of full_dcvc, records per planning round:
  - candidates proposed with dcv_impact off vs on (=removed by DCV filter), and impact of removed ones
  - kept executable candidates with impact 0
  - after selection: minutes left in round budget, whether any removed candidate would fit (would be picked last since score 0)
and per executed action: (patient, source, action_type, charged minutes)
Optional variant (monkeypatch, DIAGNOSTIC ONLY): impact := 1 if open target else 0  ("no_impact_scoring", score = 1/cost)
Usage: dcv_probe_b.py COHORT(nsclc|gen0|gen1|gen2) BUDGET SEED ARM(dcvc|no_bundles|no_dcv|no_routing|diag_noimpact|diag_noimpact_nobundles) OUT.json
"""
import json, subprocess, sys
from collections import Counter
import ctrec
from ctrec.engine import dcvc as D
from ctrec.engine.bundles import SourceCatalog
from ctrec.engine.contracts import EffortBudget, NON_EXECUTING
from ctrec.sim import runner

cohort_name, budget, seed, arm, outp = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
cfg = {"dcvc": {}, "no_bundles": {"bundles": False}, "no_dcv": {"dcv_impact": False},
       "no_routing": {"evidence_routing": False}, "diag_noimpact": {}, "diag_noimpact_nobundles": {"bundles": False}}[arm]
if cohort_name == "nsclc":
    from ctrec.sim import nsclc_pilot
    co = nsclc_pilot.cohort()
else:
    from ctrec.sim.suite import load_generator
    co = load_generator("data/cohort/generator_config.json", "neph-k3-catalog-source", [int(cohort_name[3:])],
                        "data/cohort/source_map.json")[0].cohort

rounds, executed = [], []
orig_propose, orig_select, orig_apply = D.FullDCVCPolicy.propose, D.FullDCVCPolicy.select, D.FullDCVCPolicy.apply_outcome
orig_impact = D.FullDCVCPolicy.impact
if arm.startswith("diag_noimpact"):
    D.FullDCVCPolicy.impact = lambda self, cohort, a: 1.0 if self.open_targets(cohort, a) else 0.0

state = {}


def propose(self, cohort, pending_reevaluation=None):
    on = orig_propose(self, cohort, pending_reevaluation)
    sw = self.dcv_impact
    self.dcv_impact = False
    off = orig_propose(self, cohort, pending_reevaluation)
    self.dcv_impact = sw
    on_ids = {a.action_id for a in on}
    removed = [a for a in off if a.action_id not in on_ids]
    exe = [a for a in on if a.action_type not in NON_EXECUTING]
    state["last"] = {"proposed_filter_off": len(off), "proposed_filter_on": len(on), "removed": len(removed),
                     "removed_exec": sum(a.action_type not in NON_EXECUTING for a in removed),
                     "removed_impact_max": max((orig_impact(self, cohort, a) for a in removed), default=None),
                     "kept_exec": len(exe),
                     "kept_exec_zero_impact": sum(1 for a in exe if orig_impact(self, cohort, a) == 0),
                     "removed_min_cost": min((a.expected_cost.coordinator_minutes for a in removed
                                              if a.action_type not in NON_EXECUTING), default=None)}
    state["removed"] = removed
    return on


def select(self, cands, budget, ledger=None, cohort=None):
    state["co"] = cohort
    plan = orig_select(self, cands, budget, ledger, cohort)
    r = dict(state.get("last", {}))
    r.update({"selected": len(plan.selected), "skipped_over_budget": sum(s.reason_code == "over_budget" for s in plan.skipped),
              "plan_cost": getattr(plan.total_cost, "coordinator_minutes", None)})
    rounds.append(r)
    return plan


def apply_outcome(self, cohort, action, outcome):
    pre = state.get("co") or cohort
    executed.append({"open_targets_before": len(self.open_targets(pre, action)), "round": len(rounds), "open_targets": len(self.open_targets(cohort, action)), "impact": orig_impact(self, cohort, action), "patient": action.patient_alias, "source": action.source_id, "type": action.action_type,
                     "reason": action.reason_code, "status": outcome.status,
                     "trials": list(action.target_trial_ids)})
    res = orig_apply(self, cohort, action, outcome)
    state["co"] = res[0]
    return res


D.FullDCVCPolicy.propose, D.FullDCVCPolicy.select, D.FullDCVCPolicy.apply_outcome = propose, select, apply_outcome
cat = SourceCatalog()
b = EffortBudget(coordinator_minutes=budget, clinician_minutes=60, horizon_steps=10)
spec = runner.build_spec(f"probe-{arm}-{budget}-{seed}", "full_dcvc", co, b, seed, dict(cfg), cat)
res = runner.run(spec, co, cat)
pp = {a: v["coordinator_minutes"] for a, v in res.per_patient.items()}
ps = Counter((e["patient"], e["source"]) for e in executed)
out = {"head": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(), "ctrec": ctrec.__file__,
       "cohort": cohort_name, "budget": budget, "seed": seed, "arm": arm, "diagnostic": arm.startswith("diag"),
       "result_hash": res.result_hash,
       "CI": res.metrics["system_confirmed_ineligible"], "CE": res.metrics["system_confirmed_eligible"],
       "gini": res.metrics["allocation_gini"], "cost": res.metrics["active_minutes"]["coordinator"],
       "actions_executed": len(executed),
       "rounds": rounds,
       "sum_removed": sum(r.get("removed", 0) for r in rounds),
       "sum_removed_exec": sum(r.get("removed_exec", 0) for r in rounds),
       "sum_kept_zero_impact": sum(r.get("kept_exec_zero_impact", 0) for r in rounds),
       "per_patient_minutes": pp, "patients_with_minutes": sum(v > 0 for v in pp.values()),
       "actions_per_patient": Counter(e["patient"] for e in executed),
       "actions_by_source": Counter(e["source"] for e in executed),
       "actions_by_type": Counter(e["type"] for e in executed),
       "distinct_patient_source": len(ps),
       "repeat_contacts": sum(n - 1 for n in ps.values()),
       "max_actions_one_patient_source": max(ps.values(), default=0),
       "executed_zero_open_targets": sum(e["open_targets"] == 0 for e in executed),
       "executed_zero_open_targets_before": sum(e["open_targets_before"] == 0 for e in executed),
       "executed": executed}
json.dump(out, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("rounds", "per_patient_minutes", "executed")}, ensure_ascii=False))
