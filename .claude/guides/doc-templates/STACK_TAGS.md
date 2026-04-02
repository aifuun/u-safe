# Stack Tags for Documentation Templates

> 基于技术栈的条件化内容生成系统

## 概述

Stack Tags 允许文档模板根据项目技术栈有选择性地包含内容。这是对现有 `{{#if profile}}` 系统的补充，提供更细粒度的控制。

## 标签语法

### 基本语法

```markdown
<!-- @stack: tag1, tag2, tag3 -->
这部分内容只在项目使用 tag1、tag2 或 tag3 时包含
<!-- @end -->
```

### 单标签示例

```markdown
<!-- @stack: aws -->
## AWS 架构

此项目使用 AWS 服务。
<!-- @end -->
```

### 多标签示例（OR 逻辑）

```markdown
<!-- @stack: tauri, electron -->
## 桌面应用配置

桌面应用特定设置...
<!-- @end -->
```

## 支持的标签

### 平台标签
- `tauri` - Tauri 桌面应用
- `nextjs` - Next.js Web 应用
- `react` - React 库
- `vue` - Vue.js 框架

### 后端标签
- `aws` - Amazon Web Services
- `lambda` - AWS Lambda
- `api-gateway` - AWS API Gateway
- `dynamodb` - AWS DynamoDB
- `rds` - AWS RDS
- `rust` - Rust 语言

### 前端标签
- `typescript` - TypeScript
- `javascript` - JavaScript
- `tailwindcss` - Tailwind CSS
- `emotion` - Emotion CSS-in-JS
- `styled-components` - Styled Components

### 数据库标签
- `dynamodb` - DynamoDB
- `rds` - RDS (PostgreSQL/MySQL)
- `sqlite` - SQLite
- `prisma` - Prisma ORM

### 功能标签
- `auth` - 身份验证
- `api` - API 端点
- `realtime` - 实时功能
- `offline` - 离线支持
- `animations` - 动画效果
- `i18n` - 国际化

### 测试标签
- `unit` - 单元测试
- `e2e` - 端到端测试
- `integration` - 集成测试

### 部署标签
- `vercel` - Vercel 平台
- `cloudflare` - Cloudflare Pages
- `github-actions` - GitHub Actions

## 标签检测逻辑

### 基于 Profile 的检测

```python
profile_tags = {
    'tauri': ['tauri', 'rust', 'desktop'],
    'nextjs-aws': ['nextjs', 'react', 'typescript', 'aws', 'lambda', 'api-gateway', 'dynamodb'],
    'tauri-aws': ['tauri', 'rust', 'desktop', 'aws', 'lambda', 'api-gateway', 'dynamodb']
}
```

### 基于项目检查的检测

扫描 package.json 和 Cargo.toml 自动检测标签。

## 标签解析逻辑（OR 逻辑）

```python
def resolve_stack_conditional(line: str, project_tags: list[str]) -> bool:
    """检查 @stack: 条件是否应该包含"""
    match = re.match(r'<!--\s*@stack:\s*(.+?)\s*-->', line)
    if not match:
        return True

    required_tags = [t.strip() for t in match.group(1).split(',')]
    
    # OR 逻辑：任一标签匹配即包含
    return any(tag in project_tags for tag in required_tags)
```

## 使用场景

### 场景 1：云服务相关内容

```markdown
<!-- @stack: aws -->
## AWS 服务架构

### Lambda 函数
- 函数列表

### DynamoDB 表
- 表结构
<!-- @end -->
```

### 场景 2：可选功能

```markdown
<!-- @stack: animations -->
## 动画系统

### 过渡动画
- 页面切换
<!-- @end -->
```

## 与 Profile 条件的比较

| 特性 | `{{#if profile}}` | `@stack:` |
|------|-------------------|-----------|
| 粒度 | 粗（3 个 profile） | 细（40+ 标签） |
| 逻辑 | 精确匹配 | OR 匹配 |
| 用途 | 主要结构差异 | 技术栈特性 |

## 添加新标签

1. 更新此文档添加标签定义
2. 在 `scripts/init-project.py` 中添加检测规则
3. 在相关模板中使用新标签

---

**版本：** 1.0.0
**创建日期：** 2026-03-26
