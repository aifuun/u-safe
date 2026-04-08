# SKILL_GUIDE.md - 技能创建指南

> AI 创建技能时的统一参考标准 | 指令风格文档

## 🚀 快速开始（5 分钟）

### 创建新技能的 3 种方式

1. **使用 /skill-creator（推荐）**
   ```
   /skill-creator "创建技能: 自动生成周报"
   ```
   - 自动生成 YAML frontmatter
   - 创建标准目录结构
   - 提供模板代码
   - 添加测试用例

2. **手动创建**
   ```bash
   mkdir .claude/skills/new-skill
   touch .claude/skills/new-skill/SKILL.md
   # 参考下方模板编写
   ```

3. **基于现有修改**
   ```bash
   cp -r .claude/skills/similar-skill .claude/skills/new-skill
   # 修改 SKILL.md 内容
   ```

**推荐顺序**: skill-creator → 手动创建 → 基于现有修改

---

## 📚 核心概念

### 什么是技能 (Skill)?

**官方定义** (Anthropic): 可复用的工作流自动化，通过描述触发条件让 AI 自动执行

**框架定义** (ai-dev): 符合 ADR-001 标准的 `.claude/skills/` 目录下的 SKILL.md 文件

### 技能 vs 命令 vs 规则

| 对比维度 | 技能 (Skills) | 命令 (Commands) | 规则 (Rules) |
|---------|-------------|----------------|-------------|
| **触发方式** | AI 自动触发（描述匹配） | 用户手动调用 | AI 读取参考 |
| **文件位置** | `.claude/skills/` | 已废弃 | `.claude/rules/` |
| **适用场景** | 自动化工作流 | N/A | 快速参考 |
| **示例** | `/auto-solve-issue #23` | N/A | `typescript-nominal-types.md` |

**关键区别**: 技能通过描述自动触发，命令需手动调用，规则仅供参考

### 3 层架构

```
Meta Skills (元技能)          ← 多阶段 + 检查点
    ├─ auto-solve-issue      5 phases, Task deps
    └─ work-issue (deprecated)

Composite Skills (组合技能)   ← 调用其他技能
    ├─ update-framework      调用 4 个 update-* 技能
    ├─ solve-issues          批处理包装器
    └─ maintain-project      调用检查技能

Atomic Skills (原子技能)      ← 单一职责,无依赖
    ├─ status                显示项目状态
    ├─ next                  获取下一任务
    ├─ overview              生成报告
    └─ adr                   创建 ADR
```

**设计原则**: 原子技能是基础，组合技能提供便利，元技能自动化完整流程

---

## 🔄 端到端创建流程（5 个阶段）

### 阶段 1: 捕获需求

**AI 执行步骤:**
1. 询问用户 4 个核心问题
2. 提取技能规格
3. 确定复杂度级别

**问题清单:**
```python
questions = [
    "这个技能应该做什么？（What）",
    "何时自动触发？何时不触发？（When）",
    "输出什么内容？格式要求？（Output）",
    "需要测试吗？测试级别？（Testing）"
]
```

**输出**: `skill_spec = {name, trigger_when, do_not_trigger, output_format, test_level}`

### 阶段 2: 生成 SKILL.md

**YAML Frontmatter 模板:**
```yaml
---
name: {{skill_name}}
description: |
  {{what_it_does}}
  TRIGGER when: {{trigger_conditions}}
  DO NOT TRIGGER when: {{exclusion_conditions}}
version: "1.0.0"
last-updated: "{{today}}"
---
```

**必需字段**: name, description (含 TRIGGER/DO NOT TRIGGER), version
**可选字段**: argument-hint, allowed-tools, user-invocable

### 阶段 3: 决定脚本需求

**判断逻辑:**
```python
if estimated_lines <= 200:
    approach = "SKILL.md only"  # Simple pattern
elif 200 < estimated_lines <= 350:
    approach = "SKILL.md + scripts/"  # Standard pattern
else:
    approach = "SKILL.md + scripts/ + references/"  # Complex pattern
```

**脚本要求** (if needed):
- 必须使用 Python 3.9+ (ADR-003)
- 必须有类型标注
- 遵循 shared utilities (.claude/skills/_scripts/)
- **必须遵循 Python 执行标准（零例外）**（见下方）

#### Python 执行标准（强制，零例外）

**所有 Python 代码必须通过 `uv run` 执行，零例外。**

详细标准请参考：[execution-standard.md](../../skills/_templates/execution-standard.md)

**快速规则：**

1. **正式脚本（推荐）：**
   ```bash
   uv run scripts/script_name.py [args]
   ```

2. **简单一行代码：**
   ```bash
   uv run -c "import module; module.function()"
   ```

3. **共享工具调用：**
   ```python
   # 在 scripts/xxx.py 中（已通过 uv run 启动）
   import sys
   sys.path.insert(0, '.claude/skills/_scripts')
   from utils.sync import filter_framework_only_skills
   ```

**禁止使用（零例外）：**
```bash
❌ python3 scripts/...
❌ python3 -c "..."
❌ python scripts/...
```

**理由（ADR-017 完全统一方案）：**
- ✅ 零认知负载：无需判断何时用什么
- ✅ 环境一致性：所有代码同一环境
- ✅ 长期收益：5 年节省 12 小时维护成本
- ✅ 性能影响：+10ms 人类无感知

**所有技能 SKILL.md 必须包含此引用：**

```markdown
## AI 执行指令

**Python 执行标准：**

本技能遵循 [Python 执行标准（零例外）](../_templates/execution-standard.md)。

所有 Python 代码必须使用 `uv run`：
- 正式脚本：`uv run scripts/xxx.py`
- 简单代码：`uv run -c "..."`
- 共享工具：脚本内直接 import（前提是脚本通过 uv run 启动）

**禁止使用** `python3` 直接调用。
```

**相关 ADRs:**
- [ADR-017](../../../docs/ADRs/017-uv-dependency-management.md) - UV-based Dependency Management（完全统一方案）
- [ADR-018](../../../docs/ADRs/018-mandatory-uv-execution.md) - Mandatory UV Execution（强制执行标准）

---

### 阶段 4: 选择设计模式

**判断算法:**
```python
if has_multiple_phases and has_checkpoints and uses_task_dependencies:
    pattern = "Meta"  # 元技能模式
    # 示例: auto-solve-issue (5 phases, Task deps)
elif calls_other_skills and not has_checkpoints:
    pattern = "Composite"  # 组合技能模式
    # 示例: update-framework (调用 4 个技能)
elif is_single_responsibility and not calls_other_skills:
    pattern = "Atomic"  # 原子技能模式
    # 示例: status, overview, next
else:
    pattern = "Atomic"  # 默认为 Atomic
```

**模式选择规则**:
- 默认使用 Atomic
- 仅在需要编排多个技能时使用 Composite
- 仅在需要多阶段验证时使用 Meta

### 阶段 5: 生成测试用例

**测试级别** (ADR-002):
- **Level 1 (Quick)**: 简单技能，手动测试 1-2 场景
- **Level 2 (Basic)**: 核心工作流，2-3 用例 + 人工审查
- **Level 3 (Full)**: Meta-tools，完整测试集 + benchmark

**测试模板:**
```json
{
  "skill_name": "{{skill_name}}",
  "evals": [
    {
      "prompt": "测试 {{skill_name}} 基本功能",
      "assertions": [
        "技能正确触发",
        "输出格式正确",
        "无错误发生"
      ]
    }
  ]
}
```

**注意**: 大多数技能使用 Level 1，快速迭代优先于完美测试

---

## 🎨 设计模式（3 种）

### Pattern 1: Atomic (原子技能)

**判断条件:**
```python
if (is_single_responsibility and
    not calls_other_skills and
    not has_checkpoints):
    return "Atomic"
```

**特征**:
- 单一职责
- 无外部依赖
- 直接执行
- Simple pattern (<200 lines)

**代码模板:**
```markdown
# SKILL.md
---
name: atomic-skill
description: |
  单一功能描述
  TRIGGER when: 明确触发条件
  DO NOT TRIGGER when: 排除条件
version: "1.0.0"
---

# Skill Name

## Overview
What it does.

## Usage
`/skill-name [args]`

## Example
具体使用示例
```

**真实示例**: status, next, overview

### Pattern 2: Composite (组合技能)

**判断条件:**
```python
if (calls_other_skills and
    not has_checkpoints and
    not has_multiple_phases):
    return "Composite"
```

**特征**:
- 调用其他技能
- 提供统一接口
- 简单编排逻辑
- Standard pattern (200-350 lines)

**代码模板:**
```python
# 在 SKILL.md 中调用其他技能
def execute_composite():
    # 调用技能 1
    Skill("{{sync-skill-1}}", args="{{args-1}}")

    # 调用技能 2
    Skill("{{sync-skill-2}}", args="{{args-2}}")

    # 调用技能 3
    Skill("{{sync-skill-3}}", args="{{args-3}}")

    # 报告结果
    print("✅ All components synced")
```

**真实示例**: update-framework (4 skills), solve-issues (batch wrapper)

### Pattern 3: Meta (元技能)

**判断条件:**
```python
if (has_multiple_phases and
    has_checkpoints and
    uses_task_dependencies):
    return "Meta"
```

**特征**:
- 多阶段工作流 (3-5 phases)
- 检查点验证
- Task 依赖链
- 直接技能调用
- Complex pattern (>400 lines)

**代码模板:**
```python
# 创建 Task 依赖链
tasks = [
    TaskCreate(subject="Phase 1: start-issue"),
    TaskCreate(subject="Phase 1.5: eval-plan", addBlockedBy=[task1_id]),
    TaskCreate(subject="Phase 2: execute-plan", addBlockedBy=[task2_id]),
    TaskCreate(subject="Phase 2.5: review", addBlockedBy=[task3_id]),
    TaskCreate(subject="Phase 3: finish-issue", addBlockedBy=[task4_id])
]

# 执行各阶段（直接调用技能）
for phase in phases:
    TaskUpdate(phase.task_id, status="in_progress")
    Skill(phase.skill_name, args=phase.args)

    # 检查点
    if phase.has_checkpoint:
        status = read_status_file()
        if status.score < 90:
            stop_and_prompt_user()

    TaskUpdate(phase.task_id, status="completed")
```

**真实示例**: auto-solve-issue v2.0 (5 phases, Task deps)

---

## ✅ 最佳实践（7 类）

### 1. 用户体验设计

**进度报告** - 长时间运行的技能必须显示进度:
```python
TaskUpdate(task_id, status="in_progress")  # 标记正在执行
# 执行操作...
TaskUpdate(task_id, status="completed")    # 标记完成
```

**清晰输出** - 模式感知输出 (auto 模式 2 行, interactive 模式 ≤20 行):
```python
if is_auto_mode:
    print(f"✅ Task complete: {summary}")
    print(f"Next: {next_action}")
else:
    print(detailed_report)  # ≤20 lines
```

### 2. 参数设计

**合理默认值** - 减少必需参数:
```yaml
description: |
  Sync skills from framework.
  TRIGGER when: user wants to sync skills
argument-hint: "<target-path> [--clean] [--dry-run]"
```

**自动检测** - 优先自动检测而非要求输入:
```python
# 使用 issue_detector 自动检测 issue number
from framework.issue_detector import detect_issue_number
issue_num = detect_issue_number()  # 4 strategies
```

### 3. 错误处理

**优雅失败** - 提供清晰错误信息和恢复选项:
```python
try:
    execute_operation()
except FileNotFoundError:
    print("❌ Plan file not found")
    print("Fix: /start-issue #N to create plan")
    sys.exit(1)
```

**验证输入** - 在执行前验证:
```python
if not plan_file.exists():
    raise FileNotFoundError(f"Plan not found: {plan_file}")
```

### 4. 幂等性

**可重复执行** - 技能应该支持多次运行而不产生错误:
```python
# ✅ 幂等操作
if not directory.exists():
    directory.mkdir(parents=True)

# ❌ 非幂等
directory.mkdir()  # 第二次运行会报错
```

### 5. 性能优化

**批量操作** - 避免循环中的重复调用:
```python
# ✅ 批量读取
skills = Glob(".claude/skills/*/SKILL.md")

# ❌ 逐个查找
for skill in skill_names:
    path = find_skill(skill)  # 重复文件系统操作
```

### 6. 文档编写

**示例优先** - 提供具体使用示例:
```markdown
## Examples

**Example 1**: Basic usage
\`\`\`bash
/skill-name #23
\`\`\`

**Example 2**: With options
\`\`\`bash
/skill-name #23 --option value
\`\`\`
```

### 7. Anthropic 官方最佳实践

- **TRIGGER 描述明确** - 帮助 AI 准确触发
- **DO NOT TRIGGER 排除误触发** - 避免错误调用
- **Semantic versioning** - 使用语义化版本号 (ADR-008)
- **Type hints** - Python 脚本必须有类型标注 (ADR-003)

---

## ⚠️ 常见错误（5 类）

### 1. 技能职责过大
❌ **错误**: 一个技能做太多事情
✅ **修复**: 拆分为多个原子技能，用组合技能编排

### 2. 缺少参数验证
❌ **错误**: 直接使用未验证的输入
✅ **修复**: 在执行前验证所有参数

### 3. 错误信息不明确
❌ **错误**: "Error occurred"
✅ **修复**: "❌ Plan file not found: .claude/plans/active/issue-23-plan.md"

### 4. 文档与实现不一致
❌ **错误**: SKILL.md 说接受 `--option` 但代码不支持
✅ **修复**: 保持文档和代码同步

### 5. 忽略现有技能
❌ **错误**: 创建重复功能的技能
✅ **修复**: 先检查 `.claude/skills/README.md`，复用或扩展现有技能

---

## 📚 参考资源

### 框架内部文档
- **[ADR-001](../../ADRs/001-official-skill-patterns.md)** - 官方模式标准
- **[ADR-002](../../ADRs/002-skill-creation-workflow.md)** - 创建工作流
- **[ADR-008](../../ADRs/008-skills-version-control.md)** - 语义化版本控制
- **[.claude/skills/README.md](../../.claude/skills/README.md)** - Skills 系统概览

### Anthropic 官方资源
- **[The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)** (PDF)
- **[Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)**
- **[GitHub - anthropics/skills](https://github.com/anthropics/skills)**
- **[Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)**
- **[MCP Introduction](https://anthropic.skilljar.com/introduction-to-model-context-protocol)**
- **[Claude Code in Action](https://anthropic.skilljar.com/claude-code-in-action)**

### 社区资源
- **[10 Must-Have Skills for Claude Code](https://www.anthropic.com/blog/claude-code-skills)**
- **[awesome-claude-skills](https://github.com/anthropics/awesome-claude-skills)**

---

**Version**: 1.0.0
**Last Updated**: 2026-03-24
**Total Lines**: ~240 (不含代码示例)
**Target Audience**: AI (primary), Framework Contributors (secondary)
