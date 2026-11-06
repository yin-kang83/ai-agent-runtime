# 运行时架构

## 一、三层分离

```text
模型层：读文档、提 Claim
运行时：验证、人类门、失败关闭、留痕
确定性层：计算、对账、DAG、底稿
```

本仓库只实现第二层骨架。

## 二、单轮流程

```text
Claim + Evidence
  ↓
min_evidence 检查
  ↓
Verifier.verify
  ├─ rejected → REJECTED
  └─ needs_human / accepted
        ↓
     HumanGate
        ├─ 无 gate → NEEDS_HUMAN
        ├─ 拒绝   → REJECTED
        └─ 批准   → ACCEPTED
```

## 三、有限递归

```text
propose(round) → run_once → accepted/rejected 停止
                      ↓ needs_human
                 最多 max_rounds 轮
                      ↓
                 NEEDS_HUMAN
```

硬约束：

```text
1. 生成者不能同时是最终批准者
2. 达到 max_rounds 必须停
3. 失败不自动重试到成功
4. 人工拒绝直接 REJECTED
5. 概率/置信度不能替代 Evidence
```

## 四、接入点

```text
Verifier        ← 财务/法律领域自己的校验器
HumanGate       ← 真实身份/审批系统（OIDC/工单）
Evidence        ← 底稿、合同、发票、法条
Claim           ← LLM 抽取结果或外部输入
```

## 五、不做什么

```text
不调用 LLM
不存 Prompt
不存 API Key
不实现具体会计/税务/法律判断
不替代确定性引擎
```

具体领域逻辑放在 `legal-domains/domains/*` 或 `fin-agent`，
本仓库只定义运行时的最小协议。
