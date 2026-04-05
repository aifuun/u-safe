---
category: "core"
title: "Documentation Structure"
description: "Doc structure standards"
tags: [typescript, react, rust]
profiles: [tauri, nextjs-aws, minimal]
paths: ['**/*.{ts,tsx}']
version: "1.0.0"
last_updated: "2026-03-27"
---

# 文档结构规范 (Documentation Structure Rule)

> **Complete Manual**: [docs/DOCUMENTATION_MANUAL.md](../../../docs/DOCUMENTATION_MANUAL.md)
> **Version**: 1.0.0
> **Last Updated**: 2026-03-15
> **Compliance**: ADR-001 ✅ | DOCUMENTATION_MANUAL ✅

此 Rule 提供文档结构标准的快速检查清单。完整标准和详细指南请查阅上方的手册链接。

This Rule provides quick checks for documentation structure standards. For complete standards and detailed guidance, see the manual link above.

---

## 原则 (Principles)

### 为什么需要统一文档结构 (Why Unified Structure?)

**问题 (Problems)**:
- 每个项目重新设计文档结构 → 浪费时间
- 文档组织方式不一致 → 团队切换成本高
- 缺少强制性标准 → 文档缺失或混乱

**价值 (Benefits)**:
- ✅ 降低认知负担 - 快速切换项目
- ✅ 提高效率 - 自动化工具可复用
- ✅ 保证质量 - 强制要求关键文档
- ✅ 知识传承 - 新成员只需学习一次

### Divio 文档系统 (Divio Documentation System)

基于四象限理论 (Four-quadrant theory):

| 象限 | 目的 | 受众 | 示例 |
|------|------|------|------|
| **Tutorials** | 帮助新人上手 | 初学者 | SETUP.md |
| **How-to Guides** | 解决具体问题 | 实践者 | DEPLOYMENT.md |
| **Reference** | 查阅具体细节 | 实现者 | API.md, SCHEMA.md |
| **Explanation** | 理解设计决策 | 架构师 | ADRs |

---

## 标准手册引用 (Manual Reference)

**完整手册** (Complete Manual): [docs/DOCUMENTATION_MANUAL.md](../../../docs/DOCUMENTATION_MANUAL.md)

**何时查阅手册 (When to Consult)**:
- 🆕 初始化新项目的文档结构
- 📝 创建新文档类型或目录
- ✅ 验证现有文档是否符合标准
- 🔧 使用文档模板

**快速参考 vs 深入阅读 (Quick Reference vs Deep Dive)**:
- **此 Rule**: 快速检查清单（2 分钟）
- **DOCUMENTATION_MANUAL.md**: 完整标准和模板（30 分钟）

---

## 强制要求 (Mandatory Requirements)

### 所有项目必需文件 (Universal Requirements)

| 文件 | 位置 | 用途 |
|------|------|------|
| **README.md** | `docs/README.md` | 文档导航 |
| **ADR TEMPLATE** | `docs/adr/TEMPLATE.md` | ADR 模板 |
| **PRD** | `docs/product/PRD.md` | 产品需求 |
| **ARCHITECTURE** | `docs/arch/ARCHITECTURE.md` | 系统架构 |
| **SETUP** | `docs/dev/SETUP.md` | 环境搭建 |

### 按项目类型 (Project-Type Specific)

#### Tauri (桌面应用)
**必需**: 5 个通用文件
**可选**: `qa/` (推荐), `ops/` (不需要)

#### Next.js + AWS (Web 应用)
**必需**: 5 个通用文件 + `docs/ops/DEPLOYMENT.md`
**推荐**: `qa/`, `arch/API.md`

#### Tauri + AWS (混合应用)
**必需**: 所有桌面应用文件 + `docs/ops/DEPLOYMENT.md`

### 标准目录结构 (Standard Directory Structure)

```
docs/
├── README.md          # 文档导航（必需）
├── adr/               # 架构决策记录
├── product/           # 产品文档
├── design/            # 设计规格（可选）
├── arch/              # 技术架构
├── dev/               # 开发文档
├── qa/                # 质量保证（Web 推荐）
└── ops/               # 运维文档（云应用必需）
```

**完整目录树**: 见 [DOCUMENTATION_MANUAL.md § 2](../../../docs/DOCUMENTATION_MANUAL.md#2-标准目录结构-standard-directory-structure)

---

## 命名规范 (Naming Conventions)

### 目录命名 (Directory Naming)

**规则**: 全小写，单数形式，简短英文

✅ **正确**:
```
docs/adr/          # 不是 ADRs/ 或 adrs/
docs/product/      # 不是 Product/
docs/arch/         # 不是 architecture/
```

❌ **错误**:
```
docs/ADRs/         # 大写
docs/products/     # 复数
docs/Architecture/ # 大写 + 太长
```

### 文件命名 (File Naming)

**规则**: 大写字母 + 下划线分隔

✅ **正确**:
```
ARCHITECTURE.md
TEST_PLAN.md
UI_UX_DESIGN.md
```

❌ **错误**:
```
architecture.md        # 小写
test-plan.md          # 连字符
CodingStandards.md    # 驼峰命名
```

### ADR 编号 (ADR Numbering)

**格式**: `NNN-kebab-case-title.md`

✅ **正确**:
```
001-record-architecture-decisions.md
010-implement-saga-pattern.md
123-migrate-to-typescript.md
```

❌ **错误**:
```
1-record-decisions.md           # 单数字
ADR-001-use-tauri.md           # 多余前缀
001_use_tauri_framework.md     # 下划线
001-Use-Tauri-Framework.md     # 大写
```

---

## 检查工具 (Validation Tools)

### 自动化检查 (Automated Checks)

#### `/check-docs` Skill (将在 #223 创建)
```bash
/check-docs
```

**功能** (Features):
- 检查目录结构完整性
- 验证命名规范
- 生成合规报告（分数 0-100）
- 识别缺失文件

**输出示例** (Sample Output):
```
📊 Documentation Structure Report
Compliance Score: 95/100

✅ PASSED (12)
❌ FAILED (1) - Missing: docs/adr/README.md
💡 SUGGESTIONS - Run /init-docs
```

#### `/init-docs` Skill (将在 #222 创建)
```bash
/init-docs
```

**功能** (Features):
- 创建标准目录结构
- 生成必需文件
- 从模板填充内容
- 仅创建缺失文件（`--missing-only`）

### 手动检查清单 (Manual Checklist)

#### 基础检查 (Basic Checks)

- [ ] `docs/README.md` 存在且包含导航
- [ ] `docs/adr/` 目录存在（小写）
- [ ] 至少有一个 ADR 或 TEMPLATE.md
- [ ] `docs/product/PRD.md` 存在且非空
- [ ] `docs/arch/ARCHITECTURE.md` 存在且包含架构图
- [ ] `docs/dev/SETUP.md` 存在且可按步骤执行

#### 命名规范检查 (Naming Checks)

- [ ] 所有目录名小写（`adr` 不是 `ADRs`）
- [ ] 文件名使用大写+下划线（`TEST_PLAN.md`）
- [ ] ADR 编号格式正确（`001-title.md`）

#### 质量标准 (Quality Standards)

| 等级 | 分数 | 标准 |
|------|------|------|
| 优秀 | 95-100 | 所有必需文件存在，内容完整 |
| 良好 | 85-94 | 必需文件存在，少量可选文件缺失 |
| 合格 | 70-84 | 核心文件存在，有改进空间 |
| 不合格 | <70 | 缺失关键文档或严重命名违规 |

---

## 示例 (Examples)

### 示例 1: Tauri 桌面应用结构

```
my-tauri-app/
├── docs/
│   ├── README.md                    ✅ 必需
│   ├── adr/
│   │   ├── TEMPLATE.md              ✅ 必需
│   │   └── 001-use-tauri.md
│   ├── product/
│   │   └── PRD.md                   ✅ 必需
│   ├── arch/
│   │   ├── ARCHITECTURE.md          ✅ 必需
│   │   └── SCHEMA.md
│   ├── dev/
│   │   ├── SETUP.md                 ✅ 必需
│   │   └── CONTRIBUTING.md
│   └── qa/                          ⚪ 可选
│       └── TEST_PLAN.md
└── (无 ops/ 目录 - 纯本地应用)
```

**特点** (Characteristics):
- 5 个必需文件 ✅
- 无 `ops/` (纯本地应用不需要)
- `qa/` 推荐但非强制

### 示例 2: Next.js + AWS Web 应用结构

```
my-web-app/
├── docs/
│   ├── README.md                    ✅ 必需
│   ├── adr/
│   │   ├── TEMPLATE.md              ✅ 必需
│   │   ├── 001-use-nextjs.md
│   │   └── 002-use-aws-cdk.md
│   ├── product/
│   │   ├── PRD.md                   ✅ 必需
│   │   └── roadmap.md
│   ├── arch/
│   │   ├── ARCHITECTURE.md          ✅ 必需
│   │   ├── API.md                   ⭐ 推荐
│   │   └── SCHEMA.md
│   ├── dev/
│   │   ├── SETUP.md                 ✅ 必需
│   │   ├── CONTRIBUTING.md
│   │   └── WORKFLOW.md
│   ├── qa/                          ⭐ 推荐
│   │   ├── TEST_PLAN.md
│   │   └── SECURITY_AUDIT.md
│   └── ops/
│       ├── DEPLOYMENT.md            ✅ 必需（云应用）
│       └── MONITORING.md
```

**特点** (Characteristics):
- 6 个必需文件 ✅ (通用 5 + `DEPLOYMENT.md`)
- `ops/` 必需（云应用部署）
- `qa/` 和 `arch/API.md` 强烈推荐

### 示例 3: 常见违规与修复

#### 违规 1: 大写目录名
❌ **错误**:
```
docs/ADRs/
docs/Product/
```

✅ **修复**:
```bash
mv docs/ADRs docs/adr
mv docs/Product docs/product
```

#### 违规 2: 错误的文件命名
❌ **错误**:
```
docs/arch/architecture.md      # 小写
docs/dev/test-plan.md         # 连字符
```

✅ **修复**:
```bash
mv docs/arch/architecture.md docs/arch/ARCHITECTURE.md
mv docs/dev/test-plan.md docs/qa/TEST_PLAN.md
```

#### 违规 3: ADR 编号格式错误
❌ **错误**:
```
docs/adr/1-use-tauri.md               # 单数字
docs/adr/ADR-001-use-nextjs.md       # 多余前缀
```

✅ **修复**:
```bash
mv docs/adr/1-use-tauri.md docs/adr/001-use-tauri.md
mv docs/adr/ADR-001-use-nextjs.md docs/adr/001-use-nextjs.md
```

---

## 快速命令 (Quick Commands)

```bash
# 检查文档结构
/check-docs

# 自动修复（未来功能）
/check-docs --fix

# 初始化标准目录
/init-docs

# 仅创建缺失文件
/init-docs --missing-only

# 查看完整手册
cat docs/DOCUMENTATION_MANUAL.md

# 验证 ADR 格式
ls -la docs/adr/  # 应全部为 NNN-*.md 格式
```

---

## 提交前检查清单 (Pre-Commit Checklist)

开发者在提交代码前应验证：

- [ ] `docs/README.md` 包含最新导航链接
- [ ] 所有目录名符合小写规范
- [ ] 所有文档文件名符合大写+下划线规范
- [ ] ADR 编号格式正确（三位数字 + 连字符 + 小写标题）
- [ ] 新增重要文档已添加到 `docs/README.md` 的导航
- [ ] 无损坏的文档链接
- [ ] 运行 `/check-docs` 分数 ≥ 85

---

## 相关文档 (Related Documentation)

- **[DOCUMENTATION_MANUAL.md](../../../docs/DOCUMENTATION_MANUAL.md)** - 完整标准手册（899 行）
- **[/init-docs Skill](../../skills/init-docs/)** - 自动生成标准文档（Issue #222）
- **[/check-docs Skill](../../skills/check-docs/)** - 自动检查合规性（Issue #223）
- **[Divio Documentation System](https://documentation.divio.com/)** - 四象限理论参考
- **[ADR Standards](https://adr.github.io/)** - 架构决策记录标准

---

## 常见问题 (FAQ)

**Q1: 我的项目既不是 tauri 也不是 nextjs，怎么办？**

A: 遵循通用规则（5 个必需文件），按需调整 `qa/` 和 `ops/` 目录。

**Q2: 可以用中文目录名吗？**

A: 不推荐。使用英文目录名以确保命令行工具兼容性和国际化协作。文件内容可以是中文。

**Q3: ADR 编号从几开始？**

A: 从 `001` 开始。不要重新编号已有 ADR，保持历史记录。

**Q4: `/check-docs` 报告分数低怎么办？**

A: 运行 `/init-docs --missing-only` 创建缺失文件，手动修复命名违规，重新运行 `/check-docs`。

---

**Version**: 1.0.0
**Status**: Active
**Compliance**: ADR-001 ✅ | DOCUMENTATION_MANUAL (Issue #220) ✅
**Part of**: Documentation Manual System (#219)
