# -*- coding: utf-8 -*-
"""有限递归：最多 N 轮，失败即停，不允许自己批准自己。"""
from __future__ import annotations

from typing import Callable

from .human import HumanGate
from .runtime import run_once
from .types import Claim, Evidence, RuntimePolicy, RunResult, Status
from .verifier import Verifier

Proposer = Callable[[int], Claim]


def run_loop(
    propose: Proposer,
    evidence: tuple[Evidence, ...],
    verifier: Verifier,
    human_gate: HumanGate | None,
    policy: RuntimePolicy | None = None,
) -> RunResult:
    policy = policy or RuntimePolicy()
    history: list[dict] = []

    for round_no in range(1, policy.max_rounds + 1):
        claim = propose(round_no)
        result = run_once(claim, evidence, verifier, human_gate, policy)
        history.append(
            {
                "round": round_no,
                "claim_id": claim.claim_id,
                "status": result.status.value,
                "reasons": list(result.reasons),
            }
        )
        if result.status in (Status.ACCEPTED, Status.REJECTED):
            return RunResult(
                result.status,
                round_no,
                result.reasons,
                result.evidence_used,
                result.human_approved,
                tuple(history),
            )

    return RunResult(
        Status.NEEDS_HUMAN,
        policy.max_rounds,
        ("达到最大轮次，仍需人工处理",),
        tuple(e.evidence_id for e in evidence),
        False,
        tuple(history),
    )
