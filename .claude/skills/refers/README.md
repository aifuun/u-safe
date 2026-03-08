# Official Anthropic Skills Reference

> 从 [anthropic-skills](https://github.com/anthropics/anthropic-skills) 项目精选的 5 个代表性 skills

## 📚 Skills 列表

| Skill | 大小 | 类型 | 说明 |
|-------|------|------|------|
| **skill-creator** | 260KB | 工具 | 用于创建和管理其他 skills 的元工具 |
| **mcp-builder** | 144KB | 工具 | MCP (Model Context Protocol) server 构建工具 |
| **pdf** | 80KB | 文档 | PDF 文档生成和处理 |
| **claude-api** | 236KB | API | Claude API 集成示例（多语言） |
| **canvas-design** | 5.5MB | 设计 | Canvas 设计工具和字体资源 |

## 🎯 选择标准

这 5 个 skills 代表了不同的类别：

1. **Meta-Tool (元工具)**
   - skill-creator: 创建其他 skills 的工具

2. **Developer Tools (开发工具)**
   - mcp-builder: 构建 MCP servers
   - claude-api: API 集成示例

3. **Document Processing (文档处理)**
   - pdf: PDF 生成和处理

4. **Design Tools (设计工具)**
   - canvas-design: 视觉设计工具

## 📖 使用方式

### skill-creator

用于创建新的 skills：
```bash
/skill-creator
```

查看详细内容：
- `skill-creator/SKILL.md` - 主要文档
- `skill-creator/references/` - 参考资料
- `skill-creator/agents/` - 代理配置
- `skill-creator/scripts/` - 脚本工具

### mcp-builder

构建 MCP servers：
```bash
/mcp-builder
```

### pdf

PDF 处理：
```bash
/pdf
```

### claude-api

多语言 API 示例：
- `claude-api/curl/` - cURL 示例
- `claude-api/python/` - Python 示例
- `claude-api/go/` - Go 示例
- `claude-api/java/` - Java 示例
- `claude-api/csharp/` - C# 示例

### canvas-design

Canvas 设计工具：
```bash
/canvas-design
```

## 🔗 相关资源

- **官方仓库**: https://github.com/anthropics/anthropic-skills
- **下载日期**: 2026-03-05
- **用途**: 作为参考，学习官方 skill 的最佳实践

## 📝 注意事项

1. 这些是官方 Anthropic skills 的**参考副本**
2. 用于学习和参考，不直接使用
3. 每个 skill 包含完整的 LICENSE.txt
4. 定期检查官方仓库的更新

---

**维护者**: AI Dev Framework Team
**最后更新**: 2026-03-05
**来源**: anthropic-skills repository
