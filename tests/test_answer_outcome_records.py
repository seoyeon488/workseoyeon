"""WP5 공통 응답 판별기의 WP7 연동: 답 -> ActionOutcome -> 정책 -> DecisionRecord가 한 결과로 이어지는지. API 호출 없음."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import decision_fixtures as d  # noqa: E402
from bench_incremental import load_frozen  # noqa: E402
from decision_scenarios import load_trials  # noqa: E402
from test_engine_policy import PA, _ask, _state_missing  # noqa: E402
from test_record_producer import BEFORE, Facts, PS, cohort, crit, obs, pair  # noqa: E402

from ctrec import offline_records as orc  # noqa: E402
from ctrec.agents import matcher  # noqa: E402
from ctrec.decision_state import DECLINED_ANSWERS  # noqa: E402
from ctrec.engine import answers, audit  # noqa: E402
from ctrec.engine import contracts as C  # noqa: E402
from ctrec.engine import record_producer as rp  # noqa: E402
from ctrec.engine.answers import answer_outcome  # noqa: E402
from ctrec.engine.cohort_state import CohortState  # noqa: E402
from ctrec.engine.policy import LegacyAdapterPolicy  # noqa: E402
from ctrec.eval_hygiene import AliasMap, ScopedOracleAnswerer, load_cases_hygienic  # noqa: E402

NON_ANSWERS = (*sorted(DECLINED_ANSWERS), "모름.", "  ", "\n", "모름(답변 없음)", "모름 (기록에 없음)", "잘 모르겠어요",
               "기억이 안 나요", "기억 안 나요", "답변 거부", "답변하지 않겠습니다", "말하고 싶지 않아요", "확인 불가",
               "N/A", "Unknown")
ANSWERS = ("네", "아니요", "ECOG 1이에요", "BCG 치료를 거부했습니다", "모르핀을 복용 중입니다")

PARSED = load_frozen()
ALL = load_trials()
TRIALS = {t: ALL[t] for t in PARSED}
CASES = ["M-SYN-DEMO-A-DEMO-LUNG-001-rescue-1", "M-SYN-DEMO-B-DEMO-LUNG-001-cleanup-1"]


def _load():
    amap = AliasMap(salt="t")
    for c in CASES:
        amap.alias(c)
    return load_cases_hygienic(PARSED, only=CASES, alias_map=amap)


def _offline(tmp_path, monkeypatch=None, answer=None):
    """오프라인 실행. answer를 주면 답변 대역이 그 답만 돌려줌 (이후 사실 추출·매칭·기록은 실제 경로)."""
    if monkeypatch is not None:
        monkeypatch.setattr(ScopedOracleAnswerer, "answer", lambda self, qs, pid: {q.question_id: answer for q in qs})
    hcs, _, sc = _load()
    return [orc.record_case(hc, TRIALS, sc, tmp_path / f"c{i}") for i, hc in enumerate(hcs)]


def _ops(r):
    return r.final_cohort.ops[r.rounds[0].action.patient_alias]


# ------------------------------------------------------------ 표현별 동일 분류
@pytest.mark.parametrize("text", [*NON_ANSWERS, None])
def test_every_non_answer_gets_one_classification_from_every_detector(text):
    assert answer_outcome(text) == ("no_response", C.NO_ANSWER)
    assert rp.is_declined(text) is True
    assert C.failure_scope(*answer_outcome(text)) == "item"


@pytest.mark.parametrize("text", ANSWERS)
def test_real_answers_succeed(text):
    assert answer_outcome(text) == ("succeeded", None) and rp.is_declined(text) is False
    assert C.failure_scope(*answer_outcome(text)) is None


# ------------------------------------------------------------ 생산기: 판별 결과 -> ActionOutcome
@pytest.mark.parametrize("text", ["모름", "잘 모르겠어요", "기억이 안 나요", "답변 거부"])
def test_no_answer_record_is_item_level_and_adds_no_fact(text):
    f = Facts()
    marker = f.add_answer("other", text, text)
    r = rp.build_step(obs(execution="declined", facts=f, after=BEFORE))
    o = r.record.outcome
    assert (o.status, o.error_code) == answer_outcome(text) and C.failure_scope(o.status, o.error_code) == "item"
    assert r.record.facts_added == () and o.new_fact_ids == ()
    assert [(i.code, i.fact_ids) for i in r.issues] == [("decline_marker_fact", (marker,))]


@pytest.mark.parametrize("code", sorted(C.SOURCE_FAILURE_CODES))
@pytest.mark.parametrize("execution,status", [("declined", "no_response"), ("failed", "failed")])
def test_source_failures_stay_source_level_in_the_record(execution, status, code):
    o = rp.build_step(obs(execution=execution, error_code=code, after=BEFORE)).record.outcome
    assert (o.status, o.error_code) == (status, code) and C.failure_scope(o.status, o.error_code) == "source"
    assert o.new_fact_ids == ()


def test_producer_rejects_codes_that_would_change_the_failure_scope():
    with pytest.raises(rp.ObservationError, match="declined_error_code_unknown"):
        rp.build_step(obs(execution="declined", error_code="something_else", after=BEFORE))
    with pytest.raises(rp.ObservationError, match="error_code_without_failure"):
        rp.build_step(obs(execution="answered", error_code=C.NO_ANSWER))


def test_answered_step_succeeds_with_its_attributed_fact():
    f = Facts()
    fid = f.add_answer("smoker", True, "smoker")
    o = rp.build_step(obs(facts=f)).record.outcome
    assert (o.status, o.error_code, o.new_fact_ids) == ("succeeded", None, (fid,))


def test_answer_fact_quoting_only_a_non_answer_is_not_a_result_even_on_an_answered_step():
    """답에 사실이 있어도("EGFR는 모름, ECOG는 1") 인용이 "모름"뿐인 사실은 행동의 결과가 아님. 지우지 않고 진단에 남김."""
    f = Facts()
    real = f.add_answer("ecog", 1, "ECOG는 1")
    marker = f.add_answer("egfr", True, "모름")
    r = rp.build_step(obs(facts=f))
    assert r.record.outcome.status == "succeeded" and r.record.outcome.new_fact_ids == (real,)
    assert [(i.code, i.fact_ids) for i in r.issues] == [("decline_marker_fact", (marker,))]


def test_answer_fact_without_a_quote_stays_attributed_by_its_source_ref():
    f = Facts()
    fid = f.add_answer("smoker", True, None)
    assert rp.build_step(obs(facts=f)).record.facts_added == (fid,)


# ------------------------------------------------------------ 정책과의 일관성
def _ops_after(error_code):
    co = CohortState.from_decision_states({PA: _state_missing()})
    pol = LegacyAdapterPolicy()
    a = _ask(pol, co, "ecog")
    return pol.apply_outcome(co, a, C.ActionOutcome(action_id=a.action_id, status="no_response",
                                                    error_code=error_code))[0].ops[PA]


def test_item_and_source_failures_reach_the_policy_at_different_scopes(monkeypatch):
    monkeypatch.setattr(matcher.llm, "structured", d.unknown_llm)  # _state_missing의 매칭은 LLM 대역으로
    status, code = answer_outcome("기억이 안 나요")
    assert status == "no_response"
    ops = _ops_after(code)
    assert ops.failed_sources == frozenset() and ops.failed_items == frozenset({("patient_interview", "ecog")})
    for source_code in C.SOURCE_FAILURE_CODES:
        ops = _ops_after(source_code)
        assert ops.failed_sources == frozenset({"patient_interview"}) and ops.failed_items == frozenset()


# ------------------------------------------------------------ 오프라인 실행: 판별 한 번 -> 정책·기록 일치
@pytest.mark.parametrize("answer", ["모름", "모름(답변 없음)", "잘 모르겠어요", "기억이 안 나요", "", "답변 거부"])
def test_offline_non_answers_are_recorded_as_item_failures(tmp_path, monkeypatch, answer):
    for r in _offline(tmp_path, monkeypatch, answer):
        assert r.complete and r.steps
        assert _ops(r).failed_sources == frozenset() and _ops(r).failed_items
        for s, rd in zip(r.steps, r.rounds):
            o = s.record.outcome
            assert (o.status, o.error_code, o.new_fact_ids) == ("no_response", C.NO_ANSWER, ())
            assert s.record.facts_added == () and rd.policy_transitions == ()
            assert {i.code for i in s.issues} <= {"decline_marker_fact"}  # 표지가 사실 후보로 새지 않음


def test_offline_real_answer_is_recorded_as_succeeded_and_fails_nothing(tmp_path, monkeypatch):
    for r in _offline(tmp_path, monkeypatch, "네"):
        assert r.complete and r.steps
        assert _ops(r).failed_sources == frozenset() and _ops(r).failed_items == frozenset()
        assert {s.record.outcome.status for s in r.steps} == {"succeeded"}


def test_written_outcome_is_the_outcome_the_policy_received(tmp_path):
    for r in _offline(tmp_path):
        for rec, rd in zip(audit.load_run_v2(r.run_dir).records, r.rounds):
            assert (rec.outcome.status, rec.outcome.error_code) == (rd.outcome.status, rd.outcome.error_code)


def test_source_level_code_reaches_policy_and_record_together(tmp_path, monkeypatch):
    monkeypatch.setattr(answers, "NO_ANSWER", C.UNREACHABLE)
    for r in _offline(tmp_path):
        assert r.complete
        failed = [s.record.outcome for s in r.steps if s.record.outcome.status != "succeeded"]
        assert failed and {o.error_code for o in failed} == {C.UNREACHABLE}  # 대역이 사실을 답한 단계는 succeeded
        assert _ops(r).failed_sources == frozenset({"patient_interview"})


# ------------------------------------------------------------ 불확실 인용: 집계 제외, 삭제 없음, 진단
UNRELIABLE = ("모름. 기억 안 남", "모르겠어요, 기억이 안 나요", "글쎄요", "글쎄요, 잘 기억이 안 나네요")
MIXED = "손목 수술은 했는데 종류는 몰라요"


@pytest.mark.parametrize("text", [*UNRELIABLE, MIXED])
def test_uncertain_answer_quote_is_not_counted_but_kept_and_diagnosed(text):
    f = Facts()
    fid = f.add_answer("other", text, text)
    r = rp.build_step(obs(facts=f, after=BEFORE))
    assert answer_outcome(text) == ("succeeded", None)  # non_answer 범위는 그대로
    assert r.record.outcome.status == "succeeded" and r.record.outcome.new_fact_ids == () and r.record.facts_added == ()
    assert [(i.code, i.severity, i.fact_ids) for i in r.issues] == [("uncertain_answer_fact", "warning", (fid,))]
    assert fid in {x.fact_id for x in f.after().facts} and r.record.fact_version_after == f.after().version  # 삭제 없음


def test_mixed_answer_is_blocked_by_its_quote_not_by_the_answer():
    """보수적 동작: 판별은 인용 단위. 섞인 인용 전체는 세지 않고(사실이 섞여 있어도), 확실한 절만 인용하면 셈."""
    whole, clause = Facts(), Facts()
    whole.add_answer("other", "wrist surgery", MIXED)
    fid = clause.add_answer("other", "wrist surgery", "손목 수술은 했는데")
    assert rp.build_step(obs(facts=whole, after=BEFORE)).record.facts_added == ()
    assert rp.build_step(obs(facts=clause, after=BEFORE)).record.facts_added == (fid,)


@pytest.mark.parametrize("text", ["네", "아니요", "ECOG 1이에요", "모르핀을 복용 중입니다", "BCG 치료를 거부했습니다",
                                  "수술은 받지 않았어요", "기억나요, 작년에 받았어요"])
def test_plain_answers_are_still_counted(text):
    f = Facts()
    fid = f.add_answer("other", text, text)
    r = rp.build_step(obs(facts=f, after=BEFORE))
    assert r.record.outcome.new_fact_ids == (fid,) and r.record.facts_added == (fid,) and r.issues == ()


def test_explicit_link_does_not_override_an_unreliable_quote():
    f = Facts()
    fid = f.add_answer("other", "글쎄요", "글쎄요", ref="other")
    r = rp.build_step(obs(facts=f, after=BEFORE, explicit_fact_links=(fid,)))
    assert r.record.outcome.new_fact_ids == () and [i.code for i in r.issues] == ["uncertain_answer_fact"]


def _after_citing(fid, state="MET", rule="I1"):
    c = crit("T1", rule, state).model_copy(update={"evidence_fact_ids": (fid,)})
    return cohort(pair("T1", PS.INFO_MISSING, [c, crit("T1", "I2", "MET")]),
                  pair("T2", PS.INFO_MISSING, [crit("T2", "I1", "UNKNOWN")]))


@pytest.mark.parametrize("execution,text,detail", [("declined", "모름", "quote:non_answer"),
                                                   ("answered", "모름", "quote:non_answer"),
                                                   ("answered", "글쎄요", "quote:uncertain")])
def test_verdict_citing_an_unreliable_answer_is_diagnosed_and_not_rewritten(execution, text, detail):
    f = Facts()
    fid = f.add_answer("other", text, text)
    r = rp.build_step(obs(execution=execution, facts=f, after=_after_citing(fid)))
    hit = [i for i in r.issues if i.code == "criterion_cites_unreliable_answer"]
    assert [(i.criterion_key, i.trial_id, i.after, i.fact_ids, i.detail, i.severity) for i in hit] == [
        ("T1:I1", "T1", "MET", (fid,), (detail,), "warning")]
    assert r.status == "recorded_with_warnings"  # 진단은 남기되 관찰을 고치지 않음
    assert next(c for c in r.record.criteria if c.criterion_key == "T1:I1").evidence_fact_ids == (fid,)


def test_verdict_citing_an_earlier_unreliable_fact_is_also_diagnosed():
    f = Facts()
    fid = f.add_answer("other", "글쎄요", "글쎄요")
    f.before = f.after()  # 이전 단계에서 이미 저장된 사실
    r = rp.build_step(obs(facts=f, after=_after_citing(fid)))
    assert "criterion_cites_unreliable_answer" in [i.code for i in r.issues]


def test_unknown_criterion_or_reliable_citation_gets_no_verdict_diagnostic():
    f = Facts()
    bad, good = f.add_answer("other", "모름", "모름"), f.add_answer("ecog", 1, "ECOG 1이에요")
    for after in (_after_citing(bad, state="UNKNOWN"), _after_citing(good)):
        codes = [i.code for i in rp.build_step(obs(facts=f, after=after)).issues]
        assert "criterion_cites_unreliable_answer" not in codes


@pytest.mark.parametrize("answer", UNRELIABLE)
def test_offline_unreliable_answers_stay_succeeded_without_counted_facts(tmp_path, monkeypatch, answer):
    for r in _offline(tmp_path, monkeypatch, answer):
        assert r.complete and r.steps
        assert not any(p.status in C.CONFIRMED for p in r.final_cohort.pairs())
        for s in r.steps:
            assert s.record.outcome.status == "succeeded" and s.record.outcome.new_fact_ids == ()
            assert s.record.facts_added == ()


def test_these_paths_never_build_an_api_client(tmp_path, monkeypatch):
    from ctrec import llm
    made = []
    monkeypatch.setattr(llm.anthropic, "Anthropic", lambda *a, **k: made.append(1))
    monkeypatch.setattr(llm, "_client", None)
    assert all(r.method_status == "ok" for r in _offline(tmp_path, monkeypatch, "잘 모르겠어요")) and made == []
