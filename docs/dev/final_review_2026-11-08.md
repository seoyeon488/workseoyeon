# 최종 검수 — 실험 결과·발표 자료 (2026-11-08 21시, 선우 요청)

작성: 서연 · 기준: 선우 통합본 `urgent/integration` `8afe5ea` (2026-11-08 20:50) · 검수 범위: 읽기 + 허용된 확인 실행(P0 채점, 데모 A~D 재확인)
> **데이터 검증 완료 / 임상 검수 미완료.** GT는 축소 범위 규칙 GT (임상 전문가 미검수). 정확도·성능 향상 표현을 쓰지 않습니다. 실험(정책 비교·ablation)은 다시 돌리지 않았고, 코드·GT 라벨·데이터는 바꾸지 않았습니다.

## 요약

| 항목 | 결과 |
|---|---|
| 수치 불일치 | **9건** (발표 초안 5, 데모 문서 4). 슬라이드 1~5의 데이터·라벨·실행 수치 19개 항목은 모두 일치. 불일치는 모두 통합본의 엔진 수정으로 바뀐 P0·지역 조건·데모 실행 기록. 내 문서는 직접 고침 |
| 성능 주장 | 내 문서 **삭제 1 / 수정 3**, 남의 문서 **수정 필요 4**. DCV·번들링 효과 주장은 내 문서에 없음 → 한계로 명시 |
| DCV·번들링 | no_dcv = dcvc (7개 조건 전부), no_bundles > dcvc 역전 1개 조건 (생성기 800분 11.17 vs 8.17) → "이번 실험 조건에서 차이 없음 또는 역전, 추가 검증 필요" |
| GT 명칭 | 내 문서 3개 통일. 남의 문서는 대상이 다른 GT라 구분 표기 권장 |
| known_defect | **충돌 있음.** 선우 `5fa4e24`로 P0-3이 고쳐져 strict xfail 2건이 XPASS로 실패. 해제 패치(2줄) 제안 → 적용 시 13 passed |
| P0 127건 | 오채택 36 → 22, 상충 탐지 10/27 → 15/27, 과잉 보류 4 → 4. 나빠진 사례 0 |
| 확정 데모 흐름 | 웹 W1(DEMO-NSCLC-1, 묶음 요청 → 서류 확인 → 의사 판단) 메인 + 오프라인 A(P052 EXPERT_REVIEW)·B(P045 기록 확인 후 부적격) 보조. D는 한계 설명용, C는 질문 대비용 |
| 위치 미확인 | ① 통합본 기준으로 재실행한 DCV+C·ablation 결과 (저장소 최신은 `3e4b2fd`, 11-07) ② W1~W3 번호가 붙은 문서 |

## 0. 위치 파악

| 대상 | 위치 | 생성 커밋·시각 | 비고 |
|---|---|---|---|
| 선우 최종 통합 브랜치 | `origin/urgent/integration` `8afe5ea` | 2026-11-08 20:50 | `integration/dcvc` `471a9ee`(16:29) + 선우 P0-B·지역 조건·E12·성별·GT 도구 + 동겸 웹 수정 |
| DCV+C·ablation 결과 (최신 저장본) | `docs/dev/p_results/{demo,nsclc_pilot,generator_neph_k3}.{tsv,json}`, 보고서 `docs/dev/p_common_engine_2026_11_07.md` | `3e4b2fd` 2026-11-07 20:44 (선우) | 통합본 엔진 수정 **이전** 결과. 그 뒤 재실행 결과 파일은 모든 원격 브랜치에서 **위치 미확인** |
| NSCLC 평가셋 실행 결과 | 내 `data/nsclc/eval/checks/runner_*_4f81460.json` (`9e79820`, 11-08 02:33) | 4f81460 | 이번에 데모 재확인과 같은 실행으로 `8afe5ea` 값도 확인 (5절) |
| 자동 실행(e2e) 결과 | `README.md` 11-08 "끝까지 자동 실행" 표 (`7c282b2`, 14:23, 동겸) | | 가상 시험 T-A~D, 결과 파일 `outputs/e2e/`는 git 밖 |
| 발표 자료 | 내 `docs/dev/presentation_data_gt.md`, `demo_nsclc_scenarios.md`, `nsclc_eval_dataset.md` (`docs/presentation-data-gt`) / 통합본 `docs/dev/web_demo_flow.md`, `docs/demo_capture.md`(중간발표용), `docs/team_handoff.md`, `README.md` 변경 이력 | | 별도 슬라이드 파일(.pptx 등)은 저장소에 없음 |
| 웹 데모 시나리오 W1~W3 | W 번호 문서는 **위치 미확인**. `web_demo_flow.md` §2·§4와 `README.md` 11-08 브라우저 확인 기록 3건을 W1~W3로 대응 (5절, 동겸 확인 필요) | `f1c56ef` 15:30, `894747a` 13:42, `d20cc0d` 20:43 | |

## 1. 수치 대조

대조 방법: 통합본 `8afe5ea` worktree의 파일을 스크립트로 다시 셈 (`docs/dev/final_review_scripts/verify_numbers.py`). 평가셋 파일(`data/nsclc/eval`, `data/nsclc/review`)은 `46e011e` 이후 바뀌지 않았습니다.

### 1-1. 발표 초안 `presentation_data_gt.md`

| 위치 | 발표 자료 값 | 최신 값 | 출처 파일 | 판정 |
|---|---|---|---|---|
| 슬1 프로토콜 | 8건, 조회 2026-11-02 | 8, 2026-11-02 | `data/nsclc/trials/*.json` | 일치 |
| 슬1 파싱 | 완료 6 / 미완료 2 | 6 / 2 | `protocol_status.csv` | 일치 |
| 슬1 기준 | 160 | 160 | `criteria_verification.csv` | 일치 |
| 슬1 환자 | 합성 80 | 80 | `patients.json` | 일치 |
| 슬1 라이선스 | 확인 필요 | – | – | 출처 없음 (그대로 "확인 필요") |
| 슬2 범위 안 | 72 / 160 | 72 | `criteria_verification.csv` `in_scope` | 일치 |
| 슬2 나이·성별·ECOG | 19 (지역 조건부 1) | 19 (`in_rule_engine`, region_conditional 1) | 같음 | 일치 |
| 슬2 범주형 | 34 (연결 23, 미연결 11) | 34, 23, 11 | 같음 | 일치 |
| 슬2 판단 기준 | 19 | 19 | 같음 | 일치 |
| 슬2 excluded / 범위 밖 | 9 / 79 | 9 / 79 | 같음 | 일치 |
| 슬2 원문 대조 | 60 / 11 / 1 | 60 / 11 / 1 | 같음 `result` | 일치 |
| 슬2 검사 수치 기준 | 0건 | 0 | `lab_reference.json` | 일치 |
| 슬3 엔진 import | 0 | 테스트 2건 통과 | `tests/test_nsclc_eval_gt.py` (20 passed) | 일치 |
| 슬3 순환 라벨 일치 | 237 / 240 | 237 / 240 | `checks/circular_vs_independent_4f81460.json` | 일치 |
| 슬4 쌍·시드·해시 | 240, 20261107, `a549da3b1171fd52` | 240, base_seed 20261107, 같음 | `manifest.json` | 일치 |
| 슬4 라벨 | 0 / 23 / 130 / 87 | 0 / 23 / 130 / 87 | `label_summary.json`, `pair_gt.csv` | 일치 |
| 슬4 runner 400분 | no_action 0·0·0·0, full_dcvc 0·48·0·0 | 같음 | `checks/runner_400m_h10_4f81460.json` | 일치 (통합본 재실행 없음) |
| 슬4 runner 6000분 | 20 / 23, 124 / 130, 0, 0 | 4f81460 같음, **8afe5ea도 같음** | `checks/runner_6000m_h80_4f81460.json`, `final_review_evidence/runner_6000m_h80_8afe5ea_from_demo.json` | 일치 |
| 슬4 결함 사례 | 거짓 부적격 6 → 0 | 같음 | `nsclc_eval_dataset.md` §7 D7 | 일치 |
| 슬5 판단 대기 비율 | 9.6% | 23/240 = 9.58% | `label_summary.json` | 일치 |
| 슬5 P0 사례 수 | "48건" | **127건** (102 + held-out 25) | `data/p0-eval-cases` README | **불일치** → 127 |
| 슬5 지역 조건 | "20세 거짓 부적격 2케이스" | **0** (8afe5ea INFO_MISSING) | `final_review_evidence/p0_3_region_cases_8afe5ea.txt` | **불일치** → 문장 삭제, 수정 사례로 이동 |
| 슬5 held-out 상충 | 오채택 6 / 15 | **1 / 15** | `final_review_evidence/p0_fact_cases_8afe5ea_score.md` | **불일치** → 최신 값 |
| 슬5 held-out 전해 들은 값 | 오채택 3 / 10 | **0 / 10** | 같음 | **불일치** → 최신 값 |
| 슬5 P0 전체 | 오채택 36, 과잉 보류 4, 같은 항목 7/8 | **22**, 4, 7/8 | 같음 | **불일치 1** (36 → 22), 나머지 일치 |

### 1-2. 데모 문서 `demo_nsclc_scenarios.md`

| 위치 | 문서 값 | 최신 값 (8afe5ea) | 출처 | 판정 |
|---|---|---|---|---|
| A 실행 step | ECOG 25, EGFR 431, 조직형 433 | 22, 402, (408 시점 EXPERT_REVIEW) | `final_review_evidence/demo_scenarios_8afe5ea.json` | **불일치** (step 번호만, 상태 같음) |
| B 실행 step | ECOG 근거 확인 1713 | 1726 | `demo_pairs_8afe5ea.json` | **불일치** (step 번호만) |
| C 흐름 | P061 PD-L1 "모름" → 병리 결과지 | 이 흐름 없음 (E12 항목 수정). P058로 교체 | 같음 | **불일치** → 시나리오 교체 |
| D 상태 | CONFIRMED_INELIGIBLE ✗ | INFO_MISSING | `demo_scenarios_8afe5ea.json` `D_region` | **불일치** → 갱신 |
| A·B·C 최종 상태 | EXPERT_REVIEW / CONFIRMED_INELIGIBLE / INFO_MISSING | 같음 | 같음 | 일치 |

### 1-3. 남의 발표 관련 문서 (보고만)

| 위치 | 값 | 최신 결과 | 판정 |
|---|---|---|---|
| 선우 `p_common_engine_2026_11_07.md` ablation 표 | `p_results/*.tsv`와 같음 | 같은 파일 (`3e4b2fd`) | 일치. 단 통합본 엔진 수정 이전 결과 (6절 S4) |
| 동겸 `README.md` 자동 실행 표 | offline 확정 1+6, 참여 불가 3 / llm 5, 안전 위반 0 | 결과 파일이 git 밖(`outputs/e2e/`) | **출처 없음** (저장소에서 대조 불가) |
| 동겸 `README.md` 서류 기록 수정 | 확정 1 → 4 | 같음 | 출처 없음 (같은 이유) |
| 동겸 `web_demo_flow.md` §3 | 81.5분 대 81.5분, 4명일 때 13분 | 화면 계산값 기록 | 출처 없음 (브라우저 기록) |

## 2. 성능 주장 정리

### 2-1. no_dcv = dcvc, no_bundles 역전이 나온 조건

출처: `docs/dev/p_results/{demo,nsclc_pilot,generator_neph_k3}.tsv` (`3e4b2fd`, 2026-11-07 20:44, 선우 P 보고서 `docs/dev/p_common_engine_2026_11_07.md`). 값은 seed 평균, 가정 비용, 정책 간 상대 비교 전용입니다.

| 코호트 (GT 종류) | 예산(분) | dcvc 확정 부적격 / coverage | no_dcv | no_bundles | 판정 |
|---|---|---|---|---|---|
| 합성 데모 6×3 (GT 없음) | 20 | – / 0.111 | – / 0.111 | – / 0.111 | 세 팔 같음 |
| 같음 | 45 | – / 0.167 | – / 0.167 (행동 14.3, 41.7분) | – / 0.074 | no_dcv = dcvc (확정 같음, 행동·분만 근소 차이) |
| 같음 | 90 | – / 0.259 | – / 0.259 | – / 0.167 | no_dcv = dcvc |
| NSCLC 파일럿 8×6 (작성자 판독 부적격 15쌍) | 30 | 6 / 0.125 | 6 / 0.125 | 2 / 0.042 | no_dcv = dcvc |
| 같음 | 90 | 8 / 0.188 | 8 / 0.188 | 4 / 0.104 | no_dcv = dcvc. 세 팔 모두 거짓 부적격 1 (P0-3 지역 조건 결함) |
| 생성기 neph-k3 20×3 (생성기 GT) | 200 | 7.5 / 0.125 | 7.5 / 0.125 | 6.83 / 0.114 | no_dcv = dcvc |
| 같음 | 800 | 8.17 / 0.136 | 8.17 / 0.136 | **11.17 / 0.186** | **no_dcv = dcvc, no_bundles > dcvc (역전)** |

- no_dcv: 7개 조건 모두에서 확정 수가 dcvc와 같습니다. 이 실험 조건에서는 DCV 필터가 결과를 바꾸지 않았습니다.
- no_bundles: 6개 조건에서는 dcvc 이하이고, 생성기 800분에서는 dcvc보다 많습니다(역전). 번들 점수식은 재검토가 필요합니다(선우 보고서 §6).
- 구간 추정이 없는 조건입니다(데모 seed 3, 파일럿 seed 3, 생성기 seed 2 × 복제 3). 차이가 있는 칸도 우열로 쓰지 않습니다.
- 위 결과 생성 뒤 엔진 변경(P0-B 값 보류 `02f9d2c`, 지역 조건 보류 `5fa4e24`, E12·성별 수정 `173cd3f` 등)이 통합본에 들어갔습니다. 이 표는 변경 전 결과이고, 변경 뒤 ablation 재실행 결과는 위치를 확인하지 못했습니다.

### 2-2. 문장 검사

검색 대상: 내 문서 3개(`presentation_data_gt.md`, `demo_nsclc_scenarios.md`, `nsclc_eval_dataset.md`), 통합본의 `docs/dev/web_demo_flow.md`, `docs/demo_capture.md`, `docs/team_handoff.md`, `README.md` 변경 이력 11-07~08, `docs/dev/p_common_engine_2026_11_07.md`, 웹 화면 문구(`staff.js`).
검색어: 성능, 효율, 향상, 개선, 우수, 가장 좋, 기준선보다, 정확도, False Eligible·오분류, 절감, 줄여/줄어, 절약.

| # | 위치 | 문장 | 처리 | 근거·대체 문장 |
|---|---|---|---|---|
| 1 | 내 `presentation_data_gt.md` 슬라이드 5 | "이 평가셋·이 조건에서 판단 기준 외 확인 완료 20 / 23쌍, 거짓 확정 0" | 유지 (조건 명시 강화) | `runner_6000m_h80_4f81460.json`. "full_dcvc 6000분·horizon 80·seed 1 한 번 실행" 조건을 붙임 |
| 2 | 내 `presentation_data_gt.md` 슬라이드 4 표 | 기준선(no_action) 0 vs full_dcvc 48 (400분) | 수정 | no_action은 행동을 하지 않는 기준점이라 "기준선보다 우수"로 읽히면 안 됨. "행동 없음 기준점 대비 예산 사용 시 확정 부적격 증가"로 표기, DCV·번들링 효과의 근거로 쓰지 않음 |
| 3 | 내 `presentation_data_gt.md` 슬라이드 5 주장 가능 | "엔진과 분리된 규칙 GT로 정책 결과 대조 가능" | 유지 (명칭 통일) | 도구가 있다는 사실. 성능 주장 아님 |
| 4 | 내 문서 전체 | DCV·번들링·DCV+C 효과 문장 | 없음 → 한계 슬라이드에 "DCV·번들링 효과 미입증" 추가 | 2-1 표 |
| 5 | 내 `nsclc_eval_dataset.md` §8 | "실행 사례에서 확정 적격 0, GT가 부적격이 아닌데 확정 부적격 0" | 유지 | 이 평가셋·실행 조건 한정 문구가 이미 있음 |
| 6 | 선우 `p_common_engine_2026_11_07.md` 표 열 | "False Eligible", "False Ineligible", "확정 Eligible 정확도" | 수정 필요 (선우) | 임상 오분류로 읽힘. 발표에 옮길 때는 "축소 범위 규칙 GT와 다른 확정 적격 / 부적격"으로. 문서 본문 §7은 측정 불가를 이미 밝힘 |
| 7 | 선우 `p_common_engine_2026_11_07.md` §6 | "200분에서는 dcvc가 기준선보다 확인된 부적격이 많습니다 (7.5 vs 0~1)" | 수정 필요 (선우, 발표에 쓸 때) | 수치는 맞음(`generator_neph_k3.tsv`). 같은 표 800분 역전과 seed 2·구간 없음을 함께 적어야 함. DCV 효과 근거로는 쓸 수 없음(no_dcv와 같음) |
| 8 | 동겸 웹 화면 `staff.js:225-235` | "…연락을 줄여요", "줄어드는 시간 N분 · N% 절약" | 수정 필요 (동겸) | 숫자는 비용 원장의 가정 비용(같은 환자·같은 서류 연락비 1회) 계산값. 화면에 "가정 비용 기준" 표기가 없음(코드 주석에만 있음, `staff.js:187`). "가정 비용으로 계산한 예상 절약" 표기 권장. 시뮬레이션의 번들링 효과(2-1, 800분 역전)와 구분 |
| 9 | 통합본 `README.md` 2026-11-08 담당자 화면 항목 | "묶어 코디네이터 시간을 줄이는 것" | 유지 (설계 의도 문장) | 같은 항목의 "표현 규칙"이 가정 비용임을 밝힘. 발표에서 결과로 인용하지 않음 |
| 10 | 통합본 `README.md` 자동 실행 표 | "확정 (GT와 일치)", "서류 읽기 정확 32 / 틀림 0" | 수정 필요 (동겸, 발표에 쓸 때) | 여기 GT는 가상 시험 T-A~D의 규칙 GT로, 축소 범위 규칙 GT와 다름. "정확"은 합성 정답값과 읽은 값 일치 건수라 "일치 32 / 불일치 0"으로 |
| 11 | 통합본 `README.md` §5 평가 절 "정확도·Rescue…" (10-12 이전 파이프라인) | 정확도 지표 설명 | 해당 없음 | 이번 발표(DCV+C·NSCLC) 범위 밖. 인용하지 않음 |

정리: 내 문서 **삭제 1** (지역 조건 결함 문장 — 통합본에서 고쳐져 근거가 없어짐), **수정 3** (#1 조건 명시, #2 기준점 표기, 순환 라벨 표기). 남의 문서 **수정 필요 4** (#6, #7, #8, #10 → 6절).

## 3. GT 명칭 통일

공식 명칭: **축소 범위 규칙 GT (임상 전문가 미검수)**. 코드 식별자·파일명·라벨 값은 바꾸지 않았습니다.

| 문서 | 이전 표기 | 처리 |
|---|---|---|
| 내 `nsclc_eval_dataset.md` | 독립 규칙 GT 3, 독립 GT 4, 규칙 GT 2, "정답" 3 | 직접 통일. 머리에 공식 명칭 + "이 문서의 GT는 모두 이 GT" 줄임 규칙 |
| 내 `presentation_data_gt.md` | 독립 규칙 GT 1, 규칙 GT 1, 순환 GT 1, 정답 3 | 직접 통일. 순환 GT는 다른 개념이라 "엔진 순환 라벨(비교용)"으로 바꿈 |
| 내 `demo_nsclc_scenarios.md` | 규칙 GT 1, GT 9 | 직접 통일 |
| 선우 `p_common_engine_2026_11_07.md` | 독립 GT 1, 규칙 GT 2, "독립 합성 GT" | 수정 필요 목록. 단 이 문서의 GT는 NSCLC 파일럿 작성자 판독·생성기 GT라 공식 명칭 대상이 아님 → "파일럿 작성자 판독 라벨", "생성기 라벨"로 구분 권장 |
| 선우 `gt/README.md` | 독립 GT 3 | 수정 불필요. 사람 라벨링 도구(G_C·G_P·G_U)의 GT로 다른 대상. 발표에서 같은 이름을 쓰지 않도록 주의만 |
| 동겸 `README.md` 자동 실행·웹 | 규칙 GT, 정답 | 수정 필요 목록. 가상 시험 T-A~D 규칙 GT라 "가상 시험 규칙 라벨"로 구분 권장 |
| 동겸 `web_demo_flow.md` | "합성 정답에서만" | 수정 불필요(합성 값의 출처 설명) |

## 4. known_defect 2건 충돌 확인

실행: 통합본 `urgent/integration` `8afe5ea`에 `data/p0-eval-cases`의 테스트·데이터 파일만 복사(커밋 안 함), 오프라인.

| 케이스 | 4f81460 | 8afe5ea | 판정 |
|---|---|---|---|
| age20-unknown | CONFIRMED_INELIGIBLE (I1 NOT_MET) | INFO_MISSING (I1 UNKNOWN, I2 MET) | 고쳐짐 → strict xfail이 **XPASS로 실패** |
| age20-non_USA | CONFIRMED_INELIGIBLE (I1 NOT_MET) | INFO_MISSING (I1 UNKNOWN, I2 MET) | 같음 |
| age17·age20-USA 4건 | CONFIRMED_INELIGIBLE | INFO_MISSING (I1·I2 UNKNOWN 또는 I1 UNKNOWN) | 허용 상태 안 (보수적 보류) |
| age22·25 6건 | INFO_MISSING | INFO_MISSING | 변화 없음 |

- `tests/test_p0_3_region_cases.py` 결과: 4f81460 11 passed + 2 xfailed → 8afe5ea **11 passed + 2 failed (XPASS strict)**.
- 원인: 선우 `5fa4e24` fix(rules) "hold failing country-scoped structured criteria when site country is unknown" (11-08 02:28). 12케이스 결과가 내 제안 패치의 기대값(`measured_with_proposal`)과 모두 같습니다.
- **결론: 충돌 있음.** `data/p0-eval-cases`를 통합본과 합치면 실패 2건.
- 조치 제안: `known_defect` 2건을 false로 바꾸는 패치(아래, 2줄). 적용하면 8afe5ea에서 13 passed. 내 제안 패치 `docs/proposals/p0_3_region_condition.patch`는 선우 수정과 겹치므로 적용하지 않음(폐기 제안).
  - 패치 파일: 이 브랜치 `docs/proposals/p0_3_xfail_release.patch` (`data/p0-eval-cases` 브랜치 자체는 이번 규칙상 수정하지 않음)
- 참고: 17세(모든 지역에서 불충족)도 이제 확정 부적격이 아니라 INFO_MISSING입니다. 안전한 쪽이지만, 국가와 무관하게 부적격인 경우까지 보류됩니다(선우 확인 필요, 결함 아님).

### P0 사례 127건 채점 (오프라인 어댑터, 채점 스크립트만 실행)

| 유형 | 사례 | 4f81460 안전 / 오채택 / 과잉 보류 | 8afe5ea 안전 / 오채택 / 과잉 보류 | 상충 탐지 |
|---|---|---|---|---|
| held-out 6 상충 | 15 | 9 / 6 / 0 | **14 / 1 / 0** | 7/15 → **12/15** |
| held-out 6 전해 들은 값 | 10 | 7 / 3 / 0 | **10 / 0 / 0** | - |
| 상충: 같은 항목 다른 값 | 8 | 1 / 7 / 0 | 1 / 7 / 0 | - |
| 상충: 시점 차이 (과거 값) | 8 | 4 / 4 / 0 | 4 / 4 / 0 | - |
| 상충: 부정 후 번복 (서술) | 8 | 4 / 4 / 0 | 4 / 4 / 0 | 3/8 → 3/8 |
| 상충: 문서 vs 자가보고 (값) | 4 | 4 / 0 / 0 | 4 / 0 / 0 | - |
| 상충: 문서 vs 자가보고 (서술) | 4 | 0 / 4 / 0 | 0 / 4 / 0 | 0/4 → 0/4 |
| 전해 들은 값: 의료진 | 8 | 6 / 2 / 0 | **8 / 0 / 0** | - |
| 전해 들은 값: 가족 | 8 | 6 / 2 / 0 | **8 / 0 / 0** | - |
| 전해 들은 값: 기억 불확실 | 8 | 6 / 2 / 0 | **8 / 0 / 0** | - |
| 전해 들은 값: 다른 사람 값 | 8 | 6 / 2 / 0 | 6 / 2 / 0 | - |
| 정상 대조 (본인·검사·문서·최근 값) | 38 | 34 / 0 / 4 | 34 / 0 / 4 | - |
| **합계** | 127 | 87 / 36 / 4 | **101 / 22 / 4** | 10/27 → **15/27** |

- 바뀐 사례 14건은 모두 채택 → 보류·상충 방향입니다. 보류 → 채택으로 바뀐 사례는 0건, 과잉 보류는 4건 그대로입니다.
- 남은 오채택 22건: 같은 항목 다른 값 7, 시점 차이 4, 부정 후 번복 4, 문서 vs 자가보고(서술) 4, 다른 사람 값 2, held-out 상충 1.
- 건수이며 정확도가 아닙니다. 근거 확인 함수 단위 측정이고 웹·세션 전체 경로가 아닙니다.
- 결과 파일: `docs/dev/final_review_evidence/p0_fact_cases_8afe5ea.json`, `p0_fact_cases_8afe5ea_score.md`, 케이스별 상태 `p0_3_region_cases_8afe5ea.txt`

## 5. 데모 시나리오 확정

확정 흐름 문서: `docs/dev/demo_final_flow.md`. 오프라인 상세: `docs/dev/demo_nsclc_scenarios.md`.

| 이름 | 환자 · 시험 | 흐름 | 기대 상태 | 실제 결과 | 실행 환경 |
|---|---|---|---|---|---|
| W1 | DEMO-NSCLC-1 · 가상 T-A~D | 질문 고르기 → 같은 서류 묶음 요청 → 서류 확인 5 → 의사 판단 1 | T-A·T-C·T-D 참여 가능(확정), T-B 미확정 | 같음 | 웹 데모 서버(오프라인 대역), Chrome, 동겸 기록 `f1c56ef` |
| W2 | DEMO-NSCLC-4 · 가상 T-A~D | 나이 미기재 → 환자에게 나이 질문 → 재계산 | 나이 반영 재판정 | 같음 | 같음, 동겸 기록 `894747a` |
| W3 | S003 (7세) · 가상 T-A~D | 자기 보고 나이 불충족 → 나이 근거 서류 요청 유지 → 확인 | T-A~D 참여 불가(확정) | 같음 | 같음, 동겸 기록 `d20cc0d` |
| A | P052 × NCT07680790 | ECOG 진료기록 → EGFR 병리 결과지 | EXPERT_REVIEW | EXPERT_REVIEW | 오프라인 runner, `8afe5ea` 재확인 |
| B | P045 × NCT06928389 | 자기 보고 ECOG 2 → 진료기록 확인 | CONFIRMED_INELIGIBLE | CONFIRMED_INELIGIBLE | 같음 |
| C | P058 × NCT07416058 (P061에서 교체) | I6 "모름" → 처방 목록 | INFO_MISSING | INFO_MISSING | 같음 |
| D | DEMO-REGION × NCT06216301 | 20세·국가 미상 | 확정하지 않음 | **INFO_MISSING** (4f81460에서는 CONFIRMED_INELIGIBLE) | 오프라인 판정기 |

- W1~W3 실제 결과는 동겸 기록이며 이번에 브라우저로 다시 확인하지 않았습니다. W1 기록은 담당자 화면 개편(`721fcf7`·`1e47a71`)·보류 표시 변경(`4dcf8ae`) 이전이라 통합본에서 리허설 확인이 필요합니다.
- 같은 6000분 실행 집계: 판단 대기 적격 → EXPERT_REVIEW 20/23, 확정 부적격 ∧ 규칙 GT 부적격 124/130, 거짓 확정 0, 확정 적격 0. 최종 상태 INFO_MISSING 92 → 91, VERIFICATION_PENDING 4 → 5 (나머지 같음).

### 엔진 관찰 2건

| 관찰 | 4f81460 | 8afe5ea | 결론 |
|---|---|---|---|
| E12 PD-1/PD-L1 치료력 → `biomarker:PD-L1`로 잡힘 | 발생 | `criterion:NCT06216301:E12` 64건, `biomarker:PD-L1` 0건 | 고쳐짐 (`173cd3f`) |
| 남성 환자에게 임신 여부 질문 (E16) | 발생 (P061) | 남성 47명 중 0건 | 고쳐짐 (`d03c39e`) |

### 발표 흐름 (요약, 상세는 `demo_final_flow.md`)

1. 웹 W1 메인: 환자 신청 → 담당자 질문 고르기(묶음, **가정 비용**) → 서류 확인 → 의사 판단 → T-A·C·D 확정, T-B 미확정 설명
2. 오프라인 보조 A: 실제 프로토콜 평가셋에서 판단 기준 외 확인 후 담당의 검토 (20/23, 한 번 실행)
3. 오프라인 보조 B: 자기 보고만으로 확정하지 않고 기록 확인 후 확정 (거짓 확정 0)
4. 시연에서 뺌: D(한계·수정 사례 슬라이드만), C(질문 대비), W1의 T-B 확정 장면
5. 백업: 녹화본(리허설 때 녹화 필요) → `run_e2e_synthetic.py --mode offline` 표 → 오프라인 A·B 슬라이드

## 6. 수정 필요 목록 (남의 문서·코드, 보고만)

### 선우

| # | 위치 | 내용 | 제안 |
|---|---|---|---|
| S1 | `data/p0-eval-cases` 병합 시 | strict xfail 2건이 통합본 `8afe5ea`에서 XPASS로 실패 | `docs/proposals/p0_3_xfail_release.patch`(2줄) 적용 후 병합. 내 `p0_3_region_condition.patch`는 `5fa4e24`와 겹쳐 폐기 |
| S2 | `docs/dev/p_common_engine_2026_11_07.md` 표 열 | False Eligible·False Ineligible·확정 Eligible 정확도 | 발표용으로는 "GT와 다른 확정 적격/부적격"으로. 임상 오분류로 읽힘 |
| S3 | 같은 문서 §6 | "200분에서는 dcvc가 기준선보다 확인된 부적격이 많습니다" | 800분 역전, seed 수, 구간 없음, no_dcv = dcvc를 같은 문단에 |
| S4 | 같은 문서·`p_results/` | ablation 결과가 `3e4b2fd`(11-07) 기준. 그 뒤 P0-B·지역 조건·E12·성별 수정이 들어감 | 발표에 ablation 수치를 쓸 거면 통합본 기준 재실행 결과 위치를 알려 주기 (이번 검수에서는 위치 미확인) |
| S5 | 같은 문서 GT 표기 | "독립 GT", "독립 합성 GT", "규칙 GT" | 파일럿은 "작성자 판독 라벨", 생성기는 "생성기 라벨"로 구분. 공식 명칭(축소 범위 규칙 GT)은 NSCLC 평가셋 GT 전용 |
| S6 | 17세 국가 미상 케이스 | `5fa4e24` 뒤 모든 지역에서 불충족인 17세도 INFO_MISSING | 안전한 쪽이라 결함 아님. 의도인지 확인만 |

### 동겸

| # | 위치 | 내용 | 제안 |
|---|---|---|---|
| D1 | 웹 담당자 화면 `static/staff.js:225-235` | "연락을 줄여요", "줄어드는 시간 · N% 절약"에 가정 비용 표기 없음 | 숫자 옆에 "가정 비용 기준 예상값" 표기. 시뮬레이션의 번들링 효과와 구분 (800분 역전) |
| D2 | `README.md` 자동 실행 결과 표 | "확정 (GT와 일치)", "서류 읽기 정확 32 / 틀림 0" | 가상 시험 T-A~D 규칙 라벨임을 밝히고 "일치 32 / 불일치 0"으로. 축소 범위 규칙 GT와 다른 GT |
| D3 | 웹 데모 시나리오 이름 | W1~W3 번호가 저장소에 없음 | 이 문서 5절의 W1~W3 대응(README 브라우저 확인 기록 기준)이 맞는지 확인 |
| D4 | 데모 흐름 | DEMO-NSCLC-1의 T-B(EGFR)가 오프라인 대역에서 미확정 | 시연에서 T-B를 "LLM 판정 기준, 오프라인 데모에서는 미확정"으로 설명하거나 T-A·C·D만 보여 주기 |


## 7. 이 검수에서 바꾼 것 (docs/presentation-data-gt만)

| 파일 | 변경 |
|---|---|
| `docs/dev/presentation_data_gt.md` | 최종본: 슬라이드 6장, 명칭 통일, 수치 최신화, 지역 조건 결함 문장 삭제, 한계 슬라이드 확장 |
| `docs/dev/demo_nsclc_scenarios.md` | 8afe5ea 재확인 반영 (C 교체, D 갱신, 엔진 관찰 고쳐짐), 명칭 통일 |
| `docs/dev/nsclc_eval_dataset.md` | 명칭 통일만 (수치 변경 없음) |
| `docs/dev/demo_final_flow.md` | 신규: 확정 데모 흐름 |
| `docs/dev/final_review_2026-11-08.md` | 신규: 이 문서 |
| `docs/dev/final_review_evidence/` | 확인 실행 결과 (데모 재확인·쌍별 기록·P0 채점·지역 조건 12케이스) |
| `docs/dev/final_review_scripts/` | 대조·집계 스크립트 (엔진 코드 변경 없음, 읽기·실행만) |
| `docs/proposals/p0_3_xfail_release.patch` | `data/p0-eval-cases`용 xfail 해제 패치 (적용하지 않음) |

재현
```bash
# 통합본 worktree에 data/p0-eval-cases의 tests/data/p0_3_region_cases.json, tests/test_p0_3_region_cases.py, scripts/*p0_fact*, data/eval/p0_fact_cases 복사 (커밋 안 함)
export PYTHONPATH=$PWD/src PYTHONIOENCODING=utf-8 ANTHROPIC_API_KEY=
python -m pytest -q tests/test_p0_3_region_cases.py                       # 8afe5ea: 11 passed, 2 failed (XPASS strict)
python scripts/p0_fact_adapter_offline.py --tag 8afe5ea --out p0.json && python scripts/score_p0_fact_cases.py --results p0.json --md p0.md
python docs/dev/final_review_scripts/demo_with_final.py $PWD <out_dir> 8afe5ea   # scripts/demo_nsclc_scenarios.py 필요, 약 10분
```
