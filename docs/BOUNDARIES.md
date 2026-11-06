# 边界与不变量

## 不变量

```text
1. 没有 Evidence，不产生 ACCEPTED
2. 没有 HumanGate，不产生 ACCEPTED
3. substance 未批准，只能是 NEEDS_HUMAN
4. 人工拒绝，直接 REJECTED
5. 达到 max_rounds，必须停
6. 生成者 ≠ 最终批准者
7. 验证失败不静默跳过
```

## 不能做的事

```text
不自动判断经济实质
不把模型置信度当证据
不把“重试成功”当验证通过
不把“找不到反例”当证明
不替代税务师/律师/审计判断
不存客户真实数据
```

## 运行时与领域的关系

```text
runtime：协议、门、拒绝、轮次
domain ：规则、证据、判断依据
human  ：最终签字
```

## 失败语义

```text
REJECTED    明确不通过
NEEDS_HUMAN 不能自动决定，交人
ACCEPTED    通过验证且有人批准
```

**没有“差不多通过”。**
