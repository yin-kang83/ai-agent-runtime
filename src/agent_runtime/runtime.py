# -*- coding: utf-8 -*-
"""单轮运行：验证 → 人类门 → 接受/拒绝/转人工。"""
from __future__ import annotations

from .human import HumanGate
from .types import Claim, Evidence, RuntimePolicy, RunResult, Status
from .verifier import Verifier


def run_once(
    claim: Claim,
    evidence: tuple[Evidence, ...],
    verifier: Verifier,
    human_gate: HumanGate | None,
    policy: RuntimePolicy | None = None,
) -> RunResult:
    policy = policy or RuntimePolicy()

    if len(evidence) < policy.min_evidence:
        return RunResult(Status.REJECTED, 1, ("证据不足",))

    decision = verifier.verify(claim, evidence)
    evidence_used = tuple(e.evidence_id for e in evidence)

    if decision.status is Status.REJECTED:
        return RunResult(Status.REJECTED, 1, decision.reasons, evidence_used)

    if policy.require_human:
        if human_gate is None:
            return RunResult(Status.NEEDS_HUMAN, 1, ("需要人工批准",), evidence_used)
        if not human_gate.approve(claim, evidence):
            return RunResult(Status.REJECTED, 1, ("人工拒绝",), evidence_used)

    if decision.status is Status.NEEDS_HUMAN:
        return RunResult(
            Status.ACCEPTED if policy.require_human and human_gate is not None else Status.NEEDS_HUMAN,
            1,
            decision.reasons,
            evidence_used,
            human_approved=policy.require_human and human_gate is not None,
        )

    return RunResult(
        Status.ACCEPTED,
        1,
        decision.reasons,
        evidence_used,
        human_approved=policy.require_human and human_gate is not None,
    )
