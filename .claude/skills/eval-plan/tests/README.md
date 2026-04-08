# eval-plan 测试套件

> 基于 ADR-020 的完整测试套件，用于验证 eval-plan 技能的所有功能

## 📋 概述

本测试套件为 eval-plan 技能提供全面测试覆盖，包括：

- **功能测试** (8 个测试) - 核心评估功能
- **参数测试** (4 个测试) - 命令行参数验证
- **安全测试** (5 个测试) - 安全机制验证
- **错误处理测试** (5 个测试) - 异常场景处理
- **集成测试** (3 个测试) - 端到端工作流

**总计**: 25+ 个测试用例

## 🚀 快速开始

### 1. 环境准备

```bash
# 激活虚拟环境
source /Users/woo/dev/ai-dev/.venv/bin/activate

# 确认依赖已安装
pip list | grep pytest
# 应看到:
# pytest        9.0.2
# pytest-mock   3.15.1
```

### 2. 运行所有测试

```bash
# 从 ai-dev 根目录运行
cd /Users/woo/dev/ai-dev

# 运行所有 eval-plan 测试
pytest .claude/skills/eval-plan/tests/

# 或使用完整路径（从任何位置）
pytest /Users/woo/dev/ai-dev/.claude/skills/eval-plan/tests/
```

### 3. 运行特定测试

```bash
# 运行功能测试
pytest .claude/skills/eval-plan/tests/test_functional.py

# 运行参数测试
pytest .claude/skills/eval-plan/tests/test_arguments.py

# 运行安全测试
pytest .claude/skills/eval-plan/tests/test_safety.py

# 运行错误处理测试
pytest .claude/skills/eval-plan/tests/test_error_handling.py

# 运行集成测试
pytest .claude/skills/eval-plan/tests/test_integration.py
```

## 📊 测试覆盖率

### 运行带覆盖率的测试

```bash
# 生成覆盖率报告
pytest .claude/skills/eval-plan/tests/ --cov --cov-report=term-missing

# 生成 HTML 覆盖率报告
pytest .claude/skills/eval-plan/tests/ --cov --cov-report=html

# 查看 HTML 报告
open htmlcov/index.html
```

### 覆盖率目标

根据 ADR-015 Python 测试环境标准：

| 组件 | 目标覆盖率 | 当前状态 |
|------|-----------|---------|
| 核心功能 | 80%+ | 🎯 |
| 参数处理 | 80%+ | 🎯 |
| 错误处理 | 80%+ | 🎯 |
| 整体 | 80%+ | 🎯 |

## 🧪 测试分类

### 按标记运行

测试使用 pytest markers 进行分类：

```bash
# 仅运行单元测试（快速）
pytest .claude/skills/eval-plan/tests/ -m unit

# 仅运行功能测试
pytest .claude/skills/eval-plan/tests/ -m functional

# 仅运行集成测试
pytest .claude/skills/eval-plan/tests/ -m integration

# 排除慢测试
pytest .claude/skills/eval-plan/tests/ -m "not slow"
```

### 可用标记

| 标记 | 描述 | 示例 |
|------|------|------|
| `unit` | 单元测试（快速、隔离） | 参数验证、数据结构 |
| `functional` | 功能测试（核心特性） | 架构对齐、覆盖率检查 |
| `integration` | 集成测试（端到端） | 完整评估流程 |
| `parametrize` | 参数化测试 | 多种输入组合 |
| `slow` | 慢速测试 | 大规模集成场景 |

## 📁 测试文件结构

```
.claude/skills/eval-plan/tests/
├── README.md                    # 本文件
├── conftest.py                  # 共享 fixtures
├── pytest.ini                   # pytest 配置
├── test_functional.py           # 功能测试（8个）
├── test_arguments.py            # 参数测试（4个）
├── test_safety.py               # 安全测试（5个）
├── test_error_handling.py       # 错误处理测试（5个）
└── test_integration.py          # 集成测试（3个）
```

## 🔧 测试配置

### pytest.ini

测试配置在 `pytest.ini` 中定义：

- **测试发现**: 自动发现 `test_*.py` 文件
- **覆盖率**: 目标 80%+
- **输出格式**: 详细模式 (`-v`)
- **报告**: HTML + 终端

### conftest.py

共享 fixtures 包括：

| Fixture | 描述 | 用途 |
|---------|------|------|
| `temp_dir` | 临时目录 | 文件操作测试 |
| `mock_plan_excellent` | 优秀计划 | 测试高分场景 |
| `mock_plan_good` | 良好计划 | 测试中等分场景 |
| `mock_plan_poor` | 劣质计划 | 测试低分场景 |
| `mock_architecture_rules` | 架构规则 | 测试架构验证 |
| `mock_status_file` | 状态文件 | 测试状态管理 |

## 📝 测试详情

### 1. 功能测试 (`test_functional.py`)

测试核心评估功能，基于 SKILL.md Overview 章节：

```python
# 测试 1: 架构对齐验证 (40 分)
test_reads_architecture_rules_correctly()
test_perfect_architecture_alignment_scores_40()

# 测试 2: 验收标准覆盖 (30 分)
test_parses_issue_acceptance_criteria_correctly()
test_100_percent_coverage_scores_30()

# 测试 3: 任务依赖验证 (15 分)
test_detects_circular_dependencies()
test_validates_task_order_is_reasonable()

# 测试 4: 最佳实践评估 (10 分)
test_checks_error_handling_presence()
test_checks_logging_presence()

# 测试 5: 任务清晰度 (5 分)
test_specific_tasks_score_higher()
test_vague_tasks_score_lower()

# 测试 6: 评分报告
test_calculates_total_score_0_to_100()
test_report_format_is_correct()

# 测试 7: 状态文件
test_creates_status_file()
test_status_file_contains_required_fields()

# 测试 8: 版本字段验证
test_detects_version_in_frontmatter()
test_validates_version_format()
```

### 2. 参数测试 (`test_arguments.py`)

测试命令行参数处理，基于 SKILL.md Arguments 章节：

```python
# issue-number 参数
test_missing_issue_number_raises_error()
test_valid_issue_number_is_accepted()

# --strict 选项
test_strict_mode_treats_recommendations_as_blocking()
test_strict_mode_rejects_score_below_95()

# --json 选项
test_json_output_format_is_valid()
test_json_includes_all_required_fields()

# --mode=auto 选项
test_auto_mode_triggers_auto_fix_when_score_90_or_above()
test_auto_fix_applies_minor_corrections()
```

### 3. 安全测试 (`test_safety.py`)

测试安全机制，基于 SKILL.md Safety Features 章节：

```python
# 计划结构验证
test_rejects_plan_without_tasks_section()
test_accepts_valid_plan_structure()

# 循环依赖检测
test_detects_simple_circular_dependency()
test_detects_complex_circular_dependency()

# 错误恢复机制
test_saves_checkpoint_before_each_task()
test_resumes_from_last_checkpoint()

# 失败限制
test_retries_up_to_3_times()
test_stops_after_max_retries()

# 状态文件管理
test_creates_status_file_on_completion()
test_atomic_status_file_write()
```

### 4. 错误处理测试 (`test_error_handling.py`)

测试异常场景，基于 SKILL.md Error Handling 章节：

```python
# 计划文件缺失
test_raises_error_when_plan_file_not_found()
test_suggests_running_start_issue()

# 无效 issue number
test_handles_issue_detection_failure()
test_validates_issue_exists_on_github()

# 状态文件写入失败
test_handles_permission_denied_error()
test_retries_write_on_transient_error()

# GitHub API 错误
test_handles_authentication_failure()
test_handles_rate_limit_exceeded()

# 状态文件过期
test_validates_90_minute_expiration()
test_warns_on_expired_status()
```

### 5. 集成测试 (`test_integration.py`)

测试完整工作流，基于 SKILL.md Usage Examples 章节：

```python
# Example 1: 优秀计划 (95 分)
test_excellent_plan_full_workflow()
test_excellent_plan_no_blocking_issues()

# Example 2: 良好计划 (82 分)
test_good_plan_full_workflow()
test_good_plan_has_recommendations()

# Example 3: 需要改进计划 (58 分)
test_poor_plan_full_workflow()
test_poor_plan_has_blocking_issues()
```

## 🐛 调试测试

### 详细输出

```bash
# 显示所有输出（包括 print）
pytest .claude/skills/eval-plan/tests/ -s

# 显示最详细的输出
pytest .claude/skills/eval-plan/tests/ -vv

# 显示完整回溯
pytest .claude/skills/eval-plan/tests/ --tb=long
```

### 运行单个测试

```bash
# 运行特定测试类
pytest .claude/skills/eval-plan/tests/test_functional.py::TestArchitectureAlignment

# 运行特定测试方法
pytest .claude/skills/eval-plan/tests/test_functional.py::TestArchitectureAlignment::test_reads_architecture_rules_correctly
```

### 失败时停止

```bash
# 第一个失败时停止
pytest .claude/skills/eval-plan/tests/ -x

# 2 个失败后停止
pytest .claude/skills/eval-plan/tests/ --maxfail=2
```

### 仅运行上次失败的测试

```bash
pytest .claude/skills/eval-plan/tests/ --lf
```

## 📈 持续集成

### GitHub Actions 集成

测试可集成到 CI/CD 流程：

```yaml
# .github/workflows/test-eval-plan.yml
name: Test eval-plan

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.14'
      - name: Install dependencies
        run: |
          pip install pytest pytest-mock pytest-cov
      - name: Run tests
        run: |
          pytest .claude/skills/eval-plan/tests/ --cov --cov-fail-under=80
```

## 🔍 故障排查

### 常见问题

**问题 1: ModuleNotFoundError**

```bash
# 确保在正确的目录运行
cd /Users/woo/dev/ai-dev

# 或使用绝对路径
pytest /Users/woo/dev/ai-dev/.claude/skills/eval-plan/tests/
```

**问题 2: Fixture not found**

```bash
# 确保 conftest.py 在 tests/ 目录
ls .claude/skills/eval-plan/tests/conftest.py
```

**问题 3: 虚拟环境未激活**

```bash
# 激活虚拟环境
source /Users/woo/dev/ai-dev/.venv/bin/activate

# 验证
which python  # 应指向 .venv
```

## 📚 参考文档

- **ADR-015**: Python 测试环境标准
- **ADR-020**: Skill 测试驱动文档标准
- **SKILL.md**: eval-plan 功能文档
- **pytest 文档**: https://docs.pytest.org/

## ✅ 验收标准

根据 Issue #520 验收标准：

- [x] 所有功能测试通过（8 个功能测试）
- [x] 所有参数测试通过（4 个参数测试）
- [x] 所有安全测试通过（5 个安全测试）
- [x] 所有错误处理测试通过（5 个错误测试）
- [x] 所有集成测试通过（3 个集成测试）
- [ ] 测试覆盖率 ≥ 80% ← 待验证
- [x] 所有测试文档完整
- [ ] CI/CD 集成（如果适用）

---

**维护者**: AI Development Framework Team
**最后更新**: 2026-04-07
**版本**: 1.0.0
