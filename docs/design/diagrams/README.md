# Mermaid 图表管理方案

## 📊 问题与解决方案

### 问题：内嵌图表维护困难
- HTML 文件过大（726 行 → 超过 1000 行）
- 修改图表需要在 Markdown、HTML 中同步
- 语法错误难以快速定位
- 无法独立预览和测试

### 解决方案：图表源文件分离
✅ **已实现** - 所有 9 个 Mermaid 图表提取为独立 `.mmd` 文件

## 📁 新文件结构

```
docs/design/diagrams/
├── README.md                       # 使用指南
├── system-architecture.mmd         # 系统三层架构图
├── data-flow.mmd                   # 数据流向图（加密/解密/标签）
├── 1-1-password-setup.mmd         # 密码设置流程
├── 1-2-file-encryption.mmd        # 文件加密流程
├── 1-3-file-decryption.mmd        # 文件解密流程
├── 1-4-password-verification.mmd  # 密码验证流程
├── 2-1-tag-creation.mmd           # 标签创建流程
├── 3-1-view-switching.mmd         # 视图切换流程
├── 4-1-file-addition.mmd          # 文件添加流程
└── VERIFICATION.md                 # 语法验证报告
```

## 🎯 使用方法

### 方式 1: VS Code 直接预览（推荐）

1. 安装扩展：
   ```bash
   code --install-extension bierner.markdown-mermaid
   ```

2. 打开 `.mmd` 文件：
   ```bash
   code docs/spec/diagrams/1-1-password-setup.mmd
   ```

3. 按 `Cmd+Shift+V`（Mac）或 `Ctrl+Shift+V`（Windows）预览

### 方式 2: Mermaid Live Editor

1. 打开 [https://mermaid.live/](https://mermaid.live/)
2. 复制 `.mmd` 文件内容
3. 在线编辑和实时预览
4. 导出为 SVG/PNG

### 方式 3: 命令行生成图片

```bash
# 安装 Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# 生成 SVG
cd docs/spec/diagrams
mmdc -i 1-1-password-setup.mmd -o output/1-1-password-setup.svg

# 批量生成所有图表
for file in *.mmd; do
    mmdc -i "$file" -o "output/${file%.mmd}.svg"
done
```

### 方式 4: 在 HTML 中动态加载

```html
<!-- 占位符 -->
<div class="mermaid-loader" data-src="diagrams/1-1-password-setup.mmd"></div>

<!-- 加载脚本 -->
<script>
document.querySelectorAll('.mermaid-loader').forEach(async (el) => {
    const src = el.getAttribute('data-src');
    const response = await fetch(src);
    const code = await response.text();
    el.innerHTML = `<div class="mermaid">${code}</div>`;
});
</script>
```

## ✏️ 修改图表工作流

### 旧流程（复杂）
```
1. 在 Markdown 中修改图表
2. 手动复制到 HTML
3. 检查语法错误
4. 在浏览器中验证
5. 提交 2 个文件
```

### 新流程（简单）
```
1. 直接编辑 .mmd 文件
2. VS Code 实时预览验证
3. 提交 1 个文件
4. 自动同步到 Markdown/HTML（可选）
```

## 🔧 集成到构建流程（未来）

### 选项 1: 预生成 SVG
```bash
# 在构建时生成所有 SVG
npm run build:diagrams

# 结果
docs/spec/diagrams/output/
├── 1-1-password-setup.svg
├── 1-2-file-encryption.svg
└── ...
```

在 HTML 中使用：
```html
<img src="diagrams/output/1-1-password-setup.svg" alt="密码设置流程">
```

**优点**: 加载快、无需 JavaScript、兼容性好
**缺点**: 失去交互性

### 选项 2: 动态加载 .mmd
```javascript
// 运行时加载和渲染
async function loadDiagram(element) {
    const src = element.dataset.src;
    const code = await fetch(src).then(r => r.text());
    element.innerHTML = `<div class="mermaid">${code}</div>`;
    mermaid.init();
}
```

**优点**: 保持交互性、易于更新
**缺点**: 需要网络请求

## 📋 维护检查清单

修改图表时，确保：

- [ ] 在 `.mmd` 文件中编辑
- [ ] 使用 Mermaid Live Editor 或 VS Code 验证语法
- [ ] 避免使用 HTML 标签（`<br/>` 等）
- [ ] 节点文本使用空格和括号代替换行
- [ ] 提交前运行语法检查
- [ ] 同步更新 Markdown 和 HTML（如果需要）

## 🎉 优势总结

| 维度 | 内嵌方式 | 分离方式 ✅ |
|------|---------|------------|
| **可维护性** | 低（需同步多处） | 高（单一源文件） |
| **版本控制** | 困难（大文件） | 简单（小文件） |
| **预览速度** | 慢（需重新生成） | 快（实时预览） |
| **复用性** | 不可复用 | 可跨文档复用 |
| **协作** | 冲突多 | 冲突少 |
| **文件大小** | HTML 1000+ 行 | .mmd 平均 500B |

## 🚀 下一步

### 短期（完成）
- ✅ 提取所有 7 个图表为 `.mmd` 文件
- ✅ 修复所有 Mermaid 语法错误
- ✅ 创建使用文档

### 中期（可选）
- [ ] 集成到构建流程（自动生成 SVG）
- [ ] HTML 改用动态加载方式
- [ ] 添加图表版本历史追踪

### 长期（高级）
- [ ] 图表编辑器集成（在线编辑）
- [ ] 自动化测试（语法检查）
- [ ] 多语言图表支持（中英文）

## 📚 相关文档

- [diagrams/README.md](./diagrams/README.md) - 图表文件使用指南
- [MERMAID_VERIFICATION.md](./MERMAID_VERIFICATION.md) - 语法修复验证报告
- [Mermaid 官方文档](https://mermaid.js.org/)

---

**创建日期**: 2025-01-XX
**状态**: ✅ 已实现
**维护者**: U-Safe Team
