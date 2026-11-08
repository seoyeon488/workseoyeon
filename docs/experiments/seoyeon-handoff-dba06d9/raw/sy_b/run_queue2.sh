until grep -q WP6DONE C:/Users/jsw58/AppData/Local/Temp/claude/4403c133e4f2409f/5863d4ef-72d0-4dc6-87ae-25b90c3071e4/scratchpad/sy_b/wp6_eval.log || grep -q Traceback C:/Users/jsw58/AppData/Local/Temp/claude/4403c133e4f2409f/5863d4ef-72d0-4dc6-87ae-25b90c3071e4/scratchpad/sy_b/wp6_eval.log; do sleep 10; done
cd C:/Users/jsw58/Desktop/workseoyeon-sy-exp
export PYTHONPATH="$(pwd -W)/src"; export PYTHONIOENCODING=utf-8
PY=C:/Users/jsw58/Desktop/workseoyeon/.venv/Scripts/python.exe
echo "HEAD $(git rev-parse HEAD)"; $PY -c "import ctrec;print(ctrec.__file__)"; date
mkdir -p C:/Users/jsw58/AppData/Local/Temp/claude/4403c133e4f2409f/5863d4ef-72d0-4dc6-87ae-25b90c3071e4/scratchpad/sy_b/probe2
for x in "nsclc 90" "nsclc 400" "gen0 800"; do set -- $x; for arm in dcvc no_bundles; do $PY C:/Users/jsw58/AppData/Local/Temp/claude/4403c133e4f2409f/5863d4ef-72d0-4dc6-87ae-25b90c3071e4/scratchpad/sy_b/dcv_probe_b.py $1 $2 1 $arm C:/Users/jsw58/AppData/Local/Temp/claude/4403c133e4f2409f/5863d4ef-72d0-4dc6-87ae-25b90c3071e4/scratchpad/sy_b/probe2/$1-$2-$arm.json | cut -c1-200; done; done
date; echo PROBE2_DONE
$PY C:/Users/jsw58/AppData/Local/Temp/claude/4403c133e4f2409f/5863d4ef-72d0-4dc6-87ae-25b90c3071e4/scratchpad/sy_b/cap_probe.py nsclc 90,400 1 80 C:/Users/jsw58/AppData/Local/Temp/claude/4403c133e4f2409f/5863d4ef-72d0-4dc6-87ae-25b90c3071e4/scratchpad/sy_b/cap_nsclc_k1.json
date; echo CAP_NSCLC_DONE
$PY C:/Users/jsw58/AppData/Local/Temp/claude/4403c133e4f2409f/5863d4ef-72d0-4dc6-87ae-25b90c3071e4/scratchpad/sy_b/cap_probe.py gen0 200,800 2 80 C:/Users/jsw58/AppData/Local/Temp/claude/4403c133e4f2409f/5863d4ef-72d0-4dc6-87ae-25b90c3071e4/scratchpad/sy_b/cap_gen0_k2.json dcvc,dcvc-no_dcv,dcvc-no_bundles
date; echo QUEUE2_DONE
