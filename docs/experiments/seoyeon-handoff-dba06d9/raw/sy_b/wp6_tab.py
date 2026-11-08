import json,sys
for f in sys.argv[1:]:
  d=json.load(open(f,encoding="utf-8"))
  print(f, d["head"][:8])
  ks=["CE","CE_gt_ineligible(FE)","CI","CI_gt_ineligible","CI_gt_eligible_or_pending(FI)","CI_gt_unlabeled","EXPERT_REVIEW","expert_ready_correct","correct_resolved","coverage","unresolved","waiting","unresolved_no_action","assumed_cost_minutes","actions","zero_allocation","gini","termination","secs"]
  print("| arm | "+" | ".join(ks)+" | hash |")
  for r in d["rows"]: print("| "+r["arm"]+" | "+" | ".join(str(r[k]) for k in ks)+" | "+r["result_hash"]+" |")
