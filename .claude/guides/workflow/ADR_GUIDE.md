# ADR 创建指南（AI 参考标准）

> **定位**: 此文档是 AI 创建 ADR 时的参考标准，使用指令风格，包含可执行的步骤和规则。

## 标准 ADR 结构（AI 必须遵循）

### YAML Frontmatter（必需）

```yaml
---
status: proposed | accepted | rejected | superseded
date: YYYY-MM-DD
author: AI + Human
---
```

**字段说明**（AI 填写规则）：
- `status`: 新 ADR 使用 `proposed`，讨论后改为 `accepted` 或 `rejected`
- `date`: 使用创建日期（YYYY-MM-DD 格式）
- `author`: 固定为 "AI + Human"

### 必需章节（AI 必须包含）

```markdown
# ADR-XXX: 标题

## TL;DR
[30 行以内的执行摘要]

## Context
[为什么需要这个决策？当前问题是什么？]

## Decision
[我们决定做什么？具体方案是什么？]

## Consequences
[这个决策的影响是什么？优点和缺点？]
```

**章节要求**（AI 执行）：
1. **TL;DR**: ≤30 行，包含决策核心内容
2. **Context**: 说明背景和问题
3. **Decision**: 描述具体决策方案
4. **Consequences**: 列出优点和缺点

### 长度限制（AI 检查）

- **理想长度**: 50-80 行
- **推荐上限**: ≤100 行
- **硬限制**: ≤150 行（超过需拆分）

---

## ADR 编号规范（AI 执行）

### 编号分配规则

```python
def determine_adr_number():
    """AI 执行逻辑"""
    # 规则 1: 框架级 ADR
    if is_framework_decision():
        return range(0, 100)  # 000-099

    # 规则 2: 项目级 ADR
    elif is_project_decision():
        return range(100, 999)  # 100-999

    # 规则 3: 临时/草稿 ADR
    else:
        return "DRAFT"
```

**判断标准**（AI 决策）：
- **框架级**（000-099）: 影响多个项目的架构决策
  - 示例：统一的技能模式、通用编码规范
- **项目级**（100-999）: 单个项目的架构决策
  - 示例：数据库选型、API 设计模式

### 自动检测下一个编号（AI 执行步骤）

```bash
# 步骤 1: 读取现有 ADRs
ls docs/ADRs/*.md | grep -o '[0-9]\+' | sort -n | tail -1

# 步骤 2: 计算下一个编号
NEXT_NUM=$((LAST_NUM + 1))

# 步骤 3: 格式化为 3 位数字
printf "%03d" $NEXT_NUM  # 例如: 012
```

---

## 创建步骤（AI 执行）

### 步骤 1: 确定编号

```python
# AI 执行
1. 运行: ls docs/ADRs/*.md | grep -o '[0-9]\+' | sort -n | tail -1
2. 获取最大编号 (例如: 011)
3. 计算下一个: 011 + 1 = 012
4. 判断类型: 框架级 or 项目级
5. 如果 > 099，确认是项目级决策
```

### 步骤 2: 创建文件

```bash
# AI 执行
FILE_NAME="docs/ADRs/$(printf "%03d" $NEXT_NUM)-${TITLE_KEBAB}.md"
# 例如: docs/ADRs/012-use-python-only.md
```

**命名规则**（AI 遵循）：
- 格式: `NNN-title-in-kebab-case.md`
- 编号: 3 位数字（001, 002, ..., 100）
- 标题: kebab-case，简短（≤50 字符）

### 步骤 3: 填写内容

```python
# AI 执行顺序
1. 添加 YAML frontmatter（status: proposed）
2. 写 TL;DR（≤30 行）
3. 写 Context（背景和问题）
4. 写 Decision（具体方案）
5. 写 Consequences（优缺点）
6. 检查长度（≤100 行推荐）
```

### 步骤 4: 质量自检

**执行质量检查清单**（见下一章节）

---

## 质量检查清单（AI 自检）

### 必需检查项（AI 必须通过）

```yaml
- [ ] YAML frontmatter 完整（status, date, author）
- [ ] 所有必需章节存在（TL;DR, Context, Decision, Consequences）
- [ ] TL;DR ≤30 行
- [ ] 总长度 ≤100 行（推荐）或 ≤150 行（硬限制）
- [ ] 文件名格式正确（NNN-title-kebab.md）
- [ ] 编号无冲突（检查 docs/ADRs/ 目录）
```

### 推荐检查项（AI 建议）

```yaml
- [ ] Decision 章节包含具体方案（不只是原则）
- [ ] Consequences 同时列出优点和缺点
- [ ] Context 说明现有方案的问题
- [ ] 有明确的执行指导（如何应用此决策）
- [ ] 引用相关 ADRs（如果有）
```

### 自动检查脚本（AI 可执行）

```python
def check_adr_quality(file_path):
    """AI 执行质量检查"""
    content = read_file(file_path)

    issues = []

    # 检查 1: YAML frontmatter
    if not has_yaml_frontmatter(content):
        issues.append("缺少 YAML frontmatter")

    # 检查 2: 必需章节
    required = ["TL;DR", "Context", "Decision", "Consequences"]
    for section in required:
        if not has_section(content, section):
            issues.append(f"缺少章节: {section}")

    # 检查 3: TL;DR 长度
    tldr_lines = count_lines_in_section(content, "TL;DR")
    if tldr_lines > 30:
        issues.append(f"TL;DR 过长: {tldr_lines} 行 (应 ≤30 行)")

    # 检查 4: 总长度
    total_lines = count_lines(content)
    if total_lines > 150:
        issues.append(f"总长度过长: {total_lines} 行 (硬限制 ≤150 行)")
    elif total_lines > 100:
        issues.append(f"总长度偏长: {total_lines} 行 (推荐 ≤100 行)")

    return issues
```

---

## 常见错误（AI 避免）

### 错误 1: TL;DR 过长

```markdown
❌ 错误示例:
## TL;DR
[50 行的详细说明...]

✅ 正确示例:
## TL;DR
我们决定使用 Python-only 策略替代 Bash 脚本，因为：
- 更好的可测试性（单元测试覆盖率 >80%）
- 跨平台兼容性（Windows, macOS, Linux）
- 更强的类型系统（mypy 静态检查）
```

### 错误 2: 缺少 Consequences

```markdown
❌ 错误示例:
## Decision
使用 React hooks

[缺少 Consequences 章节]

✅ 正确示例:
## Decision
使用 React hooks

## Consequences
优点:
- 代码更简洁
- 易于复用逻辑

缺点:
- 学习曲线
- 需要团队培训
```

### 错误 3: 编号冲突

```python
# AI 避免冲突
def get_next_adr_number():
    existing = list_adr_files("docs/ADRs/")
    numbers = [extract_number(f) for f in existing]
    max_num = max(numbers) if numbers else 0
    return max_num + 1  # 自动递增
```

---

## 模板使用（AI 选择）

### 决策树（AI 执行）

```python
def choose_template(decision_type):
    """AI 选择模板"""
    if is_architecture_decision():
        return "standard_adr_template"  # 完整决策
    elif is_quick_decision():
        return "quick_adr_template"  # 轻量级
    elif is_tech_selection():
        return "tech_selection_template"  # 技术选型
    else:
        return "standard_adr_template"  # 默认
```

### 使用步骤（AI 执行）

```bash
# 1. 选择模板（见下方模板章节）
# 2. 复制模板内容
# 3. 替换占位符 {{...}}
# 4. 填写具体内容
# 5. 执行质量检查
```

---

## 标准 ADR 模板

```markdown
---
status: proposed
date: {{YYYY-MM-DD}}
author: AI + Human
---

# ADR-{{NNN}}: {{标题}}

## TL;DR

{{决策的核心内容（≤30 行）}}

## Context

{{背景说明}}
- 当前问题：{{问题描述}}
- 现有方案的局限：{{局限性}}
- 需要决策的原因：{{原因}}

## Decision

{{具体决策方案}}

我们决定：{{决策内容}}

方案细节：
- {{细节 1}}
- {{细节 2}}
- {{细节 3}}

## Consequences

**优点**：
- {{优点 1}}
- {{优点 2}}

**缺点**：
- {{缺点 1}}
- {{缺点 2}}

**风险**：
- {{风险 1}}
- {{风险 2}}
```

---

## 快速 ADR 模板

```markdown
---
status: accepted
date: {{YYYY-MM-DD}}
author: AI + Human
---

# ADR-{{NNN}}: {{标题}}

## TL;DR

{{单段落决策说明（≤10 行）}}

## Decision

{{具体决策（3-5 行）}}

## Consequences

**优点**: {{优点}}
**缺点**: {{缺点}}
```

---

## 技术选型 ADR 模板

```markdown
---
status: proposed
date: {{YYYY-MM-DD}}
author: AI + Human
---

# ADR-{{NNN}}: {{技术选型标题}}

## TL;DR

我们选择 {{技术 A}} 而非 {{技术 B}}，因为 {{核心原因}}。

## Context

**需求**：{{技术需求}}

**候选方案**：
- {{技术 A}}：{{简介}}
- {{技术 B}}：{{简介}}
- {{技术 C}}：{{简介}}

## Decision

选择：**{{技术 A}}**

**对比分析**：

| 维度 | {{技术 A}} | {{技术 B}} | {{技术 C}} |
|------|-----------|-----------|-----------|
| 性能 | {{评分}} | {{评分}} | {{评分}} |
| 生态 | {{评分}} | {{评分}} | {{评分}} |
| 学习成本 | {{评分}} | {{评分}} | {{评分}} |

**决策依据**：{{为什么选择 A}}

## Consequences

**优点**：
- {{优点 1}}
- {{优点 2}}

**缺点/权衡**：
- {{缺点 1}}
- {{缺点 2}}

**迁移成本**：{{如果未来需要更换}}
```

---

## 参考资源

- ADR-001: Official Skill Patterns（框架 ADR 示例）
- ADR-002: Skill Creation Workflow（框架 ADR 示例）
- [GitHub - ADR 工具集](https://adr.github.io/)

---

**版本**: 1.0.0
**最后更新**: 2026-03-24
**用途**: AI 创建 ADR 的统一参考标准
