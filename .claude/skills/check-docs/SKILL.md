---
name: check-docs
version: "2.0.0"
last-updated: "2026-03-30"
pattern: "script-based"
compliance: "ADR-014"
---

# Check Docs - Validate Documentation Structure

> **脚本化模式 (ADR-014合规)** - 验证逻辑已提取到 `scripts/check_docs.py`

Validate documentation structure compliance with framework standards using Python script.

## Overview

This skill validates documentation structure by delegating to `scripts/check_docs.py`:

**What it does:**
1. **Structure Validation** - Checks required directories (30分)
2. **File Validation** - Verifies mandatory files (40分)
3. **Naming Convention** - Ensures kebab-case, UPPERCASE.md patterns (15分)
4. **ADR Validation** - Sequential numbering check (15分)
5. **Compliance Scoring** - Generates 0-100 score with breakdown
6. **Fix Suggestions** - Provides actionable commands

**Why script-based:**
- 891行 → 简洁的AI指令 + 可测试的Python代码
- ADR-014评分: 9/14 (≥8=脚本化)
- 逻辑复杂度: 37个条件判断
- 可测试性: 单元测试覆盖验证逻辑

**When to use:**
- After `/init-docs` to verify structure
- Before releases to ensure docs complete
- In CI/CD to enforce standards
- Project onboarding validation

## Arguments

```bash
/check-docs [options]
```

**Options:**
- `--verbose` - Detailed file-by-file output
- `--fix` - Auto-fix issues (planned)
- `--profile <name>` - Check specific profile (tauri, nextjs-aws)
- `--json` - JSON output for CI/CD

**Examples:**
```bash
/check-docs                    # Basic validation
/check-docs --verbose          # Detailed output
/check-docs --profile tauri    # Profile-specific
/check-docs --json             # Machine-readable
```

## AI Execution Instructions

**CRITICAL: 使用Python脚本执行验证**

When user invokes `/check-docs`, AI MUST:

### Step 1: 解析参数

```python
import argparse

# Parse user arguments
args = parse_args_from_skill_invocation()
# --verbose, --fix, --profile, --json

# Build script command
cmd_parts = ['python3', '.claude/skills/check-docs/scripts/check_docs.py']

if args.get('verbose'):
    cmd_parts.append('--verbose')
if args.get('profile'):
    cmd_parts.extend(['--profile', args['profile']])
if args.get('json'):
    cmd_parts.append('--json')
if args.get('fix'):
    cmd_parts.append('--fix')

script_cmd = ' '.join(cmd_parts)
```

### Step 2: 执行Python脚本

```python
# Run validation script
result = Bash(script_cmd, description="Run documentation validation")

# Script handles all validation logic:
# - Profile detection
# - Structure validation (directories)
# - File existence checks
# - Naming convention validation
# - ADR numbering validation
# - Scoring (0-100)
# - Fix generation
# - Output formatting
```

### Step 3: 解释结果给用户

```python
# Parse script output
if args.get('json'):
    # JSON mode - pass through
    print(result.stdout)
else:
    # Human-readable mode
    # Script already formatted output
    print(result.stdout)

    # Add next steps guidance
    if exit_code != 0:
        print("\n💡 Next steps:")
        print("  1. Review issues above")
        print("  2. Apply suggested fixes")
        print("  3. Re-run validation: /check-docs")
    else:
        print("\n✅ Documentation structure is compliant!")

# Exit with script's exit code
sys.exit(result.exit_code)
```

## Validation Dimensions (4个)

脚本验证4个维度，总分100:

### 1. Structure (30分)

**检查**: 必需目录存在

**Profile-aware**:
- 所有profiles: `docs/, docs/ADRs/, docs/architecture/, docs/api/, docs/guides/, docs/diagrams/`
- tauri: `docs/desktop/`
- tauri-aws: `docs/desktop/, docs/aws/`
- nextjs-aws: `docs/aws/`

**评分**: -5分/缺失目录

### 2. Files (40分)

**检查**: 必需文件存在

**Profile-aware**:
- tauri: 7个文件 (README, PRD, ARCHITECTURE, API, SETUP, TEST_PLAN)
- nextjs-aws: 8个文件 (+ DEPLOYMENT.md)

**评分**: -8分/缺失文件

### 3. Naming (15分)

**检查**: 命名规范

**规则**:
- 核心文档: UPPERCASE.md (README, PRD, etc.)
- 辅助文档: kebab-case.md (user-stories, decision-log)

**评分**: -5分/违规

### 4. ADRs (15分)

**检查**: ADR编号连续性

**规则**: 001, 002, 003, ... 无断档

**评分**: -5分/断档

## Script Output Format

### Human-Readable (默认)

```
============================================================
📋 Documentation Structure Validation Report
============================================================

✅ Overall Score: 85/100 (85.0%)
Profile: tauri
Issues: 3 | Fixes available: 3

📊 Dimension Breakdown:
  ✅ Structure     30/30
  ⚠️  Files        32/40
  ✅ Naming        15/15
  ⚠️  Adrs         10/15

⚠️  Issues Found (3):
  - Missing file: docs/API.md
  - Missing file: docs/SETUP.md
  - ADR numbering gap: 002 → 004 (missing 1)

🔧 Suggested Fixes (3):
  /init-docs --force
  ... and 2 more (use --verbose)

💡 Auto-fix: python check_docs.py --fix

============================================================
```

### JSON (--json)

```json
{
  "profile": "tauri",
  "total_score": 85,
  "max_score": 100,
  "percentage": 85.0,
  "passed": true,
  "breakdown": {
    "structure": {"score": 30, "max": 30, "passed": true},
    "files": {"score": 32, "max": 40, "passed": false},
    "naming": {"score": 15, "max": 15, "passed": true},
    "adrs": {"score": 10, "max": 15, "passed": false}
  },
  "issues_count": 3,
  "fixes_count": 3,
  "issues": ["Missing file: docs/API.md", ...],
  "fixes": [{"type": "init-docs", "command": "/init-docs --force", ...}]
}
```

## Integration

**Pairs with /init-docs:**
```
/init-docs        # 创建文档结构
/check-docs       # 验证结构合规 ← THIS SKILL
/check-docs --fix # 自动修复issues
```

**CI/CD Usage:**
```bash
# In .github/workflows/docs-check.yml
- name: Validate docs
  run: |
    uv run .claude/skills/check-docs/scripts/check_docs.py --json > report.json
    if [ $? -ne 0 ]; then
      echo "Documentation validation failed"
      exit 1
    fi
```

## Error Handling

脚本处理常见错误:

**Docs目录不存在:**
```
Score: 0/100
Issues: docs/ directory not found
Fix: /init-docs to create structure
```

**Profile文件损坏:**
```
Fallback to 'minimal' profile
Warning: docs/project-profile.md not readable
```

**权限问题:**
```
Error: Permission denied reading docs/
Fix: Check file permissions
```

## Script Architecture

**模块结构:**
```
scripts/check_docs.py
├── DocsChecker (主类)
│   ├── validate_structure() → 30分
│   ├── validate_files() → 40分
│   ├── validate_naming() → 15分
│   ├── validate_adrs() → 15分
│   └── run_full_validation() → 总分
├── detect_profile() → 自动检测
├── output_human_readable() → 格式化输出
└── main() → CLI入口
```

**数据类:**
- `ValidationResult`: 验证结果 (score, issues, fixes)
- `Fix`: 修复建议 (type, command, description)

**测试覆盖** (见 `tests/test_check_docs.py`):
- 单元测试: 4个验证函数
- 集成测试: 完整workflow
- 边界测试: 空目录、无ADR、命名边界

## Performance

- **Script startup**: < 100ms
- **Validation time**: 50-200ms (取决于文件数量)
- **Total time**: < 1s (比890行AI指令快~50%)

**优势:**
- ✅ 可测试 (单元测试覆盖)
- ✅ 可维护 (Python代码 vs 891行markdown)
- ✅ 可复用 (其他skills可调用)
- ✅ 性能稳定 (不依赖AI推理)

## Migration Notes

**从v1.1.0 (AI指令模式) → v2.0.0 (脚本模式):**

**Breaking changes:**
- 无 (API兼容)

**Improvements:**
- ✅ 891行 → ~200行 SKILL.md
- ✅ 验证逻辑可单元测试
- ✅ 性能提升 ~50%
- ✅ 符合ADR-014标准

**备份**: 旧版本保存在 `SKILL.md.backup`

## Best Practices

1. **Run after /init-docs** - 验证生成的结构
2. **Include in CI/CD** - 自动化合规检查
3. **Use --verbose for debugging** - 详细诊断
4. **Trust the script** - 经过测试验证

## Related Skills

- **/init-docs** - 创建文档结构 (互补skill)
- **/manage-docs** - 管理文档内容
- **/manage-adrs** - ADR管理

## Script Documentation

**详细脚本文档**: 见 `scripts/check_docs.py` docstrings

**运行测试**:
```bash
pytest .claude/skills/check-docs/tests/
```

**Lint检查**:
```bash
pylint .claude/skills/check-docs/scripts/check_docs.py
```

---

**Version:** 2.0.0 (脚本化重构)
**Pattern:** Script-Based (ADR-014合规)
**Compliance:** ADR-014 ✅
**Last Updated:** 2026-03-30
**Changelog:**
- v2.0.0 (2026-03-30): 脚本化重构 - 891行 → ~200行 + Python脚本 (Issue #420)
- v1.1.0 (2026-03-15): 添加auto-fix功能
- v1.0.0: 初版 (AI执行指令型，891行)

**Migration:** ADR-014评分9/14 → 脚本化模式 | 备份: SKILL.md.backup
