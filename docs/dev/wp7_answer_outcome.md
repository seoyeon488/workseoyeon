# WP7 감사 기록의 공통 응답 판별 (WP5 연동)

선행 의존: PR #10 (`feat/wp5-item-level-failure`). `engine/answers.py`, `contracts.NO_ANSWER`, `failure_scope`가 거기에 있습니다.

## 1. 판별과 결과

| 답 또는 관찰 | 판별 주체 | ActionOutcome | 범위 |
|---|---|---|---|
| 정상 답변 | `answer_outcome` | `succeeded`, `error_code=None` | 없음 |
| "모름", "잘 모르겠어요", "기억이 안 나요", 빈 답, 거부 | `answer_outcome` | `no_response`, `no_answer` | 항목 |
| 연락 불가 | 실행기가 관찰 | `no_response` 또는 `failed`, `unreachable` | 정보원 |
| 확인 자체를 거부 | 실행기가 관찰 | `no_response` 또는 `failed`, `declined_all` | 정보원 |

- 답 내용만으로는 연락 불가와 전체 거부를 알 수 없습니다. 실행기가 관찰했을 때만 `StepObservation.error_code`로 넘깁니다.
- `declined`는 위 세 코드만 받습니다. 모르는 코드는 정책에서 정보원 단위가 되므로 `ObservationError`입니다.
- 오프라인 실행기는 연락 불가를 관찰하지 않으므로 실제 실행에서 `unreachable`이 나오는 경로는 아직 없습니다.

## 2. 사실 집계와 진단

기록은 관찰을 고치지 않습니다. 사실을 지우지 않고, 판정의 인용도 바꾸지 않습니다. 행동의 결과로 세는지만 결정합니다.

| 답변 사실의 인용 | 행동 결과 집계 | 진단 (`warning`) |
|---|---|---|
| 무응답 (`non_answer`) | 안 함 | `decline_marker_fact` |
| 불확실 (E9 `hedged`) | 안 함 | `uncertain_answer_fact` |
| 그 외, 출처가 질문과 일치 | 함 | 없음 |

`MET`·`NOT_MET` 판정이 이런 사실을 인용하면 `criterion_cites_unreliable_answer`를 남기고, `detail`에 `quote:non_answer` 또는 `quote:uncertain`을 적습니다. 새 사실뿐 아니라 스냅샷 전체를 봅니다. `UNKNOWN`은 판정이 아니므로 남기지 않습니다.

## 3. 혼합 답변의 보수적 동작

판별 단위는 답 전체가 아니라 **사실의 인용**입니다.

| 답 | 인용 | 결과 |
|---|---|---|
| 손목 수술은 했는데 종류는 몰라요 | 답 전체 | 세지 않음, `uncertain_answer_fact` |
| 손목 수술은 했는데 종류는 몰라요 | 손목 수술은 했는데 | 셈 |

첫 경우는 사실이 섞여 있어도 세지 않습니다. 사실은 저장소에 그대로 남고 진단으로 확인할 수 있습니다. 이 동작은 `tests/test_answer_outcome_records.py`가 고정합니다.

답 전체 분류는 그대로입니다. "글쎄요"와 "모름. 기억 안 남"은 `non_answer`가 인식하지 못해 `succeeded`로 기록됩니다.

## 4. 미해결 P0: profile_facts 저장 관문

**상태: 미해결.** 이 문서의 감사 진단은 위험을 기록할 뿐 막지 않습니다. 사실 저장과 적격 판정은 달라지지 않습니다.

**수정 담당: profile_facts 소유자와 협의 필요.**

**재현 (LLM 호출 없음):** `tests/test_p0_profile_facts_gate.py`. 원하는 안전 동작을 단언한 `xfail(strict=True)` 테스트이며 통과로 집계되지 않습니다. 관문을 고치면 XPASS 실패가 나므로 그때 표시를 지웁니다.

- **스텁:** 프로필러 출력은 `PatientProfile`로 고정하고, 매처 LLM은 `decision_fixtures.unknown_llm`입니다.
- **원문:** `환자 기록.\n\n[추가 확인 정보 - 라운드 1]\nQ: 확인 질문\nA: <답>`
- **답:** `모름. 기억 안 남`, `모르겠어요, 기억이 안 나요`, `글쎄요`, `글쎄요, 잘 기억이 안 나네요`

| # | 입력 | 원하는 결과 | 현재 결과 |
|---|---|---|---|
| A | `other_facts`, 인용 = 답 | 저장 안 됨 | 저장됨 |
| B | `labs`의 Hb 11.0, 인용 = 답, 기준 `Hb >= 9` + `self_report_ok` | `CONFIRMED_ELIGIBLE` 아님 | `CONFIRMED_ELIGIBLE` |
| C | `age=60`(인용 없음), 답 = `글쎄요` 또는 `잘 모르겠어요`, 기준 `Age >= 18` | `CONFIRMED_ELIGIBLE` 아님 | `CONFIRMED_ELIGIBLE` |

**대조군 (일반 테스트):**
- 같은 B 입력에 인식되는 `잘 모르겠어요`를 넣으면 보류되어 `INFO_MISSING`입니다.
- 실제 답 `Hb는 11이에요`는 `CONFIRMED_ELIGIBLE`이고, 기록 필요 기준에서는 `VERIFICATION_PENDING`입니다.

**원인과 범위:**
- A·B: `_link_answer`의 보류가 `non_answer`에만 의존합니다.
- C: 단일 값 필드(`age`, `sex`, `ecog`, `primary_diagnosis`, `disease_stage`)는 추출 경로에 인용이 없어 관문이 볼 대상이 없습니다. 인식되는 무응답도 통과하므로 `non_answer`를 넓혀도 막히지 않습니다.
- 평가기는 인용문을 보지 않습니다. 기록 필요 기준은 자기 보고로 확정되지 않아 이 경로에서 `VERIFICATION_PENDING`에 머뭅니다.

**검증하지 않은 것:**
- 실제 LLM 발생 빈도. 위험은 프로필러가 "글쎄요" 같은 답에서 값을 지어낼 때만 실현됩니다.
- B의 `self_report_ok` Hb는 재현용 설정이며, 실제 시험의 기준 메타데이터에 같은 조합이 있는지는 확인하지 않았습니다.
- C의 값이 답변에서 왔는지 처음 입력에서 왔는지는 저장된 사실로 구분되지 않습니다.
