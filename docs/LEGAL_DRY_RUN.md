# 法律领域端到端干跑

目的：证明“法律领域知识 → Claim/Evidence → runtime → HumanGate”这条链能跑通。

## 运行

```powershell
cd ai-agent-runtime
$env:PYTHONPATH = (Get-Location).Path + "\src"

python examples/legal_dry_run.py --domain econ-law --rule-id LAW-001 --human approve
python examples/legal_dry_run.py --domain tax-law --rule-id TAX2-HOUSE-001 --human approve
python examples/legal_dry_run.py --domain econ-law --rule-id LAW-001 --human deny
python examples/legal_dry_run.py --domain econ-law --rule-id LAW-001 --human none
```

## 期望

```text
approve → accepted
deny    → rejected（人工拒绝）
none    → needs_human
```

## 边界

```text
这是干跑，不是法律意见
规则仍是 pending_review
不调用 LLM
不做真实身份认证
```

## 数据依赖

```text
domain-kb/domains/econ-law/knowledge/rules.json
domain-kb/domains/tax-law/tax_rules/cards.json
```

规则变了，干跑会自动读新数据；不需要改 runtime。
