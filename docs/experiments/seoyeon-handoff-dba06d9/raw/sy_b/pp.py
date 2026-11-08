import json,sys,glob,os
base=sys.argv[1]
for b in sys.argv[2].split(","):
  for arm in ["dcvc","dcvc-no_bundles","dcvc-no_evidence_routing"]:
    d=json.load(open(f"{base}/c0-{arm}-b{b}-s1/result.json",encoding="utf-8"))
    pp=d["per_patient"]
    print(b,arm,"CI",d["row"]["system_confirmed_ineligible"],"act",d["row"]["actions"],"docs",d["row"]["document_requests"],"q",d["row"]["questions"])
    for a,v in pp.items():
      print("   ",a[:14],"min=%.1f"%v["coordinator_minutes"],"CI",len(v["confirmed_ineligible"]),"wait",list(v["waiting"].values())[:6],"unres",list(v["unresolved"].values()))
