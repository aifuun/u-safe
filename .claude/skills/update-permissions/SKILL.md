---
name: update-permissions
version: "1.0.1"
framework-only: true
last-updated: "2026-03-24"
---

# Update Permissions - Sync Claude Code Permission Configuration

快速同步 Claude Code 权限配置文件到目标项目。

## 概述

此 skill 用于从 ai-dev 框架复制 `.claude/settings.json` 权限配置到其他项目。

**核心功能**：
1. **从源项目复制配置** - 从 ai-dev/.claude/settings.json 复制
2. **直接覆盖** - 无需备份，简化流程
3. **路径支持** - 支持相对路径和绝对路径
4. **安全检查** - 验证源文件和目标目录存在性
5. **警告提示** - 覆盖前显示警告信息

**为什么需要**：
新项目初始化后需要配置权限，手动复制容易出错且繁琐。此 skill 自动化这个过程，确保配置一致性。

**何时使用**：
- 新项目初始化后需要配置权限
- 现有项目想升级到 ai-dev 的最新权限配置
- 多个项目需要统一权限设置

**工作流序列**：
```
uv run scripts/init-project.py --profile=tauri --name=my-app  # 初始化项目
/update-permissions ../my-app                                    # 同步权限配置（此 skill）
```

## 参数

```bash
/update-permissions <target-project-path>
```

**常用方式**：
```bash
/update-permissions ../u-safe              # 相对路径
/update-permissions /path/to/project       # 绝对路径
```

**选项**：
- `<target-project-path>` - 必需，目标项目路径（相对或绝对）
- `--skip-validation` - 跳过路径验证（被 update-framework 调用时使用）

## AI 执行指令

**关键：参数解析和安全检查**

执行 `/update-permissions` 时，AI 必须遵循此模式：

### 第 1 步：解析目标路径

```python
import os
import sys

# 获取参数
if len(sys.argv) < 2:
    print("❌ 缺少参数")
    print("用法: /update-permissions <target-project-path>")
    sys.exit(1)

target_path = sys.argv[1]

# 转换为绝对路径
target_abs = os.path.abspath(target_path)
```

### 第 2 步：验证源文件存在

```python
source_file = "/Users/woo/dev/ai-dev/.claude/settings.json"

if not os.path.exists(source_file):
    print(f"❌ 源文件不存在: {source_file}")
    print("请确认 ai-dev 项目路径正确")
    sys.exit(1)
```

### 第 3 步：验证目标目录存在

```python
target_dir = os.path.join(target_abs, ".claude")
target_file = os.path.join(target_dir, "settings.json")

if not os.path.exists(target_dir):
    print(f"❌ 目标 .claude/ 目录不存在: {target_dir}")
    print("请先运行: uv run scripts/init-project.py")
    sys.exit(1)
```

### 第 4 步：显示警告（如果文件已存在）

```python
if os.path.exists(target_file):
    print(f"⚠️  警告: 目标文件已存在")
    print(f"   {target_file}")
    print(f"   此操作将覆盖现有配置")
```

### 第 5 步：复制文件

```python
import shutil

try:
    shutil.copy2(source_file, target_file)
    print(f"✅ 权限配置已同步")
    print(f"   源: {source_file}")
    print(f"   目标: {target_file}")
except Exception as e:
    print(f"❌ 复制失败: {e}")
    sys.exit(1)
```

### 第 6 步：验证复制成功

```python
# 验证文件大小一致
source_size = os.path.getsize(source_file)
target_size = os.path.getsize(target_file)

if source_size != target_size:
    print(f"⚠️  警告: 文件大小不一致")
    print(f"   源: {source_size} bytes")
    print(f"   目标: {target_size} bytes")
else:
    print(f"✅ 验证通过: {source_size} bytes")
```

## 工作流步骤

复制此检查清单以跟踪进度：

```
任务进度：
- [ ] 步骤 1: 解析目标路径
- [ ] 步骤 2: 验证源文件存在
- [ ] 步骤 3: 验证目标目录存在
- [ ] 步骤 4: 显示警告（如果需要）
- [ ] 步骤 5: 复制文件
- [ ] 步骤 6: 验证复制成功
```

### 步骤 1: 解析目标路径

**处理相对路径和绝对路径**：
```python
# 相对路径: ../u-safe
# 绝对路径: /Users/woo/dev/u-safe

target_path = sys.argv[1]
target_abs = os.path.abspath(target_path)  # 统一转换为绝对路径
```

### 步骤 2: 验证源文件存在

**检查 ai-dev 项目的 settings.json**：
```bash
source_file="/Users/woo/dev/ai-dev/.claude/settings.json"

if [ ! -f "$source_file" ]; then
    echo "❌ 源文件不存在: $source_file"
    exit 1
fi
```

### 步骤 3: 验证目标目录存在

**确保目标项目已初始化**：
```bash
target_dir="${target_abs}/.claude"

if [ ! -d "$target_dir" ]; then
    echo "❌ 目标 .claude/ 目录不存在: $target_dir"
    echo "请先运行: uv run scripts/init-project.py"
    exit 1
fi
```

### 步骤 4: 显示警告

**如果目标文件已存在**：
```bash
target_file="${target_dir}/settings.json"

if [ -f "$target_file" ]; then
    echo "⚠️  警告: 目标文件已存在"
    echo "   ${target_file}"
    echo "   此操作将覆盖现有配置"
fi
```

### 步骤 5: 复制文件

**使用 cp 命令覆盖**：
```bash
cp "${source_file}" "${target_file}"

if [ $? -eq 0 ]; then
    echo "✅ 权限配置已同步"
else
    echo "❌ 复制失败"
    exit 1
fi
```

### 步骤 6: 验证复制成功

**比较文件大小**：
```bash
source_size=$(stat -f%z "${source_file}")
target_size=$(stat -f%z "${target_file}")

if [ "$source_size" -eq "$target_size" ]; then
    echo "✅ 验证通过: ${source_size} bytes"
else
    echo "⚠️  警告: 文件大小不一致"
    echo "   源: ${source_size} bytes"
    echo "   目标: ${target_size} bytes"
fi
```

## 错误处理

### 缺少参数

```
❌ 缺少参数

用法: /update-permissions <target-project-path>

示例:
  /update-permissions ../u-safe
  /update-permissions /path/to/project
```

### 源文件不存在

```
❌ 源文件不存在

路径: /Users/woo/dev/ai-dev/.claude/settings.json

检查:
  1. ai-dev 项目路径是否正确？
  2. settings.json 文件是否存在？
```

### 目标目录不存在

```
❌ 目标 .claude/ 目录不存在

路径: /path/to/project/.claude

解决:
  1. 先初始化项目: uv run scripts/init-project.py
  2. 或检查目标路径是否正确
```

### 复制失败

```
❌ 复制失败

错误: Permission denied

解决:
  1. 检查目标目录权限
  2. 使用 chmod 修改权限
```

## 示例

### 示例 1: 使用相对路径

**用户说：**
> "sync permissions to u-safe project"

**执行：**
```bash
/update-permissions ../u-safe
```

**输出：**
```
⚠️  警告: 目标文件已存在
   /Users/woo/dev/u-safe/.claude/settings.json
   此操作将覆盖现有配置

✅ 权限配置已同步
   源: /Users/woo/dev/ai-dev/.claude/settings.json
   目标: /Users/woo/dev/u-safe/.claude/settings.json

✅ 验证通过: 1234 bytes
```

### 示例 2: 使用绝对路径

**用户说：**
> "update permissions for /Users/woo/dev/my-project"

**执行：**
```bash
/update-permissions /Users/woo/dev/my-project
```

**输出：**
```
✅ 权限配置已同步
   源: /Users/woo/dev/ai-dev/.claude/settings.json
   目标: /Users/woo/dev/my-project/.claude/settings.json

✅ 验证通过: 1234 bytes
```

### 示例 3: 目标目录不存在

**用户说：**
> "sync permissions to non-existent-project"

**执行：**
```bash
/update-permissions ../non-existent-project
```

**输出：**
```
❌ 目标 .claude/ 目录不存在: /Users/woo/dev/non-existent-project/.claude
请先运行: uv run scripts/init-project.py
```

## 集成

**与项目初始化集成：**
```bash
# 1. 初始化新项目
uv run scripts/init-project.py --profile=tauri --name=my-app

# 2. 同步权限配置（此 skill）
/update-permissions ../my-app

# 3. 开始开发
cd ../my-app
```

**与其他 skills 集成：**
- `/update-framework` - 同步完整框架（包括 skills, rules, workflow, pillars）
- `/update-skills` - 仅同步 skills
- `/configure-permissions` - 配置权限模板（此 skill 是直接复制）

## 最佳实践

1. **新项目初始化后立即同步** - 确保权限配置一致
2. **定期同步** - 当 ai-dev 更新权限配置时
3. **验证配置** - 同步后检查 `.claude/settings.json` 内容
4. **备份重要配置** - 如果目标项目有自定义配置，先备份

## 性能

- **平均时间：** <1 秒
- **文件大小：** ~1-2 KB

快速因为：
- 简单的文件复制操作
- 无需网络请求
- 最小化验证步骤

## 注意事项

⚠️ **覆盖风险**：
- 此 skill 会**直接覆盖**目标项目的 `.claude/settings.json`
- 如果目标项目有自定义权限配置，将会丢失
- 覆盖前会显示警告，但不会要求确认

⚠️ **源文件路径硬编码**：
- 源文件路径为 `/Users/woo/dev/ai-dev/.claude/settings.json`
- 如果 ai-dev 项目位置不同，需要修改此 skill

## 最终验证

**完成前的关键检查：**

```
- [ ] 源文件存在
- [ ] 目标目录存在
- [ ] 文件复制成功
- [ ] 文件大小一致
- [ ] 警告信息已显示（如果适用）
```

如果任何项失败，在完成前解决。

## 输出模式检测

**当被 update-framework 调用时：**
- 检查环境变量：`CALLED_BY_UPDATE_FRAMEWORK`
- 如果设置：输出简化的 1-2 行摘要（例如："✅ Permissions 同步完成: settings.json"）
- 如果未设置：输出完整详细报告（当前行为）

这减少了 update-framework 编排多个同步操作时的总输出长度。

## 相关 Skills

- **/configure-permissions** - 配置权限模板（通过选择模板）
- **/update-framework** - 同步完整框架
- **/update-skills** - 同步 skills 目录

---

**Version:** 1.0.0
**Pattern:** Tool-Utility (direct file operation)
**Compliance:** ADR-001 ✅
**Last Updated:** 2026-03-24
