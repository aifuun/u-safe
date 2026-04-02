# cleanup-project Architecture

## Overview

Script-based skill for cleaning temporary files with safety mechanisms (ADR-014 compliant).

**Pattern**: Script Type (score 6/14 on ADR-014 matrix)

**Key Requirements**:
- Safety first: Prevent accidental deletion of important files
- Profile-aware: Different cleanup rules for tauri/nextjs-aws/common
- Testable: File deletion logic must have >60% test coverage
- Transparent: Dry-run mode and confirmation prompts

## Architecture Layers

### 1. Core Logic (scripts/cleanup.py)

**ProjectCleaner Class**:
```python
class ProjectCleaner:
    """
    核心清理类 - 扫描、检查、删除临时文件
    """

    def __init__(self, profile: str, dry_run: bool = False):
        """
        Args:
            profile: "tauri" | "nextjs-aws" | "common"
            dry_run: 仅预览，不实际删除
        """
        self.profile = profile
        self.dry_run = dry_run
        self.whitelist = self._load_whitelist()

    def scan_temp_files(self) -> List[Path]:
        """
        扫描临时文件（基于 profile 规则）

        Returns:
            匹配的文件/目录路径列表
        """
        pass

    def check_safe_to_delete(self, file: Path) -> bool:
        """
        安全检查 - 防止误删重要文件

        Args:
            file: 待检查的文件路径

        Returns:
            True 如果安全（可以删除）
            False 如果不安全（应跳过）
        """
        pass

    def dry_run_cleanup(self) -> Dict:
        """
        预览模式 - 显示将要删除的文件

        Returns:
            {
                "files": List[str],
                "total_size": int (bytes),
                "total_count": int
            }
        """
        pass

    def execute_cleanup(self) -> Dict:
        """
        执行清理 - 实际删除文件

        Returns:
            {
                "deleted": List[str],
                "skipped": List[str],
                "errors": List[str],
                "total_size": int (bytes)
            }
        """
        pass
```

### 2. Safety Protection Mechanism

**Whitelist (Must NOT Delete)**:
```python
PROTECTED_PATTERNS = [
    # Git repository
    '.git/**',

    # Framework settings
    '.claude/settings.json',

    # Environment secrets
    '.env',
    '.env.*',

    # Source code
    '*.py',
    '*.md',
    '*.ts',
    '*.tsx',
    '*.rs',

    # Configuration
    'package.json',
    'Cargo.toml',
    'pyproject.toml',

    # Documentation
    'docs/**/*.md',
    'README.md'
]
```

**Blacklist (Allowed to Delete)**:
```python
CLEANUP_RULES = {
    'tauri': [
        'target/**',
        'src-tauri/target/**',
        'node_modules/**',
        '**/.DS_Store',
        '**/__pycache__/**',
        '**/*.pyc',
        '.claude/.work-issue-state.json',
        '.claude/.review-status.json',
        '.claude/.eval-plan-status.json'
    ],
    'nextjs-aws': [
        '.next/**',
        'out/**',
        'cdk.out/**',
        'node_modules/**',
        '.cache/**',
        '.claude/.work-issue-state.json',
        '.claude/.review-status.json',
        '.claude/.eval-plan-status.json'
    ],
    'common': [
        '**/.DS_Store',
        '**/Thumbs.db',
        '**/__pycache__/**',
        '**/*.pyc',
        '.claude/.work-issue-state.json',
        '.claude/.review-status.json',
        '.claude/.eval-plan-status.json'
    ]
}
```

**Safety Check Logic**:
```python
def check_safe_to_delete(self, file: Path) -> bool:
    """
    双重检查：whitelist 和 blacklist
    """
    # Step 1: Whitelist check (高优先级)
    if matches_any_pattern(file, PROTECTED_PATTERNS):
        return False  # 绝对不删除

    # Step 2: Blacklist check (允许删除)
    cleanup_patterns = CLEANUP_RULES[self.profile]
    if matches_any_pattern(file, cleanup_patterns):
        return True  # 可以删除

    # Step 3: 未匹配任何规则 - 默认不删除（保守策略）
    return False
```

### 3. Workflow

**Execution Flow**:
```
1. Detect Profile (docs/project-profile.md or feature files)
   ↓
2. Initialize ProjectCleaner(profile, dry_run)
   ↓
3. Scan Temp Files (scan_temp_files)
   ↓
4. Safety Check (check_safe_to_delete for each file)
   ↓
5. Preview (dry_run_cleanup) OR Execute (execute_cleanup)
   ↓
6. Report (files deleted, skipped, errors)
```

**Error Handling**:
- **Permission errors**: Skip file, log warning, continue
- **Path not found**: Skip, log warning (already deleted?)
- **I/O errors**: Skip, log error with reason
- **Critical errors** (profile detection fails): Abort with clear message

### 4. Testing Strategy

**Test Coverage Target: >60%**

**Test Categories**:

1. **Safety Tests** (test_cleanup_safety.py):
   ```python
   def test_protected_files_not_deleted():
       """重要文件绝对不删除"""

   def test_git_directory_protected():
       """.git/ 目录受保护"""

   def test_source_code_protected():
       """*.py, *.md 文件受保护"""

   def test_env_files_protected():
       """.env 文件受保护"""
   ```

2. **Functionality Tests**:
   ```python
   def test_scan_temp_files():
       """扫描逻辑正确"""

   def test_dry_run_preview():
       """Dry-run 模式不实际删除"""

   def test_execute_cleanup():
       """实际删除逻辑正确"""
   ```

3. **Profile Tests**:
   ```python
   def test_tauri_profile_rules():
       """Tauri profile 规则正确"""

   def test_nextjs_aws_profile_rules():
       """Next.js-AWS profile 规则正确"""
   ```

4. **Edge Cases**:
   ```python
   def test_nonexistent_file():
       """文件不存在时不报错"""

   def test_permission_error():
       """权限错误时优雅降级"""
   ```

## ADR-014 Compliance

**Score: 6/14** - Script Type

| Criterion | Score | Reason |
|-----------|-------|--------|
| **Logic Complexity** | 2/3 | 文件扫描 + 安全检查逻辑复杂 |
| **File Operations** | 2/2 | 删除文件和目录 |
| **Safety Risk** | 2/2 | 误删可能丢失代码 |
| **Testability** | 0/2 | 原 SKILL.md 无法测试 |
| **Profile Dependency** | 0/2 | 需要 profile-aware |
| **External Tools** | 0/2 | 使用 find, du, git |
| **Error Handling** | 0/1 | 需要健壮的错误处理 |

**Refactor Goals**:
- ✅ Extract logic to Python script (testable)
- ✅ Add safety mechanism (whitelist + confirmation)
- ✅ Add comprehensive tests (>60% coverage)
- ✅ Keep SKILL.md < 500 lines (AI instructions only)

## File Structure

```
.claude/skills/cleanup-project/
├── SKILL.md                  # AI instructions (< 500 lines)
├── ARCHITECTURE.md           # This file
├── scripts/
│   └── cleanup.py            # Core logic (NEW)
└── tests/
    └── test_cleanup_safety.py # Safety tests (NEW)
```

## References

- **ADR-014**: Script Type Pattern (score 6-10)
- **Parent Issue**: #403 (Skill refactoring batch)
- **Dependencies**: #409 (auto-solve-issue), #410 (manage-rules) ✅

---

**Version**: 1.0.0
**Last Updated**: 2026-03-30
**Compliance**: ADR-014 ✅
