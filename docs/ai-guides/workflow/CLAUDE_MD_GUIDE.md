# CLAUDE.md 维护指南（AI 参考标准）

> **定位**: 此文档是 AI 维护 CLAUDE.md 时的参考标准，使用指令风格，包含可执行的检查步骤和规则。

## 标准 CLAUDE.md 结构（AI 必须遵循）

### 必需章节（AI 必须包含）

```markdown
# 项目名称

> 项目简介（1-2 句话）

## 🎯 What Is This Project?
[核心价值主张，50-100 字]

## ⚡ Skills System (列表)
[当前可用的技能清单]

## 🚀 How to Use
[快速开始指南，≤50 行]

## 📖 Key Documentation
[重要文档链接]
```

**章节要求**（AI 检查）：
- `What Is This Project?`: 必需，说明项目定位
- `Skills System`: 必需，列出所有可用技能
- `How to Use`: 必需，提供使用指导
- `Key Documentation`: 推荐，链接到详细文档

### 可选章节（AI 按需添加）

```markdown
## 📊 Current Status
[项目状态概览，≤30 行]

## 🏗️ Core Architecture
[架构概览，≤40 行，详细内容链接到 docs/]

## 💡 Common Use Cases
[常见使用场景，≤30 行]

## 🔗 Related Documents
[相关文档列表]
```

### 不应包含的内容（AI 避免）

❌ **不要包含**：
- 详细的技术文档（应在 `docs/` 下）
- 完整的 API 文档（应在 `docs/arch/API.md`）
- 详细的架构设计（应在 `docs/arch/ARCHITECTURE.md`）
- 完整的 ADR 内容（应在 `docs/ADRs/`）
- 详细的开发指南（应在 `docs/dev/`）

✅ **应该包含**：
- 项目概览和定位
- 快速开始指导
- 技能清单（从 `.claude/skills/` 目录同步）
- 重要文档的链接

---

## 长度限制规范（AI 检查）

### 推荐长度（AI 目标）

```python
def check_length(line_count):
    """AI 执行长度检查"""
    if line_count <= 100:
        return "ideal"  # 理想长度
    elif line_count <= 150:
        return "good"  # 良好
    elif line_count <= 200:
        return "acceptable"  # 可接受
    else:
        return "too_long"  # 需要优化
```

**长度指南**：
- **小型项目**: ≤100 行（理想）
- **中型项目**: 100-150 行（良好）
- **大型项目**: 150-200 行（可接受上限）
- **超大项目**: >200 行（需要重构）

### 硬限制（AI 强制）

```yaml
硬限制: 300 行
- 超过 300 行：必须拆分内容到 docs/ 目录
- 超过 200 行：强烈建议重构
```

### 超长处理（AI 执行）

```python
def handle_oversize_claude_md(line_count):
    """AI 处理超长 CLAUDE.md"""
    if line_count > 300:
        # 步骤 1: 移动详细内容到 docs/
        move_to_docs([
            "详细架构" -> "docs/arch/ARCHITECTURE.md",
            "API 文档" -> "docs/arch/API.md",
            "开发指南" -> "docs/dev/SETUP.md"
        ])

        # 步骤 2: 保留概览和链接
        keep_in_claude_md([
            "项目简介",
            "快速开始",
            "技能清单",
            "文档链接"
        ])

        # 步骤 3: 重新检查长度
        new_count = count_lines("CLAUDE.md")
        assert new_count <= 200, "重构后仍超长"
```

---

## 维护流程（AI 执行）

### 步骤 1: 检查行数

```bash
# AI 执行
wc -l CLAUDE.md | awk '{print $1}'
```

**判断逻辑**（AI 决策）：
```python
line_count = count_lines("CLAUDE.md")

if line_count <= 150:
    status = "健康"
elif line_count <= 200:
    status = "需要关注"
elif line_count <= 300:
    status = "建议重构"
else:
    status = "必须重构"
```

### 步骤 2: 检查必需章节

```python
def check_required_sections(content):
    """AI 执行章节检查"""
    required = [
        "What Is This Project?",
        "Skills System",
        "How to Use"
    ]

    missing = []
    for section in required:
        if not has_section(content, section):
            missing.append(section)

    return missing
```

### 步骤 3: 检查技能列表同步

```python
def check_skills_sync():
    """AI 执行技能同步检查"""
    # 1. 读取 .claude/skills/ 目录
    actual_skills = list_skills(".claude/skills/")

    # 2. 读取 CLAUDE.md 中的技能列表
    documented_skills = extract_skills_from_claude_md("CLAUDE.md")

    # 3. 对比差异
    missing = set(actual_skills) - set(documented_skills)
    extra = set(documented_skills) - set(actual_skills)

    return {
        "missing": list(missing),  # 新增但未文档化
        "extra": list(extra)  # 文档中但已删除
    }
```

### 步骤 4: 生成修复建议

```python
def generate_fixes(issues):
    """AI 生成修复建议"""
    suggestions = []

    # 1. 长度问题
    if issues.line_count > 200:
        suggestions.append({
            "type": "length",
            "action": "将详细内容移动到 docs/ 目录",
            "details": "保留概览，链接详细文档"
        })

    # 2. 缺少章节
    for section in issues.missing_sections:
        suggestions.append({
            "type": "missing_section",
            "action": f"添加 '{section}' 章节",
            "template": get_section_template(section)
        })

    # 3. 技能不同步
    if issues.skills_diff.missing:
        suggestions.append({
            "type": "skills_sync",
            "action": "添加新技能到清单",
            "skills": issues.skills_diff.missing
        })

    return suggestions
```

---

## 质量检查清单（AI 自检）

### 必需检查项（AI 必须通过）

```yaml
- [ ] 长度 ≤200 行（或 ≤300 行硬限制）
- [ ] 包含必需章节（What Is This, Skills, How to Use）
- [ ] 技能列表与 .claude/skills/ 同步
- [ ] 无详细技术文档（应在 docs/）
- [ ] 所有链接有效（指向存在的文件）
```

### 推荐检查项（AI 建议）

```yaml
- [ ] 项目简介 ≤100 字
- [ ] How to Use 章节 ≤50 行
- [ ] 使用 emoji 标记章节（提高可读性）
- [ ] 包含版本信息或最后更新日期
- [ ] 链接到 ADRs（如果有重要架构决策）
```

### 自动检查脚本（AI 可执行）

```python
def check_claude_md_quality(file_path):
    """AI 执行质量检查"""
    content = read_file(file_path)
    line_count = count_lines(content)

    issues = []

    # 检查 1: 长度
    if line_count > 300:
        issues.append(f"❌ 长度超限: {line_count} 行（硬限制 ≤300）")
    elif line_count > 200:
        issues.append(f"⚠️  长度偏长: {line_count} 行（推荐 ≤200）")

    # 检查 2: 必需章节
    required = ["What Is This Project?", "Skills System", "How to Use"]
    missing = check_required_sections(content)
    if missing:
        issues.append(f"❌ 缺少章节: {', '.join(missing)}")

    # 检查 3: 技能同步
    skills_diff = check_skills_sync()
    if skills_diff["missing"]:
        issues.append(f"⚠️  未文档化的技能: {', '.join(skills_diff['missing'])}")
    if skills_diff["extra"]:
        issues.append(f"⚠️  已删除的技能: {', '.join(skills_diff['extra'])}")

    # 检查 4: 详细文档存在
    if has_detailed_docs(content):
        issues.append("⚠️  包含详细文档（应移到 docs/）")

    return issues
```

---

## 常见错误（AI 避免）

### 错误 1: 包含详细技术文档

```markdown
❌ 错误示例（CLAUDE.md）:
## Architecture
详细的 DDD 架构说明...（100 行）
详细的 API 设计...（80 行）

✅ 正确示例（CLAUDE.md）:
## 🏗️ Core Architecture
本项目采用 DDD + Clean Architecture。

详细架构说明: [docs/arch/ARCHITECTURE.md](docs/arch/ARCHITECTURE.md)
```

### 错误 2: 技能列表未同步

```python
# AI 自动同步
def sync_skills_to_claude_md():
    """AI 执行技能同步"""
    # 1. 扫描 .claude/skills/
    skills = scan_skills_directory()

    # 2. 生成技能列表 markdown
    skills_section = generate_skills_section(skills)

    # 3. 更新 CLAUDE.md
    update_section("CLAUDE.md", "Skills System", skills_section)
```

### 错误 3: 超长但未重构

```python
# AI 执行重构
def refactor_oversize_claude_md():
    """AI 重构超长 CLAUDE.md"""
    content = read_file("CLAUDE.md")

    # 1. 提取详细内容
    detailed_sections = extract_detailed_sections(content)

    # 2. 创建 docs/ 文件
    for section in detailed_sections:
        create_doc_file(section)

    # 3. 更新 CLAUDE.md（保留概览 + 链接）
    summary = create_summary_with_links(detailed_sections)
    write_file("CLAUDE.md", summary)
```

---

## 小型项目模板（≤100 行）

```markdown
# {{项目名称}}

> {{一句话简介}}

## 🎯 What Is This Project?

{{核心价值主张（50-80 字）}}

## ⚡ Skills System

- **/skill-1** - {{描述}}
- **/skill-2** - {{描述}}
- **/skill-3** - {{描述}}

## 🚀 How to Use

### Quick Start
```bash
{{安装命令}}
{{运行命令}}
```

### Common Commands
- {{命令 1}}
- {{命令 2}}

## 📖 Key Documentation

- [Setup Guide](docs/dev/SETUP.md)
- [Architecture](docs/arch/ARCHITECTURE.md)

---

**Version:** {{version}}
**Last Updated:** {{date}}
```

---

## 中型项目模板（100-150 行）

```markdown
# {{项目名称}}

> {{一句话简介}}

## 🎯 What Is This Project?

{{核心价值主张（80-100 字）}}

**Tech Stack**: {{主要技术}}

## 📊 Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| {{组件 1}} | {{状态}} | {{说明}} |
| {{组件 2}} | {{状态}} | {{说明}} |

## ⚡ Skills System ({{总数}}+ skills)

### Issue Lifecycle
- **/start-issue** - {{描述}}
- **/execute-plan** - {{描述}}
- **/finish-issue** - {{描述}}

### Quality & Review
- **/review** - {{描述}}
- **/eval-plan** - {{描述}}

### Project Management
- **/overview** - {{描述}}
- **/status** - {{描述}}

**Full list**: [.claude/skills/README.md](.claude/skills/README.md)

## 🚀 How to Use

### Quick Start
```bash
{{详细安装步骤}}
```

### Common Workflows
1. **{{工作流 1}}**: {{说明}}
2. **{{工作流 2}}**: {{说明}}

## 🏗️ Core Architecture

{{简要架构说明（≤30 行）}}

**Detailed docs**: [docs/arch/ARCHITECTURE.md](docs/arch/ARCHITECTURE.md)

## 💡 Common Use Cases

### Use Case 1: {{场景名称}}
{{简要说明}}

### Use Case 2: {{场景名称}}
{{简要说明}}

## 📖 Key Documentation

- **[Setup Guide](docs/dev/SETUP.md)** - Installation
- **[Architecture](docs/arch/ARCHITECTURE.md)** - System design
- **[ADRs](docs/ADRs/)** - Architecture decisions

---

**Version:** {{version}}
**Last Updated:** {{date}}
```

---

## 大型项目模板（150-200 行）

```markdown
# {{项目名称}}

> {{一句话简介}}

## 🎯 What Is This Project?

{{核心价值主张（100-150 字）}}

**What it solves:**
- {{问题 1}}
- {{问题 2}}
- {{问题 3}}

**Tech Stack**: {{主要技术栈}}

## 📊 Current Status

**Phase**: {{当前阶段}}

| Component | Status | Version | Notes |
|-----------|--------|---------|-------|
| {{组件 1}} | {{状态}} | {{版本}} | {{说明}} |
| {{组件 2}} | {{状态}} | {{版本}} | {{说明}} |

## ⚡ Skills System ({{总数}}+ skills)

### Issue Lifecycle (6 skills)
- **/start-issue** - {{描述}}
- **/execute-plan** - {{描述}}
- **/finish-issue** - {{描述}}
- **/solve-issues** - {{描述}}
- **/auto-solve-issue** - {{描述}}
- **/worktree** - {{描述}}

### Quality & Validation (3 skills)
- **/review** - {{描述}}
- **/eval-plan** - {{描述}}
- **/skill-creator** - {{描述}}

### Framework Sync (5 skills)
- **/update-framework** - {{描述}}
- **/update-skills** - {{描述}}
- **/update-rules** - {{描述}}
- **/update-pillars** - {{描述}}
- **/update-workflow** - {{描述}}

### Project Management (4 skills)
- **/overview** - {{描述}}
- **/status** - {{描述}}
- **/maintain-project** - {{描述}}
- **/configure-permissions** - {{描述}}

**Full skills documentation**: [.claude/skills/README.md](.claude/skills/README.md)

## 🚀 How to Use

### Installation
```bash
{{详细安装步骤}}
```

### Quick Start
```bash
{{基本使用命令}}
```

### Common Workflows

**Workflow 1: {{工作流名称}}**
```bash
{{命令序列}}
```

**Workflow 2: {{工作流名称}}**
```bash
{{命令序列}}
```

## 🏗️ Core Architecture

{{架构概览（≤40 行）}}

**Key components:**
- {{组件 1}}: {{说明}}
- {{组件 2}}: {{说明}}

**Detailed architecture**: [docs/arch/ARCHITECTURE.md](docs/arch/ARCHITECTURE.md)

## 💡 Common Use Cases

### Use Case 1: {{场景名称}}
{{详细说明}}

### Use Case 2: {{场景名称}}
{{详细说明}}

### Use Case 3: {{场景名称}}
{{详细说明}}

## 📖 Key Documentation

| Category | Document | Purpose |
|----------|----------|---------|
| **Setup** | [SETUP.md](docs/dev/SETUP.md) | Installation guide |
| **Architecture** | [ARCHITECTURE.md](docs/arch/ARCHITECTURE.md) | System design |
| **ADRs** | [ADRs/](docs/ADRs/) | Architecture decisions |
| **API** | [API.md](docs/arch/API.md) | API documentation |

## 🔗 Related Documents

- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[LICENSE](LICENSE)** - License information
- **[CHANGELOG.md](CHANGELOG.md)** - Version history

---

**Version:** {{version}}
**Last Updated:** {{date}}
**Changelog:**
- {{version}}: {{变更说明}}
```

---

## 参考资源

- 现有项目示例：ai-dev/CLAUDE.md（1156 行，需要重构示例）
- 理想项目示例：u-safe/CLAUDE.md（假设 ≤150 行）
- [Markdown 最佳实践](https://www.markdownguide.org/basic-syntax/)

---

**版本**: 1.0.0
**最后更新**: 2026-03-24
**用途**: AI 维护 CLAUDE.md 的统一参考标准
