# Workflow Architecture - MVP → Issues → TODO Core

> Understanding the three-layer architecture for feature development workflow

---

## 📐 Architecture Overview

```
LONG-TERM ORGANIZATION        SESSION TRACKING           EXECUTION
(Strategic)                   (Tactical)                 (Operational)
    │                             │                          │
    ▼                             ▼                          ▼

MVP 文件 (路标)          GitHub Issues               plans/active/ (清单)
docs/dev/MVP*.md        + Dev Plan Comments         .claude/plans/active/
     │                        │                          │
     ├─ 业务目标          ├─ Issue #N              ├─ Current
     ├─ 验收标准          │  ├─ Description       │   Issue
     ├─ 相关 Issues       │  ├─ Dev Plan          │   └─ Steps
     └─ 环境配置          │  ├─ Test Cases        │      (打勾)
                          │  └─ Labels            │
                          │     (tier, pillar)    │
                          │                       │
                          └───────────────────────┴─ *next 推荐下一步
```

---

## 🔄 Three-Layer Hierarchy Explained

### Layer 1: MVP 文件 (Strategic Vision)

**位置**: `docs/dev/MVP*.md`  
**所有者**: Product/Tech Lead  
**更新频率**: Per release (v0.1, v0.2, v1.0)  
**生命周期**: 一周到一个月  

```
MVP3 - 批处理上传
├─ Goal: Process batched Bedrock results, write to DynamoDB
├─ Acceptance Criteria:
│  ├─ [x] 1000 items processed in < 10s (6x speedup)
│  ├─ [x] Idempotent transactionId generation
│  └─ [ ] CloudWatch metrics + alarms
├─ Related Issues:
│  └─ #99 batch-result-handler
└─ Environment:
   └─ Lambda timeout: 10min
```

**MVP 文件的职责**:
- ✅ 定义业务目标
- ✅ 列出验收标准（可打勾）
- ✅ 超链接引用相关 Issues（不重复内容）
- ✅ 记录环境配置和依赖
- ❌ 不包含代码实现细节
- ❌ 不包含测试场景

**与 Workflow 的关系**:
- `workflow/planning.md` Step 0: 检查 MVP 中的需求
- `workflow/planning.md` Step 5: Plan 文档与 MVP 验收标准对齐

---

### Layer 2: GitHub Issues (Technical Tasks)

**位置**: GitHub Issues  
**所有者**: Tech Lead / AI  
**更新频率**: When planning or working on issue  
**生命周期**: 一周内（从创建到关闭）  

```
Issue #99: batch-result-handler - 4 core improvements

Description: Process S3 Bedrock output, write to DynamoDB
Acceptance Criteria:
  ☐ Improvement #1: Idempotency
  ☐ Improvement #4: Streaming + BatchWriteItem
  ☐ Improvement #5: S3 key mapping
  ☐ Improvement #7: IAM least privilege

Comments:
  1️⃣ Development Plan:
     └─ [Copy from .claude/*-PLAN.md]

  2️⃣ Test Cases:
     └─ [Copy from .claude/*-TEST-CASES.md]

Labels: status/planned, tier/t3, pillar/b, pillar/q, pillar/r
```

**GitHub Issues 的职责**:
- ✅ 技术任务的完整描述
- ✅ 代码改动范围（哪些文件）
- ✅ 开发计划（从 workflow/planning.md 复制）
- ✅ 测试用例（从 workflow/planning.md 复制）
- ✅ 讨论记录和变更历史
- ✅ 标签（tier, pillar, status, priority）

**与 Workflow 的关系**:
- `workflow/planning.md` Step 2: 创建或找到 Issue #N
- `workflow/planning.md` Step 6: 在 Issue 中添加 Dev Plan + Test Cases
- `workflow/Phase-C-Development.md` *issue pick: 加载 Issue 细节

---

### Layer 3: plans/active/ (Session Tracking)

**位置**: `.claude/plans/active/`  
**所有者**: AI  
**更新频率**: Per session  
**生命周期**: 当日（Session 结束清空或关闭 Issues）  

```markdown
## Current Session [2026-01-09]

### Active Issues
- [x] #99 batch-result-handler (已完成)
  - [x] Step 1: Fix timestamp bug (idempotency)
  - [x] Step 2: Create MVP3.1 roadmap
  - [x] Step 3: [next step]

- [ ] #102 SQS + DLQ Configuration (in progress)
  - [x] Design architecture
  - [ ] Implement CDK stack
  - [ ] Test event flow

### Next Up (from MVP3.1)
- [ ] #103 trace propagation (2-3h)
- [ ] #104 migrateImageFiles (4-6h)
```

**plans/active/ 的职责**:
- ✅ 记录当前 Session 的 1-3 个活跃 Issue
- ✅ Session 内的进度追踪（子任务打勾）
- ✅ 记录下一个要开始的 Issue
- ✅ 标记任何阻塞项
- ❌ 不是 GitHub Issues 的镜像副本
- ❌ Session 结束后清空

**与 Workflow 的关系**:
- `workflow/Phase-C-Development.md` *issue pick: 创建 plans/active/ 条目
- `workflow/Phase-C-Development.md` *next: 推荐下一个 Sub-task 或 Issue

---

## 🎯 Data Flow Between Layers

```
MVP (大图景，strategic)
     │
     ▼
Planning Workflow (Phase B, tactical)
     │
     ▼
GitHub Issues (detailed plan + tests)
     │
     ▼
*issue pick
     │
     ▼
plans/active/ (今日工作，operational)
     │
     ▼
*next (执行步骤，execute)
     │
     ▼
*issue close
     │
     ▼
MVP updated (验收标准打勾)
```

---

## 🔗 How Workflow Connects the Three Layers

### PHASE B: Planning → GitHub Issues (Step 0-8)

```
Step 0: Check Docs
  ↓
  🔍 检查 MVP 文件的需求是否清晰
  🔍 检查 REQUIREMENTS/ARCHITECTURE/SCHEMA/DESIGN
  ↓
Step 1-3: Analyze & Decompose
  ↓
  📋 从 MVP 或 Feature Request 提取需求
  ✅ 创建或复用 GitHub Issue #N
  ↓
Step 4-8: Plan → Evaluate → Confirm → Test Cases → Prioritize
  ↓
  📝 创建 .claude/*-PLAN.md (implemention steps)
  📝 创建 .claude/*-TEST-CASES.md (test matrix)
  💬 在 Issue #N 的评论中添加这两个文档
  🏷️ 应用标签: status/planned, tier/*, pillar/*
  ↓
GitHub Issue #N is now READY
```

### PHASE C: Development → plans/active/ (Execution)

```
*issue pick #N
  ↓
  📂 加载 Issue #N 的详细信息（来自 GitHub）
     ├─ Acceptance Criteria
     ├─ Dev Plan Comment (from .claude/*-PLAN.md)
     └─ Test Cases Comment (from .claude/*-TEST-CASES.md)
  ↓
  📝 在 plans/active/ 创建活跃任务条目
     ├─ Issue Title
     ├─ Acceptance Criteria (打勾列表)
     └─ Steps from Dev Plan (打勾列表)
  ↓
*tier (if needed)
  ↓
*next (Phase 1-4)
  ↓
  🔨 For each step in dev plan:
     1. Check Pillar from plans/active/
     2. Execute step
     3. Run tests
     4. Mark step complete in plans/active/
  ↓
*issue close #N
  ↓
  ✅ Close Issue in GitHub
  ✅ Commit with Issue ID
  ✅ Archive decision to MEMORY.md
  ✅ Clear plans/active/ entry
```

---

## 📊 Summary Table

| Layer | File | When | Owner | Lifecycle | Purpose |
|-------|------|------|-------|-----------|---------|
| **MVP** | `docs/dev/MVP*.md` | Planning release | Tech Lead | 1-4 weeks | Big picture, goals, acceptance |
| **Issues** | GitHub #N + comments | Planning feature | AI/Tech Lead | 1-7 days | Detailed plan, technical approach |
| **TODO** | `.claude/plans/active/` | Development session | AI | Same day | Today's work, progress tracking |

---

## 🎮 The *next Command Flow

`*next` is a smart task navigation system with three levels:

```
*next
  │
  ├─ Level 1: Check plans/active/
  │  ├─ Active issue?
  │  │  ├─ Yes → Show next sub-task from dev plan
  │  │  │        Execute Phase 1-4
  │  │  └─ No → Go to Level 2
  │  └─ Mark steps complete as you go
  │
  ├─ Level 2: Check GitHub Issues (from current MVP)
  │  ├─ Uncompleted issues?
  │  │  ├─ Yes → Recommend highest priority issue
  │  │  │        Prompt: "Start #N? (y/n)"
  │  │  │        Create plans/active/ entry on confirm
  │  │  └─ No → Go to Level 3
  │  └─ Pull plan from Issue comments
  │
  └─ Level 3: Check next MVP
     ├─ All issues done?
     │  ├─ Yes → Recommend next MVP
     │  │        Suggest next feature to plan
     │  └─ No → Done
     └─ Load MVP file
```

---

## ✅ Success Criteria

✅ **You understand the architecture when:**

- [ ] You can explain MVP → Issues → Issue Plan layers
- [ ] You know what information lives in each layer
- [ ] You understand Phase B creates Issues from MVP
- [ ] You understand Phase C executes Issues via plans/active/
- [ ] You know when to check each layer (strategic vs tactical vs operational)

---

## 📚 See Also

- **Planning Workflow** (Phase B): `workflow/planning.md`
- **Development Workflow** (Phase C): `workflow/Phase-C-Development.md`
- **Complete Example**: `architecture-examples.md` (coming)
