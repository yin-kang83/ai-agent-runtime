# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))

from legal_dry_run import RuleView, build_claim_evidence, run_dry


def _rule():
    return RuleView(
        domain="econ-law",
        rule_id="LAW-001",
        statement="民法调整平等主体之间的人身关系和财产关系。",
        citation="《中华人民共和国民法典》第2条（2021-01-01施行）",
        effective_date="2021-01-01",
        status="pending_review",
    )


def test_build_claim_evidence():
    claim, evidence = build_claim_evidence(_rule())
    assert claim.evidence_ids == ("EVID-LAW-001",)
    assert evidence[0].digest.startswith("sha256:")
    assert "民法典" in evidence[0].content


def test_dry_run_approved():
    out = run_dry(_rule(), "approve")
    assert out["result"]["status"] == "accepted"
    assert out["result"]["human_approved"] is True


def test_dry_run_denied():
    out = run_dry(_rule(), "deny")
    assert out["result"]["status"] == "rejected"
    assert "人工拒绝" in out["result"]["reasons"]


def test_dry_run_needs_human():
    out = run_dry(_rule(), "none")
    assert out["result"]["status"] == "needs_human"
