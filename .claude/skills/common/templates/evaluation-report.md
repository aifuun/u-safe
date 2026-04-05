# 评估报告模板

## 基本信息

**Issue编号**: #{issue_number}
**评估时间**: {timestamp}
**综合得分**: {overall_score}/100
**评估状态**: {status_emoji} {status}

---

## 📊 4视角评分概览

| 视角 | 权重 | 得分 | 状态 | 关键发现 |
|------|------|------|------|----------|
| 1️⃣ 目标达成 | 30% | {goal_score}/100 | {goal_status} | {goal_summary} |
| 2️⃣ 架构设计 | 30% | {arch_score}/100 | {arch_status} | {arch_summary} |
| 3️⃣ 质量保障 | 25% | {quality_score}/100 | {quality_status} | {quality_summary} |
| 4️⃣ 风险控制 | 15% | {risk_score}/100 | {risk_status} | {risk_summary} |

**说明**：
- ✅ PASS: 优秀（≥90分）
- ⚠️ PARTIAL: 部分通过（60-89分）
- ❌ FAIL: 不通过（<60分）

---

## 1️⃣ 目标达成（30%）

**得分**: {goal_score}/100 {goal_status}

### 检查项结果

{goal_checks_detail}

### 关键发现

{goal_findings}

### 改进建议

{goal_recommendations}

---

## 2️⃣ 架构设计（30%）

**得分**: {arch_score}/100 {arch_status}

### 检查项结果

{arch_checks_detail}

### 关键发现

{arch_findings}

### 改进建议

{arch_recommendations}

---

## 3️⃣ 质量保障（25%）

**得分**: {quality_score}/100 {quality_status}

### 检查项结果

{quality_checks_detail}

### 关键发现

{quality_findings}

### 改进建议

{quality_recommendations}

---

## 4️⃣ 风险控制（15%）

**得分**: {risk_score}/100 {risk_status}

### 检查项结果

{risk_checks_detail}

### 关键发现

{risk_findings}

### 改进建议

{risk_recommendations}

---

## 🎯 综合评估

### 总体得分
- **加权得分**: {weighted_score}/1.0
- **百分制得分**: {overall_score}/100
- **评估状态**: {status_emoji} **{status}**

### 关键问题（必须修复）

{critical_issues_list}

### 改进建议（可选）

{recommendations_list}

---

## 📋 后续行动

{next_actions_list}

---

## 📝 附录

### 评分计算公式

```
综合得分 = 目标达成×30% + 架构设计×30% + 质量保障×25% + 风险控制×15%
```

### 通过标准

| 得分范围 | 状态 | 说明 |
|----------|------|------|
| ≥90分 | ✅ APPROVED | 优秀，可以合并 |
| 80-89分 | ⚠️ APPROVED_WITH_CONCERNS | 有保留地批准，建议后续改进 |
| 60-79分 | ❌ NEEDS_IMPROVEMENT | 需要修复后再合并 |
| <60分 | 🚫 REJECTED | 存在严重问题，不建议继续 |

### 关键项否决规则

如果任何 **critical** 级别的检查项失败，即使总分≥90，状态最高也只能是 **APPROVED_WITH_CONCERNS**。

---

**评估框架版本**: 1.0.0
**使用技能**: /eval-plan, /review
**生成时间**: {timestamp}

---

<!--
模板变量说明：

基本信息：
- {issue_number}: Issue编号
- {timestamp}: 评估时间戳（ISO格式）
- {overall_score}: 综合得分（0-100）
- {status}: 评估状态（APPROVED/APPROVED_WITH_CONCERNS/NEEDS_IMPROVEMENT/REJECTED）
- {status_emoji}: 状态对应的emoji（✅/⚠️/❌/🚫）

视角得分：
- {goal_score}, {arch_score}, {quality_score}, {risk_score}: 各视角得分（0-100）
- {goal_status}, {arch_status}, {quality_status}, {risk_status}: 各视角状态（✅/⚠️/❌）
- {goal_summary}, {arch_summary}, {quality_summary}, {risk_summary}: 各视角关键发现摘要（1句话）

检查项详情：
- {goal_checks_detail}: 目标达成视角的检查项详情（表格格式）
- {arch_checks_detail}: 架构设计视角的检查项详情
- {quality_checks_detail}: 质量保障视角的检查项详情
- {risk_checks_detail}: 风险控制视角的检查项详情

关键发现和建议：
- {goal_findings}, {arch_findings}, {quality_findings}, {risk_findings}: 各视角关键发现
- {goal_recommendations}, {arch_recommendations}, {quality_recommendations}, {risk_recommendations}: 各视角改进建议

综合评估：
- {weighted_score}: 加权得分（0-1）
- {critical_issues_list}: 关键问题列表（Markdown列表）
- {recommendations_list}: 改进建议列表（Markdown列表）
- {next_actions_list}: 后续行动列表（Markdown列表）

-->
