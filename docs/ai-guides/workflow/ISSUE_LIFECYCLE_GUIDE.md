# Issue Lifecycle Guide

> AI reference for executing the complete issue workflow - from planning to completion

---
skills_versions:
  start-issue: "2.2.0"
  eval-plan: "1.3.0"
  execute-plan: "3.1.0"
  review: "2.2.0"
  finish-issue: "3.1.0"
  auto-solve-issue: "2.0.0"
  solve-issues: "1.0.0"
last_synced: "2026-03-24"
---

## 完整工作流 (AI 执行顺序)

### Phase 1: Planning - /start-issue

**AI 执行步骤**:
1. 创建 worktree 分支: `git worktree add ../repo-{N}-{title} -b feature/{N}-{title}`
2. 读取 GitHub issue: `gh issue view {N} --json number,title,body`
3. 生成实现计划（8-12 个任务）到 worktree 路径
4. 创建计划文件: `{worktree}/.claude/plans/active/issue-{N}-plan.md`
5. 分析依赖和风险，记录 worktree 元数据

**质量标准 (AI 检查)**:
- [ ] 任务数 ≤8 (理想 3-5)
- [ ] 每个任务有验收标准
- [ ] 包含测试任务
- [ ] Worktree 路径记录在计划元数据中

**输出**: Worktree 创建成功，分支已推送，计划文件就绪

---

### Phase 1.5: Validation - /eval-plan (checkpoint)

**AI 执行步骤**:
1. 读取计划文件（从 worktree 路径）
2. 检查架构对齐（与 .claude/rules/architecture/ 比对）
3. 检查完整性（所有验收标准有对应任务）
4. 生成评分（0-100）

**评分阈值 (AI 判断)**:
- ≥95: 优秀 → 自动继续执行
- 90-94: 良好 → 可选修复（auto 模式自动修复微小问题）
- 70-89: 需改进 → 停止，必须修复（interactive 模式）
- <70: 不合格 → 停止，重新规划

**评分维度** (满分 100):
- Architecture alignment: 40 分
- Coverage: 30 分
- Dependencies: 15 分
- Best practices: 10 分
- Clarity: 5 分

**Auto-fix 机制** (score ≥90):
- 自动修复类型: missing_todo, incomplete_test, format_issue, missing_file_ref, logic_gap
- 不修复类型: architecture_violation, missing_acceptance_criteria, circular_dependency

**输出**: `.claude/.eval-plan-status.json` (有效期 90 分钟)

---

### Phase 2: Implementation - /execute-plan

**AI 执行步骤**:
1. 读取计划（从 worktree 路径）
2. 创建 todo list（TaskCreate + 依赖链）
3. 逐个执行任务：
   - TaskUpdate(in_progress)
   - 执行实现（使用 worktree 路径）
   - 验证完成（tests, lint, build if applicable）
   - TaskUpdate(completed)
4. 所有任务完成进入 Phase 2.5

**最佳实践 (AI 遵循)**:
- 所有文件操作使用 worktree 绝对路径
- Git 操作使用 `-C {worktree_path}` 标志
- 每个任务完成后运行快速验证
- 保持任务粒度合理（单一职责）

**输出**: 所有代码变更在 worktree 中，未提交

---

### Phase 2.5: Review - /review (checkpoint)

**AI 执行步骤**:
1. 运行静态检查（types, lint）
2. 运行测试（unit, integration）
3. 检查代码质量（复杂度，重复）
4. 生成评分（0-100）

**评分阈值 (AI 判断)**:
- ≥90: 通过 → 自动继续 finish-issue
- 80-89: 可接受 → interactive 模式询问
- <80: 不合格 → 停止，修复问题

**检查维度** (满分 100):
- Quality gates: TypeScript, tests, linting
- ADR compliance: 检查 docs/ADRs/ 合规性
- Best practices: Error handling, logging, docs
- Security: Input validation, no hardcoded secrets
- Performance: No N+1 queries, reasonable complexity
- Completeness: All acceptance criteria met

**输出**: `.claude/.review-status.json` (有效期 90 分钟)

---

### Phase 3: Completion - /finish-issue

**AI 执行步骤**:
1. 创建 commit (worktree 中):
   ```bash
   git -C {worktree_path} add .
   git -C {worktree_path} commit -m "feat: {title} (Issue #{N})\n\nFixes #{N}\n\nCo-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
   ```
2. Push 到远程: `git -C {worktree_path} push origin {branch}`
3. 创建 PR: `gh pr create --title "..." --body "..."`
4. 合并到 main: `gh pr merge --squash --delete-branch`
5. 关闭 issue: `gh issue close {N}`
6. 清理 worktree: `git worktree remove {worktree_path}`
7. 删除本地分支: `git branch -D {branch}`
8. 删除状态文件: `.eval-plan-status.json`, `.review-status.json`
9. 删除所有 todos: TaskUpdate(status="deleted")

**Commit 消息格式**:
```
{type}: {title} (Issue #{N})

{详细描述}

Fixes #{N}

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**输出**: PR 已合并，issue 已关闭，worktree 已清理，回到 main 分支

---

## 工作流决策树 (AI 判断)

```
用户请求 → 判断模式
    ├─ 自动模式: /solve-issues #123 或 /auto-solve-issue #123
    │  ├─ 执行所有 5 个阶段
    │  ├─ Checkpoint 1 (eval-plan): score ≥90 → continue | <90 → stop
    │  ├─ Checkpoint 2 (review): score ≥90 → continue | <90 → stop
    │  └─ 无人工干预（除非 checkpoint 失败）
    │
    ├─ 交互模式: /solve-issues #123 --interactive
    │  ├─ Phase 1: start-issue → 自动执行
    │  ├─ Checkpoint 1: eval-plan → 显示结果，询问 [C]ontinue/[E]dit/[S]top
    │  ├─ Phase 2: execute-plan → 自动执行
    │  ├─ Checkpoint 2: review → 显示结果，询问 [C]ontinue/[F]ix/[S]top
    │  └─ Phase 3: finish-issue → 自动执行
    │
    └─ 手动模式: 单独调用技能
       ├─ /start-issue #123
       ├─ /eval-plan #123
       ├─ /execute-plan #123
       ├─ /review
       └─ /finish-issue #123
```

**模式选择规则**:
- 信任度高 + 简单 issue → 自动模式
- 复杂 issue / 需要验证 → 交互模式
- 学习 / 调试 → 手动模式

---

## 错误处理 (AI 决策)

### eval-plan 评分 <90

**问题**: 计划质量不足

**AI 决策流程**:
1. 分析失败原因（从 .eval-plan-status.json 读取 issues）
2. 分类问题：
   - Auto-fixable (score ≥90 但有微小问题) → 自动修复
   - Needs manual fix (70-89) → 提示用户修复
   - Critical (< 70) → 停止工作流
3. 如果 auto 模式 + score <90 → 停止，输出问题列表
4. 如果 interactive 模式 → 询问用户 [E]dit plan, [C]ontinue anyway, [Q]uit

**修复示例**:
```python
# Read issues from status file
issues = json.load('.claude/.eval-plan-status.json')['issues']

# Apply fixes
for issue in issues['recommendations']:
    if issue['category'] == 'architecture':
        # Suggest moving logic to correct layer
        print(f"Fix: {issue['fix']}")
```

---

### review 评分 <90

**问题**: 代码质量不足

**AI 决策流程**:
1. 分析代码问题（从 .review-status.json 读取）
2. 分类问题类型：
   - Tests failing → 修复测试
   - Linting errors → 运行 auto-fix (`npm run lint --fix`)
   - Type errors → 修复类型定义
   - Security issues → 立即修复
3. 修复问题
4. 重新运行 /review
5. 如果修复后 score ≥90 → 继续
6. 如果多次修复仍 <90 → 停止，需要人工介入

**修复示例**:
```bash
# Linting errors
npm run lint --fix
git -C {worktree_path} add .

# Type errors
# Read error messages, fix type definitions

# Re-run review
/review
```

---

### CI 失败

**问题**: GitHub Actions 失败

**AI 决策流程**:
1. 读取 CI 日志: `gh run view {run_id} --log-failed`
2. 分析失败原因（tests, build, lint）
3. 在 worktree 中修复问题
4. Commit fix: `git -C {worktree_path} commit -m "fix: resolve CI failure"`
5. Push: `git -C {worktree_path} push`
6. 等待 CI 重新运行
7. 如果仍失败 → 重复 1-6
8. 如果 3 次失败 → 停止，需要人工介入

---

### 合并冲突

**问题**: PR 合并时发现冲突

**AI 决策流程**:
1. 在 worktree 中拉取 main: `git -C {worktree_path} fetch origin main`
2. 尝试合并: `git -C {worktree_path} merge origin/main`
3. 如果有冲突 → 分析冲突文件
4. 解决冲突：
   - Simple conflicts (imports, formatting) → 自动解决
   - Logic conflicts → 停止，需要人工介入
5. 测试解决方案: `npm test`
6. Commit 解决: `git -C {worktree_path} commit -m "fix: resolve merge conflict"`
7. Push: `git -C {worktree_path} push`

---

## 最佳实践 (AI 参考)

### Worktree 路径处理

**所有操作必须使用 worktree 绝对路径**:

```bash
# ✅ CORRECT
Read {worktree_path}/.claude/plans/active/issue-{N}-plan.md
Edit {worktree_path}/src/component.tsx
Write {worktree_path}/docs/new-doc.md
git -C {worktree_path} status

# ❌ WRONG
Read .claude/plans/active/issue-{N}-plan.md  # Uses main repo
Edit src/component.tsx  # Uses main repo
git status  # Missing -C flag
```

---

### 状态文件管理

**Phase 1.5 输出**: `.claude/.eval-plan-status.json`
- 写入位置: 主仓库（非 worktree）
- 有效期: 90 分钟
- 用途: auto-solve-issue checkpoint 决策

**Phase 2.5 输出**: `.claude/.review-status.json`
- 写入位置: 主仓库（非 worktree）
- 有效期: 90 分钟
- 用途: auto-solve-issue checkpoint 决策

**Phase 3 清理**: 删除两个状态文件

---

### Checkpoint 决策逻辑

**Checkpoint 1 (eval-plan)**:
```python
status = json.load('.claude/.eval-plan-status.json')
score = status['score']

if mode == 'auto':
    if score >= 90:
        continue_to_phase_2()
    else:
        stop_and_report_issues()
elif mode == 'interactive':
    show_results()
    choice = ask_user(['Continue', 'Edit', 'Stop'])
    if choice == 'Continue':
        continue_to_phase_2()
```

**Checkpoint 2 (review)**:
```python
status = json.load('.claude/.review-status.json')
score = status['score']

if mode == 'auto':
    if score >= 90:
        continue_to_phase_3()
    else:
        stop_and_report_issues()
elif mode == 'interactive':
    show_results()
    choice = ask_user(['Continue', 'Fix', 'Stop'])
    if choice == 'Fix':
        fix_issues_and_rerun_review()
```

---

## 版本同步 (维护者参考)

**当技能版本更新时**:
1. 更新 SKILL.md 中的版本号（YAML frontmatter）
2. 同步更新本文件顶部的 skills_versions
3. 运行检查: `python scripts/check-guide-sync.py`
4. 如果不一致 → PR 会 CI 失败

**自动检查机制**:
- PR 提交时运行 `.github/workflows/check-docs-sync.yml`
- 脚本检查 7 个技能版本与本文件一致性
- 不一致时 CI 失败，阻止合并

---

## 相关资源

- **技能文档**: `.claude/skills/{skill-name}/SKILL.md`
- **状态文件**: `.claude/.eval-plan-status.json`, `.claude/.review-status.json`
- **计划模板**: `.claude/workflow/MAIN.md`
- **版本检查**: `scripts/check-guide-sync.py`

---

**Version**: 1.0.0
**Last Updated**: 2026-03-24
**Maintained By**: AI Development Framework Team
