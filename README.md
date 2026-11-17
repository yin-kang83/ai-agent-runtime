# ai-agent-runtime

> DOI: [10.5281/zenodo.24295144](https://doi.org/10.5281/zenodo.24295144)


> 面向确定性财务/法律智能体的 Agent 运行时骨架。
> 不调用模型、不存 Prompt、不存密钥；只负责：Claim/Evidence、验证、失败关闭、人类门、有限递归。

## 定位

```text
模型负责“读世界、提 Claim”
runtime 负责“验证、拒绝、留痕、让人签字”
确定性工具负责“算”
```

本仓库不是大模型客户端，也不是知识库。

## 核心对象

```text
Claim      模型/外部提出的主张
Evidence   证据
Decision   accepted / rejected / needs_human
HumanGate  人工批准/拒绝
RunResult  一次运行结果
```

## 最小示例

```python
from agent_runtime import Claim, Evidence, EvidenceVerifier, run_once
from agent_runtime.types import RuntimePolicy
from agent_runtime.human import StaticHumanGate

claim = Claim(
    claim_id="C-001",
    content="该交易实质为融资",
    evidence_ids=("E-001",),
)
ev = Evidence(evidence_id="E-001", content="回购条款", digest="sha256:...")
verifier = EvidenceVerifier()
result = run_once(claim, (ev,), verifier, StaticHumanGate(True), RuntimePolicy())
print(result.status)  # accepted
```

## 边界

```text
不自动判断经济实质
不替代税务师/律师/审计判断
不调用 LLM
不存 API Key
不把“模型置信度”当证据
```

## 测试

```powershell
python -m pytest -q
```

## 设计文档

- `docs/ARCHITECTURE.md`
- `docs/BOUNDARIES.md`

## 许可

私有工作仓，All rights reserved。
