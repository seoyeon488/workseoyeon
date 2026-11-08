# NSCLC 오프라인 데모 시나리오 A~D

작성: 서연 (데이터) · 2026-11-08 · 최종 재확인: 통합본 `urgent/integration` `8afe5ea` (21시 검수)
데이터: `data/nsclc/eval` (240쌍) · 실행: #20 runner, full_dcvc, 6000분, horizon 80, seed 1, 오프라인(LLM 0회)
실행 기록: `docs/dev/final_review_evidence/demo_scenarios_8afe5ea.json`, `demo_pairs_8afe5ea.json` (이전 `data/nsclc/eval/checks/demo_scenarios_4f81460.json`)
확정 발표 흐름: `docs/dev/demo_final_flow.md` · 최종 통합본 `integration/phase1-final`의 같은 이름 문서가 기준이며, 이 파일은 21시 판에 23시 정정만 더한 것입니다

> 합성 환자입니다(실제 환자 아님). **데이터 검증 완료 / 임상 검수 미완료.** 이 문서의 GT는 **축소 범위 규칙 GT (임상 전문가 미검수)**이며 아래에서 "규칙 GT"로 줄여 씁니다. 웹·엔진 코드는 바꾸지 않았습니다.

| # | 환자 × 시험 | 보여 줄 것 | 규칙 GT 라벨 | 4f81460 | 8afe5ea | 판정 |
|---|---|---|---|---|---|---|
| A | P052 × NCT07680790 | 판단 기준 외 확인을 마치고 담당의 검토로 넘어감 | 전문가 판단 대기 적격 | EXPERT_REVIEW | EXPERT_REVIEW | ✓ |
| B | P045 × NCT06928389 | 자기 보고 ECOG 2를 진료기록으로 확인한 뒤 부적격 확정 | 부적격 | CONFIRMED_INELIGIBLE | CONFIRMED_INELIGIBLE | ✓ |
| C | **P058 × NCT07416058** (변경) | 환자가 "모름" → 투약 목록 요청은 처리됐지만 새 사실 0 → 확정하지 않음 | 미평가 (범위 안 미연결 기준) | INFO_MISSING | INFO_MISSING | ✓ (확정하지 않음) |
| D | DEMO-REGION × NCT06216301 | 지역 조건: 국가를 모르면 확정하지 않음 | 미평가 (지역 조건) | CONFIRMED_INELIGIBLE ✗ | **INFO_MISSING** | ✓ (선우 `5fa4e24`로 고쳐짐) |

- C 변경 사유: 이전 C(P061 × NCT06216301)의 "PD-L1 모름 → 병리 결과지" 흐름은 엔진 수정(`173cd3f`, E12 확인 항목) 뒤 더 나오지 않습니다. P061의 새 "모름 → 서류" 흐름은 I10(피임 동의, excluded)과 I8(기준값 없음, 미연결)이라 데모에 맞지 않습니다. 같은 선택 규칙(`scripts/demo_nsclc_scenarios.py`)이 고른 P058로 바꿨습니다. P061 × NCT06216301의 최종 상태는 여전히 INFO_MISSING입니다.

---

## A. 판단 대기 적격 — P052 × NCT07680790 (EGFR 변이 비편평 NSCLC 시험)

**초기 입력 (공개 값):** 69세 남성. 백금 항암제 없음, docetaxel 없음, anti-PD-1/PD-L1 치료 있음. 4주 내 다른 임상시험 약 없음, 큰 수술 없음

| 항목 | 정보원 | 실제 값 (숨긴 값) | 8afe5ea 실행 기록 |
|---|---|---|---|
| ECOG | 진료기록 | 1 | step 22 REQUEST_DOCUMENT medical_record → 성공 |
| EGFR 변이 | 병리 결과지 (환자가 모르는 항목) | exon 19 결실/L858R | step 402 REQUEST_DOCUMENT pathology_report → 성공 |
| 조직형 | 진료기록 | 선암 | step 408 시점에 이미 EXPERT_REVIEW |

**상태 변화:** INFO_MISSING → (ECOG·EGFR·조직형 확인) → **EXPERT_REVIEW**

**규칙 GT 근거 (`rule_gt.csv`)**

| 기준 | 원문 | 규칙 GT |
|---|---|---|
| I1 | "Participants must have histologically or cytologically confirmed non-squamous NSCLC" | PASS (선암) |
| I3 | "Participants must have documented EGFR-TKI-sensitizing mutation (exon 19 deletion or exon 21 L858R substitution)" | PASS |
| I5 | "Participants must have ECOG Performance Status 0-1" | PASS (1) |
| I6·I7 | 구조화 항목 18세 이상·성별 제한 없음 | PASS |
| I2 | "... or recurrent disease not amenable to curative surgery or definitive radiotherapy ..." | NEEDS_EXPERT |
| E3 | "Participants must not have clinically significant cardiac disease" | NEEDS_EXPERT |

데모 문구: "판단 기준 외 확인 완료. 담당의 판단 2건(병기·치료 적합성, 심장 질환) 대기". 확정 적격으로 표시하지 않습니다.

## B. 부적격 확정 — P045 × NCT06928389 (백금·PD-1/L1 치료 후 2차 시험)

**초기 입력 (공개 값):** 57세 남성, ECOG 2 (자기 보고·미검증), 백금 항암제 있음, docetaxel 없음, 큰 수술 없음

| step (8afe5ea) | 행동 | 결과 |
|---|---|---|
| 1440 | E1 소세포암 여부 진료기록 요청 | 연락 불가 (실패) |
| 1441 | I9 PD-1/L1 치료력 환자 질문 | 응답 |
| 1726 | ECOG 근거 진료기록 요청 (`basis:ecog`) | 성공 → **VERIFICATION_PENDING → CONFIRMED_INELIGIBLE** |

**규칙 GT 근거:** I4 "Eastern Cooperative Oncology Group (ECOG) performance status of 0 or 1." → ecog=2 FAIL. 이 환자의 다른 두 시험(NCT07416058, NCT07680790)도 같은 ECOG 기준으로 확정 부적격입니다.

데모 문구: "ECOG 2 (진료기록 확인) - 기준 0-1 불충족으로 부적격 확정". 자기 보고만으로는 확정하지 않다가 기록 확인 뒤 확정하는 흐름입니다.

## C. 값을 얻지 못하면 확정하지 않음 — P058 × NCT07416058 (드라이버 변이 대상 시험)

**초기 입력 (공개 값):** 63세 여성, anti-PD-1/PD-L1 치료 있음, 큰 수술 없음

| step (8afe5ea) | 행동 | 결과 |
|---|---|---|
| 61 | 병리 결과지 요청 (드라이버 변이) | 성공 |
| 69 | 환자 질문: I6 "a 2-week washout period is required for prior TKI therapy or chemotherapy" (마지막 항암 시점) | **환자 "모름"** (no_answer) |
| 1840 | 투약 목록 요청 (I6) | 처리됨(succeeded)이지만 **새 사실 0** — I6은 여전히 미확인 (phase1-final 기록 step 1837) |

**상태 변화:** INFO_MISSING 유지
- 이 시험에는 범위 안 미연결 기준(I7 "Prior immunotherapy is not permitted.", I8 PD-L1 TPS 중앙 검사, E14·E15 임신·수유)이 남아 있습니다.
- I6 값도 끝내 얻지 못했고, 미연결 기준도 남아 있어 확정하지 않는 것이 맞습니다. 규칙 GT도 NOT_EVALUATED입니다.

데모 문구: "확인하지 못한 항목과 원문만으로 판정할 수 없는 항목이 남아 확정하지 않습니다". **"모르는 값을 서류로 확보했다"고 말하지 않습니다.**
- 정정 (23시): 21시 판에서 "처방 목록으로 확보"라고 쓴 것은 행동 결과(succeeded)만 보고 쓴 오류였습니다. 통합본 `docs/dev/demo_nsclc_scenarios.md`의 기록대로 새 사실은 0건입니다. 240쌍 전체에서 "모름 → 같은 항목 서류 → 새 값 확보"인 쌍은 0개입니다(통합본 문서).
- 주의: P058은 합성 값상 공개 항목 `repro.pregnant_or_breastfeeding = yes`(63세)인 합성 생성 결과입니다. 데모에서는 I6 흐름만 보여 줍니다.

## D. 지역 조건 — DEMO-REGION × NCT06216301 (평가셋 밖 데모 환자)

- 평가셋 240쌍에는 NCT06216301 후보 중 22세 미만 환자가 없어 이 경우가 생기지 않습니다. P0-3 회귀 케이스(`tests/data/p0_3_region_cases.json`, branch `data/p0-eval-cases`)의 환자를 씁니다.
- **초기 입력:** 20세 여성, 국가 미상 (나이·성별 문서 확인됨)
- **원문:** "≥22 years of age in the USA / ≥18 years of age outside of the USA."

| | 상태 |
|---|---|
| 규칙 GT 기대 | NOT_EVALUATED (I1 지역 조건부, 국가를 모름) |
| `4f81460` | CONFIRMED_INELIGIBLE (I1 NOT_MET) — 결함 |
| `8afe5ea` | **INFO_MISSING (I1 UNKNOWN, 불충족 근거 없음)** — 확정하지 않음 |

- 통합본에서는 정상 동작으로 보여 줄 수 있습니다. 다만 평가셋 밖 환자이고 웹 화면 경로가 아니라 오프라인 판정기 결과입니다.

## 엔진 관찰 2건 (8afe5ea에서 다시 확인)

| 관찰 | 4f81460 | 8afe5ea | 결론 |
|---|---|---|---|
| NCT06216301 E12(PD-1/PD-L1 **치료력** 12개월)의 확인 항목 | `biomarker:PD-L1` | `criterion:NCT06216301:E12` (64건 모두) | 고쳐짐 (`173cd3f` E12 info key) |
| 남성 환자에게 E16 임신·수유 확인 행동 | P061 등에서 발생 | 0건 (남성 47명 전체) | 고쳐짐 (`d03c39e` 성별로 해당 없음 판정) |

출처: `docs/dev/final_review_evidence/runner_6000m_h80_8afe5ea_from_demo.json` (`obs_e12_info_keys`, `obs_pregnancy_actions_for_male`)

## 재현

```bash
export PYTHONPATH=$PWD/src PYTHONIOENCODING=utf-8 ANTHROPIC_API_KEY=
python scripts/demo_nsclc_scenarios.py --out <out>.json        # 약 10분
python docs/dev/final_review_scripts/demo_with_final.py $PWD <out_dir> <tag>   # 같은 실행 + 쌍별 집계·엔진 관찰
```
