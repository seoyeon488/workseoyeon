p="dcv_probe_b.py"
s=open(p,encoding="utf-8").read()
s=s.replace('''    plan = orig_select(self, cands, budget, ledger, cohort)''','''    state["co"] = cohort
    plan = orig_select(self, cands, budget, ledger, cohort)''')
s=s.replace('''def apply_outcome(self, cohort, action, outcome):
    executed.append({''','''def apply_outcome(self, cohort, action, outcome):
    pre = state.get("co") or cohort
    executed.append({"open_targets_before": len(self.open_targets(pre, action)), ''')
s=s.replace('''    return orig_apply(self, cohort, action, outcome)''','''    res = orig_apply(self, cohort, action, outcome)
    state["co"] = res[0]
    return res''')
s=s.replace('''       "executed_zero_open_targets": sum(e["open_targets"] == 0 for e in executed),''','''       "executed_zero_open_targets": sum(e["open_targets"] == 0 for e in executed),
       "executed_zero_open_targets_before": sum(e["open_targets_before"] == 0 for e in executed),''')
open(p,"w",encoding="utf-8").write(s)
