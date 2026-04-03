# Skills Migration Guide

> AI执行型 → 脚本型迁移手册

**Version**: 1.0.0 | **Last Updated**: 2026-03-30

---

## Quick Reference

| 当前模式 | 目标 | 指南章节 |
|---------|------|---------|
| AI执行型 (大型,>800行) | 脚本型 | [完整迁移](#完整迁移ai执行型-脚本型) |
| AI执行型 (中型,500-800行) | 文档拆分 | [文档拆分](#文档拆分策略) |
| AI执行型 (小型,<500行) | 添加标注 | [添加代码块标注](#添加代码块标注) |
| 脚本型 (需优化) | 优化 | [脚本型优化](#脚本型skill优化) |

---

## 添加代码块标注

**适用**: 保持AI执行型的小型skills (<500行)
**工作量**: 每个skill 2-4小时

### 步骤

1. **识别代码块** - 找出所有Python/Bash代码块
2. **分类标注** - 按类型添加注释
3. **验证** - 确保AI能正确理解

### 标注类型

\`\`\`python
# AI-EXECUTABLE - AI直接执行
import sys
sys.path.insert(0, '.claude/skills/_scripts')
from framework.issue_detector import detect_issue_number
issue_num = detect_issue_number()
\`\`\`

\`\`\`python
# EXAMPLE-ONLY - 仅供参考
def example_pattern():
    # 实际实现在 _scripts/utils/module.py
    pass
\`\`\`

\`\`\`python
# SHARED-LOGIC - 应提取到共享模块
# TODO: 提取到 _scripts/utils/validation.py (使用于3+个skills)
def validate_something():
    pass
\`\`\`

---

## 文档拆分策略

**适用**: 500-800行的AI执行型skills
**工作量**: 每个skill 6-8小时

### 拆分步骤

1. **保留在SKILL.md** (<500行):
   - Overview
   - Arguments
   - AI Execution Instructions (核心步骤)
   - 常用示例 (2-3个)
   - Top 3错误处理

2. **移动到REFERENCE.md**:
   - 详细架构说明
   - 边界案例
   - 所有高级示例
   - 性能优化细节
   - 完整troubleshooting

### 示例

\`\`\`markdown
<!-- SKILL.md -->
## Advanced Topics

详细信息请参考:
- [架构设计](./REFERENCE.md#architecture)
- [错误场景](./REFERENCE.md#error-scenarios)
- [性能优化](./REFERENCE.md#performance)

<!-- REFERENCE.md -->
# Reference - Skill Name

## Architecture
[详细架构文档...]

## Error Scenarios
[边界案例处理...]
\`\`\`

---

## 完整迁移(AI执行型→脚本型)

**适用**: >800行复杂skills
**工作量**: 每个skill 20-40小时

### 迁移步骤 (8步)

#### Step 1: 评估 (2h)
- 使用ADR-014评分矩阵确认需迁移
- 识别可复用逻辑
- 制定迁移计划

#### Step 2: 创建目录结构 (0.5h)
\`\`\`bash
.claude/skills/<skill-name>/
├── SKILL.md          # 简化为使用指南
├── scripts/
│   ├── main.py      # 主脚本
│   └── tests/
│       └── test_main.py
\`\`\`

#### Step 3: 提取代码到Python (8-16h)
- 从SKILL.md提取所有Python代码块
- 添加类型注解
- 添加文档字符串
- 重构为可测试模块

#### Step 4: 简化SKILL.md (4h)
- 删除内嵌代码（保留示例）
- 添加脚本调用说明
- 保持<500行

#### Step 5: 编写测试 (8-12h)
- 单元测试（覆盖率>60%）
- 集成测试
- 边界案例测试

#### Step 6: 提取共享逻辑 (2-4h)
- 识别重复代码
- 提取到_scripts/
- 更新引用

#### Step 7: 验证 (2h)
- 运行测试
- 手动测试workflow
- 验证文档准确性

#### Step 8: 更新版本 (0.5h)
- 更新version号
- 添加CHANGELOG
- 标记breaking changes

### 迁移示例: eval-plan

**Before (AI执行型):**
- SKILL.md: 925行
- 包含大量Python代码

**After (脚本型):**
- SKILL.md: ~300行 (使用指南)
- scripts/eval_plan.py: ~400行
- scripts/tests/test_eval_plan.py: ~200行
- 测试覆盖率: 75%

---

## 脚本型Skill优化

**适用**: 已是脚本型但需改进的skills
**工作量**: 每个skill 8-15小时

### 优化检查清单

- [ ] 测试覆盖率 >60%
- [ ] SKILL.md <500行
- [ ] 无代码重复
- [ ] 使用类型注解
- [ ] 错误处理完整
- [ ] 文档与代码同步

### 优化步骤

1. **添加测试** (如果缺失)
2. **拆分大型脚本** (>300行)
3. **提取共享逻辑**
4. **优化SKILL.md** (简化文档)

---

## 共享逻辑提取示例

### 示例1: JSON处理

**Before (重复3+次):**
\`\`\`python
# 在多个skills的SKILL.md中重复
import json
with open(file_path, 'r') as f:
    data = json.load(f)
\`\`\`

**After (提取到_scripts/utils/json_handler.py):**
\`\`\`python
# _scripts/utils/json_handler.py
def read_json(file_path: str) -> dict:
    with open(file_path, 'r') as f:
        return json.load(f)

# 在skills中使用
from _scripts.utils.json_handler import read_json
data = read_json(file_path)
\`\`\`

### 示例2: Issue号检测

**Before (重复5+次):**
\`\`\`python
# 每个skill都实现一遍
branch = subprocess.check_output(['git', 'branch', '--show-current'])
match = re.search(r'(\d+)', branch)
issue_num = int(match.group(1))
\`\`\`

**After (已提取到_scripts/framework/issue_detector.py):**
\`\`\`python
from _scripts.framework.issue_detector import detect_issue_number
issue_num = detect_issue_number()
\`\`\`

---

## 常见问题

### Q: 如何判断是否应迁移？
A: 使用ADR-014评分矩阵，总分≥10建议迁移。

### Q: 迁移会破坏向后兼容性吗？
A: Skill调用方式不变（仍是/skill-name），但内部实现改变。

### Q: 如何处理中断的迁移？
A: 保留原SKILL.md备份，迁移失败可回滚。

### Q: 测试覆盖率要求多高？
A: 脚本型最低60%，核心功能建议80%+。

---

## 版本历史

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-30 | 初始版本 |
