# Issue #21: Phase 4 (M4): 标签系统 - Tag System

**GitHub**: https://github.com/aifuun/u-safe/issues/21
**Branch**: feature/21-tag-system
**Worktree**: /Users/woo/dev/u-safe-21-tag-system
**Started**: 2026-03-19

---

## 🎯 目标

实现 P1 标签管理和视图切换

**Duration**: 12 天 (乐观: 10 天，悲观: 14 天)
**Week**: Week 5-6

---

## 📋 任务清单

**依赖顺序**: Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6

### Phase 1: Tag Management Foundation (3 天)
**依赖**: 无（基础功能）

#### 1.1 标签创建 (0.5 天)
- [ ] 设计 `Tag` 数据结构 (id, name, parent_id, color, created_at)
- [ ] 实现 Rust IPC 命令 `create_tag(name, parent_id?, color?)`
  - [ ] 验证标签名称（非空，≤50字符，无特殊字符）
  - [ ] 检查同级标签重名
  - [ ] SQLite INSERT 操作 + 返回新标签 ID
  - [ ] 记录日志: `log::info!("[tag:create] name={}, parent_id={:?}")`
- [ ] 前端 TagCreateForm 组件
  - [ ] 输入框 + 颜色选择器 + 父标签下拉框
  - [ ] 表单验证（客户端）
  - [ ] 调用 `invoke('create_tag', { name, parentId, color })`
  - [ ] 错误处理：显示 Toast 提示
- [ ] 错误处理: 标签名重复返回明确错误 `TagNameDuplicate`

#### 1.2 标签编辑 (0.5 天)
- [ ] 实现 Rust IPC 命令 `update_tag(id, name?, color?)`
  - [ ] 验证标签存在
  - [ ] 验证新名称不重复（同级）
  - [ ] SQLite UPDATE 操作
  - [ ] 记录日志: `log::info!("[tag:update] id={}, changes={:?}")`
- [ ] 前端 TagEditForm 组件
  - [ ] 预填充当前标签信息
  - [ ] 表单验证
  - [ ] 错误处理：标签不存在、名称冲突
- [ ] 错误处理: 标签不存在返回 `TagNotFound`

#### 1.3 层级标签结构 (0.5 天)
- [ ] 数据库 Schema 验证：`tags.parent_id` 外键约束
- [ ] 实现 Rust 查询 `get_tag_tree()` 返回嵌套结构
  - [ ] 递归查询最多 5 层
  - [ ] 防止循环引用检查
  - [ ] 记录日志: `log::info!("[tag:tree:query] depth={}")`
- [ ] 前端 TagTree 组件基础结构
  - [ ] 递归渲染标签层级
  - [ ] 展开/折叠状态管理
- [ ] 错误处理: 循环引用检测 `CircularDependencyError`

#### 1.4 标签树组件 (UI) (0.5 天)
- [ ] TagTree 交互功能
  - [ ] 点击展开/折叠子标签
  - [ ] 拖拽重新排序（预留接口）
  - [ ] 右键菜单：编辑、删除、添加子标签
- [ ] 样式：缩进、图标、颜色标记
- [ ] 性能优化：虚拟滚动（支持 100+ 标签）

#### 1.5 标签删除 + 级联检查 (1 天)
- [ ] 实现 Rust IPC 命令 `delete_tag(id, force?)`
  - [ ] 检查标签是否有子标签（有则报错或递归删除）
  - [ ] 检查标签是否关联文件（有则报错或解除关联）
  - [ ] SQLite DELETE 操作（级联删除 file_tags 关联）
  - [ ] 记录日志: `log::warn!("[tag:delete] id={}, has_files={}, has_children={}")`
- [ ] 前端删除确认对话框
  - [ ] 显示关联文件数量
  - [ ] 显示子标签数量
  - [ ] 提供选项：仅删除标签、删除标签+子标签、取消
- [ ] 错误处理：
  - [ ] `TagHasChildren` - 标签有子标签
  - [ ] `TagHasFiles` - 标签关联文件
  - [ ] `TagInUse` - 标签正在使用中

---

### Phase 2: File-Tag Association (2 天)
**依赖**: Phase 1 完成（标签基础功能）

#### 2.1 文件打标签 IPC 命令 (0.5 天)
- [ ] 实现 Rust IPC 命令 `add_tag_to_file(file_id, tag_id)`
  - [ ] 验证文件存在 (files 表查询)
  - [ ] 验证标签存在 (tags 表查询)
  - [ ] 检查关联是否已存在（幂等性）
  - [ ] SQLite INSERT INTO file_tags (file_id, tag_id, created_at)
  - [ ] 记录日志: `log::info!("[file:tag:add] file_id={}, tag_id={}")`
- [ ] 错误处理：
  - [ ] `FileNotFound` - 文件不存在
  - [ ] `TagNotFound` - 标签不存在
  - [ ] `DuplicateAssociation` - 关联已存在（幂等返回成功）

#### 2.2 文件解除标签 (0.5 天)
- [ ] 实现 Rust IPC 命令 `remove_tag_from_file(file_id, tag_id)`
  - [ ] 验证关联存在
  - [ ] SQLite DELETE FROM file_tags WHERE ...
  - [ ] 幂等性：关联不存在时返回成功
  - [ ] 记录日志: `log::info!("[file:tag:remove] file_id={}, tag_id={}")`
- [ ] 错误处理：关联不存在时不报错（幂等）

#### 2.3 标签批量操作 (0.5 天)
- [ ] 实现 Rust IPC 命令 `add_tags_to_file(file_id, tag_ids[])`
  - [ ] 批量验证标签存在
  - [ ] 批量插入 file_tags（使用事务）
  - [ ] 记录日志: `log::info!("[file:tag:batch_add] file_id={}, count={}")`
- [ ] 实现 Rust IPC 命令 `remove_tags_from_file(file_id, tag_ids[])`
  - [ ] 批量删除（使用事务）
  - [ ] 记录日志: `log::info!("[file:tag:batch_remove] file_id={}, count={}")`
- [ ] 错误处理: 部分标签不存在时返回 `PartialSuccess` + 失败列表

#### 2.4 关联关系查询 (0.5 天)
- [ ] 实现 Rust IPC 命令 `get_file_tags(file_id)`
  - [ ] 查询文件的所有标签（JOIN tags 表获取标签详情）
  - [ ] 返回标签数组（按创建时间排序）
- [ ] 实现 Rust IPC 命令 `get_tag_files(tag_id, recursive?)`
  - [ ] 查询标签关联的所有文件
  - [ ] recursive=true 时递归查询子标签的文件
  - [ ] 返回文件列表 + 元数据
- [ ] 记录日志: `log::info!("[query:file_tags] file_id={}, count={}")`

---

### Phase 3: Tag View & Search (3 天)
**依赖**: Phase 2 完成（文件-标签关联）

#### 3.1 标签树组件增强 (0.5 天)
- [ ] TagTree 显示每个标签的文件数量
  - [ ] 查询文件计数（缓存优化）
  - [ ] 递归统计子标签文件数
- [ ] 点击标签时切换到标签视图
  - [ ] 触发 `onTagSelect(tagId)` 事件
- [ ] 标签高亮：当前选中标签

#### 3.2 标签分组文件列表 (1 天)
- [ ] TagFileList 组件
  - [ ] 显示选中标签的所有文件
  - [ ] 文件卡片：文件名、大小、加密状态、标签列表
  - [ ] 支持拖拽文件到标签（添加标签）
- [ ] 实现 Rust 查询 `get_files_by_tag(tag_id, recursive, sort_by?)`
  - [ ] 支持排序：name, size, created_at, modified_at
  - [ ] 分页支持（可选）
  - [ ] 记录日志: `log::info!("[view:tag_files] tag_id={}, count={}")`
- [ ] 空状态：标签无文件时显示提示

#### 3.3 子标签递归查询 (0.5 天)
- [ ] 实现 Rust 递归查询 `get_descendant_tags(tag_id)`
  - [ ] 返回所有子标签 ID 列表（最多 5 层）
  - [ ] 防止无限递归（深度限制）
  - [ ] 记录日志: `log::info!("[query:descendants] tag_id={}, depth={}")`
- [ ] 前端开关：递归查询子标签文件（默认开启）
- [ ] 错误处理: 超过 5 层时返回 `MaxDepthExceeded`

#### 3.4 标签过滤器 (0.5 天)
- [ ] TagFilter 组件
  - [ ] 多标签选择（AND / OR 逻辑）
  - [ ] 清除过滤
- [ ] 实现 Rust IPC 命令 `filter_files_by_tags(tag_ids[], logic: 'AND' | 'OR')`
  - [ ] AND: 文件必须有所有标签
  - [ ] OR: 文件有任意标签即可
  - [ ] 返回过滤后的文件列表
  - [ ] 记录日志: `log::info!("[filter:tags] tag_ids={:?}, logic={}")`

#### 3.5 基础搜索 (0.5 天)
- [ ] SearchBar 组件
  - [ ] 输入框：搜索文件名或标签名
  - [ ] 实时搜索（防抖 300ms）
- [ ] 实现 Rust IPC 命令 `search_files(query, search_in: 'name' | 'tags' | 'both')`
  - [ ] SQLite LIKE 查询：`WHERE file.name LIKE '%query%'`
  - [ ] 标签搜索：`WHERE tag.name LIKE '%query%'` + JOIN file_tags
  - [ ] 性能优化：添加索引 `CREATE INDEX idx_tags_name ON tags(name)`
  - [ ] 记录日志: `log::info!("[search] query={}, results={}")`

#### 3.6 搜索结果高亮 (0.5 天)
- [ ] 前端高亮匹配文本
  - [ ] 使用 `<mark>` 标签包裹匹配部分
  - [ ] CSS 样式：背景黄色高亮
- [ ] 搜索结果排序：精确匹配优先 → 前缀匹配 → 包含匹配

---

### Phase 4: View Switching (1 天)
**依赖**: Phase 3 完成（标签视图）

#### 4.1 物理视图 ↔ 标签视图切换 (0.5 天)
- [ ] ViewSwitcher 组件
  - [ ] 按钮切换：物理视图 | 标签视图
  - [ ] 状态管理：useViewStore (Zustand)
  - [ ] 路由同步：`/files` (物理) vs `/tags` (标签)
- [ ] 实现视图切换逻辑
  - [ ] 切换时保存当前滚动位置
  - [ ] 切换时清空搜索状态（可选）

#### 4.2 视图状态持久化 (0.25 天)
- [ ] 将视图选择保存到 localStorage
  - [ ] `view_mode: 'physical' | 'tag'`
  - [ ] 应用启动时恢复视图
- [ ] 保存每个视图的状态
  - [ ] 物理视图：当前目录、排序方式
  - [ ] 标签视图：选中标签、过滤条件

#### 4.3 切换动画 (0.25 天)
- [ ] CSS 过渡动画：淡入淡出 (300ms)
  - [ ] `transition: opacity var(--duration-base) var(--ease-out)`
  - [ ] 支持 `@media (prefers-reduced-motion: reduce)` 无动画
- [ ] 骨架屏：视图加载时显示

---

### Phase 5: Testing & Edge Cases (1 天)
**依赖**: Phase 4 完成（基础功能完整）

#### 5.1 单元测试: 标签 CRUD (0.25 天)
- [ ] 测试 `create_tag` - 成功创建、名称重复、验证失败
- [ ] 测试 `update_tag` - 成功更新、标签不存在、名称冲突
- [ ] 测试 `delete_tag` - 成功删除、有子标签、有关联文件
- [ ] 测试 `get_tag_tree` - 层级结构、循环引用检测

#### 5.2 边缘情况测试 (0.25 天)
- [ ] 测试深度 >5 层的标签嵌套（应报错）
- [ ] 测试孤立文件（无标签）查询
- [ ] 测试循环依赖：标签 A → B → A（应检测并报错）
- [ ] 测试标签删除时文件关联处理（cascade delete）
- [ ] 测试并发操作：同时创建同名标签

#### 5.3 性能测试 (0.25 天)
- [ ] 测试 100 个标签的树渲染性能 (< 500ms)
- [ ] 测试 1000 个文件的标签过滤性能 (< 1s)
- [ ] 测试递归查询 5 层标签的性能
- [ ] 数据库索引验证：
  - [ ] `CREATE INDEX idx_file_tags_file_id ON file_tags(file_id)`
  - [ ] `CREATE INDEX idx_file_tags_tag_id ON file_tags(tag_id)`
  - [ ] `CREATE INDEX idx_tags_parent_id ON tags(parent_id)`

#### 5.4 UI/UX 测试 (0.25 天)
- [ ] 标签树交互测试：展开/折叠、拖拽
- [ ] 视图切换流畅性测试
- [ ] 搜索响应时间测试 (< 500ms)
- [ ] 错误提示清晰度测试
- [ ] 可访问性测试：键盘导航、屏幕阅读器

---

### Phase 6: Extensions & Polish (2 天)
**依赖**: Phase 5 完成（核心功能稳定）

#### 6.1 标签重命名 + 递归更新 (0.5 天)
- [ ] 实现 `rename_tag(id, new_name)` IPC 命令
  - [ ] 验证新名称不重复（同级）
  - [ ] 更新标签名称
  - [ ] 记录日志: `log::info!("[tag:rename] id={}, old={}, new={}")`
- [ ] 前端重命名 UI（内联编辑）

#### 6.2 标签拖拽排序 (1 天)
- [ ] 实现标签 `display_order` 字段
  - [ ] 数据库迁移：添加 `display_order INTEGER` 列
- [ ] 实现 Rust IPC 命令 `reorder_tags(tag_ids[])`
  - [ ] 批量更新 display_order
  - [ ] 记录日志: `log::info!("[tag:reorder] count={}")`
- [ ] 前端拖拽库集成 (react-dnd 或 dnd-kit)
  - [ ] 拖拽重新排序
  - [ ] 拖拽改变父标签（移动到其他标签下）
- [ ] 错误处理: 拖拽到自身子标签时报错 `InvalidMove`

#### 6.3 多文件批量打标签 (0.5 天)
- [ ] 实现 Rust IPC 命令 `add_tag_to_files(file_ids[], tag_id)`
  - [ ] 批量插入 file_tags（使用事务）
  - [ ] 幂等性：已存在的关联跳过
  - [ ] 记录日志: `log::info!("[batch:tag_files] tag_id={}, count={}")`
- [ ] 前端多选文件 UI
  - [ ] Checkbox 批量选择
  - [ ] 右键菜单：添加标签
  - [ ] 批量操作进度条

---

## 🔍 错误处理策略

### 标签操作错误码
- `TagNotFound` - 标签不存在
- `TagNameDuplicate` - 同级标签名称重复
- `TagHasChildren` - 标签有子标签，无法删除
- `TagHasFiles` - 标签关联文件，无法删除
- `CircularDependency` - 检测到循环引用
- `MaxDepthExceeded` - 标签嵌套超过 5 层
- `InvalidMove` - 无效的拖拽移动（如移动到自身子标签）

### 文件-标签关联错误码
- `FileNotFound` - 文件不存在
- `DuplicateAssociation` - 关联已存在（幂等返回成功）
- `PartialSuccess` - 部分操作成功（批量操作时）

### 错误日志格式
```rust
log::error!("[tag:create:failed] name={}, error={}", name, error);
log::warn!("[tag:delete:blocked] id={}, reason=has_children", id);
```

---

## 📊 日志规范

### 标签操作日志
- `[tag:create]` - 标签创建
- `[tag:update]` - 标签更新
- `[tag:delete]` - 标签删除
- `[tag:rename]` - 标签重命名
- `[tag:reorder]` - 标签排序

### 查询日志
- `[query:tag_tree]` - 标签树查询
- `[query:file_tags]` - 文件标签查询
- `[query:tag_files]` - 标签文件查询
- `[query:descendants]` - 子标签递归查询

### 性能日志
- `[perf:tag_tree]` - 标签树渲染性能
- `[perf:filter]` - 过滤操作性能
- `[perf:search]` - 搜索操作性能

### 错误日志
- `[tag:create:failed]` - 创建失败
- `[tag:delete:blocked]` - 删除被阻止
- `[circular_dependency:detected]` - 循环依赖检测

---

## ✅ 成功标准

- ✅ 支持 5 层标签嵌套
- ✅ 标签创建/编辑 < 200ms
- ✅ 视图切换 < 200ms
- ✅ 100 个标签无卡顿
- ✅ 搜索响应 < 500ms (1000 个文件)

---

## 📚 参考文档

- `docs/roadmap/MVP_v1.0_Implementation_Plan.md`
- `docs/spec/Database_Schema.md`
- `.claude/plans/active/mvp-v1.0-plan.md`

---

## 🔄 进度追踪

- [ ] Plan reviewed
- [ ] Implementation started
- [ ] Tests added
- [ ] Ready for review

---

## 🚀 下一步

1. Review this plan
2. Get first task: `/next`
3. Start implementation
4. When done: `/finish-issue #21`

---

**Phase**: 4/6
**Milestone**: M4
**Priority**: P1
**Dependencies**: Phase 3 (M3) must be complete
