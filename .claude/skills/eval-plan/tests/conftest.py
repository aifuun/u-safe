"""
Shared pytest fixtures for eval-plan tests.

This conftest provides reusable fixtures for:
- Mock plans with varying quality scores
- Mock issue bodies with acceptance criteria
- Mock status files
- Mock architecture rules
- Helper functions for test setup
"""

import json
import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta


@pytest.fixture
def temp_dir():
    """Provide temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_plan_excellent():
    """Mock plan with excellent quality (95+ score expected)."""
    return """---
version: 1.0.0
issue: 123
title: "feat: Add user authentication"
created: 2026-04-07
status: active
---

# Issue #123: feat: Add user authentication

**GitHub**: https://github.com/test/repo/issues/123
**Branch**: feature/123-add-user-auth
**Worktree**: /tmp/test-worktree
**Started**: 2026-04-07

## 背景

实现用户认证功能，包括登录、登出、会话管理。

## 任务

### Task 1: 创建 AuthService 服务层
- 实现登录逻辑 (src/services/auth.ts)
- 实现登出逻辑
- 添加会话管理
- 单元测试覆盖 90%+

### Task 2: 创建 UserRepository 数据层
- 实现用户查询 (src/repositories/user.ts)
- 实现密码验证
- 错误处理和日志记录
- 单元测试覆盖 90%+

### Task 3: 创建 API 端点
- POST /auth/login (src/routes/auth.ts)
- POST /auth/logout
- GET /auth/session
- 集成测试覆盖

### Task 4: 添加前端集成
- 登录表单组件
- 会话状态管理
- E2E 测试

## 验收标准

- [ ] 用户可以使用邮箱和密码登录
- [ ] 登录后创建会话 token
- [ ] 用户可以登出并清除会话
- [ ] 未授权访问返回 401
- [ ] 所有 API 端点有集成测试

## 架构对齐

- ✅ 遵循三层架构：UI → Service → Repository
- ✅ 依赖方向从外向内
- ✅ 服务层不依赖 UI
- ✅ Repository 隔离数据访问

## 最佳实践

- ✅ 错误处理：每层都有 try-catch
- ✅ 日志记录：关键操作记录日志
- ✅ 输入验证：API 层验证所有输入
- ✅ 测试覆盖：单元测试 + 集成测试
"""


@pytest.fixture
def mock_plan_good():
    """Mock plan with good quality (80-90 score expected)."""
    return """---
version: 1.0.0
issue: 124
title: "fix: Fix login button"
created: 2026-04-07
status: active
---

# Issue #124: fix: Fix login button

## 任务

### Task 1: 修复按钮样式
- 更新 CSS (src/components/LoginButton.css)

### Task 2: 添加测试
- 编写单元测试

## 验收标准

- [ ] 按钮在移动端正常显示
- [ ] 测试覆盖

## 架构对齐

- 遵循组件化架构
"""


@pytest.fixture
def mock_plan_poor():
    """Mock plan with poor quality (< 70 score expected)."""
    return """---
version: 1.0.0
issue: 125
title: "Update authentication"
created: 2026-04-07
status: active
---

# Issue #125: Update authentication

## 任务

### Task 1: 修复认证
- 修复认证问题

### Task 2: 更新代码
- 更新相关代码

## 验收标准

- [ ] 认证正常工作
"""


@pytest.fixture
def mock_issue_body_with_criteria():
    """Mock GitHub issue body with acceptance criteria."""
    return """
## Description

Add user authentication feature.

## Acceptance Criteria

- [ ] Users can log in with email and password
- [ ] Login creates session token
- [ ] Users can log out and clear session
- [ ] Unauthorized access returns 401
- [ ] All API endpoints have integration tests

## Technical Details

Use JWT tokens for session management.
"""


@pytest.fixture
def mock_issue_body_without_criteria():
    """Mock GitHub issue body without acceptance criteria."""
    return """
## Description

Fix the login button styling issue.

## Details

The button doesn't display correctly on mobile devices.
"""


@pytest.fixture
def mock_architecture_rules():
    """Mock architecture rules content."""
    return {
        "layered-architecture.md": """
# Layered Architecture

## Layers

1. UI Layer
2. Service Layer
3. Repository Layer

## Rules

- Dependencies flow inward (UI → Service → Repository)
- Service layer never depends on UI
- Repository layer isolated from business logic
""",
        "dependency-injection.md": """
# Dependency Injection

## Pattern

Use constructor injection for all dependencies.

## Rules

- No global state
- Inject interfaces, not concrete classes
"""
    }


@pytest.fixture
def mock_status_file(temp_dir):
    """Create mock eval-plan status file."""
    status = {
        "timestamp": datetime.now().isoformat(),
        "issue_number": 123,
        "status": "approved",
        "score": 95,
        "breakdown": {
            "architecture": 40,
            "coverage": 30,
            "dependencies": 15,
            "practices": 10,
            "clarity": 5
        },
        "issues_count": {
            "blocking": 0,
            "recommendations": 0
        },
        "valid_until": (datetime.now() + timedelta(minutes=90)).isoformat()
    }

    status_file = temp_dir / ".eval-plan-status.json"
    status_file.write_text(json.dumps(status, indent=2))
    return status_file


@pytest.fixture
def mock_expired_status_file(temp_dir):
    """Create mock expired status file."""
    status = {
        "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
        "issue_number": 123,
        "status": "approved",
        "score": 95,
        "valid_until": (datetime.now() - timedelta(minutes=30)).isoformat()
    }

    status_file = temp_dir / ".eval-plan-status.json"
    status_file.write_text(json.dumps(status, indent=2))
    return status_file


# Helper functions

def create_plan_file(temp_dir, content):
    """Create a plan file with given content."""
    plans_dir = temp_dir / ".claude" / "plans" / "active"
    plans_dir.mkdir(parents=True, exist_ok=True)
    plan_file = plans_dir / "issue-123-plan.md"
    plan_file.write_text(content)
    return plan_file


def create_architecture_rules(temp_dir, rules_dict):
    """Create architecture rules files."""
    rules_dir = temp_dir / ".claude" / "rules" / "architecture"
    rules_dir.mkdir(parents=True, exist_ok=True)

    for filename, content in rules_dict.items():
        rule_file = rules_dir / filename
        rule_file.write_text(content)

    return rules_dir
