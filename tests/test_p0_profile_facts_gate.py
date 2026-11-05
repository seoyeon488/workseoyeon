"""미해결 P0 재현: profile_facts 저장 관문이 미인식 무응답을 막지 못함 (docs/dev/wp7_answer_outcome.md §4).

xfail 테스트는 **원하는 안전 동작**을 단언합니다. 지금은 실패하는 것이 정상이며 통과로 집계되지 않습니다.
strict라서 관문을 고치면 XPASS 실패가 나므로, 그때 표시를 지우고 일반 테스트로 바꿉니다.
프로필러 출력은 스크립트로 고정합니다(LLM 호출 없음). 실제 LLM에서의 발생 빈도는 검증하지 않았습니다.
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import decision_fixtures as d  # noqa: E402
from test_engine_policy import PA  # noqa: E402
from test_profile_facts import _profile  # noqa: E402

from ctrec.agents import matcher  # noqa: E402
from ctrec.decision_state import build_state  # noqa: E402
from ctrec.engine import contracts as C  # noqa: E402
from ctrec.engine.cohort_state import CohortState  # noqa: E402
from ctrec.fact_store import FactStore  # noqa: E402
from ctrec.profile_facts import ingest_profile  # noqa: E402
from ctrec.schemas import Fact, LabValue, QAPair, RuleMeta  # noqa: E402

PID = "SYN-PA"
UNRECOGNIZED = ["모름. 기억 안 남", "모르겠어요, 기억이 안 나요", "글쎄요", "글쎄요, 잘 기억이 안 나네요"]
# qa_pairs 관문은 integration/dcvc(PR #7)에 있고 PR #10 기준 브랜치에는 없음. 두 트리 모두에서 돌도록 있을 때만 넘김
HAS_GATE = "qa_pairs" in inspect.signature(ingest_profile).parameters
EMPTY = dict(age=None, age_value=None, age_unit=None, sex="unknown", primary_diagnosis=None, disease_stage=None,
             diagnoses=[], biomarkers=[], labs=[], medications=[], treatment_history=[], ecog=None, other_facts=[],
             missing_or_ambiguous=[])
SELF_REPORT_HB = {"I4": RuleMeta(required_evidence="self_report_ok")}


def p0(reason):
    return pytest.mark.xfail(strict=True, raises=AssertionError, reason=f"P0 미해결: {reason}")


@pytest.fixture(autouse=True)
def stub_llm(monkeypatch):
    monkeypatch.setattr(matcher.llm, "structured", d.unknown_llm)


def _ingest(answer, **profile):
    raw = f"환자 기록.\n\n[추가 확인 정보 - 라운드 1]\nQ: 확인 질문\nA: {answer}"
    qa = [QAPair(round=1, question_id="Q1", question="확인 질문", answer=answer, purpose="eligibility",
                 target=["T1:I1"], session_id="S1")]
    store = FactStore()
    ingest_profile(store, _profile(**{**EMPTY, **profile}).model_copy(update={"patient_id": PID}), raw_text=raw,
                   session_id="S1", **({"qa_pairs": qa} if HAS_GATE else {}))
    return store, raw, qa


def _status(store, raw, qa, rules, meta=None):
    v = d.view({"T1": d.trial("T1", rules, meta=meta)}, store, source_text=raw, patient=PID, qa=qa)
    return CohortState.from_decision_states({PA: build_state(v)}).pairs()[0].status


def _hb(answer):
    return _ingest(answer, labs=[LabValue(name="Hb", value=11.0, unit="g/dL", date="2026-09-01", source_quote=answer)])


# ------------------------------------------------------------ 7e: 미인식 무응답의 추출값이 저장됨
@p0("미인식 무응답에서 추출한 값이 저장됨 (non_answer 범위 밖)")
@pytest.mark.parametrize("answer", UNRECOGNIZED)
def test_p0_extraction_quoting_an_unrecognized_non_answer_is_not_stored(answer):
    store, _, _ = _ingest(answer, other_facts=[Fact(description=f"EGFR status: {answer}", date=None, source_quote=answer)])
    assert store.facts(PID, "other_fact") == []


# ------------------------------------------------------------ 7h: 저장된 값이 확정 적격까지 이어짐 (저장소 직접 주입 없음)
@p0("미인식 무응답의 값이 자기 보고 허용 기준을 충족해 CONFIRMED_ELIGIBLE이 됨")
@pytest.mark.parametrize("answer", UNRECOGNIZED)
def test_p0_unrecognized_non_answer_never_reaches_confirmed_eligible(answer):
    store, raw, qa = _hb(answer)
    assert _status(store, raw, qa, [d.HB], SELF_REPORT_HB) != C.PairStatus.CONFIRMED_ELIGIBLE


# ------------------------------------------------------------ 같은 뿌리의 다른 경로: 단일 값 필드에는 인용이 없음
@p0("단일 값 필드는 인용이 없어 관문이 볼 것이 없음 (인식되는 무응답도 통과, non_answer 확장으로 막히지 않음)")
@pytest.mark.parametrize("answer", ["글쎄요", "잘 모르겠어요"])
def test_p0_scalar_value_without_a_quote_never_reaches_confirmed_eligible(answer):
    store, raw, qa = _ingest(answer, age=60, age_value=60, age_unit="years")
    assert _status(store, raw, qa, [d.AGE]) != C.PairStatus.CONFIRMED_ELIGIBLE


# ------------------------------------------------------------ 대조군 (일반 테스트): 재현이 입력 탓이 아님을 보임
@pytest.mark.skipif(not HAS_GATE, reason="qa_pairs 관문은 integration/dcvc에 있음")
def test_control_recognized_non_answer_with_a_quote_is_withheld():
    store, raw, qa = _hb("잘 모르겠어요")
    assert store.facts(PID, "lab:hemoglobin") == []
    assert _status(store, raw, qa, [d.HB], SELF_REPORT_HB) == C.PairStatus.INFO_MISSING


def test_control_real_self_report_is_confirmed_and_record_required_rule_stays_pending():
    store, raw, qa = _hb("Hb는 11이에요")
    assert _status(store, raw, qa, [d.HB], SELF_REPORT_HB) == C.PairStatus.CONFIRMED_ELIGIBLE
    assert _status(store, raw, qa, [d.HB]) == C.PairStatus.VERIFICATION_PENDING  # 기록 필요 기준은 자기 보고로 확정 안 됨
