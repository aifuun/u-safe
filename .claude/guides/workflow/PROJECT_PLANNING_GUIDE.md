# PROJECT_PLANNING_GUIDE.md - AI 项目规划参考手册

> AI 规划项目的统一参考标准 - 从 PRD 到可执行 Issues 的完整流程

**主要受众**: AI (Claude Code)
**次要受众**: 人类开发者
**用途**: AI 执行项目规划时的操作手册

---

## 📐 4 层规划体系

```
Vision Layer     → PRD (产品需求文档)
    ↓
Strategy Layer   → MVP Roadmap (最小可行产品路线图)
    ↓
Campaign Layer   → GitHub Issues (可执行任务)
    ↓
Tactics Layer    → Issue Execution (执行，见 ISSUE_LIFECYCLE_GUIDE)
```

---

## Layer 1: Vision - PRD 创建

**AI 执行流程**:

### 步骤 1: 收集关键信息

使用 AskUserQuestion 收集以下信息:

```python
questions = [
    {
        "question": "项目的核心目标是什么？",
        "header": "Core Goal",
        "options": [
            {"label": "解决特定问题", "description": "明确的痛点"},
            {"label": "探索新技术", "description": "学习/实验"},
            {"label": "商业产品", "description": "盈利导向"}
        ]
    },
    {
        "question": "目标用户是谁？",
        "header": "Target Users",
        "options": [
            {"label": "开发者", "description": "技术人员"},
            {"label": "普通用户", "description": "非技术人员"},
            {"label": "企业客户", "description": "B2B"}
        ]
    },
    {
        "question": "核心功能有哪些？（可多选）",
        "header": "Core Features",
        "multiSelect": True,
        "options": [
            {"label": "用户管理", "description": "认证、权限"},
            {"label": "数据处理", "description": "CRUD、分析"},
            {"label": "协作功能", "description": "共享、评论"}
        ]
    }
]
```

### 步骤 2: 生成 PRD 文档

```python
def generate_prd(project_name, answers):
    """
    根据用户回答生成 PRD
    """
    template = f"""
# PRD: {project_name}

## 产品概述

**目标**: {answers['core_goal']}
**用户**: {answers['target_users']}
**核心价值**: [AI 根据目标和用户生成]

## 问题陈述

**当前痛点**:
- [AI 根据用户输入推断]
- [具体问题描述]

**解决方案**:
- [产品如何解决这些问题]

## 核心功能

### Must Have (必须有)
{generate_features(answers['core_features'], priority='must')}

### Should Have (应该有)
{generate_features(answers['core_features'], priority='should')}

### Could Have (可以有)
{generate_features(answers['core_features'], priority='could')}

## 成功指标

- [用户增长目标]
- [使用频率目标]
- [性能指标]

## 技术栈建议

- Frontend: [根据用户类型推荐]
- Backend: [根据功能复杂度推荐]
- Database: [根据数据特性推荐]
"""

    return template
```

### 步骤 3: 写入 PRD 文件

```python
prd_content = generate_prd(project_name, user_answers)
Write("docs/product/PRD.md", prd_content)
```

### PRD 模板（3 种规模）

#### 小型项目模板（<10 功能点）

```markdown
# PRD: {project_name}

## 概述
一句话描述产品

## 核心功能（3-5 个）
1. 功能 1 - 解决什么问题
2. 功能 2 - 解决什么问题
3. 功能 3 - 解决什么问题

## 技术栈
- Frontend: React + TypeScript
- Backend: Node.js + Express
- Database: PostgreSQL

## MVP 范围
Phase 1: 核心功能 1, 2
Phase 2: 核心功能 3
```

#### 中型项目模板（10-30 功能点）

```markdown
# PRD: {project_name}

## 执行摘要
产品定位、目标用户、核心价值

## 问题与机会
- 当前痛点
- 市场机会
- 竞争分析

## 产品功能
### 用户管理模块
- 注册/登录
- 个人资料
- 权限管理

### 核心业务模块
- [具体功能描述]

### 辅助功能模块
- 通知系统
- 搜索功能

## 非功能需求
- 性能要求
- 安全要求
- 可扩展性

## 技术架构
- 前后端分离
- RESTful API
- 微服务（可选）

## 路线图
Q1: MVP 发布
Q2: 功能增强
Q3: 规模化
```

#### 大型项目模板（>30 功能点）

```markdown
# PRD: {project_name}

## 1. 战略背景
### 1.1 愿景与使命
### 1.2 市场分析
### 1.3 目标与KPI

## 2. 用户研究
### 2.1 用户画像
### 2.2 用户旅程
### 2.3 痛点分析

## 3. 产品定义
### 3.1 核心功能
### 3.2 功能优先级（MoSCoW）
### 3.3 用户故事

## 4. 技术规格
### 4.1 系统架构
### 4.2 技术选型
### 4.3 数据模型
### 4.4 API 设计

## 5. 实施计划
### 5.1 阶段划分
### 5.2 资源需求
### 5.3 风险管理

## 6. 度量与迭代
### 6.1 成功指标
### 6.2 反馈机制
### 6.3 迭代计划
```

---

## Layer 2: Strategy - MVP 规划

**AI 执行流程**:

### 步骤 1: 从 PRD 提取功能列表

```python
def extract_features_from_prd(prd_path):
    """
    从 PRD 中提取所有功能
    """
    prd_content = Read(prd_path)
    features = []

    # 解析 ## 核心功能 章节
    # 提取每个功能的标题和描述

    return features  # [{name, description, estimated_effort}]
```

### 步骤 2: 应用 MoSCoW 优先级

```python
def prioritize_features(features):
    """
    使用 MoSCoW 方法排序功能

    Must Have: MVP 必须包含
    Should Have: v1.1 应该有
    Could Have: v1.2 可以有
    Won't Have: 不做
    """
    prioritized = {
        'must': [],
        'should': [],
        'could': [],
        'wont': []
    }

    for feature in features:
        priority = classify_feature(feature)
        prioritized[priority].append(feature)

    return prioritized


def classify_feature(feature):
    """
    判断功能优先级的规则
    """
    # 规则 1: 核心价值判断
    if is_core_value_proposition(feature):
        return 'must'

    # 规则 2: 用户体验关键路径
    if is_critical_user_journey(feature):
        return 'must'

    # 规则 3: 技术依赖
    if is_foundation_for_others(feature):
        return 'must'

    # 规则 4: 用户体验增强
    if enhances_user_experience(feature):
        return 'should'

    # 规则 5: Nice to have
    if is_nice_to_have(feature):
        return 'could'

    return 'wont'
```

### 步骤 3: 生成 Roadmap

```python
def generate_roadmap(prioritized_features):
    """
    生成产品路线图
    """
    roadmap = f"""
# Roadmap: {project_name}

## MVP (v1.0) - Must Have
{format_features(prioritized_features['must'])}

**预计工时**: {estimate_effort(prioritized_features['must'])}
**目标完成**: {calculate_deadline(effort)}

## v1.1 - Should Have
{format_features(prioritized_features['should'])}

**预计工时**: {estimate_effort(prioritized_features['should'])}

## v1.2 - Could Have
{format_features(prioritized_features['could'])}

**预计工时**: {estimate_effort(prioritized_features['could'])}

## Backlog - Won't Have (此版本)
{format_features(prioritized_features['wont'])}
"""

    return roadmap
```

### Roadmap 模板

```markdown
# Roadmap: TaskHub

## MVP (v1.0) - 基础任务管理
**目标**: 让用户能创建、管理、完成任务
**工时**: 40 小时
**完成日期**: 2026-04-15

### 核心功能
1. ✅ 用户注册/登录 (4h)
2. ✅ 创建任务 (6h)
3. ✅ 任务列表展示 (4h)
4. ✅ 任务状态管理 (待办/进行中/完成) (6h)
5. ✅ 任务编辑/删除 (4h)
6. ✅ 基础搜索 (4h)
7. ✅ 响应式 UI (8h)
8. ✅ 数据持久化 (4h)

## v1.1 - 协作功能
**目标**: 支持团队协作
**工时**: 32 小时
**完成日期**: 2026-05-15

### 增强功能
1. 任务分配给其他用户 (8h)
2. 评论系统 (8h)
3. 任务优先级 (4h)
4. 任务标签 (6h)
5. 通知系统 (6h)

## v1.2 - 高级功能
**目标**: 提升用户体验
**工时**: 24 小时

### 优化功能
1. 任务依赖关系 (8h)
2. 甘特图视图 (8h)
3. 数据导出 (4h)
4. 批量操作 (4h)
```

---

## Layer 3: Campaign - Issue 分解

**AI 执行流程**:

### 步骤 1: 为每个 MVP 功能创建 Issue

```python
def create_issues_from_mvp(mvp_features):
    """
    将 MVP 功能转换为 GitHub Issues
    """
    issues = []

    for feature in mvp_features:
        # 检查功能规模
        tasks = break_down_feature(feature)

        if len(tasks) <= 8:
            # 单个 issue
            issue = create_issue(feature, tasks)
            issues.append(issue)
        else:
            # 拆分为多个 issues
            sub_issues = split_feature_into_issues(feature, tasks)
            issues.extend(sub_issues)

    return issues
```

### 步骤 2: 任务分解规则

```python
def break_down_feature(feature):
    """
    将功能拆分为具体任务

    规则: 按照技术栈分层
    """
    tasks = []

    # 1. 数据层
    if needs_data_model(feature):
        tasks.append({
            'title': f'设计 {feature.name} 数据模型',
            'description': '定义 schema, 关系, 索引',
            'estimate': '1-2h'
        })
        tasks.append({
            'title': f'创建 {feature.name} migration',
            'description': '数据库迁移脚本',
            'estimate': '0.5h'
        })

    # 2. API 层
    if needs_api(feature):
        tasks.append({
            'title': f'实现 {feature.name} API endpoints',
            'description': 'CRUD operations',
            'estimate': '2-3h'
        })
        tasks.append({
            'title': f'添加 {feature.name} API 验证',
            'description': '输入验证, 错误处理',
            'estimate': '1h'
        })

    # 3. UI 层
    if needs_ui(feature):
        tasks.append({
            'title': f'创建 {feature.name} 组件',
            'description': 'React components',
            'estimate': '2-3h'
        })
        tasks.append({
            'title': f'集成 {feature.name} 状态管理',
            'description': 'Redux/Context',
            'estimate': '1-2h'
        })

    # 4. 测试
    tasks.append({
        'title': f'编写 {feature.name} 测试',
        'description': 'Unit + Integration tests (>80% coverage)',
        'estimate': '2h'
    })

    # 5. 文档
    tasks.append({
        'title': f'更新 {feature.name} 文档',
        'description': 'API docs, User guide',
        'estimate': '0.5h'
    })

    return tasks
```

### 步骤 3: Issue 尺寸检查

```python
def validate_issue_size(tasks):
    """
    验证 issue 规模是否合理

    规则:
    - 理想: 3-5 个任务, 2-3 小时
    - 推荐: ≤8 个任务, ≤4 小时
    - 硬限制: ≤15 个任务, ≤8 小时
    """
    task_count = len(tasks)
    total_effort = sum([estimate_hours(t) for t in tasks])

    if task_count <= 5 and total_effort <= 3:
        return 'IDEAL'  # 理想
    elif task_count <= 8 and total_effort <= 4:
        return 'ACCEPTABLE'  # 可接受
    elif task_count <= 15 and total_effort <= 8:
        return 'TOO_LARGE'  # 需要拆分
    else:
        return 'MUST_SPLIT'  # 必须拆分
```

### 步骤 4: 创建 GitHub Issues

```python
def create_github_issue(feature, tasks):
    """
    使用 gh CLI 创建 issue
    """
    issue_body = f"""
## 功能描述
{feature.description}

## 任务列表
{format_tasks(tasks)}

## 验收标准
- [ ] 所有任务完成
- [ ] 测试覆盖率 >80%
- [ ] 代码审查通过
- [ ] 文档更新

## 预计工时
{sum_effort(tasks)} 小时
"""

    # 使用 Bash tool 调用 gh CLI
    Bash(f'gh issue create --title "{feature.name}" --body "{issue_body}" --label "enhancement,MVP"')
```

### Issue 模板

```markdown
## 功能描述
实现用户任务创建功能，包括标题、描述、截止日期、优先级。

## 任务列表
1. 设计 Task 数据模型
   - 字段: id, title, description, due_date, priority, status, user_id
   - 关系: belongs_to :user
   - 索引: user_id, status, due_date

2. 创建 Task migration
   - 数据库表创建
   - 添加外键约束

3. 实现 Task API endpoints
   - POST /api/tasks - 创建任务
   - GET /api/tasks - 任务列表
   - GET /api/tasks/:id - 任务详情
   - PUT /api/tasks/:id - 更新任务
   - DELETE /api/tasks/:id - 删除任务

4. 添加 Task API 验证
   - 标题: required, 1-200 字符
   - 描述: optional, <2000 字符
   - 截止日期: optional, 未来日期
   - 优先级: enum(low, medium, high)

5. 创建 TaskForm 组件
   - 表单字段 UI
   - 客户端验证
   - 错误提示

6. 创建 TaskList 组件
   - 任务列表渲染
   - 过滤和排序
   - 响应式布局

7. 集成 Task 状态管理
   - Redux slice: tasks
   - Actions: createTask, fetchTasks, updateTask, deleteTask
   - Selectors

8. 编写 Task 测试
   - 单元测试: API, Components (>80% coverage)
   - 集成测试: E2E create task flow
   - 边界测试: 验证规则

9. 更新 Task 文档
   - API 文档: endpoints, schemas
   - 用户指南: 如何创建任务

## 验收标准
- [ ] 所有 9 个任务完成
- [ ] 测试覆盖率 >80%
- [ ] 代码审查通过 (linting, types)
- [ ] API 文档更新
- [ ] 用户指南更新

## 预计工时
11 小时

## 依赖
- Issue #1: 用户认证系统 (必须先完成)

## 标签
enhancement, MVP, P0
```

### 步骤 5: 标记依赖关系

```python
def mark_dependencies(issues):
    """
    标记 issues 之间的依赖关系

    规则:
    - 用户认证 → 所有需要登录的功能
    - 数据模型 → 基于该模型的功能
    - 基础组件 → 复合组件
    """
    for issue in issues:
        dependencies = find_dependencies(issue, issues)

        if dependencies:
            # 在 issue body 中添加依赖说明
            update_issue_with_dependencies(issue, dependencies)
```

---

## Layer 4: Tactics - 执行衔接

**与 ISSUE_LIFECYCLE_GUIDE 衔接点**:

### 输入（从 Campaign Layer）
- GitHub Issues 列表
- 每个 issue 的任务分解
- 依赖关系图

### 工具引用

```bash
# 单个 issue 执行
/solve-issues #123

# 批量执行（按依赖顺序）
/solve-issues [#123, #124, #125]
```

### 输出（到 ISSUE_LIFECYCLE_GUIDE）
- 每个 issue 进入 5 阶段工作流
- 自动化执行（start → eval → execute → review → finish）

**详见**: [ISSUE_LIFECYCLE_GUIDE.md](./ISSUE_LIFECYCLE_GUIDE.md)

---

## 完整示例：任务管理应用

### 场景
用户: "规划一个团队任务管理应用的 MVP"

### Vision Layer - PRD 创建

**AI 执行**:
```
1. AskUserQuestion 收集信息
   - 核心目标? → 团队协作管理任务
   - 目标用户? → 小型开发团队 (3-10人)
   - 核心功能? → 任务 CRUD, 分配, 状态追踪

2. 生成 PRD → docs/product/PRD.md
```

**PRD 片段**:
```markdown
# PRD: TaskHub

## 产品概述
TaskHub 是轻量级团队任务管理工具，帮助小型开发团队高效协作。

## 核心功能
### Must Have (MVP)
1. 用户注册/登录
2. 创建/编辑/删除任务
3. 任务分配给团队成员
4. 任务状态管理 (待办/进行中/完成)
5. 任务列表和搜索

### Should Have (v1.1)
6. 评论系统
7. 任务优先级
8. 通知系统

### Could Have (v1.2)
9. 任务依赖关系
10. 甘特图视图
```

### Strategy Layer - MVP 规划

**AI 执行**:
```
1. 提取 PRD 功能列表 → 10 个功能
2. MoSCoW 排序
   - Must: 1-5
   - Should: 6-8
   - Could: 9-10
3. 生成 Roadmap
```

**Roadmap 片段**:
```markdown
# Roadmap: TaskHub

## MVP (v1.0)
1. 用户认证 (4h)
2. 任务 CRUD (11h)
3. 任务分配 (6h)
4. 状态管理 (6h)
5. 列表/搜索 (8h)

**总计**: 35 小时
**目标**: 2026-04-15

## v1.1
6. 评论系统 (8h)
7. 优先级 (4h)
8. 通知 (6h)
```

### Campaign Layer - Issue 分解

**AI 执行**:
```
1. 为每个 MVP 功能创建 issue
2. 任务分解（数据/API/UI/测试/文档）
3. 尺寸检查（任务数 ≤8）
4. 创建 GitHub issues
```

**创建的 Issues**:
```
Issue #1: 实现用户认证系统 (5 tasks, 4h)
Issue #2: 实现任务 CRUD 功能 (9 tasks, 11h)
Issue #3: 实现任务分配功能 (6 tasks, 6h)
Issue #4: 实现任务状态管理 (7 tasks, 6h)
Issue #5: 实现任务列表和搜索 (8 tasks, 8h)
```

### Tactics Layer - 执行

**AI 执行**:
```bash
# 按依赖顺序批量执行
/solve-issues [#1, #2, #3, #4, #5]

# 每个 issue 自动进入 5 阶段:
# Phase 1: start-issue → 创建分支 + 计划
# Phase 1.5: eval-plan → 验证计划 (score: 95/100)
# Phase 2: execute-plan → 实现任务
# Phase 2.5: review → 代码审查 (score: 92/100)
# Phase 3: finish-issue → 提交 + PR + 合并
```

---

## 最佳实践

### 1. Issue 规模控制

**AI 遵循的规则**:
```python
def ensure_reasonable_issue_size(tasks):
    """
    自动拆分过大的 issue
    """
    if len(tasks) > 8:
        # 拆分策略 1: 按技术栈分层
        layer_groups = group_by_layer(tasks)  # {data, api, ui, test}

        if all(len(g) <= 8 for g in layer_groups):
            return layer_groups  # 每层一个 issue

        # 拆分策略 2: 按功能模块
        module_groups = group_by_module(tasks)
        return module_groups

    return [tasks]  # 无需拆分
```

### 2. 优先级排序

**AI 判断规则**:
```python
def determine_priority(feature):
    """
    P0: 核心价值，MVP 必须
    P1: 用户体验增强
    P2: Nice to have
    """
    if is_blocking_other_features(feature):
        return 'P0'

    if is_core_user_journey(feature):
        return 'P0'

    if enhances_experience(feature):
        return 'P1'

    return 'P2'
```

### 3. 风险识别

**AI 提醒用户**:
```python
def identify_risks(roadmap):
    """
    检测潜在风险
    """
    risks = []

    # 技术风险
    if uses_new_technology(roadmap):
        risks.append({
            'type': 'TECHNICAL',
            'description': '使用未验证的新技术',
            'mitigation': '在 spike issue 中验证可行性'
        })

    # 依赖风险
    if has_circular_dependencies(roadmap):
        risks.append({
            'type': 'DEPENDENCY',
            'description': '存在循环依赖',
            'mitigation': '重新设计依赖关系'
        })

    # 资源风险
    total_effort = sum_effort(roadmap)
    if total_effort > available_time:
        risks.append({
            'type': 'RESOURCE',
            'description': f'工时超出 ({total_effort}h > {available_time}h)',
            'mitigation': '缩减 MVP 范围或延长时间线'
        })

    return risks
```

---

**版本**: 1.0.0
**最后更新**: 2026-03-24
**总行数**: 400+
**风格**: 指令风格（AI 可执行）

