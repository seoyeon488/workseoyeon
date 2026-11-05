# WP6 실험 재현성·평가 파이프라인 감사

> 2026-11-05 · 감사 기준: `integration/dcvc` `0b402c6` · 브랜치 `audit/wp6-experiment-readiness`
> 범위: 분석·문서 작성만. 소스·테스트·데이터 변경 0, 외부 LLM·유료 API 호출 0, 실제 환자 데이터 사용 0.
> 이 문서의 수치는 모두 오프라인 대역 실행이거나 저장소 문서에서 옮긴 값이며, 임상 성능이 아닙니다.

## 결론

**WP6 정책 비교 실험은 현재 실행할 수 없습니다.** 실험 설계(`docs/dev/wp6_experiment_design.md`)의 실행 계층이 코드에 없습니다.

- 없는 것: `src/ctrec/sim/`, `CohortEnvironment`, `ResponseModel`, `OfflineEvaluator`, Runner, 기준선 3종, `full_dcvc`, manifest, `result_hash`.
- 코호트 생성기, 역전 지표, 항목 단위 `no_answer`는 미병합 브랜치에 있습니다. 세 브랜치 모두 자기 테스트는 통과합니다.
- NSCLC 쪽은 시험 8개 선정, 파싱 6개까지입니다. **환자 코호트와 정답 라벨은 0건**이고, 슬롯 196행은 모두 `검수 필요` 상태입니다.
- 지금 실행되는 평가는 기존 다질환 합성셋의 질문 겨냥 구조 평가와 WP7 감사 기록뿐입니다. Matcher 대역이 LLM 기준을 모두 판정 불가로 두므로 Confirmed Eligible이 0건입니다. 따라서 **accuracy와 False Eligible은 산출할 수 없고, 이 문서도 산출하지 않았습니다.**

발표에는 실험 인프라 검증 결과(§4)만 쓸 수 있습니다. 정책 우열이나 임상 정확성은 주장할 수 없습니다.

최소 실행 계획은 §9, 의료 전문가 검증과 엔지니어링 작업의 구분은 §10, 수치별 근거는 §11에 있습니다.

---

## 0. 수치를 읽는 기준

### 0.1 구조 지표와 임상 매칭 정확도는 다릅니다

| 구분 | 무엇을 재는가 | 현재 해당 지표 | 임상 매칭 정확도로 쓸 수 있나 |
|---|---|---|---|
| 인프라 지표 | 실행·기록이 깨지지 않는가 | 테스트 수, 기록 완료 수, 누출 0, 재현 일치 | 아니오 |
| 구조 지표 | 대역 환경에서 질문이 숨긴 기준을 겨냥했는가 | `coverage_exact`, `questions_total`, `unanswered_rate` | 아니오 |
| 합성 벤치마크 일치율 | LLM 생성 라벨과 얼마나 같은가 | `accuracy`, `premature_match` (`eval/evaluate.py`) | 아니오. 현재 입력이 없어 산출도 불가 |
| 임상 매칭 정확도 | 독립 임상 정답과 얼마나 같은가 | **없음** | 독립 GT가 있어야 정의 가능 |

`coverage_exact`의 0.81이나 0.41은 "매칭이 81% 맞다"는 뜻이 아닙니다. 숨긴 기준을 겨냥한 질문이 있었던 사례의 비율입니다.

### 0.2 Eligible의 세 단계

| 단계 | 정의 | 코드 위치 | 현재 값 |
|---|---|---|---|
| ① ELIGIBLE 예측 | 판정 값이 ELIGIBLE. 증거 수준을 보지 않음 | `TrialMatch.eligibility` | 오프라인 0건 |
| ② Confirmed Eligible | ①이면서 필수 기준의 gap이 없음. **시스템이 정한 증거 규칙을 통과했다는 뜻** | `PairStatus.CONFIRMED_ELIGIBLE` | 오프라인 0건 |
| ③ 증거로 확인된 Eligible | ②의 근거가 문서로 검증되고, 독립 GT로도 적격 | **없음** | 측정 불가 |

혼동하기 쉬운 점:

- `confirmed_correct_pairs`라는 이름과 달리, `evaluate.py` 경로의 값은 ①의 개수입니다. ②도 ③도 아닙니다.
- ②와 ③도 다릅니다. `self_report_ok` 기준은 자기 보고로 ②가 됩니다. `clinical_record` 기준도 입력이 그렇게 **선언**되면 `document_verified` 없이 판정이 유지됩니다(§2.2 D).
- 따라서 ②의 개수는 "증거로 확인된 적격 수"로 표기하지 않습니다. 표기는 "시스템 확정 적격"으로 씁니다.

### 0.3 독립 GT가 없으면 accuracy와 False Eligible은 산출할 수 없습니다

- **독립 GT의 조건**: 평가 대상 시스템, 그 시스템의 규칙 엔진, 라벨 생성 LLM과 분리된 판단이어야 합니다. 현재 저장소에는 없습니다.
- 기존 라벨은 LLM이 만들었고 임상의 검토가 없습니다. NSCLC 라벨은 0건입니다.
- 코드가 숫자를 낼 수 있어도(`accuracy`, `premature_match`) 이를 accuracy나 False Eligible로 보고하지 않습니다. 기존 라벨로 낸 값은 "합성 벤치마크 일치율"입니다.
- 생성기 oracle은 평가기와 같은 규칙 엔진을 씁니다(`cohort/truth.py`). 이 비교는 **구현 일관성 검사**이며, 일치해도 임상적으로 맞다는 근거가 아닙니다. 불일치 건수는 False Eligible이 아니라 "규칙 GT 불일치"로 표기합니다.
- 이 문서는 어떤 세트에서도 accuracy와 False Eligible을 산출하지 않았습니다.

### 0.4 현재 integration 결과와 미병합 기능

§2~§5의 실행 결과는 표에 따로 적은 브랜치 사본 실행을 빼면 모두 `0b402c6` 기준입니다.

| 위치 | 기능 | 이 문서의 취급 |
|---|---|---|
| **integration `0b402c6`** | `LegacyAdapterPolicy`, `EffortLedger`, `ExperimentSpec`, DecisionRecord v2, `metrics`, `eval_hygiene`, 질문 평가, NSCLC 시험·슬롯 후보 | 실행 수치의 기준 |
| 미병합 `research/cohort-generator` `dfd3790` | 코호트 생성기 (신증후군 예시) | 브랜치 사본에서 테스트 35개, 재현 확인만. 현재 기능으로 세지 않음 |
| 미병합 PR #3 `feat/wp7-reversal-metrics` `af413eb` | 역전 지표 | 브랜치 사본 테스트 80 통과, 1 건너뜀만. 지표 값 없음 |
| 미병합 PR #10 `feat/wp5-item-level-failure` `617156b` | 항목 단위 `no_answer` | 브랜치 사본 테스트 54개만. **H의 수치는 PR #10 이전 동작** |
| 미병합 `feat/wp7-inspector-diagnostics` `abdaec8` | Inspector 진단 | 이번 감사에서 실행하지 않음 |
| 어디에도 없음 | `sim/`, 기준선 3종, `full_dcvc`, manifest, DCV·회복 루프 제거 | 설계만 존재 또는 미구현 |

브랜치 SHA는 2026-11-05 fetch 기준입니다. 병행 작업으로 바뀔 수 있습니다.

---

## 1. 실험 설계 대비 구현 현황

구분 기준:

| 구분 | 뜻 |
|---|---|
| 구현 및 테스트 확인 | 기준 커밋에 코드와 테스트가 있고 이번에 통과 확인 |
| 구현만 확인 | 코드는 있으나 해당 동작의 테스트나 실험 연결이 없음 |
| 설계만 존재 | WP6 설계에 명세가 있고 기준 커밋에 코드가 없음 |
| 미구현 | 요구는 있으나 설계 명세도 코드도 없음 |
| 검증 불가 | 선행 조건이 없어 참·거짓을 확인할 수 없음 |

미병합 브랜치의 코드는 기준 커밋에 없으므로 `설계만 존재`로 두고 비고에 브랜치를 적었습니다.

### 1.1 실행 계층

| 설계 항목 (§) | 상태 | 근거 |
|---|---|---|
| `ExperimentSpec`, `spec_hash` (§2) | 구현 및 테스트 확인 | `engine/contracts.py:579`, `tests/test_engine_contract_v02.py`. 실행기가 없어 호출처는 테스트뿐 |
| `require_catalog_hash`, `catalog_claims` (§2, §6) | 구현 및 테스트 확인 | `engine/experiment.py`. `src`·`scripts`의 호출처 0 |
| `CohortEnvironment` (§1) | 설계만 존재 | `src/ctrec/sim/` 없음 |
| `ResponseModel`, `derive_seed` (§3.2) | 설계만 존재 | 실패·지연·부분 응답 모델 없음. 현재 답변기는 결정적 |
| `OfflineEvaluator`의 `fact_llm` 결정적 판정 (§3.3) | 설계만 존재 | 현재 대역은 LLM 기준을 모두 UNKNOWN으로 둠 |
| Runner, `scripts/run_cohort_experiment.py` (§1) | 설계만 존재 | 파일 없음 |
| manifest, `result_hash` (§6) | 설계만 존재 | 생성 코드 없음 |
| `spec.seed` 사용 | 미구현 | `src`·`scripts`에서 읽는 곳 없음 |
| `spec.ablations`, `policy_config` 해석 | 미구현 | 계약 필드와 해시만 있고 읽는 코드 없음 |
| `horizon_steps` (§3.1) | 미구현 | 필드만 있음. `LegacyAdapterPolicy`는 1단계 계획만 만듦 |
| 다환자 코호트 실행 | 구현만 확인 | `plan_cohort`는 테스트에서만 호출. `offline_records`는 환자 1명 `CohortState`만 만듦 |

### 1.2 정책·기준선·ablation

| 항목 | 상태 | 근거 |
|---|---|---|
| `legacy_greedy` | 구현 및 테스트 확인 | `LegacyAdapterPolicy`, `tests/test_engine_policy.py` (36개) |
| `random` | 설계만 존재 | `R_random_*`는 질문 동점만 섞는 평가 전용 도구로, 행동 선택 정책이 아님 |
| `patient_order` | 설계만 존재 | 코드 없음 |
| `cheapest_first` | 설계만 존재 | 코드 없음 |
| `oracle_upper` | 설계만 존재 | 코드 없음 |
| `full_dcvc` | 설계만 존재 | 코드 없음. "DCV"가 무엇을 계산하는지 코드에 없음 (`contracts`의 버전 문자열뿐) |
| `-bundles` | 설계만 존재 | `bundle()`은 테스트에서만 호출. 묶음 청구는 `EffortLedger`에 고정되어 끌 설정 없음 |
| `-partial_reeval` | 설계만 존재 | WP4 미착수 |
| `-evidence_level` | 설계만 존재 | 평가기 설정 없음 |
| `-fairness_floor` | 구현만 확인 | `EffortBudget.per_patient_floor_minutes=0`으로 표현 가능. 실험 경로 없음 |
| DCV 제거 ablation | 미구현 | **설계 §5에 없음** |
| 회복 루프 제거 ablation | 미구현 | **설계 §5에 없음** |
| `--ablation` (`eval_question_plans`) | 구현 및 테스트 확인 | 이름은 같지만 동점 처리만 바꾸며, 위 ablation과 무관 |
| 소규모 완전탐색 (§5) | 설계만 존재 | 코드 없음 |

### 1.3 지표

| 축 (§4) | 상태 | 근거 |
|---|---|---|
| 쌍 단위 혼동표, 누락 포함 정확도 | 구현 및 테스트 확인 | `metrics.cohort_eligibility_metrics`. 입력은 LLM 실행 결과(`result.json`)이며 오프라인 입력 경로 없음 |
| 안전: 확정 적격 ∧ 정답 부적격 | 구현만 확인 | `confirmed` 인자는 있으나 `eval/evaluate.py`가 넘기지 않음 (§2.2 D) |
| 진척: 단계·예산별 확정 쌍 비율 | 설계만 존재 | 집계 코드 없음 |
| 비용 5축, 달력 경과 시간 | 설계만 존재 | 원장은 있으나 실험 집계 없음 |
| 역전 지표 | 설계만 존재 | `origin/feat/wp7-reversal-metrics` (PR #3, 미병합. 브랜치 테스트 80 통과, 1 건너뜀) |
| 공정성 `allocation_report` | 구현 및 테스트 확인 | `engine/fairness.py`. 실험 연결 없음 |
| 환자 부담 (질문 수, 모름 수) | 구현만 확인 | `questions_total`, `unanswered_rate`가 있으나 설계의 Runner 지표는 없음 |
| 신뢰구간 (환자 단위 부트스트랩) | 설계만 존재 | 코드 없음 |
| dev/test 분리 | 설계만 존재 | 생성기 브랜치의 `split` 필드. 기준 커밋에 없음 |

### 1.4 데이터·선행 작업

| 항목 | 상태 | 근거 |
|---|---|---|
| NSCLC 시험 선정 | 구현만 확인 | `data/nsclc/trials/` 8개. 선정표 전체가 `검수 필요` |
| NSCLC 파싱 | 구현만 확인 | 8개 중 6개. `NCT05255302`, `NCT04892953`은 `TruncatedError`로 실패 (`docs/dev/wp2a_parse_pilot_NCT06928389.md:262-263`) |
| NSCLC FROZEN 저장소, `frozen_store_hash` | 미구현 | `data/nsclc`에 FROZEN 파일 없음 |
| NSCLC 슬롯 사전, 생성 설정, `source_map.json` | 설계만 존재 | `slot_candidates.csv` 196행은 후보일 뿐이며 사전·설정 파일 없음 |
| NSCLC 환자 코호트 | 미구현 | `data/patients`·`data/labels`에 NSCLC 시험 ID 참조 0건 |
| 코호트 생성기 | 설계만 존재 | `origin/research/cohort-generator`. 텍스트 충돌은 없음. 예시는 신증후군 소아 |
| 항목 단위 `no_answer`, `failure_scope` | 설계만 존재 | `origin/feat/wp5-item-level-failure` (PR #10, 미병합) |
| 웹·시뮬레이터 동일 정책 (M14) | 검증 불가 | `web/engine_runner.py`, `sim/` 모두 없음 |
| oracle 접근 금지 테스트 (§9) | 설계만 존재 | 다만 별칭·프롬프트 누출 차단은 구현 및 테스트 확인 (`eval_hygiene`) |
| 임상 검수 | 검증 불가 | `docs/dev/wp2b_clinical_review_questions.md`는 질문지이며 답변 기록 없음 |

---

## 2. 핵심 검증과 실제 실행 결과

### 2.1 실행 결과

환경: Windows 11, Python 3.10.11, 임시 가상환경, `anthropic 1.17.0`, `pydantic 2.14.3`, `pytest 9.2.0`. `ANTHROPIC_API_KEY`는 빈 값이고, 외부 연결이 실패하도록 프록시를 막은 상태입니다.

| 명령 | 결과 | 소요 |
|---|---|---|
| `pytest -q` (전체) | **2082 통과, 7 건너뜀, 실패 0** | 232초 |
| 관련 테스트 10개 파일 (엔진·감사·평가) | 222 통과, 1 건너뜀 | 27초 |
| `run_offline_records --set masked --repeat` | 성공. 101/101 완료, 단계 109 | 42초 |
| `run_offline_records --set validation --repeat` | 성공. 100/100 완료, 단계 109 | 10초 |
| `eval_question_plans` 2회 | 성공. 사례 101, 실패 0 | 회당 약 40초 |
| `eval_question_priority` | 성공. 개발 101 + 검증 100 | 139초 |
| `eval_question_fidelity` | 성공. 정책 A와 실제 루프 일치 228/228 (101 + 100 + 27). `R_random_1..3` 포함 | 6분 26초 |
| `decision_scenarios --json` | 성공 | 수 초 |
| `eval/evaluate.py` | **실행 불가**. `outputs`가 없어 "정답과 겹치는 예측이 없습니다"로 중단 | - |
| `budget_sweep`, `question_policy_sweep` | **실행하지 않음**. 내부에서 `ctrec batch`로 실제 LLM을 부름 | - |
| 생성기 브랜치 테스트 (브랜치 사본) | 35 통과 | 4초 |
| PR #3 브랜치 테스트 (브랜치 사본) | 80 통과, 1 건너뜀 | 4초 |
| PR #10 브랜치 테스트 (정책·기록 파일) | 54 통과 | 6초 |

병합 시도(`git merge-tree`)는 세 브랜치 모두 기준 커밋과 텍스트 충돌이 없었습니다. 병합 후 동작 검증은 아니며, 통합 검증은 C 작업 범위입니다.

**출력 구조**

```text
<out>/summary.json                                  # run_offline_records: total, issue_codes, truth_leaks, repeat_*, runs[]
<out>/run/<순번>/decision_records.jsonl             # DecisionRecord v2
<out>/run/<순번>/decision_record_issues.jsonl       # 진단 (있을 때만)
<out>/repeat/<순번>/...                             # --repeat
<out>/summary.json, <out>/cases.csv                 # eval_question_plans
<out>/priority_comparison.json                      # eval_question_priority
```

실험 단위 manifest, 결과 해시, 정책 비교표는 어느 스크립트도 만들지 않습니다.

**현재 지표의 실제 정의**

| 지표 | 실제 정의 | 주의 |
|---|---|---|
| `accuracy` | 예측 = 정답 / 예측이 있는 쌍. UNCERTAIN·NOT_EVALUATED는 오답 | 코호트 판은 누락도 분모에 넣음 |
| `coverage` (`metrics`) | ELIGIBLE/INELIGIBLE로 판정한 비율 | 확정 상태(PairStatus) 기반이 아님. 미검증 INELIGIBLE도 포함 |
| `coverage_exact` (`question_eval`) | 숨긴 기준의 EXACT 규칙을 겨냥한 질문이 있는 사례 비율 | **이름은 같지만 판정 coverage가 아닌 질문 겨냥 지표** |
| `premature_match` | 정답 비적격 쌍 중 ELIGIBLE 예측 비율 | False Eligible에 가장 가깝지만 정답이 독립적이지 않음 |
| `confirmed_correct_pairs` | 정답 ELIGIBLE ∧ 예측 ELIGIBLE. `confirmed`를 줄 때만 그 쌍으로 제한 | 현재 호출에서는 확정 여부를 보지 않음 |
| `final_label_agreement` | 마지막 판정 = 라벨인 쌍 / 라벨 쌍 | 대역에서는 판정 개선을 측정할 수 없음 |
| `unanswered_rate` | 답이 '모름'인 질문 비율 | 답변 시뮬레이터가 EXACT만 공개한 결과 |

### 2.2 핵심 질문 A~K

| | 질문 | 판정 | 근거 |
|---|---|---|---|
| A | 동일 코호트·예산·안전 제약에서 정책 비교 | **불가** | 코호트 정책은 1개, 실행은 환자 1명 단위, 공통 Runner 없음. WP7 예산은 `100000`분으로 제약이 아님. 가능한 비교는 같은 사례·같은 질문 수의 **질문 순서** 비교뿐 |
| B | 기준선 3종 존재 | **없음** | `random`은 동점 섞기만, cost-first는 `cheapest_first` 설계만. **"patient-independent"는 설계에 없는 이름이며** 설계의 `patient_order`(환자 순서대로)와 뜻이 다를 수 있음 |
| C | ablation 실행 | **불가** | 번들링 제거는 설계만, DCV 제거·회복 루프 제거는 설계에도 없음. `spec.ablations`를 읽는 코드 없음 |
| D | Confirmed Eligible을 필수 증거 충족 시에만 집계 | **상태는 예, 지표는 아니오** | 아래 설명 |
| E | False Eligible을 독립 GT와 비교 | **아니오** | 이름의 지표 없음. `premature_match`, `confirmed_wrong_pairs`가 있으나 정답이 LLM 생성 라벨이고 임상 검토 없음. NSCLC 라벨 0건 |
| F | 지표별 계산 | **일부** | 아래 표 |
| G | 임상판단 기준을 규칙 GT 분모에서 제외 | **아니오** | 규칙 단위 GT 정확도 지표가 없음. 쌍 지표는 제외 없이 전부 분모 |
| H | no_answer·무응답·소진 반영 | **일부** | `no_answer` 기록과 소진 전이는 작동. 항목 단위 처리 미병합, 확률적 무응답 없음 |
| I | 동일 seed 재현 | **현재 실행은 예, 실험은 검증 불가** | §3 |
| J | 비용·시간 구분 | **계약은 구분, 산출은 미완** | 아래 설명 |
| K | 합성 코호트 근거·검토 문서화 | **기존 셋은 문서화, NSCLC는 코호트 없음** | 아래 설명 |

**D. Confirmed Eligible**

- 상태 계층은 맞습니다. `derive_pair_status`는 ELIGIBLE이어도 필수 기준 gap이 있으면 확정하지 않습니다. 이번 확인 결과 `unverified` → VERIFICATION_PENDING, `physician_review` → EXPERT_REVIEW, gap 없음 → CONFIRMED_ELIGIBLE입니다.
- 미검증 INELIGIBLE도 CONFIRMED_INELIGIBLE이 되지 않습니다.
- 지표 계층은 연결되지 않았습니다. `eval/evaluate.py:37`이 `confirmed`를 넘기지 않아, 예시 2쌍에서 `confirmed_correct_pairs=1, confirmed_wrong_pairs=1`로 나옵니다. `confirmed=set()`을 넘기면 둘 다 0입니다.
- `load_predictions`는 `eligibility`만 읽고 PairStatus를 읽지 않습니다.
- 따라서 `evaluate.py`의 "confirmed" 값은 **ELIGIBLE 예측 수이며 확정 수가 아닙니다.**

상태 계층의 제한도 있습니다. 판정은 "상태는 예"로 유지하되, 뜻은 "시스템 증거 규칙을 통과함"으로 한정합니다.

| 근거 (`clinical_record` 필요 기준) | 결과 | 비고 |
|---|---|---|
| 자기 보고, 출처 미상 | 판정 보류 (`unverified`) | `matcher._apply_evidence_policy`. 부당 승격 차단 |
| 입력이 `clinical_record`로 **선언**됨 | `passes=True` 유지, `needs_verification=False` | `document_verified` 확인 없음 (§11 E7 실행 확인) |

- Confirmed Ineligible은 `document_verified`를 요구하는데(`decision_state` mismatch), Confirmed Eligible 경로는 출처 선언만 봅니다. 두 방향의 증거 기준이 다릅니다.
- `self_report_ok` 기준은 설계상 자기 보고로 확정됩니다.
- 현재 저장소 데이터는 출처를 선언하지 않아(README) 이 경로가 오프라인에서 발생하지 않습니다. 시뮬레이터가 `clinical_record` 사실을 만들면 발생할 수 있으므로 §9 작업 4에서 처리합니다.

오프라인 최종 쌍 상태 (진단용, 정답 대조 안 함):

| 세트 | 쌍 | BLOCKED_FAILURE | INFO_MISSING | VERIFICATION_PENDING | 확정 |
|---|---|---|---|---|---|
| masked | 140 | 104 | 30 | 6 | **0** |
| validation | 119 | 104 | 0 | 15 | **0** |

**F. 지표별 현황**

| 지표 | 현황 |
|---|---|
| Ineligible | 혼동표에 포함. Confirmed Ineligible 단독 집계 없음 |
| Coverage | 있음. 단 판정 기준이며 확정 기준이 아님 |
| Unresolved | 없음. `acquisition`의 항목 상태와 BLOCKED·EXPERT 쌍을 합치는 정의 필요 |
| 행동 수 | 질문 수와 WP7 단계 수만. 질문 외 행동(문서 요청, 임상의 검토)은 오프라인에서 실행되지 않음 (masked 109건 전부 `ASK_PATIENT`) |
| 비용 | 기록 안에는 있음. 실험 집계와 비교표 없음 |

**G. 임상판단 기준**

- 기준 데이터 471개 규칙 중 39개가 `underspecified`이고, 26개 시험 중 17개에 있습니다.
- 라벨 쌍 중 해당 시험에 속한 쌍은 masked 93/140, synthetic 51/77입니다. 이 쌍들이 전부 분모에 들어갑니다.
- 이 값은 시험 단위 상한입니다. 해당 기준이 실제로 판정을 가르는지는 확인하지 않았습니다.
- README §5.1은 `NCT07616128`의 약물 기준을 라벨 판정에 쓰지 않았다고 적고 있어, 실제로 임상판단 기준을 건너뛴 라벨이 존재합니다.
- 설계는 expert·UNRESOLVED를 "판정 불가"로 빼도록 정했지만(§3.4) 코드는 없고, 라벨도 ELIGIBLE/INELIGIBLE 두 값뿐입니다.
- 생성기는 검수 전 기준을 `assume_pass`로 충족 처리합니다. 신증후군 예시에서 연결 기준 25개, 미연결 42개입니다. 끄는 옵션 여부는 설계 Q-G3에 미해결로 남아 있습니다.

**H. 무응답·소진**

- 기록은 동작합니다. masked 결과는 `no_response`/`no_answer` 101건, `succeeded` 8건입니다.
- 소진 전이는 `INFO_MISSING→BLOCKED_FAILURE` 103건, `VERIFICATION_PENDING→BLOCKED_FAILURE` 1건입니다.
- 그러나 **"모름" 한 번이 그 환자의 `patient_interview` 전체를 실패시킵니다.** 사례 93건이 1단계에서 끝납니다. PR #10이 이 동작을 바꾸므로 현재 수치는 잠정값입니다.
- `failed`, `partial`, 지연, 연락 불가는 오프라인에서 발생하지 않습니다.
- `patient_interview`는 대체 정보원이 없어 대체 경로 시험이 실행되지 않습니다.

**J. 비용·시간**

| 구분 | 현재 위치 | 상태 |
|---|---|---|
| 실제 API 비용 | `data/nsclc/parse_runs/usage_calls_*.jsonl`, LLM 파일럿 보고서 | 오프라인 실행은 `llm_cost_usd=0`. 잘 분리됨 |
| 가정 행동 비용 | `bundles.DEFAULT_SOURCES` | 분 단위 비용이 있는 7개 정보원 전부 `assumed`. `catalog_claims`가 `relative_policy_comparison_only`를 내지만 **어떤 산출물에도 기록되지 않음** |
| 실측 시간 | `summary.json`의 `seconds` | 평가기 벽시계 시간. 업무시간과 무관 |
| 시뮬레이션 시간 | 없음 | `ActionOutcome.latency_minutes`가 기본값 `0.0`이라 **"측정 안 함"과 "지연 0분"이 구분되지 않음** |

`patient_wait_minutes`는 `EffortCost.__add__`에서 최댓값으로 합쳐지고 달력 시간이 아닙니다. 합산하면 의미 없는 값이 됩니다(masked 합계 145,440분).

**K. 합성 코호트**

- 기존 셋: README §5.1에 구성과 "임상의 검토 없음"이 있고, 평가 출력에 "합성 벤치마크 성능" 표기가 붙습니다. `supplement_report.json`은 `unverified_synthetic`을 명시합니다.
- 검증셋: 시험 23개가 개발셋과 겹치고, 숨김 대상은 임상 판단이 아니라 층화 무작위입니다 (`build_report.json`).
- 생성기: 설계 문서와 검수 시트가 있으나 검수자의 임상 자격은 기록되어 있지 않습니다.
- NSCLC: 임상 검수 전이라고 명시되어 있고, 규칙상 검수 전에는 정답을 만들지 않습니다. 코호트 없음.

---

## 3. 재현 가능 여부

| 대상 | 판정 | 근거 |
|---|---|---|
| `eval_question_plans` | **재현됨** | 해시 시드 0·12345로 2회 실행. `cases.csv` 바이트 동일, `summary.json` 차이는 벽시계 `seconds`뿐 |
| WP7 기록 (정규화 후) | **재현됨** | 프로세스 간 101/101 동일, `--repeat` 불일치 0 (masked·validation) |
| WP7 기록 (원본 바이트) | **재현 안 됨** | 파일 해시가 실행마다 다름. 사실 ID가 uuid 기반 (`F-…`) |
| WP7 집계 | **재현됨** | salt `wp7-offline`·`other-salt`의 `total`, `issue_codes` 동일 |
| 생성기 (브랜치 사본) | **재현됨** | 2회 실행 21개 파일 해시 동일. 신증후군 예시 기준 |
| WP6 `result_hash` | **검증 불가** | 구현 없음 |
| 응답 seed 재현 | **검증 불가** | `ResponseModel` 없음 |
| 실제 LLM 경로 | **비결정적** | 감사 문서 M10 갭 (temperature 제어 없음). 이번에 호출하지 않음 |

WP6 구현 전에 막아야 할 재현성 위험이 두 가지 있습니다.

1. **`result_hash`가 그대로는 깨집니다.** 설계 §6은 `DecisionRecord` 직렬화를 해시하는데, 기록에 uuid 기반 사실 ID가 들어 있습니다. `normalized_files`처럼 정규화해서 해시해야 합니다.
2. **별칭 salt가 결과를 바꿀 수 있습니다.** `select`의 동점은 `patient_alias` 순서로 풀리고, `AliasMap`의 기본 salt는 실행마다 무작위입니다. 동점 2행동에 예산 1건분인 시연에서 salt 5개 중 4개는 P2, 1개는 P1이 선택되었습니다. 지금은 환자 1명 실행이라 드러나지 않습니다. `ExperimentSpec`에 salt 필드가 없으므로 seed에서 유도하거나 필드를 추가해야 합니다.

그 밖의 재현 조건:

- `requirements.txt`는 범위 지정이고 잠금 파일이 없습니다. README가 권장하는 `requirements.lock.txt`도 저장소에 없습니다.
- 한국어 Windows의 Python 3.10에서 `pip install -r requirements.txt`가 cp949 `UnicodeDecodeError`로 실패합니다. `PYTHONUTF8=1`이 필요합니다.
- `docs/dev/wp7_offline_records.md` §5는 현행과 다릅니다. 문서는 진단 109건(`decline_marker_fact` 101)이고, 현재는 8건(`unattributed_fact`)입니다. PR #7의 "모름" 사실 보류 뒤 갱신되지 않은 것으로 보입니다.

---

## 4. 발표에 사용할 수 있는 검증된 수치

모두 **인프라 검증**이며 성능 주장이 아닙니다. 표기 조건을 함께 씁니다.

| 수치 | 표기 조건 |
|---|---|
| 전체 테스트 2082 통과, 7 건너뜀, 실패 0 | 커밋 `0b402c6`, 외부 API 차단 상태 |
| 오프라인 감사 기록 masked 101/101, validation 100/100 완료. 정합성 문제 0, 차단 0, 정답 누출 0 | 오프라인 대역. 판정 품질 평가가 아님 |
| 동일 조건 재실행 일치: 사례 결과 동일, 감사 기록은 사실 ID 정규화 후 동일 | 오프라인 대역 |
| 평가 위생: 프롬프트 1002건 검사, 누출 0, 1라운드 Matcher 동일 | masked 101건, 대역 포함 |
| 평가 충실도: 평가 경로 정책 A와 실제 Decision Loop 일치 228/228 | 개발 101, 검증 100, 보충 27. 오프라인 대역 |
| NSCLC: 시험 8개 선정, 6개 파싱, 슬롯 후보 196행 | **전부 임상 검수 전** |
| 안전 경계: 자기 보고·출처 미상 근거로는 `clinical_record` 기준이 확정되지 않음 | 계약·단위 테스트 기준. 실제 판정 경로 수치가 아니며, 선언된 기록 출처는 예외 (§2.2 D) |

원문에서 옮긴 값이며 이번에 재실행하지 않은 것:

| 수치 | 표기 조건 |
|---|---|
| 실제 LLM 파일럿 A: 합성 3사례, 16회 호출, $0.589, 366초 | `origin/report/llm-pilot-a-1026`. 저자 스스로 "정확도 지표가 아님", Console 청구 대조 미확인으로 기재 |
| NSCLC 파싱 API 비용 누적 $2.07 | `usage_calls_full_v2.jsonl` 마지막 `total_cum_usd`. 공시 단가 기준 |

---

## 5. 사용하면 안 되는 미검증 수치

| 수치·주장 | 이유 |
|---|---|
| 적격성 accuracy, False Eligible, 오확정 수 | 독립 GT 없음, 오프라인 확정 0건 (§0.3) |
| "False Eligible 0" | 확정 쌍이 0건이라 나온 값이며 안전성 근거가 아님 |
| `confirmed_correct_pairs`를 "확정"이나 "증거로 확인된 적격"으로 표기 | `evaluate.py` 경로의 값은 ELIGIBLE 예측 수 (§0.2) |
| `coverage_exact`를 매칭 정확도나 판정 coverage로 표기 | 질문 겨냥 구조 지표 (§0.1) |
| Rescue, Cleanup, False Removal, Top-1, Precision@k | 실행 가능한 `outputs` 없음 |
| `final_label_agreement` 0.05 (7/140), `gt_resolved_after` 0 (0/80) | Matcher 대역의 산물. 두 방식이 같음 |
| `unanswered_rate` 0.909 (baseline), 0.961 (candidate) | 답변 시뮬레이터 설계의 산물. 실제 환자 응답률이 아님 |
| BLOCKED_FAILURE 104건, 사례당 1단계 종료 | 소진 규칙이 미확정이고 PR #10이 바꿈 |
| 코디네이터 630분, 대기 145,440분 등 모든 분 단위 값 | 전부 가정값, 예산 비제약. 절대 절감 주장 불가 |
| `latency_minutes` 0 | 미측정의 기본값 |
| 정책 우열, "Decision Loop가 낫다", 번들링 효과 | 비교 실행이 없음 |
| 역전 지표 값 | PR #3 미병합, 확정 0건이라 의미 없음 |
| 생성기의 `eligible_rate` 등 | 신증후군 예시, 미연결 기준 충족 처리 |
| README의 환자당 $0.2–0.7 | 문서 자체가 참고값으로 표기 |
| 과거 보고서의 테스트 수치 | 커밋이 달라 현재 상태가 아님 |

**구조 지표의 주의 사항 (내부 참고용)**

`coverage_exact`는 재현되지만 발표 수치로 쓰기에는 맥락이 필요합니다. 그리고 **제안 경로에 불리한 결과입니다.**

| 세트 | baseline | candidate (Decision Loop = `A_current`) | `B_protocol` | `E_info_value` | `R_random` 평균 (seed 3개) |
|---|---|---|---|---|---|
| masked 101 | 0.8103 (47/58) | 0.4138 (24/58) | 0.8103 | 0.6724 | 0.5460 |
| validation 100 | 0.61 | 0.45 | 0.65 | 0.54 | 0.52 |
| supplement 27 | 측정 안 함 | 0.4444 | 0.4444 | 0.4815 | 0.4691 |

- baseline은 `eval_question_plans`·`eval_question_priority`, 나머지는 실제 루프 경로인 `eval_question_fidelity` 값입니다.
- 대역 환경의 질문 겨냥률이며 임상 성능이 아닙니다.
- **현재 Decision Loop의 동점 처리는 세 세트 모두 동점 무작위 섞기 평균보다 낮습니다.** 다만 무작위는 seed 3개뿐이고 신뢰구간이 없어, 통계적 결론은 아닙니다.
- 동점 순서만 프로토콜 순서로 바꾼 `B_protocol`이 masked에서 0.8103이므로, 차이의 상당 부분은 정보 키 문자열 순서로 풀리는 동점 처리에서 나옵니다.
- 이 값을 빼고 "Decision Loop 도입 효과"를 말하면 안 됩니다.

---

## 6. 평가 완성에 필요한 작업

### P0: 없으면 정책 비교 결과가 나오지 않음

아래 7건은 §9에서 구현 작업 4개로 묶었습니다. 표의 범위 전체가 아니라 §9의 축소 범위부터 진행합니다.

| # | 작업 | 완료 기준 |
|---|---|---|
| 1 | **실험 이름 합의.** patient-independent ↔ `patient_order`, DCV 제거, 회복 루프 제거의 정의를 설계 §5에 반영 | 문서에 이름·정의·끄는 스위치가 확정됨 |
| 2 | **GT 정책 결정.** 임상 검수 범위와 "판정 불가" 처리, 검수 없이 낼 수 있는 지표의 경계 | 검수 답변 또는 "구조 벤치마크 한정" 결정이 기록됨 |
| 3 | 생성기 통합, NSCLC 슬롯 사전·생성 설정·`source_map.json`, `assume_pass` 처리(Q-G3) | NSCLC 코호트가 `validate()` 통과 |
| 4 | `sim/` 구현: 환경, `ResponseModel`, `OfflineEvaluator`, Runner | 같은 spec 2회 → `result_hash` 동일 |
| 5 | 기준선 3종과 `full_dcvc` 구현, 정책 선택 인터페이스에 seed 전달 | `test_engine_policy` 조건 통과 |
| 6 | PR #10 병합, 소진·재질문·대체 규칙 확정 (설계 §0.1의 TODO) | "모름" 뒤 다른 질문이 계속됨 |
| 7 | 지표 연결: PairStatus 기반 CE/CI/Unresolved, `confirmed` 전달, 임상판단 기준 분모 제외 | 판정 불가 쌍이 분모에서 빠지고 별도 집계됨 |

### P1: 결과를 신뢰하고 발표하려면 필요

| # | 작업 |
|---|---|
| 1 | 결과 해시의 사실 ID 정규화, 별칭 salt를 spec에서 유도 |
| 2 | manifest에 `catalog_claims`, 코드 커밋, 환경, 잠금 파일 해시 기록 |
| 3 | PR #3 병합, 역전 열 추가 |
| 4 | ablation 실행 경로: `-bundles`, `-evidence_level`, `-fairness_floor`, 합의된 DCV·회복 루프 제거 |
| 5 | `latency_minutes`에서 미측정과 0을 구분, 달력 시간 집계 |
| 6 | NSCLC 나머지 2개 시험 파싱 재시도(별도 승인 필요), FROZEN 해시 |
| 7 | 부트스트랩 신뢰구간, dev/test 분리 |
| 8 | 비용 근거 결정 (계약 안건 5). 가정값이면 상대 비교로 표기 고정 |
| 9 | 동점 순서 문제 결정: 문자열 순서(`A_current`) 유지 여부 |

### P2: 품질 개선

| # | 작업 |
|---|---|
| 1 | 소규모 완전탐색, `null` 시나리오 점검 |
| 2 | M14 동등성 테스트 (WP8 이후) |
| 3 | `-partial_reeval` (WP4 이후) |
| 4 | `coverage` 이름 충돌 정리 (`coverage_exact`와 판정 coverage) |
| 5 | `requirements.txt`의 cp949 설치 실패 해결 |
| 6 | `wp7_offline_records.md` §5 수치 갱신 |
| 7 | `PolicyEngine` 프로토콜 갱신 (`select`의 `cohort`, `apply_outcome`이 프로토콜에 없음) |

---

## 7. 다른 팀원에게 위임할 작업

담당자는 저장소 문서에 적힌 소유 영역을 따랐습니다. 확정은 팀에서 해 주세요.

| 대상 | 작업 |
|---|---|
| 서연 (WP2·WP6) | P0-3 NSCLC 데이터, P0-4 시뮬레이터, P0-7 지표, 파싱 잔여 2개 |
| 동겸 (WP5) | P0-5 기준선·`full_dcvc`, P0-6 소진 규칙, 설계 Q-D2 답변, `bundle` 끄기 |
| 선우 (계약·승인) | Q-J1·Q-J2 답변, 계약 안건 1·5, salt 처리 방식, 유료 재파싱 승인 |
| 생성기 작성자 | Q-G1~G3 답변, 생성기 통합 |
| 임상 검수자 (호흡기·종양내과) | `wp2b_clinical_review_questions.md` 답변. 없으면 팀이 P0-2를 범위 축소로 결정 |
| A 작업 (answer_outcome) | 병합 후 H 항목의 수치 재측정 |
| C 작업 (PR 통합 검증) | 이 문서의 병합 무충돌은 텍스트 기준일 뿐이므로 통합 테스트로 확인 |

---

## 8. 최소 재현 명령

Git Bash 기준이며 worktree 루트에서 실행합니다. 편집 설치(`pip install -e`)가 다른 체크아웃을 가리킬 수 있으므로 `PYTHONPATH=src`를 씁니다.

```bash
git fetch origin
git worktree add -b <브랜치> ../<폴더> 0b402c6
cd ../<폴더>
python -m venv <저장소 밖 경로>/venv
PYTHONUTF8=1 <venv의 python> -m pip install -r requirements.txt

export PYTHONUTF8=1 ANTHROPIC_API_KEY= PYTHONPATH=src
PY=<venv의 python>
OUT=<저장소 밖 출력 경로>

$PY -m pytest -q -p no:cacheprovider
$PY scripts/run_offline_records.py --out $OUT/masked --set masked --repeat
$PY scripts/run_offline_records.py --out $OUT/validation --set validation --repeat
PYTHONHASHSEED=0     $PY scripts/eval_question_plans.py --out $OUT/qa
PYTHONHASHSEED=12345 $PY scripts/eval_question_plans.py --out $OUT/qb
cmp $OUT/qa/cases.csv $OUT/qb/cases.csv
diff $OUT/qa/summary.json $OUT/qb/summary.json
$PY scripts/eval_question_priority.py --out $OUT/priority
$PY scripts/eval_question_fidelity.py --out $OUT/fidelity
```

실행하면 안 되는 명령 (실제 LLM 호출): `scripts/budget_sweep.py`, `scripts/question_policy_sweep.py`, `python -m ctrec batch`.

---

## 9. 최소 실행 계획

**목표**: 같은 합성 코호트·예산·seed에서 `full_dcvc`와 기준선을 돌려 재현 가능한 비교표를 만듭니다.

**이 계획으로 주장할 수 있는 것**: 합성 조건에서의 정책 간 **상대 비교**(행동 수, 가정 비용, 시스템 확정 진척)와 재현성입니다. 임상 정확도, False Eligible, 실제 업무시간 절감은 이 계획으로 나오지 않습니다(§0.3).

| 순서 | 작업 | 범위 | 묶은 P0 | 완료 기준 |
|---|---|---|---|---|
| 1 | **최소 합성 코호트 및 규칙 GT** | 생성기 통합. NSCLC 파싱 6개 시험과 구조화 규칙 범위. 미연결 기준은 `assume_pass`가 아니라 "라벨 없음" | P0-2 일부, P0-3 | `validate()` 통과, 같은 설정 2회 생성 해시 동일, 라벨 없음 쌍 수 보고 |
| 2 | **재현 가능한 Runner** | 환경·`ResponseModel`·규칙 범위 평가기·Runner·manifest. PR #10 병합 후 `no_answer` 포함. 사실 ID 정규화와 salt 고정 포함 | P0-4, P0-6 | 같은 spec 2회 → `result_hash` 동일, seed 변경 시 응답 변화, 실패·무응답 새 사실 0 + 비용 청구, LLM 호출 0 |
| 3 | **Full DCVC와 최소 baseline** | `full_dcvc` 정의 확정과 구현, `random`, `cheapest_first`, 기존 `legacy_greedy`. 세 번째 기준선은 이름 합의 뒤 결정 | P0-1, P0-5 | `PolicyEngine` 구현이 WP6 설계 §5의 테스트 조건 통과, 모든 정책이 같은 `source_catalog_hash`와 예산으로 실행 |
| 4 | **필수 지표 집계** | PairStatus 기반 집계, 판정 불가 분모 제외, `catalog_claims` 기록, 선언 출처 처리 | P0-7 | 아래 지표가 정책·seed별로 나옴, 고정 입력 테스트 통과 |

순서 1과 3은 병렬로 진행할 수 있습니다. 순서 2는 1의 코호트 형식과 PR #10이 필요하고, 순서 4는 2의 기록이 필요합니다.

**필수 지표 (최소 집합)**

| 지표 | 정의 | 표기 |
|---|---|---|
| 시스템 확정 적격 수 | `CONFIRMED_ELIGIBLE` 쌍 | 증거로 확인된 적격이라고 쓰지 않음 |
| 시스템 확정 부적격 수 | `CONFIRMED_INELIGIBLE` 쌍 | |
| 미해결 수 | 그 밖 상태별 쌍 (`BLOCKED_FAILURE`, `EXPERT_REVIEW` 등 분리) | 정의는 작업 4에서 고정 |
| 확정 비율 | 시스템 확정 쌍 / 라벨과 무관한 전체 평가 쌍 | 기존 `coverage`와 다른 이름 사용 |
| 행동 수 | 유형별 실행 행동 | |
| 비용 | 코디네이터·임상의 분(가정값), 경과 시간(시뮬레이션) 분리 | 상대 비교 전용 |
| 규칙 GT 불일치 | 규칙 범위에서 시스템 확정과 생성 라벨이 다른 쌍 | **False Eligible로 쓰지 않음**. 구현 일관성 검사 |

**시작 전에 정할 위험 3가지**

1. **규칙 범위가 좁습니다.** NSCLC 파싱 160개 규칙 중 구조화 규칙은 19개이고 검사값 규칙은 0개입니다. 나머지 기준을 판정하지 못하면 Confirmed Eligible이 계속 0건일 수 있습니다. 작업 2에서 "규칙 범위에 든 기준만 평가 대상으로 삼는 시나리오"를 쓸지, 검수된 `categorical` 평가기를 넣을지 정해야 합니다. 전자를 쓰면 결과에 "일부 기준만 평가"를 명시합니다.
2. **`full_dcvc`의 정의가 코드와 설계에 없습니다.** 계산식과 끄는 스위치가 정해지기 전에는 작업 3을 끝낼 수 없고, DCV 제거 ablation도 정의되지 않습니다.
3. **규칙 GT는 순환적입니다.** 같은 규칙 엔진이 정답과 판정을 모두 만듭니다. 그래서 불일치 0은 구현 검증일 뿐입니다.

**이 계획에서 뺀 것** (P1 이후): NSCLC 2개 시험 재파싱, `oracle_upper`, 부트스트랩 신뢰구간, 부분 재평가, 웹 동등성, 임상 검수 이후의 정답 확장.

---

## 10. 의료 전문가 검증과 엔지니어링 작업의 구분

**판단 기준**: 결과가 임상적으로 맞는지를 정해야 하면 전문가 영역이고, 정해진 규칙을 코드로 옮기고 검사할 수 있으면 엔지니어링 영역입니다.

### 의료 전문가 검증이 필요한 항목

| 항목 | 대상 | 근거 |
|---|---|---|
| 독립 GT 쌍 라벨 | accuracy, False Eligible 산출의 전제 | §0.3 |
| 슬롯 해석 | `slot_candidates.csv` 196행, 특히 `categorical` 72, `fact_llm` 83, `expert` 16, `unresolved` 3 | `wp2b_clinical_review_questions.md` |
| 기준 의미 | AGA 범위, 유전자별 3값 구조, 항응고 중 INR 판정 등 | 같은 질문지 A·검사 항목 |
| `underspecified` 처리 | 기준 데이터 39개, NSCLC 10개 규칙 | §2.2 G |
| 증거 요구 수준 | 어떤 기준이 `clinical_record`여야 하는가 | Confirmed Eligible의 의미를 결정 |
| 사전 분포와 조합 | 슬롯 값 분포, 동시 양성 허용 여부의 임상적 타당성 | `slot_combination_candidates.md` |
| 숨김 대상의 타당성 | 숨긴 기준이 실제로 판정을 가르는가 | 검증셋은 층화 무작위 (§2.2 K) |

행동 비용의 실측·문헌값은 임상 진단이 아니라 **연구 코디네이터 업무 근거**가 필요한 항목입니다. 이것도 엔지니어가 임의로 정할 수 없습니다.

### 엔지니어링만으로 처리할 수 있는 항목

| 항목 | 해당 작업 |
|---|---|
| 생성기 통합, 구조화 규칙 바인딩, `assume_pass` 비활성화 | §9-1 |
| Runner, `ResponseModel` 코드, 결정적 난수, manifest, `result_hash` | §9-2 |
| 사실 ID 정규화, salt 고정, 잠금 파일, 설치 인코딩 | §9-2, P1·P2 |
| `latency_minutes` 미측정 구분, 경과 시간 집계 | P1 |
| `random`, `cheapest_first` 구현, `bundle` 끄기 스위치 | §9-3 |
| PairStatus 기반 집계, `confirmed` 연결, 분모 제외 로직, 이름 정리 | §9-4 |
| PR #3·#10 병합과 회귀 검증, 문서 갱신 | P0·P1 |

### 팀 결정이 필요한 항목 (의료도 구현도 아님)

- `full_dcvc` 정의, 기준선과 ablation 이름 (P0-1)
- "모름"의 재질문·소진 규칙 (P0-6)
- `ResponseModel` 파라미터 값. 코드는 엔지니어링이지만 값은 전부 가정이며 manifest에 `assumed`로 남깁니다.
- 동점 순서 정책, 규칙 범위 시나리오 채택 여부
- 임상 검수가 불가능할 때 발표 범위를 줄일지 여부

**경계 규칙**: 엔지니어링 작업이 끝나도 임상 주장이 생기지는 않습니다. 전문가 검증이 없는 항목은 "검수 전"을 유지하고, 기본값으로 정답을 만들지 않습니다.

---

## 11. 수치별 근거

`근거`의 E 번호는 §11.2 스크립트 출력 구역입니다. 모든 명령은 §8의 환경 변수를 전제로 합니다.

### 11.1 근거표

| 수치 | 근거 |
|---|---|
| 테스트 2082 통과, 7 건너뜀 | `$PY -m pytest -q -p no:cacheprovider` |
| 관련 테스트 222 통과, 1 건너뜀 | 같은 명령에 `tests/test_engine_policy.py tests/test_engine_contracts.py tests/test_engine_contract_v02.py tests/test_engine_audit.py tests/test_record_producer.py tests/test_offline_records.py tests/test_eval_entry.py tests/test_eval_hygiene.py tests/test_question_eval.py tests/test_masked_benchmark.py` 지정 |
| 기록 완료 101/101, 100/100, 단계 109, 정합성 0, 누출 0 | `run_offline_records --repeat`의 `summary.json` (`total`, `truth_leaks`, `repeat_mismatch`) |
| 진단 8건 (masked), 9건 (validation) | 같은 파일 `issue_codes` |
| `no_response` 101, `succeeded` 8, 전이 103 + 1, 93건 1단계 종료, 630분, 145,440분 | E1 |
| 원본 바이트 불일치 | E2 (run과 repeat 해시가 다름) |
| 최종 쌍 상태, 확정 0건, ELIGIBLE 예측 0건 | E3 |
| `underspecified` 39/471, 17/26, 93/140, 51/77 | E4 |
| NSCLC 8/6, 참조 0, 규칙 160·구조화 19·`underspecified` 10, 슬롯 196 | E5 |
| 구조화 규칙 19개의 구성, 검사값 규칙 0개 | `docs/dev/wp2a_parse_pilot_NCT06928389.md:308` |
| `NCT05255302`, `NCT04892953` 파싱 실패 | 같은 문서 `:262-263` |
| `confirmed_correct_pairs` 예시, 상태 파생 결과 | E6 |
| `clinical_record` 선언 시 판정 유지 | E7 |
| salt 5개 중 1개만 다른 선택 | E8 |
| 분 단위 비용 7개 정보원 `assumed`, `relative_policy_comparison_only` | E9 |
| masked `coverage_exact` baseline, candidate, `final_label_agreement`, `gt_resolved_after`, `unanswered_rate` | `eval_question_plans --out`의 `summary.json` `methods.*` |
| `cases.csv` 동일, `summary.json` 차이는 `seconds`뿐 | §8의 `cmp`, `diff` |
| 프롬프트 1002건, 누출 0 | 같은 `summary.json` `hygiene` |
| validation baseline 0.61 | `eval_question_priority --out`의 `validation.summary.baseline` |
| 정책 A~E, `R_random` 값, 228/228 | `eval_question_fidelity --out`의 `policies:*`, `fidelity:*` |
| 생성기 35 통과, 2회 생성 해시 동일, 연결 25·미연결 42 | §11.3 |
| PR #3 80 통과·1 건너뜀, PR #10 54 통과 | §11.3 |
| 병합 무충돌 | §11.3 `git merge-tree` 종료 코드 0 |
| 파일럿 16회, $0.589, 366초 | `git show origin/report/llm-pilot-a-1026:docs/llm_pilot_results_A_20261026.md` (재실행 안 함) |
| NSCLC 파싱 누적 $2.07 | `data/nsclc/parse_runs/usage_calls_full_v2.jsonl` 마지막 행 `total_cum_usd` (재실행 안 함) |
| 환자당 $0.2–0.7 | `README.md:243` (재실행 안 함) |
| 설치 cp949 실패 | `PYTHONUTF8` 없이 `pip install -r requirements.txt` (한국어 Windows, Python 3.10) |

### 11.2 재계산 스크립트

아래 내용을 저장소 밖에 `audit_evidence.py`로 저장합니다. worktree 루트에서 먼저 `run_offline_records --out $OUT/masked --set masked --repeat`를 실행한 뒤 `$PY audit_evidence.py $OUT`로 실행합니다. 이 문서의 E 구역 값은 이 스크립트로 다시 계산해 일치를 확인했습니다. E2의 해시 값 자체는 실행마다 다르며, run과 repeat가 다르다는 점만 근거입니다.

```python
"""WP6 감사 수치 재계산. 저장소를 바꾸지 않고 LLM을 부르지 않음. 사용: python audit_evidence.py <OUT>"""
import collections, csv, glob, hashlib, json, pathlib, sys, tempfile
OUT = pathlib.Path(sys.argv[1]); R = pathlib.Path(".").resolve()
sys.path[:0] = [str(R / "scripts"), str(R / "src")]
import run_offline_records as ror
from bench_incremental import load_frozen
from decision_scenarios import load_trials
from ctrec import offline_records as orc
from ctrec.agents import matcher
from ctrec.engine.bundles import SourceCatalog
from ctrec.engine.contracts import Action, EffortBudget, derive_pair_status as dps
from ctrec.engine.experiment import catalog_claims
from ctrec.engine.policy import LegacyAdapterPolicy
from ctrec.eval_hygiene import AliasMap
from ctrec.metrics import cohort_eligibility_metrics as cem
from ctrec.schemas import CriterionAssessment

print("[E1] WP7 masked 기록 집계")
o, t, a, per = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
coord = wait = 0
for f in sorted((OUT / "masked" / "run").glob("*/decision_records.jsonl")):
    n = 0
    for line in open(f, encoding="utf-8"):
        r = json.loads(line); n += 1; x = r["outcome"]
        o[(x["status"], x["error_code"])] += 1; a[r["action"]["action_type"]] += 1
        coord += x["cost_charged"]["coordinator_minutes"]; wait += x["cost_charged"]["patient_wait_minutes"]
        for p in r["pairs"]:
            if p["before"] != p["after"]:
                t[(p["before"], p["after"], p["authority"], p["reason_code"])] += 1
    per[n] += 1
print(dict(o), dict(a), "steps_per_case", dict(per), "coord", coord, "wait", wait, dict(t))
h = lambda d: hashlib.sha256(b"".join(pathlib.Path(p).read_bytes() for p in sorted(glob.glob(str(d / "*" / "*.jsonl"))))).hexdigest()[:16]
print("[E2] 원본 해시 run/repeat", h(OUT / "masked" / "run"), h(OUT / "masked" / "repeat"))

print("[E3] 최종 쌍 상태 (정답 대조 없음)")
parsed = load_frozen(); allt = load_trials(); trials = {k: allt[k] for k in parsed}
for name in ("masked", "validation"):
    hcs, _, scan = ror._cases(parsed, ror.SETS[name], "audit"); c, e = collections.Counter(), collections.Counter()
    with tempfile.TemporaryDirectory() as td:
        for i, hc in enumerate(hcs):
            for s in orc.record_case(hc, trials, scan, pathlib.Path(td) / str(i)).final_cohort.pairs():
                c[s.status.value] += 1; e[s.eligibility] += 1
    print(name, sum(c.values()), dict(c), dict(e))

print("[E4] 임상판단 기준과 라벨 쌍")
under = {k: [r.rule_id for r in p.rules if r.underspecified] for k, p in parsed.items()}
print("rules", sum(len(p.rules) for p in parsed.values()), "underspecified", sum(map(len, under.values())), "trials", len(parsed), "with", sum(map(bool, under.values())))
for f in ("data/labels/masked_labels.csv", "data/labels/synthetic_labels.csv"):
    rows = list(csv.DictReader(open(f, encoding="utf-8")))
    print(f, sum(bool(under.get(r["trial_id"])) for r in rows), "/", len(rows))

print("[E5] NSCLC 데이터")
ns = {pathlib.Path(p).stem for p in glob.glob("data/nsclc/trials/*.json")}
pp = {pathlib.Path(p).stem for p in glob.glob("data/nsclc/parsed/*.json")}
refs = sum(any(n in pathlib.Path(p).read_text(encoding="utf-8") for n in ns)
           for p in glob.glob("data/patients/**/*.json", recursive=True) + glob.glob("data/labels/*.csv"))
print("trials", len(ns), "parsed", len(pp), "missing", sorted(ns - pp), "files_referencing", refs)
kind = collections.Counter()
for f in glob.glob("data/nsclc/parsed/*.json"):
    d = json.load(open(f, encoding="utf-8"))
    for r in d.get("rules") or d.get("parsed", {}).get("rules") or []:
        kind["structured" if r.get("structured_evaluable") else "underspecified" if r.get("underspecified") else "other"] += 1
slots = list(csv.DictReader(open("data/nsclc/cohort/slot_candidates.csv", encoding="utf-8-sig")))
print("rules", sum(kind.values()), dict(kind), "slot_rows", len(slots), dict(collections.Counter(r["review_status"] for r in slots)),
      dict(collections.Counter(r["adjudication_candidate"] for r in slots)))

print("[E6] 'confirmed' 지표와 상태")
g = {("p", "t"): "INELIGIBLE", ("p", "u"): "ELIGIBLE"}; p = {k: "ELIGIBLE" for k in g}
x, y = cem(g, p), cem(g, p, confirmed=set())
print("confirmed=None", x["confirmed_correct_pairs"], x["confirmed_wrong_pairs"], "confirmed=set()", y["confirmed_correct_pairs"], y["confirmed_wrong_pairs"])
print(dps("ELIGIBLE", {"unverified"}).value, dps("ELIGIBLE", {"physician_review"}).value, dps("ELIGIBLE", set()).value,
      dps("INELIGIBLE", set(), "provisional").value, dps("INELIGIBLE", set(), "confirmed").value)

print("[E7] 증거 게이트: clinical_record 필요 기준, 근거 출처별 판정 유지 여부")
for src in ("clinical_record", "unknown"):
    q = CriterionAssessment(rule_id="I1", kind="inclusion", criterion_text="c", holds="yes", passes=True, confidence="high",
                            evidence="e", reasoning="r", missing_info=None, method="llm")
    meta = matcher.RuleMeta(required_evidence="clinical_record")
    q = matcher._apply_evidence_policy(q, meta, "note", input_source=src)
    print(src, "evidence_source", q.evidence_source, "passes", q.passes, "needs_verification", q.needs_verification)

print("[E8] 별칭 salt와 동점 선택 (동점 2행동, 예산 1건분)")
def act(al):
    return Action(action_id=f"{al}:f", action_type="REQUEST_DOCUMENT", patient_alias=al, source_id="lab_report", target_trial_ids=("T1",),
                  target_criteria=("T1:I1",), required_fields=("lab:x",), reason_code="x", tier=2, value_score=1, priority=1.0,
                  sequence=0, fingerprint="f", policy_version="v")
for s in ("s1", "s2", "s3", "s4", "s5"):
    m = AliasMap(salt=s); u, v = m.alias("P1"), m.alias("P2")
    print(s, "P1" if LegacyAdapterPolicy().select([act(u), act(v)], EffortBudget(coordinator_minutes=9)).selected[0].patient_alias == u else "P2")

print("[E9] 비용 주장 범위", json.dumps(catalog_claims(SourceCatalog()), ensure_ascii=False))
```

### 11.3 브랜치 사본 확인

worktree를 건드리지 않도록 원격 ref를 저장소 밖에 풀어서 실행합니다.

```bash
for b in research/cohort-generator feat/wp7-reversal-metrics feat/wp5-item-level-failure; do
  git merge-tree --write-tree origin/integration/dcvc origin/$b >/dev/null; echo "$b rc=$?"
done

mkdir -p $DIR/gen $DIR/rev $DIR/item
git archive origin/research/cohort-generator   | tar -x -C $DIR/gen
git archive origin/feat/wp7-reversal-metrics   | tar -x -C $DIR/rev
git archive origin/feat/wp5-item-level-failure | tar -x -C $DIR/item

(cd $DIR/gen  && $PY -m pytest -q -p no:cacheprovider tests/test_cohort_generator.py)
(cd $DIR/rev  && $PY -m pytest -q -p no:cacheprovider tests/test_reversal_metrics.py)
(cd $DIR/item && $PY -m pytest -q -p no:cacheprovider tests/test_engine_policy.py tests/test_offline_records.py)

(cd $DIR/gen && for i in 1 2; do
   $PY scripts/build_cohort_benchmark.py generate --config data/cohort/generator_config.json --out $OUT/gen_$i
 done)   # 두 폴더의 파일 해시 비교. 연결·미연결 기준 수는 report.json의 bound_rules, unbound_rules
```
