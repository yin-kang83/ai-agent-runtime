# -*- coding: utf-8 -*-
from agent_runtime import (
    Claim,
    Evidence,
    EvidenceVerifier,
    RuntimePolicy,
    Status,
    StaticHumanGate,
    run_loop,
    run_once,
)

EV = (Evidence("E-001", "回购条款", "sha256:abc"),)
VERIFIER = EvidenceVerifier()


def _claim(**kw):
    base = dict(claim_id="C-001", content="该交易实质为融资", evidence_ids=("E-001",))
    base.update(kw)
    return Claim(**base)


def test_accepted_with_evidence_and_human():
    r = run_once(_claim(), EV, VERIFIER, StaticHumanGate(True))
    assert r.status is Status.ACCEPTED
    assert r.human_approved is True
    assert "evidence_present" in r.reasons


def test_rejected_without_evidence():
    r = run_once(_claim(evidence_ids=()), (), VERIFIER, StaticHumanGate(True))
    assert r.status is Status.REJECTED
    assert any("证据" in x for x in r.reasons)


def test_rejected_when_evidence_missing():
    r = run_once(_claim(evidence_ids=("E-999",)), EV, VERIFIER, StaticHumanGate(True))
    assert r.status is Status.REJECTED
    assert any("缺少证据" in x for x in r.reasons)


def test_substance_unapproved_needs_human():
    r = run_once(
        _claim(substance="融资", substance_basis=("REPO-1",), substance_approved=False),
        EV,
        VERIFIER,
        None,
    )
    assert r.status is Status.NEEDS_HUMAN


def test_substance_approved_by_human():
    r = run_once(
        _claim(substance="融资", substance_basis=("REPO-1",), substance_approved=True),
        EV,
        VERIFIER,
        StaticHumanGate(True),
    )
    assert r.status is Status.ACCEPTED


def test_human_rejection():
    r = run_once(_claim(), EV, VERIFIER, StaticHumanGate(False))
    assert r.status is Status.REJECTED
    assert "人工拒绝" in r.reasons


def test_policy_without_human():
    r = run_once(_claim(), EV, VERIFIER, None, RuntimePolicy(require_human=False))
    assert r.status is Status.ACCEPTED


def test_policy_min_evidence():
    r = run_once(_claim(), EV, VERIFIER, StaticHumanGate(True), RuntimePolicy(min_evidence=2))
    assert r.status is Status.REJECTED


def test_loop_accepts_first_round():
    calls = {"n": 0}

    def propose(round_no):
        calls["n"] += 1
        return _claim(claim_id=f"C-{round_no}")

    r = run_loop(propose, EV, VERIFIER, StaticHumanGate(True), RuntimePolicy(max_rounds=3))
    assert r.status is Status.ACCEPTED
    assert r.rounds == 1
    assert calls["n"] == 1
    assert r.history[0]["status"] == "accepted"


def test_loop_stops_after_max_rounds():
    def propose(round_no):
        return _claim(claim_id=f"C-{round_no}", substance="融资", substance_approved=False)

    r = run_loop(propose, EV, VERIFIER, None, RuntimePolicy(max_rounds=2))
    assert r.status is Status.NEEDS_HUMAN
    assert r.rounds == 2
    assert len(r.history) == 2


def test_loop_rejected_stops():
    def propose(round_no):
        return _claim(claim_id=f"C-{round_no}", evidence_ids=())

    r = run_loop(propose, EV, VERIFIER, StaticHumanGate(True), RuntimePolicy(max_rounds=3))
    assert r.status is Status.REJECTED
    assert r.rounds == 1


def test_claim_validation():
    errors = _claim(content="").validate()
    assert any("content" in e for e in errors)


def test_evidence_validation():
    errors = Evidence("E-1", "").validate()
    assert errors
