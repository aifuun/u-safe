# Issue #22: Phase 5 (M5): 体验完善 - UX Polish

**GitHub**: https://github.com/aifuun/u-safe/issues/22
**Branch**: feature/22-ux-polish
**Worktree**: /Users/woo/dev/u-safe-22-ux-polish
**Started**: 2026-03-20

---

## 🎯 目标

实现 P2 辅助功能，提升易用性

**Duration**: 10 天 (乐观: 8 天，悲观: 12 天)
**Week**: Week 7
**Phase**: 5/6
**Milestone**: M5
**Priority**: P2
**Dependencies**: Phase 4 (M4) must be complete

---

## 📋 任务清单

### File Operations (2 天)

#### 1.1 拖拽导入功能
- [ ] 实现拖拽区域组件 (DragDropZone)
  - 使用 HTML5 Drag & Drop API
  - 视觉反馈: 拖入时高亮边框
  - 支持多文件拖拽
- [ ] 文件类型验证
  - 白名单: 常见文档、图片、视频格式
  - 大小限制: 单文件 < 2GB (警告), < 5GB (阻止)
  - 错误提示: 不支持的格式、文件过大
- [ ] 批量导入逻辑
  - 队列处理: 一次最多 100 个文件
  - 进度显示: 总进度 + 当前文件
  - 失败处理: 记录失败文件，继续处理

#### 1.2 文件删除流程
- [ ] 确认对话框 (Modal)
  - 显示文件名和大小
  - 警告: 删除后无法恢复
  - 按钮: 取消 (默认) / 确认删除 (危险色)
- [ ] 数据库清理逻辑
  - 删除 `files` 表记录
  - 删除 `file_tags` 关联
  - 删除 `encryption_meta` 元数据
- [ ] 物理文件删除
  - 加密文件: 删除 `.u-safe/` 中的加密版本
  - 临时文件: 清理可能的解密缓存

#### 1.3 文件重命名功能
- [ ] UI 交互
  - 双击文件名进入编辑模式
  - 输入验证: 不允许空白、特殊字符
  - ESC 取消、Enter 确认
- [ ] 数据库更新
  - 更新 `files.name` 字段
  - 保持 `file_tags` 关联不变
- [ ] 元数据同步
  - 更新 `encryption_meta.original_name`
  - 不重命名加密文件 (保持内部 ID)

### Progress & Feedback (2 天)

#### 2.1 Tauri IPC 进度事件设计
- [ ] 后端事件定义 (Rust)
  ```rust
  // Event payloads
  struct EncryptProgress { file_id: String, percent: f32, bytes_done: u64 }
  struct DecryptProgress { file_id: String, percent: f32, bytes_done: u64 }

  // Emit events
  app.emit_all("encrypt-progress", EncryptProgress { ... })
  app.emit_all("decrypt-progress", DecryptProgress { ... })
  app.emit_all("operation-complete", { file_id, status })
  ```
- [ ] 前端事件监听 (TypeScript)
  ```typescript
  import { listen } from '@tauri-apps/api/event';

  useEffect(() => {
    const unlisten = listen<EncryptProgress>('encrypt-progress', (event) => {
      setProgress(event.payload.percent);
    });
    return () => { unlisten.then(fn => fn()); };
  }, []);
  ```

#### 2.2 进度条组件
- [ ] 使用自建组件 (不依赖第三方库)
  - 基于 `docs/design/FEEDBACK.md` 规范
  - 使用 Design Tokens: `--color-primary`, `--radius-md`
- [ ] 显示内容
  - 百分比文字: "45%"
  - 进度条填充: 0-100% 动画
  - 状态文字: "正在加密..." / "正在解密..."
- [ ] 交互
  - 取消按钮 (可选，复杂实现)
  - 完成后自动消失 (3 秒延迟)

#### 2.3 Toast 提示组件
- [ ] 组件库选择: 自建 Toast (参考 `docs/design/FEEDBACK.md`)
- [ ] Toast 配置
  - 位置: 右上角 (Desktop), 顶部居中 (Mobile)
  - 持续时间: 成功 3 秒, 错误 5 秒, 警告 4 秒
  - 最大数量: 同时显示 3 个
- [ ] 类型
  - Success: ✅ 绿色, "文件加密成功"
  - Error: ❌ 红色, "加密失败: 磁盘空间不足"
  - Warning: ⚠️ 黄色, "文件过大，可能耗时较长"
  - Info: ℹ️ 蓝色, "文件已添加到队列"

#### 2.4 错误信息友好化
- [ ] 映射技术错误到用户语言
  - `ENOSPC` → "磁盘空间不足，请清理空间后重试"
  - `EACCES` → "无权限访问该文件"
  - `InvalidPassword` → "密码错误，请重新输入"
- [ ] 提供解决建议
  - 错误消息 + 操作提示
  - 示例: "加密失败: 磁盘空间不足。请删除一些文件后重试。"

#### 2.5 Loading 状态
- [ ] 按钮 Loading
  - Spinner 图标 (CSS 动画)
  - 禁用按钮点击
  - 文字: "加密中..." / "删除中..."
- [ ] 页面 Loading
  - Skeleton 占位符 (文件列表)
  - 全屏 Loading (首次加载)

### UI Polish (3 天)

#### 3.1 响应式布局 (参考 `docs/spec/UI_UX_Design_System.md`)
- [ ] 移动端适配 (< 768px)
  - 单列布局
  - 触摸友好: 按钮最小 44×44px
  - 隐藏侧边栏，使用汉堡菜单
- [ ] 平板适配 (768px - 1024px)
  - 双列布局 (侧边栏 + 主内容)
  - 文件卡片网格: 2 列
- [ ] 桌面大屏优化 (> 1024px)
  - 三列布局 (侧边栏 + 文件列表 + 详情面板)
  - 文件卡片网格: 3-4 列

#### 3.2 Design Token 应用 (参考 `docs/design/`)
- [ ] 颜色 (`COLOR.md`)
  - 使用 `--color-primary` (品牌色)
  - 使用 `--color-success`, `--color-error` (语义色)
  - 使用 `--bg-default`, `--bg-card` (背景色)
- [ ] 间距 (`SPACING.md`)
  - 使用 `--space-4` (16px, 卡片 padding)
  - 使用 `--space-2` (8px, 按钮间距)
  - 使用 `--space-6` (24px, 章节间距)
- [ ] 圆角 (`RADIUS.md`)
  - 使用 `--radius-md` (8px, 卡片/按钮)
  - 使用 `--radius-sm` (4px, 输入框)
- [ ] 阴影 (`SHADOWS.md`)
  - 使用 `--shadow-1` (卡片默认)
  - 使用 `--shadow-2` (卡片 hover)
  - 使用 `--shadow-3` (模态框)
- [ ] 动画 (`MOTION.md`)
  - 使用 `--duration-fast` (200ms, 按钮 hover)
  - 使用 `--ease-out` (过渡曲线)
  - 支持 `@media (prefers-reduced-motion: reduce)`

#### 3.3 交互动画
- [ ] 过渡动画
  - 按钮 hover: `background-color var(--duration-fast) var(--ease-out)`
  - 卡片 hover: `box-shadow var(--duration-fast) var(--ease-out)`
  - 模态框: 淡入淡出 + 缩放
- [ ] 微交互
  - 文件添加: 从顶部滑入
  - 文件删除: 淡出 + 高度折叠
  - Toast: 从右侧滑入

#### 3.4 无障碍支持 (参考 `docs/design/ACCESSIBILITY.md`)
- [ ] ARIA 属性
  - 按钮: `aria-label="删除文件"`, `role="button"`
  - 模态框: `role="dialog"`, `aria-modal="true"`, `aria-labelledby`
  - 进度条: `role="progressbar"`, `aria-valuenow`, `aria-valuemin`, `aria-valuemax`
- [ ] 键盘导航
  - Tab 顺序合理
  - Enter 触发按钮
  - Escape 关闭模态框
  - 焦点捕获 (模态框打开时)
- [ ] 颜色对比度
  - 文本: 4.5:1 (WCAG AA)
  - 大文本: 3:1 (WCAG AA)
  - 非文本 (图标、边框): 3:1
- [ ] 焦点可见
  - 使用 `outline: 2px solid var(--color-primary)`
  - 不使用 `outline: none` (除非有自定义焦点样式)

#### 3.5 平台特性 (Windows/macOS)
- [ ] Windows Mica 材质 (可选)
  - **依赖条件**: Windows 11 (Build 22000+)
  - **实现**:
    ```rust
    // 检测 Windows 版本
    if cfg!(target_os = "windows") && is_windows_11() {
        window.set_decorations(false);
        window.set_effects(WindowEffects::Mica);
    }
    ```
  - **降级方案**: Windows 10 使用半透明 Acrylic 或纯色背景
- [ ] 系统主题自适应
  - 监听系统主题变化 (Tauri event)
  - 自动切换明暗模式
  - 用户可手动覆盖 (设置页面)
- [ ] 原生窗口控制
  - 使用 Tauri 原生标题栏
  - 自定义最小化/最大化/关闭按钮样式

### Testing (1.5 天)

#### 4.1 文件操作测试
- [ ] 拖拽大文件 (>100MB)
  - 验证进度条显示
  - 验证内存使用 (不应加载整个文件到内存)
  - 验证加密成功
- [ ] 批量导入 (50+ 文件)
  - 验证队列处理
  - 验证错误处理 (部分失败)
  - 验证总进度显示
- [ ] 删除已加密文件
  - 验证数据库清理
  - 验证物理文件删除
  - 验证关联标签清理
- [ ] 重命名文件
  - 验证输入验证
  - 验证数据库更新
  - 验证标签关联保持

#### 4.2 进度与反馈测试
- [ ] 加密/解密进度
  - 验证进度事件触发
  - 验证百分比计算准确
  - 验证完成后自动消失
- [ ] Toast 提示
  - 验证成功/错误/警告样式
  - 验证持续时间
  - 验证最大数量限制
- [ ] 错误信息
  - 验证技术错误映射到用户语言
  - 验证解决建议显示

#### 4.3 无障碍测试
- [ ] 键盘导航
  - Tab 遍历所有交互元素
  - Enter 触发按钮
  - Escape 关闭模态框
- [ ] 屏幕阅读器 (NVDA/VoiceOver)
  - 验证 ARIA 标签朗读
  - 验证焦点顺序合理
- [ ] 颜色对比度
  - 使用工具检查 (Axe DevTools)
  - 确保 WCAG AA 合规

#### 4.4 响应式测试
- [ ] 移动端 (375px, 414px)
  - 验证布局不溢出
  - 验证触摸目标大小
- [ ] 平板 (768px, 1024px)
  - 验证双列布局
- [ ] 桌面 (1440px, 1920px)
  - 验证三列布局

#### 4.5 错误恢复测试
- [ ] 中断恢复
  - 加密进行到 50% 时关闭应用
  - 重启后验证是否可继续/重新开始
  - 验证临时文件清理
- [ ] 网络中断 (如果涉及)
  - 重命名时断网
  - 验证错误提示
  - 验证重试机制

#### 4.6 回归测试
- [ ] P0 功能: 加密/解密核心逻辑
- [ ] P1 功能: 标签管理、文件浏览
- [ ] 完整用户流程: 导入 → 加密 → 添加标签 → 解密 → 删除

---

## ✅ 成功标准

- ✅ 所有 P2 功能可用
- ✅ 操作反馈及时
- ✅ UI 响应式适配
- ✅ 无明显 Bug

---

## 📚 参考文档

### 核心文档
- `docs/roadmap/MVP_v1.0_Implementation_Plan.md` - MVP 实施计划
- `docs/spec/UI_UX_Design_System.md` - 完整设计系统规范
- `.claude/plans/active/mvp-v1.0-plan.md` - MVP 总计划

### Design System (docs/design/)
- `docs/design/COLOR.md` - 颜色系统和语义 tokens
- `docs/design/SPACING.md` - 间距 tokens (--space-1 到 --space-10)
- `docs/design/RADIUS.md` - 圆角 tokens (--radius-xs 到 --radius-full)
- `docs/design/SHADOWS.md` - 阴影系统 (--shadow-1 到 --shadow-4)
- `docs/design/MOTION.md` - 动画 tokens (duration, easing)
- `docs/design/FEEDBACK.md` - Toast, Modal, Progress 组件规范
- `docs/design/ACCESSIBILITY.md` - WCAG 2.1 AA/AAA 无障碍标准

### Rules (Claude Code 编码规范)
- `.claude/rules/frontend/design-system.md` - Design System 集成规则
- `.claude/rules/frontend/design-tokens.md` - Design Tokens 使用规则
- `.claude/rules/frontend/css.md` - CSS 编写规范
- `.claude/rules/desktop/tauri-ipc.md` - Tauri IPC 通信规范
- `.claude/rules/desktop/tauri-native-apis.md` - Tauri 原生 API 使用
- `.claude/rules/desktop/tauri-performance.md` - Tauri 性能优化
- `.claude/rules/desktop/tauri-security.md` - Tauri 安全规范

---

## 📝 实施策略

### Phase 1: File Operations (2 天)

**顺序**: 拖拽导入 → 文件删除 → 文件重命名

#### 1. 拖拽导入 (0.8 天)
- **组件**: `src/components/DragDropZone.tsx`
- **实现步骤**:
  1. HTML5 Drag & Drop API (`onDragEnter`, `onDragOver`, `onDrop`)
  2. 文件类型验证 (白名单: `.jpg`, `.png`, `.pdf`, `.docx` 等)
  3. 大小限制检查 (< 2GB 警告, < 5GB 阻止)
  4. 批量处理队列 (RxJS 或自建队列)
- **关键文件**:
  - `src/02_modules/file/components/DragDropZone.tsx`
  - `src/02_modules/file/headless/useFileDrop.ts` (hook)
  - `src/02_modules/file/headless/fileValidator.ts` (验证逻辑)

#### 2. 文件删除 (0.6 天)
- **组件**: 确认对话框 + 删除逻辑
- **实现步骤**:
  1. 模态框组件 (参考 `docs/design/FEEDBACK.md`)
  2. IPC 命令: `delete_file(file_id)` (Rust)
  3. 数据库清理:
     ```sql
     DELETE FROM files WHERE id = ?;
     DELETE FROM file_tags WHERE file_id = ?;
     DELETE FROM encryption_meta WHERE file_id = ?;
     ```
  4. 物理文件删除: 删除 `.u-safe/{file_id}.enc`
- **关键文件**:
  - `src-tauri/src/commands/file.rs` (`delete_file` command)
  - `src/02_modules/file/headless/useFileDelete.ts`
  - `src/components/ConfirmDialog.tsx`

#### 3. 文件重命名 (0.6 天)
- **交互**: 双击文件名 → 输入框 → Enter 确认
- **实现步骤**:
  1. 内联编辑组件 (双击进入编辑模式)
  2. 输入验证: 非空、长度限制、特殊字符过滤
  3. IPC 命令: `rename_file(file_id, new_name)` (Rust)
  4. 数据库更新:
     ```sql
     UPDATE files SET name = ? WHERE id = ?;
     UPDATE encryption_meta SET original_name = ? WHERE file_id = ?;
     ```
- **关键文件**:
  - `src-tauri/src/commands/file.rs` (`rename_file` command)
  - `src/02_modules/file/components/InlineEdit.tsx`
  - `src/02_modules/file/headless/useFileRename.ts`

---

### Phase 2: Progress & Feedback (2 天)

**顺序**: Tauri IPC 事件设计 → 进度条组件 → Toast 组件 → 错误映射 → Loading 状态

#### 1. Tauri IPC 进度事件 (0.5 天)
- **事件定义** (Rust):
  ```rust
  // src-tauri/src/events.rs
  #[derive(Serialize, Deserialize)]
  pub struct EncryptProgress {
      pub file_id: String,
      pub percent: f32,      // 0.0 - 100.0
      pub bytes_done: u64,
      pub bytes_total: u64,
      pub status: String,    // "encrypting", "complete", "failed"
  }

  // 在加密函数中发送事件
  app.emit_all("encrypt-progress", EncryptProgress {
      file_id: file_id.clone(),
      percent: (bytes_done as f32 / bytes_total as f32) * 100.0,
      bytes_done,
      bytes_total,
      status: "encrypting".to_string(),
  }).unwrap();
  ```
- **前端监听** (TypeScript):
  ```typescript
  // src/02_modules/crypto/headless/useEncryptProgress.ts
  import { listen } from '@tauri-apps/api/event';

  export function useEncryptProgress(fileId: string) {
    const [progress, setProgress] = useState(0);

    useEffect(() => {
      const unlisten = listen<EncryptProgress>('encrypt-progress', (event) => {
        if (event.payload.file_id === fileId) {
          setProgress(event.payload.percent);
        }
      });
      return () => { unlisten.then(fn => fn()); };
    }, [fileId]);

    return progress;
  }
  ```
- **关键文件**:
  - `src-tauri/src/events.rs` (事件定义)
  - `src-tauri/src/crypto/encrypt.rs` (发送事件)
  - `src/02_modules/crypto/headless/useEncryptProgress.ts`
  - `src/02_modules/crypto/headless/useDecryptProgress.ts`

#### 2. 进度条组件 (0.4 天)
- **设计规范**: `docs/design/FEEDBACK.md` - Progress Bar
- **组件**: `src/components/ProgressBar.tsx`
- **实现**:
  ```tsx
  <div className="progress-bar" role="progressbar" aria-valuenow={percent} aria-valuemin={0} aria-valuemax={100}>
    <div className="progress-bar__fill" style={{ width: `${percent}%` }} />
    <span className="progress-bar__text">{percent}%</span>
  </div>
  ```
- **样式** (使用 Design Tokens):
  ```css
  .progress-bar {
    background: var(--bg-card);
    border-radius: var(--radius-md);
    height: var(--space-6);
  }
  .progress-bar__fill {
    background: var(--color-primary);
    transition: width var(--duration-base) var(--ease-out);
  }
  ```
- **关键文件**:
  - `src/components/ProgressBar.tsx`
  - `src/components/ProgressBar.css`

#### 3. Toast 提示组件 (0.5 天)
- **设计规范**: `docs/design/FEEDBACK.md` - Toast
- **组件**: 自建 Toast 系统 (不依赖第三方库)
- **实现**:
  ```tsx
  // src/components/Toast/ToastProvider.tsx
  export function ToastProvider({ children }) {
    const [toasts, setToasts] = useState<Toast[]>([]);

    const addToast = (toast: Toast) => {
      setToasts(prev => [...prev, { ...toast, id: Date.now() }]);
      setTimeout(() => removeToast(toast.id), toast.duration || 3000);
    };

    return (
      <ToastContext.Provider value={{ addToast }}>
        {children}
        <div className="toast-container">
          {toasts.map(toast => <ToastItem key={toast.id} {...toast} />)}
        </div>
      </ToastContext.Provider>
    );
  }
  ```
- **配置**:
  - 位置: 右上角 (`top-right`)
  - 持续时间: Success 3s, Error 5s, Warning 4s
  - 最大数量: 3 个 (超过则移除最旧的)
- **关键文件**:
  - `src/components/Toast/ToastProvider.tsx`
  - `src/components/Toast/ToastItem.tsx`
  - `src/components/Toast/useToast.ts` (hook)
  - `src/components/Toast/toast.css`

#### 4. 错误信息友好化 (0.3 天)
- **错误映射表**:
  ```typescript
  // src/utils/errorMapper.ts
  const ERROR_MESSAGES: Record<string, string> = {
    'ENOSPC': '磁盘空间不足，请清理空间后重试',
    'EACCES': '无权限访问该文件',
    'InvalidPassword': '密码错误，请重新输入',
    'FileTooLarge': '文件过大（超过 5GB），暂不支持',
    // ...
  };

  export function friendlyError(technicalError: string): string {
    return ERROR_MESSAGES[technicalError] || `操作失败: ${technicalError}`;
  }
  ```
- **使用**:
  ```typescript
  try {
    await invoke('encrypt_file', { fileId });
  } catch (err) {
    toast.error(friendlyError(err.message));
  }
  ```
- **关键文件**:
  - `src/utils/errorMapper.ts`

#### 5. Loading 状态 (0.3 天)
- **按钮 Loading**:
  ```tsx
  <button disabled={isLoading} className={isLoading ? 'loading' : ''}>
    {isLoading ? <Spinner /> : '加密'}
  </button>
  ```
- **Skeleton 占位符**:
  ```tsx
  {isLoading ? <FileSkeleton /> : <FileList files={files} />}
  ```
- **关键文件**:
  - `src/components/Spinner.tsx`
  - `src/components/Skeleton.tsx`

---

### Phase 3: UI Polish (3 天)

**顺序**: Design Tokens 应用 → 响应式布局 → 动画 → 无障碍 → 平台特性

#### 1. Design Tokens 全面应用 (0.6 天)
- **审查所有组件**, 确保使用 Tokens (不硬编码):
  - 颜色: `var(--color-primary)`, `var(--bg-card)`, etc.
  - 间距: `var(--space-4)`, `var(--space-2)`, etc.
  - 圆角: `var(--radius-md)`, `var(--radius-sm)`, etc.
  - 阴影: `var(--shadow-1)`, `var(--shadow-2)`, etc.
  - 动画: `var(--duration-fast)`, `var(--ease-out)`, etc.
- **检查工具**: Stylelint (已配置)
  ```bash
  npm run lint:css  # 检查硬编码值
  ```
- **参考文档**:
  - `docs/design/COLOR.md`
  - `docs/design/SPACING.md`
  - `docs/design/RADIUS.md`
  - `docs/design/SHADOWS.md`
  - `docs/design/MOTION.md`

#### 2. 响应式布局 (0.8 天)
- **断点** (参考 `docs/spec/UI_UX_Design_System.md`):
  ```css
  /* Mobile */
  @media (max-width: 767px) { /* 单列 */ }

  /* Tablet */
  @media (min-width: 768px) and (max-width: 1023px) { /* 双列 */ }

  /* Desktop */
  @media (min-width: 1024px) { /* 三列 */ }
  ```
- **实现**:
  - 使用 CSS Grid / Flexbox
  - 移动端: 隐藏侧边栏 (汉堡菜单)
  - 平板: 侧边栏 + 主内容
  - 桌面: 侧边栏 + 文件列表 + 详情面板
- **关键文件**:
  - `src/App.css` (主布局)
  - `src/02_modules/file/views/FileView.css`

#### 3. 交互动画 (0.6 天)
- **过渡动画**:
  ```css
  .button {
    transition: background-color var(--duration-fast) var(--ease-out);
  }
  .card {
    transition: box-shadow var(--duration-fast) var(--ease-out);
  }
  ```
- **微交互**:
  - 文件添加: `@keyframes slideInDown`
  - 文件删除: `@keyframes fadeOut`
  - Toast: `@keyframes slideInRight`
- **Reduced Motion 支持**:
  ```css
  @media (prefers-reduced-motion: reduce) {
    * { animation: none !important; transition: none !important; }
  }
  ```
- **关键文件**:
  - `src/styles/animations.css`

#### 4. 无障碍支持 (0.6 天)
- **ARIA 属性**:
  - 按钮: `aria-label="删除文件"`, `role="button"`
  - 模态框: `role="dialog"`, `aria-modal="true"`, `aria-labelledby`
  - 进度条: `role="progressbar"`, `aria-valuenow`, `aria-valuemin`, `aria-valuemax`
- **键盘导航**:
  - Tab 顺序: 合理的焦点管理
  - Enter: 触发按钮/链接
  - Escape: 关闭模态框
  - 焦点捕获: 模态框打开时限制焦点在模态框内
- **颜色对比度检查**:
  - 使用 Axe DevTools 检查
  - 确保文本 ≥ 4.5:1, 大文本 ≥ 3:1
- **焦点可见**:
  ```css
  button:focus-visible {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
  }
  ```
- **参考文档**: `docs/design/ACCESSIBILITY.md`
- **关键文件**:
  - 所有交互组件 (按钮、输入框、模态框等)

#### 5. 平台特性 (0.4 天)
- **Windows Mica 材质**:
  ```rust
  // src-tauri/src/main.rs
  #[cfg(target_os = "windows")]
  fn apply_mica_effect(window: &tauri::Window) -> Result<(), String> {
      // 检测 Windows 版本
      let version = windows::System::version();
      if version.build >= 22000 {  // Windows 11
          window.set_decorations(false);
          window.set_effects(WindowEffects::Mica);
      } else {
          // Windows 10: 使用 Acrylic 或纯色
          window.set_effects(WindowEffects::Acrylic);
      }
      Ok(())
  }
  ```
- **系统主题自适应**:
  ```typescript
  // src/hooks/useSystemTheme.ts
  import { invoke } from '@tauri-apps/api';

  export function useSystemTheme() {
    const [theme, setTheme] = useState<'light' | 'dark'>('light');

    useEffect(() => {
      invoke<string>('get_system_theme').then(setTheme);

      const unlisten = listen('theme-changed', (event) => {
        setTheme(event.payload as 'light' | 'dark');
      });

      return () => { unlisten.then(fn => fn()); };
    }, []);

    return theme;
  }
  ```
- **关键文件**:
  - `src-tauri/src/platform/windows.rs`
  - `src-tauri/src/platform/macos.rs`
  - `src/hooks/useSystemTheme.ts`

---

### Phase 4: Testing (1.5 天)

**顺序**: 文件操作测试 → 进度反馈测试 → 无障碍测试 → 响应式测试 → 错误恢复测试 → 回归测试

#### 1. 文件操作测试 (0.4 天)
- **测试场景**:
  - 拖拽大文件 (100MB+): 验证进度条、内存使用
  - 批量导入 (50 文件): 验证队列处理
  - 删除文件: 验证数据库清理、物理删除
  - 重命名: 验证输入验证、数据库更新
- **工具**: 手动测试 + 自动化测试 (Vitest)

#### 2. 进度反馈测试 (0.3 天)
- **测试场景**:
  - 加密进度: 验证事件触发、百分比准确
  - Toast: 验证显示时间、最大数量
  - 错误映射: 验证技术错误转用户语言

#### 3. 无障碍测试 (0.3 天)
- **工具**: Axe DevTools, NVDA (Windows), VoiceOver (macOS)
- **测试**:
  - 键盘导航: Tab、Enter、Escape
  - 屏幕阅读器: ARIA 标签朗读
  - 颜色对比度: WCAG AA 合规

#### 4. 响应式测试 (0.2 天)
- **设备**: Chrome DevTools (模拟移动端、平板)
- **测试**:
  - 375px (iPhone SE): 单列布局
  - 768px (iPad): 双列布局
  - 1440px (Desktop): 三列布局

#### 5. 错误恢复测试 (0.3 天)
- **测试场景**:
  - 加密中断: 50% 时关闭应用 → 重启验证恢复
  - 网络中断: 重命名时断网 → 验证错误提示
  - 磁盘满: 加密时磁盘满 → 验证友好错误

#### 6. 回归测试 (完整用户流程, 综合在上述测试中)
- **流程**: 导入 → 加密 → 添加标签 → 解密 → 删除
- **验证**: P0 + P1 功能无回归

---

### 错误恢复策略 (新增)

#### 加密/解密中断恢复
- **问题**: 用户关闭应用时，正在进行的加密/解密任务中断
- **解决方案**:
  1. **进度保存** (Rust):
     ```rust
     // 在加密过程中，定期保存进度到临时文件
     // .u-safe/progress/{file_id}.json
     {
       "file_id": "abc123",
       "operation": "encrypt",
       "percent": 45.5,
       "bytes_done": 123456789,
       "timestamp": "2026-03-20T08:00:00Z"
     }
     ```
  2. **恢复检查** (启动时):
     ```rust
     // 启动时检查 .u-safe/progress/ 目录
     // 如果有未完成任务，询问用户是否继续
     if let Some(progress) = load_incomplete_tasks() {
         app.emit_all("incomplete-tasks", progress).unwrap();
     }
     ```
  3. **用户选择**:
     - 继续: 从上次进度继续加密/解密
     - 重新开始: 删除临时文件，重新加密
     - 取消: 清理临时文件
- **实现文件**:
  - `src-tauri/src/crypto/recovery.rs`
  - `src/02_modules/crypto/components/RecoveryDialog.tsx`

#### 数据库事务回滚
- **问题**: 删除文件时，数据库清理失败
- **解决方案**: 使用 SQLite 事务
  ```rust
  // src-tauri/src/db/file.rs
  pub fn delete_file_with_cleanup(file_id: &str) -> Result<(), String> {
      let tx = conn.transaction()?;

      tx.execute("DELETE FROM files WHERE id = ?", [file_id])?;
      tx.execute("DELETE FROM file_tags WHERE file_id = ?", [file_id])?;
      tx.execute("DELETE FROM encryption_meta WHERE file_id = ?", [file_id])?;

      tx.commit()?;  // 全部成功才提交

      // 数据库清理成功后，删除物理文件
      std::fs::remove_file(format!(".u-safe/{}.enc", file_id))?;

      Ok(())
  }
  ```

---

## 🔄 进度跟踪

- [ ] Plan reviewed
- [ ] File Operations 实现完成
- [ ] Progress & Feedback 实现完成
- [ ] UI Polish 实现完成
- [ ] Testing 完成
- [ ] Ready for review

---

## 📝 Next Steps

1. Review this plan
2. Get first task: /next
3. Start implementation
4. When done: /finish-issue #22
