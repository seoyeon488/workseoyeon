cd C:/Users/jsw58/Desktop/workseoyeon-sy-exp
export PYTHONPATH="$(pwd -W)/src"; export PYTHONIOENCODING=utf-8
PY=C:/Users/jsw58/Desktop/workseoyeon/.venv/Scripts/python.exe
mkdir -p C:/Users/jsw58/AppData/Local/Temp/claude/4403c133e4f2409f/5863d4ef-72d0-4dc6-87ae-25b90c3071e4/scratchpad/sy_b/probe
echo "HEAD $(git rev-parse HEAD)"; date
for c in nsclc; do for b in 90 400; do for arm in dcvc no_dcv no_bundles diag_noimpact diag_noimpact_nobundles; do
  s=$(date +%s); $PY C:/Users/jsw58/AppData/Local/Temp/claude/4403c133e4f2409f/5863d4ef-72d0-4dc6-87ae-25b90c3071e4/scratchpad/sy_b/dcv_probe_b.py $c $b 1 $arm C:/Users/jsw58/AppData/Local/Temp/claude/4403c133e4f2409f/5863d4ef-72d0-4dc6-87ae-25b90c3071e4/scratchpad/sy_b/probe/$c-$b-$arm.json; echo "secs $(($(date +%s)-s))"; done; done; done
for arm in dcvc no_dcv no_bundles diag_noimpact; do
  s=$(date +%s); $PY C:/Users/jsw58/AppData/Local/Temp/claude/4403c133e4f2409f/5863d4ef-72d0-4dc6-87ae-25b90c3071e4/scratchpad/sy_b/dcv_probe_b.py gen0 800 1 $arm C:/Users/jsw58/AppData/Local/Temp/claude/4403c133e4f2409f/5863d4ef-72d0-4dc6-87ae-25b90c3071e4/scratchpad/sy_b/probe/gen0-800-$arm.json; echo "secs $(($(date +%s)-s))"; done
for arm in dcvc no_bundles; do $PY C:/Users/jsw58/AppData/Local/Temp/claude/4403c133e4f2409f/5863d4ef-72d0-4dc6-87ae-25b90c3071e4/scratchpad/sy_b/dcv_probe_b.py gen0 200 1 $arm C:/Users/jsw58/AppData/Local/Temp/claude/4403c133e4f2409f/5863d4ef-72d0-4dc6-87ae-25b90c3071e4/scratchpad/sy_b/probe/gen0-200-$arm.json; done
date; echo PROBES_DONE
