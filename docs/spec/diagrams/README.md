# Mermaid 图表文件

本目录存放所有 PRD_Core_Logic 文档的 Mermaid 图表源文件。

## 文件列表

| 文件名 | 标题 | 类型 | 说明 |
|--------|------|------|------|
| `1-1-password-setup.mmd` | 用户首次设置密码流程 | sequenceDiagram | 密码初始化和主密钥生成 |
| `1-2-file-encryption.mmd` | 文件加密流程 | flowchart TD | 64KB 分块加密详细流程 |
| `1-3-file-decryption.mmd` | 文件解密流程 | flowchart TD | 临时解密和内存清零 |
| `1-4-password-verification.mmd` | 密码验证机制 | sequenceDiagram | Argon2id 验证和缓存机制 |
| `2-1-tag-creation.mmd` | 标签创建流程 | flowchart TD | 层级标签创建和验证 |
| `3-1-view-switching.mmd` | 视图切换逻辑 | stateDiagram-v2 | 物理视图和标签视图切换 |
| `4-1-file-addition.mmd` | 新增文件流程 | flowchart TD | 文件添加和加密选项 |

## 使用方法

### 方法 1: Mermaid Live Editor

1. 访问 [Mermaid Live Editor](https://mermaid.live/)
2. 复制 `.mmd` 文件内容
3. 在线编辑和预览
4. 导出为 SVG/PNG

### 方法 2: VS Code 扩展

安装 `Mermaid Preview` 扩展：
```bash
code --install-extension bierner.markdown-mermaid
```

然后直接在 VS Code 中预览 `.mmd` 文件。

### 方法 3: 命令行工具

安装 Mermaid CLI：
```bash
npm install -g @mermaid-js/mermaid-cli
```

生成图片：
```bash
mmdc -i 1-1-password-setup.mmd -o 1-1-password-setup.svg
mmdc -i 1-1-password-setup.mmd -o 1-1-password-setup.png
```

### 方法 4: HTML 动态加载

在 HTML 中使用 JavaScript 加载：
```html
<div class="mermaid-container" data-src="diagrams/1-1-password-setup.mmd"></div>

<script>
document.querySelectorAll('.mermaid-container').forEach(async (el) => {
    const src = el.getAttribute('data-src');
    const response = await fetch(src);
    const diagram = await response.text();
    el.innerHTML = `<div class="mermaid">${diagram}</div>`;
});
</script>
```

## 语法规范

### 命名约定
- 文件名：`{章节}-{子节}-{名称}.mmd`
- 格式：kebab-case
- 编码：UTF-8

### 中文支持
所有图表支持中文节点和标签，无需特殊处理。

### 避免的语法
- ❌ HTML 标签（`<br/>`, `<b>` 等）
- ❌ 特殊字符未转义
- ✅ 使用空格和括号代替换行

## 维护流程

1. **修改图表**：直接编辑 `.mmd` 文件
2. **验证语法**：使用 Mermaid Live Editor 验证
3. **更新文档**：同步到 Markdown 和 HTML 版本
4. **提交代码**：
   ```bash
   git add docs/spec/diagrams/
   git commit -m "docs: update diagram X"
   ```

## 版本控制

所有 `.mmd` 文件都纳入 Git 版本控制，方便追踪修改历史和协作。

---

**创建日期**: 2025-01-XX
**维护者**: U-Safe Team
