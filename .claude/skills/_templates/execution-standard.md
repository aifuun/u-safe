# Python 执行标准（零例外）

> **强制执行标准** - 所有 AI 开发框架中的 Python 代码必须通过 `uv run` 执行

## 概述

本标准强制所有 Python 代码使用 `uv run` 执行，**零例外**。这遵循 [ADR-017](../../docs/ADRs/017-uv-dependency-management.md) 和 [ADR-018](../../docs/ADRs/018-mandatory-uv-execution.md) 的完全统一方案。

**核心原则：**
> "Complete unification provides superior long-term value despite higher upfront cost." - ADR-017

**5 年 ROI（来自 ADR-017 分析）：**
- ✅ **维护成本**：节省 12 小时
- ✅ **认知负载**：减少 60%
- ✅ **文档一致性**：100%
- ✅ **性能影响**：+10ms（用户无感知）

## 执行规范

### 1. 正式脚本（推荐）

对于有明确功能的 Python 代码，创建正式脚本文件：

```bash
# ✅ 正确 - 使用 uv run 执行脚本
uv run scripts/update_skills.py ../target-project

uv run scripts/generate_rules.py --profile tauri

uv run scripts/validate_plans.py issue-479-plan.md
```

**文件结构示例：**
```
.claude/skills/my-skill/
├── SKILL.md
└── scripts/
    ├── main.py          # 主入口
    ├── utils.py         # 辅助函数
    └── config.py        # 配置
```

**PEP 723 依赖声明（如有外部依赖）：**
```python
#!/usr/bin/env python3
# /// script
# dependencies = [
#   "pyyaml>=6.0",
#   "requests>=2.28.0"
# ]
# ///

import yaml
import requests

# 脚本实现...
```

### 2. 简单一行代码

对于临时或简单操作，使用 `uv run -c`：

```bash
# ✅ 正确 - 使用 uv run -c 执行单行代码
uv run -c "import json; print(json.dumps({'status': 'ok'}))"

uv run -c "from datetime import datetime; print(datetime.now().isoformat())"

# 提取信息示例
uv run -c "import sys; sys.path.insert(0, '.claude/skills/_scripts'); from utils.version import get_version; print(get_version('1.2.3'))"
```

**何时使用：**
- 快速数据转换（JSON、日期格式化）
- 简单信息提取（版本号、配置值）
- 临时验证操作

### 3. 共享工具调用

如果已经在 `uv run` 环境中（如通过 `uv run scripts/main.py` 启动），可以直接 import 共享工具：

```python
# 在 scripts/my_script.py 中（已通过 uv run 启动）

import sys
sys.path.insert(0, '.claude/skills/_scripts')

# ✅ 正确 - 已在 uv run 环境中，直接 import
from utils.sync import filter_framework_only_skills
from utils.version import validate_version_format
from framework.issue_detector import detect_issue_number

# 使用共享工具
skills_to_sync, excluded = filter_framework_only_skills(skill_dirs)
is_valid = validate_version_format("1.2.3")
issue_num = detect_issue_number()
```

**注意：**
- 这仅适用于**脚本内部代码**
- 脚本本身必须通过 `uv run scripts/xxx.py` 启动
- 不适用于直接在 Shell 中执行的命令

## 禁止使用（零例外）

以下调用方式**完全禁止**：

```bash
# ❌ 禁止 - 直接调用 python3
python3 scripts/update_skills.py

# ❌ 禁止 - 直接调用 python3 -c
python3 -c "import json; print(json.dumps({}))"

# ❌ 禁止 - 无版本号的 python
python scripts/validate.py
python -c "import sys; print(sys.version)"
```

**理由：**
1. **认知负载**：开发者需判断何时用 `python3`、何时用 `uv run`
2. **环境不一致**：`python3` 可能使用系统 Python，`uv run` 使用项目环境
3. **依赖问题**：`python3` 可能找不到 PEP 723 声明的依赖
4. **长期成本**：混合方案 5 年多花 12 小时维护成本

## 实施指南

### 技能文档中的引用

所有 `SKILL.md` 应引用此标准：

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

### Skill Creator 模板

`/skill-creator` 生成的新技能应自动包含：

1. 标准引用（如上）
2. 符合规范的 `scripts/` 目录结构
3. `uv run` 使用示例

### 渐进式更新

**新技能：**
- ✅ 自动符合标准（通过 `/skill-creator`）

**旧技能：**
- ⏳ 在修改时同步更新
- 📋 不强制一次性完成
- 🎯 但明确零例外目标

## 示例对比

### 示例 1：更新技能同步

**❌ 错误方式：**
```bash
# AI 执行时错误地使用 python3
python3 -c "import sys; sys.path.insert(0, '.claude/skills/_scripts'); from utils.sync import filter_framework_only_skills; ..."
```

**✅ 正确方式 A（推荐）：**
```bash
# 创建正式脚本
uv run scripts/sync_skills.py ../target-project
```

**✅ 正确方式 B（简单操作）：**
```bash
# 使用 uv run -c
uv run -c "import sys; sys.path.insert(0, '.claude/skills/_scripts'); from utils.sync import filter_framework_only_skills; print(filter_framework_only_skills([...]))"
```

### 示例 2：版本检测

**❌ 错误方式：**
```bash
python3 -c "import re; print(re.search(r'version: \"(.+)\"', open('SKILL.md').read()).group(1))"
```

**✅ 正确方式：**
```bash
uv run -c "import sys; sys.path.insert(0, '.claude/skills/_scripts'); from utils.version import get_version_from_frontmatter; print(get_version_from_frontmatter(open('SKILL.md').read()))"
```

### 示例 3：Issue 检测

**❌ 错误方式：**
```bash
python3 -c "import re; branch = 'feature/479-xxx'; print(re.search(r'(\d+)', branch).group(1))"
```

**✅ 正确方式：**
```bash
uv run -c "import sys; sys.path.insert(0, '.claude/skills/_scripts'); from framework.issue_detector import detect_issue_number; print(detect_issue_number())"
```

## 相关文档

- **[ADR-017](../../docs/ADRs/017-uv-dependency-management.md)** - UV-based Dependency Management（完全统一决策）
- **[ADR-018](../../docs/ADRs/018-mandatory-uv-execution.md)** - Mandatory UV Execution（强制执行标准）
- **[SKILL_GUIDE.md](../../.claude/guides/workflow/SKILL_GUIDE.md)** - 技能创建指南
- **[PEP 723](https://peps.python.org/pep-0723/)** - Inline script metadata

## 常见问题

### Q: 为什么不允许例外？

**A:** 例外规则会增加认知负担。开发者需要判断"这个场景该用哪个？"，这违背了零认知负载原则。ADR-017 的 5 年 ROI 分析显示，混合方案多花 12 小时维护成本。

### Q: +10ms 性能开销可接受吗？

**A:** 是的。+10ms 对人类完全无感知（人类反应时间 ~200ms）。相比之下，60% 的认知负担减少和 12 小时的长期节省更有价值。

### Q: 简单操作也要用 uv run -c 吗？

**A:** 是的。这确保环境一致性。即使是简单的 JSON 转换，使用 `uv run -c` 也保证了与项目其他部分相同的 Python 版本和环境。

### Q: 如果我只是想快速测试怎么办？

**A:** 即使是快速测试，也建议使用 `uv run -c`。好习惯从一开始养成，避免"临时代码"变成"生产代码"的陷阱。

---

**Last Updated:** 2026-04-03
**Related Issues:** #476, #479
**Related ADRs:** ADR-017, ADR-018
**Version:** 1.0.0
