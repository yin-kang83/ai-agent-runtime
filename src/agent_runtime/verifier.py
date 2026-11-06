# -*- coding: utf-8 -*-
"""验证器：只做可解释的确定性检查，不猜。"""
from __future__ import annotations

from typing import Protocol

from .types import Claim, Decision, Evidence, Status


class Verifier(Protocol):
    def verify(self, claim: Claim, evidence: tuple[Evidence, ...]) -> Decision:
        ...


class EvidenceVerifier:
    """最小验证器：证据存在、id 对得上、substance 已批准。

    边界：
    - 只验证“claim 与 evidence 是否一致到可复核”，不验证 evidence 本身真实；
    - 不判断经济实质；
    - 缺证据/证据对不上 -> rejected；
    - substance 未批准 -> needs_human。
    """

    def verify(self, claim: Claim, evidence: tuple[Evidence, ...]) -> Decision:
        claim_errors = claim.validate()
        if claim_errors:
            if any("substance 未批准" in e for e in claim_errors):
                return Decision(Status.NEEDS_HUMAN, tuple(claim_errors), requires_review=True)
            return Decision(Status.REJECTED, tuple(claim_errors))

        known = {e.evidence_id: e for e in evidence}
        ev_errors: list[str] = []
        for ev in evidence:
            ev_errors.extend(ev.validate())
        if ev_errors:
            return Decision(Status.REJECTED, tuple(ev_errors))

        missing = [eid for eid in claim.evidence_ids if eid not in known]
        if missing:
            return Decision(Status.REJECTED, (f"缺少证据: {', '.join(missing)}",))

        if claim.substance and not claim.substance_approved:
            return Decision(Status.NEEDS_HUMAN, ("substance 未批准",), requires_review=True)

        return Decision(Status.ACCEPTED, ("evidence_present",))
