# -*- coding: utf-8 -*-
"""运行时核心类型。"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Status(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    NEEDS_HUMAN = "needs_human"


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    content: str
    digest: str = ""

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.evidence_id:
            errors.append("evidence_id 为空")
        if not self.content.strip():
            errors.append(f"{self.evidence_id}: content 为空")
        return errors


@dataclass(frozen=True)
class Claim:
    claim_id: str
    content: str
    evidence_ids: tuple[str, ...] = ()
    legal_form: str | None = None
    substance: str | None = None
    substance_basis: tuple[str, ...] = ()
    substance_approved: bool = False
    metadata: tuple[tuple[str, str], ...] = ()

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.claim_id:
            errors.append("claim_id 为空")
        if not self.content.strip():
            errors.append(f"{self.claim_id}: content 为空")
        if not self.evidence_ids:
            errors.append(f"{self.claim_id}: evidence_ids 为空")
        if self.substance and not self.substance_approved:
            errors.append(f"{self.claim_id}: substance 未批准")
        return errors


@dataclass(frozen=True)
class Decision:
    status: Status
    reasons: tuple[str, ...] = ()
    requires_review: bool = False


@dataclass(frozen=True)
class RuntimePolicy:
    max_rounds: int = 3
    require_human: bool = True
    min_evidence: int = 1
    fail_closed: bool = True

    def __post_init__(self) -> None:
        if self.max_rounds < 1:
            raise ValueError("max_rounds 必须 >= 1")
        if self.min_evidence < 0:
            raise ValueError("min_evidence 必须 >= 0")


@dataclass(frozen=True)
class RunResult:
    status: Status
    rounds: int
    reasons: tuple[str, ...] = ()
    evidence_used: tuple[str, ...] = ()
    human_approved: bool = False
    history: tuple[dict, ...] = field(default_factory=tuple)
