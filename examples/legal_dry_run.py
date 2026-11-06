# -*- coding: utf-8 -*-
"""端到端干跑：legal-domains 规则 → Claim/Evidence → runtime → HumanGate。"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from agent_runtime import (
    Claim,
    Evidence,
    EvidenceVerifier,
    RuntimePolicy,
    StaticHumanGate,
    run_once,
)


@dataclass(frozen=True)
class RuleView:
    domain: str
    rule_id: str
    statement: str
    citation: str
    effective_date: str
    status: str


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_rule(legal_root: Path, domain: str, rule_id: str) -> RuleView:
    if domain == "econ-law":
        path = legal_root / "domains" / "econ-law" / "knowledge" / "rules.json"
        doc = _load_json(path)
        rules = doc.get("rules", doc) if isinstance(doc, dict) else doc
        for r in rules:
            if r.get("id") == rule_id:
                refs = r.get("source_refs") or []
                return RuleView(
                    domain=domain,
                    rule_id=rule_id,
                    statement=str(r.get("statement", "")),
                    citation="；".join(str(x) for x in refs) or "[待核实]",
                    effective_date=str(r.get("effective_date", "[待核实]")),
                    status=str(r.get("status", "pending_review")),
                )
    elif domain == "tax-law":
        path = legal_root / "domains" / "tax-law" / "tax_rules" / "cards.json"
        doc = _load_json(path)
        cards = doc.get("cards", []) if isinstance(doc, dict) else doc
        for c in cards:
            if c.get("id") == rule_id:
                variants = c.get("variants") or []
                conclusion = variants[0].get("conclusion", "") if variants else ""
                return RuleView(
                    domain=domain,
                    rule_id=rule_id,
                    statement=f"{c.get('point', '')}：{conclusion}",
                    citation=str(c.get("citation", "[待核实]")),
                    effective_date="[待核实]",
                    status="pending_review",
                )
    else:
        raise ValueError(f"不支持领域: {domain}")

    raise KeyError(f"找不到规则: {domain}/{rule_id}")


def build_claim_evidence(rule: RuleView) -> tuple[Claim, tuple[Evidence, ...]]:
    content = f"{rule.statement}\n依据：{rule.citation}\n生效日期：{rule.effective_date}"
    digest = "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()
    evidence = Evidence(
        evidence_id=f"EVID-{rule.rule_id}",
        content=content,
        digest=digest,
    )
    claim = Claim(
        claim_id=f"CLAIM-{rule.rule_id}",
        content=rule.statement,
        evidence_ids=(evidence.evidence_id,),
        metadata=(("domain", rule.domain), ("rule_id", rule.rule_id)),
    )
    return claim, (evidence,)


def run_dry(rule: RuleView, human: str = "approve") -> dict:
    claim, evidence = build_claim_evidence(rule)
    gate = {"approve": StaticHumanGate(True), "deny": StaticHumanGate(False), "none": None}[human]
    result = run_once(claim, evidence, EvidenceVerifier(), gate, RuntimePolicy())
    return {
        "rule": asdict(rule),
        "claim": {
            "claim_id": claim.claim_id,
            "content": claim.content,
            "evidence_ids": list(claim.evidence_ids),
        },
        "evidence": [
            {"evidence_id": e.evidence_id, "digest": e.digest, "content": e.content}
            for e in evidence
        ],
        "result": {
            "status": result.status.value,
            "reasons": list(result.reasons),
            "human_approved": result.human_approved,
            "evidence_used": list(result.evidence_used),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="legal-domains + ai-agent-runtime 端到端干跑")
    ap.add_argument("--legal-root", default=r"E:\legal-domains")
    ap.add_argument("--domain", choices=["econ-law", "tax-law"], default="econ-law")
    ap.add_argument("--rule-id", default="LAW-001")
    ap.add_argument("--human", choices=["approve", "deny", "none"], default="approve")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    rule = load_rule(Path(args.legal_root), args.domain, args.rule_id)
    out = run_dry(rule, args.human)
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"规则：{out['rule']['domain']}/{out['rule']['rule_id']}")
        print(f"状态：{out['result']['status']}")
        print(f"原因：{', '.join(out['result']['reasons'])}")
        print(f"人工批准：{out['result']['human_approved']}")
        print(f"证据：{', '.join(out['result']['evidence_used'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
