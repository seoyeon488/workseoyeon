# 03. DCV+C 최신 실험 결과 (dba06d9 = PR #53 head)

- 작성: Agent B, 2026-11-08 18:00–21:30
- 실행 위치: worktree `C:/Users/jsw58/Desktop/workseoyeon-sy-exp` (branch `work/seoyeon-exp`)
- `git rev-parse HEAD` = **dba06d9d26b1ee5ee653e17375ac5d48903ac521** (모든 로그 첫 줄에 기록)
- `ctrec.__file__` = `C:\Users\jsw58\Desktop\workseoyeon-sy-exp\src\ctrec\__init__.py` (PYTHONPATH 지정, 모든 로그에 기록)
- 소스·테스트·데이터·GT는 바꾸지 않았습니다. 추가한 것은 scratchpad의 분석 스크립트뿐입니다.
- 실행은 한 번에 하나씩 순차로 했습니다 (urgent-int3 브라우저 테스트와 CPU를 나눠 쓰지 않도록).
- 결과 폴더(이하 `$S`): `C:/Users/jsw58/AppData/Local/Temp/claude/4403c133e4f2409f/5863d4ef-72d0-4dc6-87ae-25b90c3071e4/scratchpad/sy_b/`

> **해석 주의 (필수)**
> - 환자는 모두 합성입니다. GT는 작성자 라벨(NSCLC 파일럿), 생성기 합성 라벨(neph-k3), 독립 규칙 GT(PR #43 평가셋, 임상 검수 미완료)입니다. **어떤 수치도 임상 정확도가 아닙니다.**
> - **적격 GT 쌍이 어느 코호트에도 없습니다** (NSCLC 파일럿 0, neph-k3 0, PR #43 평가셋 CONFIRMED_ELIGIBLE 0). 그래서 CE·VE·FE·FI가 0인 것은 "생길 수 없는 0"이고 안전성 증거가 아닙니다.
> - 비용(분)은 `engine/bundles.py` DEFAULT_SOURCES의 **가정값**입니다. 실제 병원 업무 시간 절감으로 읽으면 안 됩니다.
> - result_hash는 실험 ID(arm 이름·예산·seed)가 spec에 들어가므로 팔끼리 항상 다릅니다. 팔이 "같은 행동을 했는지"는 해시가 아니라 행·환자별 결과·실행 행동 목록으로 비교했습니다 (아래 각 절).

열 약어: CE = system_confirmed_eligible, VE = verified_eligible(CE∧GT 적격), FE = false_eligible(CE∧GT 부적격), CI = system_confirmed_ineligible, VI = verified_ineligible(CI∧GT 부적격), FI = false_ineligible(CI∧GT 적격), unver = 라벨 없는 쌍의 확정, Cov = coverage, Unres = 미해결, wait = 남은 행동 있음 또는 임상의 검토, noact = 남은 행동 없는 미해결, min = 가정 코디네이터 분, act = 실행 행동 수, zero = 처음에 열린 쌍이 있는데 0분을 받은 환자 수, gini = 환자별 배정 지니. 값은 평균±표준편차(seed·replicate), 표준편차 0이면 평균만.

---

## E1-a. NSCLC 파일럿 suite

| 항목 | 값 |
|---|---|
| 명령 | `$PY -m ctrec.sim.suite --cohort nsclc --budgets 30,90,400 --seeds 1,2,3,4,5 --json $S/e1_nsclc.json --out $S/e1_nsclc_out` |
| 코호트 | `sim-nsclc-pilot-8x6` (실제 NSCLC 프로토콜 6개 × 합성 환자 8명 = 48쌍). GT = `manual_protocol_reading_ineligible_only` (작성자 부적격 라벨 14 + 의심 1, 적격 0) |
| seed / 예산 | 1–5 / 30, 90, 400분 (clinician 60분, horizon 10) |
| 실행 시간 | 14분 45초 (135회) |
| 결과 | `$S/e1_nsclc.json`, 실행별 `$S/e1_nsclc_out/c0-<arm>-b<예산>-s<seed>/result.json`, 표 `$S/e1_nsclc_table.md`·`.tsv`(해시 포함), 로그 `$S/e1_nsclc.log` |

| 예산 | 팔 | n | CE | VE | FE | CI | VI | FI | unver | Cov | Unres | wait | noact | min | act | zero/8 | gini |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 30 | no_action | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 48 | 48 | 0 | 0 | 0 | 8 | 0 |
| 30 | random | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 48 | 48 | 0 | 30 | 10 | 4 | 0.538±0.013 |
| 30 | patient_independent | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 48 | 48 | 0 | 30 | 21 | 7 | 0.875 |
| 30 | cost_first | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 48 | 48 | 0 | 30 | 19.6±0.55 | 2 | 0.625 |
| 30 | **dcvc** | 5 | 0 | 0 | 0 | **6** | 6 | 0 | 0 | 0.125 | 42 | 42 | 0 | 30 | 9 | 7 | 0.875 |
| 30 | dcvc-no_bundles | 5 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 0.042 | 46 | 46 | 0 | 30 | 8 | 1 | 0.525 |
| 30 | dcvc-no_dcv | 5 | 0 | 0 | 0 | 6 | 6 | 0 | 0 | 0.125 | 42 | 42 | 0 | 30 | 9 | 7 | 0.875 |
| 30 | dcvc-no_recovery | 5 | 0 | 0 | 0 | 6 | 6 | 0 | 0 | 0.125 | 42 | 42 | 0 | 30 | 9 | 7 | 0.875 |
| 30 | dcvc-no_evidence_routing | 5 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 0.042 | 46 | 46 | 0 | 30 | 4 | 6 | 0.767 |
| 90 | no_action | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 48 | 48 | 0 | 0 | 0 | 8 | 0 |
| 90 | random | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 48 | 48 | 0 | 90 | 48.4±1.67 | 0 | 0.119±0.018 |
| 90 | patient_independent | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 48 | 48 | 0 | 90 | 81 | 7 | 0.875 |
| 90 | cost_first | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 48 | 48 | 0 | 90 | 80 | 2 | 0.792 |
| 90 | **dcvc** | 5 | 0 | 0 | 0 | **8** | 8 | 0 | 0 | 0.167 | 40 | 40 | 0 | 90 | 48 | 6 | 0.753 |
| 90 | dcvc-no_bundles | 5 | 0 | 0 | 0 | 4 | 4 | 0 | 0 | 0.083 | 44 | 44 | 0 | 90 | 22 | 0 | 0.375 |
| 90 | dcvc-no_dcv | 5 | 0 | 0 | 0 | 8 | 8 | 0 | 0 | 0.167 | 40 | 40 | 0 | 90 | 48 | 6 | 0.753 |
| 90 | dcvc-no_recovery | 5 | 0 | 0 | 0 | 8 | 8 | 0 | 0 | 0.167 | 40 | 39.8±0.45 | 0.2±0.45 | 90 | 48 | 6 | 0.753 |
| 90 | dcvc-no_evidence_routing | 5 | 0 | 0 | 0 | 4 | 4 | 0 | 0 | 0.083 | 44 | 44 | 0 | 90 | 48 | 5 | 0.733 |
| 400 | no_action | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 48 | 48 | 0 | 0 | 0 | 8 | 0 |
| 400 | random | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 48 | 48 | 0 | 400 | 334.4±7.7 | 0 | 0.073±0.024 |
| 400 | patient_independent | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 48 | 48 | 0 | 400 | 343 | 5 | 0.647 |
| 400 | cost_first | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 48 | 48 | 0 | 400 | 377 | 1 | 0.528 |
| 400 | dcvc | 5 | 0 | 0 | 0 | 8 | 8 | 0 | 0 | 0.167 | 40 | 40 | 0 | 400 | 335 | 0 | 0.502 |
| 400 | **dcvc-no_bundles** | 5 | 0 | 0 | 0 | **14** | 14 | 0 | 0 | 0.292 | 34 | 34 | 0 | 400 | 117±0.71 | 0 | 0 |
| 400 | dcvc-no_dcv | 5 | 0 | 0 | 0 | 8 | 8 | 0 | 0 | 0.167 | 40 | 40 | 0 | 400 | 335 | 0 | 0.502 |
| 400 | dcvc-no_recovery | 5 | 0 | 0 | 0 | 8 | 8 | 0 | 0 | 0.167 | 40 | 27.8±4.27 | 12.2±4.27 | 400 | 335 | 0 | 0.502 |
| 400 | dcvc-no_evidence_routing | 5 | 0 | 0 | 0 | 4 | 4 | 0 | 0 | 0.083 | 44 | 44 | 0 | 400 | 338 | 3 | 0.581 |

- 고유 result_hash 수: 각 팔 5/5 (no_action 1/5). 해시 목록은 `$S/e1_nsclc_table.tsv`.
- no_dcv와 dcvc: 15/15 실행에서 행(arm·config·해시 제외)과 환자별 결과가 완전히 같습니다.
- seed 간 표준편차가 거의 0입니다. 이 코호트에서 seed는 응답 모델에만 들어가고 결과를 거의 바꾸지 않습니다. 실질 표본은 "seed 5개"가 아니라 "결정적 실행 1개"에 가깝습니다.
- 모든 CI가 작성자 부적격 라벨과 일치합니다 (VI = CI). 400분 no_bundles의 CI 14는 작성자 부적격 라벨 14쌍 전부입니다.
- 400분에서도 기준선 3종은 CI 0입니다.

**이전 보고 (a634109) 비교 (seed 1–3, `trialog-overnight/work/V6_policy_experiments.md` §3.1)**

| 예산 | 팔 | 이전 보고 (a634109) CI / act / zero | 현재 dba06d9 CI / act / zero |
|---|---|---|---|
| 30 | dcvc | 6 / 9 / 7 | 6 / 9 / 7 |
| 30 | no_bundles | 2 / 8 / 1 | 2 / 8 / 1 |
| 30 | no_evidence_routing | 2 / 4 / 6 | 2 / 4 / 6 |
| 30 | patient_independent | 0 / 17 / 7 | 0 / 21 / 7 |
| 90 | dcvc | 8 / 48 / 6 | 8 / 48 / 6 |
| 90 | no_bundles | 4 / 22 / 0 | 4 / 22 / 0 |
| 90 | patient_independent | 0 / 77 / 7 | 0 / 81 / 7 |
| 400 | 전 팔 | (이전 실행 없음) | 위 표 |

- dcvc 계열은 30·90분에서 이전 보고와 지표가 같습니다. 기준선 patient_independent의 행동 수만 달라졌습니다 (원인 커밋은 찾지 않았습니다).

---

## E1-b. 생성기 neph-k3 suite

| 항목 | 값 |
|---|---|
| 명령 | `$PY -m ctrec.sim.suite --cohort generator --scenario neph-k3-catalog-source --replicate 0,1,2 --budgets 200,800 --seeds 1,2 --json $S/e1_gen.json --out $S/e1_gen_out` |
| 코호트 | `neph-k3-catalog-source` replicate 0,1,2 (각 20명 × 3시험 = 60쌍). GT = 생성기 합성 쌍 라벨. **GT 적격 0**, 라벨 있는 쌍 29 / 29 / 32 (모두 부적격) |
| seed / 예산 | 1,2 × replicate 3 = 6회 / 200, 800분 |
| 실행 시간 | 45분 5초 (108회). 계획(30분)보다 깁니다. 축소 없이 전부 돌렸습니다 |
| 결과 | `$S/e1_gen.json`, `$S/e1_gen_out/c<rep>-<arm>-b<예산>-s<seed>/result.json`, 표 `$S/e1_gen_table.md`·`.tsv`, 로그 `$S/e1_gen.log` |

| 예산 | 팔 | n | CE | FE | CI(=VI) | FI | Cov | Unres | wait | noact | min | act | zero/20 | gini |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 200 | no_action | 6 | 0 | 0 | 0 | 0 | 0 | 60 | 60 | 0 | 0 | 0 | 20 | 0 |
| 200 | random | 6 | 0 | 0 | 0.33±0.82 | 0 | 0.006 | 59.67±0.82 | 59.67 | 0 | 200 | 74.5±7.6 | 0.67±0.82 | 0.210±0.048 |
| 200 | patient_independent | 6 | 0 | 0 | 0.83±0.98 | 0 | 0.014 | 59.17±0.98 | 59.17 | 0 | 200 | 143.7±0.5 | 17 | 0.860 |
| 200 | cost_first | 6 | 0 | 0 | 0 | 0 | 0 | 60 | 60 | 0 | 200 | 169±3.9 | 11.67±1.86 | 0.748±0.037 |
| 200 | **dcvc** | 6 | 0 | 0 | **4±4.34** | 0 | 0.067±0.072 | 56±4.34 | 56 | 0 | 199.7 | 109±35.2 | 12±1.55 | 0.673±0.077 |
| 200 | dcvc-no_bundles | 6 | 0 | 0 | 3.33±3.33 | 0 | 0.056 | 56.67±3.33 | 56.67 | 0 | 200 | 35±6.3 | 5.33±1.86 | 0.473±0.050 |
| 200 | dcvc-no_dcv | 6 | 0 | 0 | 4±4.34 | 0 | 0.067 | 56±4.34 | 56 | 0 | 199.7 | 109±35.2 | 12±1.55 | 0.673±0.077 |
| 200 | dcvc-no_recovery | 6 | 0 | 0 | 4±4.34 | 0 | 0.067 | 56±4.34 | 54.33±5.01 | 1.67±1.03 | 199.7 | 109±35.2 | 12±1.55 | 0.673±0.077 |
| 200 | dcvc-no_evidence_routing | 6 | 0 | 0 | 4±4.34 | 0 | 0.067 | 56±4.34 | 56 | 0 | 199.9 | 85.2±22.8 | 11.67±1.37 | 0.724±0.065 |
| 800 | no_action | 6 | 0 | 0 | 0 | 0 | 0 | 60 | 60 | 0 | 0 | 0 | 20 | 0 |
| 800 | random | 6 | 0 | 0 | 2.83±4.49 | 0 | 0.047 | 57.17±4.49 | 57.17 | 0 | 800 | 532.7±22.1 | 0 | 0.103±0.014 |
| 800 | patient_independent | 6 | 0 | 0 | 1.83±2.48 | 0 | 0.031 | 58.17±2.48 | 58.17 | 0 | 800 | 585.8±35.5 | 8±0.89 | 0.440±0.045 |
| 800 | cost_first | 6 | 0 | 0 | 0 | 0 | 0 | 60 | 60 | 0 | 800 | 700 | 0 | 0.167±0.025 |
| 800 | dcvc | 6 | 0 | 0 | 5±5.87 | 0 | 0.083±0.098 | 55±5.87 | 54.67±6.38 | 0.33±0.52 | 799.8 | 609±38.8 | 0 | 0.192±0.022 |
| 800 | **dcvc-no_bundles** | 6 | 0 | 0 | **8±3.69** | 0 | 0.133±0.061 | 52±3.69 | 52 | 0 | 800 | 480.3±64.2 | 0 | 0.086±0.029 |
| 800 | dcvc-no_dcv | 6 | 0 | 0 | 5±5.87 | 0 | 0.083 | 55±5.87 | 54.67±6.38 | 0.33±0.52 | 799.9 | 609.2±39.0 | 0 | 0.192±0.022 |
| 800 | dcvc-no_recovery | 6 | 0 | 0 | 5±5.87 | 0 | 0.083 | 55±5.87 | 39.33±5.39 | 15.67±1.75 | 798.5±3.0 | 606.7±39.2 | 0 | 0.193±0.024 |
| 800 | dcvc-no_evidence_routing | 6 | 0 | 0 | 4±4.34 | 0 | 0.067 | 56±4.34 | 56 | 0 | 800 | 609±25.2 | 4±0.89 | 0.328±0.015 |

replicate·seed별 CI (replicate, seed: CI):

| 예산 | 팔 | r0s1 | r0s2 | r1s1 | r1s2 | r2s1 | r2s2 |
|---|---|---|---|---|---|---|---|
| 200 | random | 0 | 0 | 0 | 2 | 0 | 0 |
| 200 | dcvc | 2 | 2 | 9 | 10 | 0 | 1 |
| 200 | dcvc-no_bundles | 2 | 2 | 7 | 8 | 0 | 1 |
| 200 | dcvc-no_evidence_routing | 2 | 2 | 9 | 10 | 0 | 1 |
| 800 | random | 0 | 0 | 7 | 10 | 0 | 0 |
| 800 | dcvc | 2 | 2 | 12 | 13 | 0 | 1 |
| 800 | dcvc-no_bundles | 7 | 7 | 12 | 13 | 4 | 5 |
| 800 | dcvc-no_evidence_routing | 2 | 2 | 9 | 10 | 0 | 1 |

- 표준편차가 큰 것은 replicate 1이 다른 두 replicate보다 확정이 많기 때문입니다. seed 차이는 작습니다.
- no_dcv와 dcvc: 12회 중 11회는 행·환자별 결과가 같습니다. 800분 replicate 1 seed 2 한 번만 행동 1개(문서 요청 1, 0.5분)가 다르고 CI는 같습니다 (04 문서 §1).
- FE·FI·VE는 GT 적격이 0이라 모든 팔에서 0이며, 안전성 근거가 아닙니다.

**이전 보고 (a634109) 비교** — 같은 명령이지만 **코호트 자체가 달라졌습니다** (라벨 있는 쌍: 이전 29/39/38 → 현재 29/29/32). 이전 숫자는 현재 결과로 쓰면 안 됩니다.

| 예산 | 팔 | 이전 보고 (a634109) CI | 현재 dba06d9 CI | 이전 act → 현재 act |
|---|---|---|---|---|
| 200 | random | 0.83±0.98 | 0.33±0.82 | 74.5 → 74.5 |
| 200 | dcvc | 7.5±2.0 | 4±4.34 | 108 → 109 |
| 200 | dcvc-no_bundles | 6.83±2.2 | 3.33±3.33 | 27.7 → 35 |
| 200 | dcvc-no_evidence_routing | 6.83±2.2 | 4±4.34 | 54.7 → 85.2 |
| 800 | random | 5.33±1.6 | 2.83±4.49 | 505 → 533 |
| 800 | dcvc | 8.17±1.7 | 5±5.87 | 576 → 609 |
| 800 | dcvc-no_bundles | 11.2±0.41 | 8±3.69 | 433 → 480 |
| 800 | dcvc-no_recovery | 8.17±1.7 (noact 7.83) | 5±5.87 (noact 15.67) | 576 → 607 |

- "800분에서 no_bundles > dcvc"는 현재 코드에서도 재현됩니다 (8 vs 5, 6회 중 4회 우세, 2회 동률, 열세 0).
- 200분에서 dcvc의 기준선 대비 우위(4 vs random 0.33, patient_independent 0.83)는 유지되지만 크기가 줄고 분산이 커졌습니다. replicate 2에서는 dcvc 0–1입니다.
- 코호트 라벨 수 변화의 원인 커밋(생성기·슬롯 사전 쪽으로 추정: d03c39e, 8b6bd00, EXPERT_SLOTS_EXTRA)은 찾지 않았습니다.

---

## E1-c. WP6 runner + PR #43 평가셋 (240쌍)

| 항목 | 값 |
|---|---|
| CLI 지원 여부 | `python -m ctrec.sim --policies`는 정책 ID(no_action, random, patient_order, cheapest_first, legacy_greedy, full_dcvc)만 받습니다. **ablation 설정(policy_config)을 넘길 방법이 CLI에 없습니다** (`sim/__main__.py`는 rephrase만 cfg로 넘김). suite는 이 평가셋을 로드하지 못합니다 (`--cohort`가 demo/generator/nsclc뿐) |
| 우회 | scratch 드라이버 `$S/wp6_eval_arms.py`: `sim/__main__.load_cohorts`·`load_gt`와 같은 로더로 평가셋과 `pair_gt.csv`를 읽고, suite의 ARMS(같은 policy_id·config)를 `runner.build_spec`/`runner.run(labels=, gt_kind=)`으로 돌림. 저장소 코드 변경 없음 |
| 명령 | `$PY $S/wp6_eval_arms.py 400 1 $S/wp6_eval_400.json` 다음 `$PY $S/wp6_eval_arms.py 6000 1 $S/wp6_eval_6000.json` (cwd = worktree) |
| 데이터 | `data/nsclc/eval/` (scenario nsclc-eval-v1, 80명 × 3시험 = 240쌍). GT kind `independent_rule_gt_reduced_scope`: ineligible 130, eligible_pending_expert 23, unlabeled(NOT_EVALUATED) 87, CONFIRMED_ELIGIBLE 0. 임상 검수 미완료 |
| seed / 예산 | **seed 1만** / 400, 6000분 (clinician 60분, horizon 10) |
| 실행 시간 | 400분 4분 23초, 6000분 54분 45초 (9팔) |
| 결과 | `$S/wp6_eval_400.json`, `$S/wp6_eval_6000.json`, 로그 `$S/wp6_eval.log` |

열: CE, FE(CE∧GT 부적격), CI, CI∧GT부적격, FI(CI∧GT 적격 또는 판단 대기 적격), EXP = EXPERT_REVIEW, ready = correct_expert_ready(EXPERT_REVIEW∧pending_expert), correct_resolved(CE∧eligible + ready).

**400분**

| 팔 | CE | FE | CI | CI∧부적격 | FI | EXP | ready | correct_resolved | Cov | Unres | wait | noact | min | act | zero/80 | gini | hash |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_action | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 240 | 240 | 0 | 0 | 0 | 80 | 0 | a5a82411ac9152db |
| random | 0 | 0 | 5 | 5 | 0 | 0 | 0 | 0 | 0.021 | 235 | 235 | 0 | 400 | 88 | 32 | 0.543 | b0d398ccc4d5ba45 |
| patient_independent | 0 | 0 | 8 | 8 | 0 | 0 | 0 | 0 | 0.033 | 232 | 231 | 1 | 400 | 187 | 72 | 0.912 | 8c33142e1ff91790 |
| cost_first | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 240 | 240 | 0 | 400 | 255 | 45 | 0.699 | 2265a418447ed093 |
| dcvc | 0 | 0 | 47 | 47 | 0 | 0 | 0 | 0 | 0.196 | 193 | 193 | 0 | 398.5 | 88 | 44 | 0.689 | e487f6ca93a9a302 |
| dcvc-no_bundles | 0 | 0 | **51** | 51 | 0 | 0 | 0 | 0 | 0.213 | 189 | 189 | 0 | 399.5 | 53 | 41 | 0.642 | 18e531be0b4bcfdb |
| dcvc-no_dcv | 0 | 0 | 47 | 47 | 0 | 0 | 0 | 0 | 0.196 | 193 | 193 | 0 | 398.5 | 88 | 44 | 0.689 | e74d9b539ddfd446 |
| dcvc-no_recovery | 0 | 0 | 47 | 47 | 0 | 0 | 0 | 0 | 0.196 | 193 | 193 | 0 | 398.5 | 88 | 44 | 0.689 | b152ecc74e16bdba |
| dcvc-no_evidence_routing | 0 | 0 | 49 | 49 | 0 | 0 | 0 | 0 | 0.204 | 191 | 191 | 0 | 399.5 | 63 | 42 | 0.658 | b9b113a0ee4fb157 |

**6000분**

| 팔 | CE | FE | CI | CI∧부적격 | FI | EXP | ready | correct_resolved | Cov | Unres | wait | noact | min | act | zero/80 | gini | hash |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_action | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 240 | 240 | 0 | 0 | 0 | 80 | 0 | a5a82411ac9152db |
| random | 0 | 0 | 110 | 110 | 0 | 16 | 16 | 16 | 0.458 | 130 | 127 | 3 | 6000 | 2678 | 0 | 0.100 | ecbbbd3fd2c82763 |
| patient_independent | 0 | 0 | 112 | 112 | 0 | 16 | 16 | 16 | 0.467 | 128 | 120 | 8 | 6000 | 2847 | 0 | 0.149 | 6c52c360fedaf9de |
| cost_first | 0 | 0 | 117 | 117 | 0 | 8 | 8 | 8 | 0.488 | 123 | 120 | 3 | 5999.5 | 2772 | 0 | 0.102 | 085485af88f12c4c |
| **dcvc** | 0 | 0 | **124** | 124 | 0 | 20 | **20** | **20** | 0.517 | 116 | 113 | 3 | 5862.5 | 2440 | 0 | 0.092 | 8e969e203c18f50f |
| dcvc-no_bundles | 0 | 0 | 124 | 124 | 0 | 20 | 20 | 20 | 0.517 | 116 | 113 | 3 | 5862.5 | 2440 | 0 | 0.092 | 4d7c3ab13fbc7f47 |
| dcvc-no_dcv | 0 | 0 | 124 | 124 | 0 | 20 | 20 | 20 | 0.517 | 116 | 114 | 2 | 6000 | 2589 | 0 | 0.083 | 17760c566087be16 |
| dcvc-no_recovery | 0 | 0 | 121 | 121 | 0 | 20 | 20 | 20 | 0.504 | 119 | 116 | 3 | 5192 | 1893 | 0 | 0.062 | e314c7289a5dd3ca |
| dcvc-no_evidence_routing | 0 | 0 | 114 | 114 | 0 | 19 | 19 | 19 | 0.475 | 126 | 125 | 1 | 6000 | 2856 | 0 | 0.121 | f8547ffa8629a8b6 |

- 모든 팔에서 FE 0, FI 0(CI가 모두 GT 부적격), CI∧GT unlabeled 0입니다. 적격 GT(CONFIRMED_ELIGIBLE)가 0이므로 FE 0은 안전성 증거가 아닙니다.
- 6000분 dcvc: correct_expert_ready 20/23, CI 124/130, false-CI 0. 400분 dcvc: CI∧GT 부적격 47/130.
- 6000분에서 dcvc는 기준선 3종보다 expert-ready(20 vs 16/16/8)와 CI(124 vs 110/112/117)가 높습니다. seed 1, 1회입니다.
- 6000분에서 no_dcv는 **행동이 다릅니다** (2589 vs 2440, 6000 vs 5862.5분). 예산이 남아 impact 0 행동을 더 산 것으로 보이며, 지표는 같습니다. 측정한 조건 중 필터가 행동을 크게 바꾼 것은 이 조건뿐이고, 결과는 바뀌지 않았습니다.
- 6000분에서 no_bundles는 dcvc와 지표·행동 수·비용이 모두 같습니다. 400분에서는 no_bundles가 더 높습니다 (51 vs 47).
- dcvc의 6000분 종료 사유는 budget_exhausted인데 쓴 분은 5862.5분입니다. 남은 137.5분으로 살 양수 점수 행동이 없었던 것으로 보입니다 (확인하지 않음).
- no_recovery는 6000분에서 CI 121(−3)이고 5192분만 씁니다. 회복이 없으면 남은 길이 일찍 닫힙니다.

**이전 보고 (4f81460, 70fe9a5 checks) 비교**

| 지표 (full_dcvc) | 이전 보고 (4f81460) | 현재 dba06d9 |
|---|---|---|
| 400분 CI∧GT 부적격 | 48/130 | 47/130 |
| 6000분 expert-ready | 20/23 | 20/23 |
| 6000분 CI | 124/130 | 124/130 |
| 6000분 false-CI | 0 | 0 |

- 400분에서 1쌍 줄었습니다. 원인은 찾지 않았습니다.

**suite 팔을 이 GT로 돌리는 데 필요한 것** (위 scratch 드라이버가 임시로 하는 일, 제안만)
1. suite에 `--cohort nsclc-eval` 로더 (`sim/__main__.load_cohorts`와 같은 방식, `--trials-dir data/nsclc/trials`).
2. `pair_gt.csv`를 suite 라벨로 바꾸는 변환. `eligible_pending_expert`를 ELIGIBLE과 섞지 않는 별도 칸이 필요합니다. 현재 `suite.pair_metrics`는 ELIGIBLE/INELIGIBLE/UNLABELED만 다뤄서, 판단 대기 적격은 UNLABELED로 빠집니다.
3. 주지표 `correct_expert_ready`(EXPERT_REVIEW∧pending_expert)를 suite 행에 추가.
4. 또는 `python -m ctrec.sim`에 `--policy-config arm=json` 같은 인자를 추가해 ablation 설정을 넘기게 함.

---

## 진단 probe (scratch, 공식 팔 아님)

| 항목 | 값 |
|---|---|
| 스크립트 | `$S/dcv_probe_b.py` (FullDCVCPolicy.propose/select/apply_outcome을 그 프로세스 안에서만 감싸 계측. 저장소 코드 변경 없음) |
| 실행 | `$S/run_probes.sh`, 로그 `$S/probes.log`, 결과 `$S/probe/<cohort>-<예산>-<arm>.json` (seed 1) |
| 조건 | NSCLC 90·400분: dcvc, no_dcv, no_bundles, diag_noimpact, diag_noimpact_nobundles. 생성기 replicate 0 800분: dcvc, no_dcv, no_bundles, diag_noimpact. 200분: dcvc, no_bundles |
| 실행 시간 | 약 6분 |
| 검산 | probe의 dcvc·no_dcv·no_bundles CI·비용·지니는 suite 같은 조건(seed 1)과 같습니다 |

diag_noimpact = C 점수의 impact를 "열린 대상이 있으면 1, 없으면 0"으로 바꾼 진단 변형입니다 (점수 = 1/비용). 공식 ablation이 아닙니다.

| 코호트·예산 | 팔 | CI | 실행 행동 | 계획 0에서 고른 행동 / 쓴 분 | 실행 직전 열린 대상 0인 행동 [실행 직후 기준] | (환자,정보원) 고유 / 반복 접촉 | 분>0 환자 | gini |
|---|---|---|---|---|---|---|---|---|
| NSCLC 90 | dcvc | 8 | 48 | 48 / 90 | 24 (50%) [26] | 2 / 46 | 2/8 | 0.753 |
| NSCLC 90 | no_dcv | 8 | 48 | 48 / 90 | (dcvc와 같은 행동 목록) [26] | 2 / 46 | 2/8 | 0.753 |
| NSCLC 90 | no_bundles | 4 | 22 | 22 / 90 | 0 [2] | 14 / 8 | 8/8 | 0.375 |
| NSCLC 90 | diag_noimpact | 0 | 80 | 80 / 90 | - [0] | 2 / 78 | 2/8 | 0.858 |
| NSCLC 400 | dcvc | 8 | 335 | 332 / 400 | 107 (32%) [109] | 12 / 323 | 8/8 | 0.503 |
| NSCLC 400 | no_dcv | 8 | 335 | 332 / 400 | (dcvc와 같음) [109] | 12 / 323 | 8/8 | 0.503 |
| NSCLC 400 | no_bundles | 14 | 118 | 112 / 400 | 27 (23%) [30] | 30 / 88 | 8/8 | 0 |
| NSCLC 400 | diag_noimpact | 0 | 375 | 375 / 400 | - [0] | 5 / 370 | 5/8 | 0.400 |
| NSCLC 400 | diag_noimpact_nobundles | 0 | 370 | 370 / 400 | - [0] | 6 / 364 | 6/8 | 0.359 |
| gen r0 200 | dcvc | 2 | 92 | 92 / 199.5 | - [21] | 8 / 84 | 7/20 | 0.686 |
| gen r0 200 | no_bundles | 2 | 32 | 32 / 200 | - [3] | 19 / 13 | 13/20 | 0.530 |
| gen r0 800 | dcvc | 2 | 585 | 579 / 800 | 42 (7%) [42] | 38 / 547 | 20/20 | 0.217 |
| gen r0 800 | no_dcv | 2 | 585 | 579 / 800 | (dcvc와 같음) [42] | 38 / 547 | 20/20 | 0.217 |
| gen r0 800 | no_bundles | 7 | 444 | 438 / 800 | 52 (12%) [53] | 53 / 391 | 20/20 | 0.103 |
| gen r0 800 | diag_noimpact | 2 | 685 | 682 / 800 | - [19] | 39 / 646 | 20/20 | 0.082 |

- "실행 직전" = 같은 계획에서 앞 행동들의 결과까지 반영한 상태에서 이 행동의 대상 쌍이 모두 닫혀 있던 경우 (재계측 `$S/probe2/`, 20:02–20:06). "[실행 직후]" = 이 행동 자신의 결과까지 반영한 상태 (첫 probe `$S/probe/`). 직후 기준은 자기 결과로 쌍을 닫은 행동도 세므로 과대 계산입니다. "-"는 재계측하지 않음.

해석은 `04_DCV_ABLATION_ANALYSIS.md`에 있습니다.

---

## 돌리지 않은 것

| 항목 | 상태 | 이유 / 필요한 것 |
|---|---|---|
| E1 NSCLC (30,90,400 × seed 1–5) | **완료** | - |
| E1 생성기 (200,800 × seed 1,2 × replicate 0,1,2) | **완료**, 축소 없음 | 45분 걸렸습니다 (계획 30분) |
| WP6 평가셋 9팔 × 400·6000분 | **seed 1만 완료** | 6000분 9팔에 55분이 걸려 seed 반복은 하지 못했습니다. 분산 정보가 없습니다 |
| WP6 평가셋을 공식 CLI로 ablation | **불가** | `python -m ctrec.sim`에 policy_config 인자가 없고, suite는 평가셋 로더가 없습니다. scratch 드라이버로 대신했습니다 (위 E1-c 하단 제안) |
| 데모 코호트 재측정 | 미실행 | 우선순위 밖 (과제 목록에 없음). 이전 데모 수치는 현재 결과로 쓰면 안 됩니다 |
| E2 공식 no_impact·floor>0 팔 | 미실행 (코드 변경 필요) | 진단 변형 diag_noimpact(scratch, seed 1)만 했습니다. floor>0 팔은 진단도 하지 않았습니다 |
| E3 생성기 800분 번들 역전의 인과 추적 | 부분 | 집중 지표만 계측했습니다. 어떤 행동이 확정을 만드는지(행동→쌍 전이) 추적은 하지 않았습니다 |
| E6 비용 민감도(×0.5, ×2) | 미실행 | 카탈로그 값을 바꾸려면 코드 또는 scratch 카탈로그 주입이 필요해 시간 밖으로 미뤘습니다 |
| E5 적격 GT 코호트, E7 recovery_stress | 미실행 | 과제 범위 밖 |
| 라운드 한도 진단의 K·horizon 민감도, seed 반복 | 미실행 | K=1(NSCLC), K=2(생성기 r0), seed 1만 |
| 생성기 라벨 수 변화(29/39/38 → 29/29/32)의 원인 커밋 | 미조사 | - |
| 평가셋 400분 dcvc 48 → 47의 원인 | 미조사 | - |
