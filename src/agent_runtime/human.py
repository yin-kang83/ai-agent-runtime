# -*- coding: utf-8 -*-
"""人类门：只在明确批准时放行。"""
from __future__ import annotations

from typing import Protocol

from .types import Claim, Evidence


class HumanGate(Protocol):
    def approve(self, claim: Claim, evidence: tuple[Evidence, ...]) -> bool:
        ...


class DenyAllGate:
    def approve(self, claim: Claim, evidence: tuple[Evidence, ...]) -> bool:
        return False


class StaticHumanGate:
    """测试用：固定返回批准/拒绝。生产环境应接入真实身份与审批记录。"""

    def __init__(self, approved: bool) -> None:
        self.approved = approved

    def approve(self, claim: Claim, evidence: tuple[Evidence, ...]) -> bool:
        return self.approved
