# Issue #36: 降低密码最小长度要求至 8 位字符 + 增强用户教育

## 问题概述

**当前状态**: 密码最小长度要求 12 位字符，超出业界标准（NIST/OWASP 推荐 8 位）

**目标**:
1. 降低最小长度至 8 位（符合 NIST SP 800-63B、OWASP 标准）
2. 增强用户教育，说明 Argon2id 加密原理
3. 更新相关文档说明

**安全性依据**: U-Safe 使用 Argon2id KDF（64MB 内存 + 3 次迭代），即使 8 位强密码，暴力破解也需要 1000+ 年（RTX 4090 单卡）。安全性来自内存密集型 KDF，而非超长密码。

## 实施计划

### Phase 1: 代码修改

#### 1.1 修改密码验证逻辑

**文件**: `app/src/01_views/setup/SetupPasswordView.tsx`

**修改点**:
- Line 32: `if (pwd.length < 12)` → `if (pwd.length < 8)`
- Line 33: 错误消息 `'密码长度至少 12 个字符'` → `'密码长度至少 8 个字符'`
- Line 116: Placeholder 文本 `"至少12位，包含大小写、数字、特殊字符"` → `"至少8位，包含大小写、数字、特殊字符"`
- Line 178: 密码要求列表 `至少 12 个字符` → `至少 8 个字符`

**保留项**:
- 复杂度要求（大小写、数字、特殊字符）不变
- 强密码阈值（Line 56: `pwd.length >= 16`）不变

#### 1.2 增强用户教育界面

**文件**: `app/src/01_views/setup/SetupPasswordView.tsx`

**新增内容**: 在密码要求说明区域（Line 174-184）后添加安全教育说明

```tsx
{/* 安全加密说明 */}
<div className="security-info" role="region" aria-label="安全加密说明">
  <h3>💡 安全加密原理</h3>
  <p className="info-text">
    U-Safe 使用军事级 Argon2id 加密算法保护您的文件：
  </p>
  <ul className="info-list">
    <li><strong>内存密集型防护</strong>：每次验证需 64MB 内存 + 0.5 秒计算</li>
    <li><strong>硬件限制</strong>：无法使用 GPU 并行加速破解</li>
    <li><strong>时间成本</strong>：破解 8 位强密码需 1000+ 年（RTX 4090 单卡）</li>
  </ul>
  <p className="info-highlight">
    ✅ 示例强密码：<code>Pass@2026</code>（8位，易记且安全）
  </p>
</div>
```

**CSS 样式**: 在 `<style>` 标签内添加（Line 187 后）

```css
.security-info {
  margin-top: var(--space-6);
  padding: var(--space-4);
  background: color-mix(in srgb, var(--color-primary) 5%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-primary) 20%, transparent);
  border-radius: var(--radius-md);
}

.security-info h3 {
  margin: 0 0 var(--space-2) 0;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-primary);
}

.info-text {
  margin: 0 0 var(--space-2) 0;
  font-size: var(--text-xs);
  color: var(--text-secondary);
  line-height: 1.6;
}

.info-list {
  margin: 0 0 var(--space-3) 0;
  padding-left: var(--space-5);
  font-size: var(--text-xs);
  color: var(--text-secondary);
  line-height: 1.8;
}

.info-list li {
  margin: var(--space-1) 0;
}

.info-list strong {
  color: var(--text-primary);
  font-weight: 600;
}

.info-highlight {
  margin: 0;
  padding: var(--space-2) var(--space-3);
  background: color-mix(in srgb, var(--color-success) 10%, transparent);
  border-left: 3px solid var(--color-success);
  font-size: var(--text-xs);
  color: var(--text-primary);
  border-radius: var(--radius-sm);
}

.info-highlight code {
  /* @decorative: Minimal padding for inline code */
  padding: 2px var(--space-1);
  background: color-mix(in srgb, var(--color-primary) 10%, transparent);
  border-radius: var(--radius-xs);
  font-family: var(--font-family-mono);
  font-size: var(--text-xs);
  color: var(--color-primary);
}
```

### Phase 2: 文档更新

#### 2.1 更新 ADR-004 密码策略说明

**文件**: `docs/adr/004-encryption-strategy.md`

**修改点**: Line 59

```diff
- **密码要求**: 最短 12 字符，zxcvbn 评估强度
+ **密码要求**: 最短 8 字符（符合 NIST SP 800-63B、OWASP 标准），必须包含大小写字母、数字、特殊字符
```

**新增说明**: 在 Line 60 后添加

```markdown
- **安全性依据**: Argon2id 内存密集型 KDF（64MB + 3 次迭代）提供核心防护，即使 8 位强密码，暴力破解成本也达 1000+ 年（RTX 4090 单卡）。参考：VeraCrypt、1Password、Bitwarden 均采用 8 位最小长度。
```

## 验收标准

### 功能验收
- [ ] 用户可以使用 8 位强密码成功设置主密码（例如：`Pass@123`）
- [ ] 密码长度 < 8 位时显示错误提示："密码长度至少 8 个字符"
- [ ] 密码缺少复杂度要求时仍显示错误（大小写、数字、特殊字符）
- [ ] 密码设置界面显示安全加密原理说明
- [ ] 示例密码 `Pass@2026` 显示在教育信息中

### 文档验收
- [ ] ADR-004 更新了密码策略说明（8 位最小长度 + 安全性依据）
- [ ] 密码要求说明与 NIST/OWASP 标准对齐

### UI/UX 验收
- [ ] 密码输入提示文本更新为"至少8位"
- [ ] 密码要求列表更新为"至少 8 个字符"
- [ ] 安全教育说明区域样式符合设计系统（使用 Design Tokens）
- [ ] 信息层次清晰（标题、列表、高亮示例）

### 安全验收
- [ ] 保留所有复杂度要求（大小写、数字、特殊字符）
- [ ] Rust 后端 `derive_master_key` 逻辑不受影响（仅前端验证变更）
- [ ] Argon2id 参数不变（64MB 内存 + 3 次迭代）

## 测试计划

### 手动测试用例

| 测试场景 | 输入密码 | 预期结果 |
|---------|---------|---------|
| 最短有效密码 | `Pass@123` (9位) | ✅ 密码强度：中等，允许设置 |
| 边界测试 | `Pass@12` (8位) | ✅ 密码强度：中等，允许设置 |
| 长度不足 | `Pass@1` (7位) | ❌ 错误："密码长度至少 8 个字符" |
| 缺少大写 | `pass@123` | ❌ 错误："密码需要包含：大写字母" |
| 缺少数字 | `Pass@word` | ❌ 错误："密码需要包含：数字" |
| 缺少特殊字符 | `Password123` | ❌ 错误："密码需要包含：特殊字符" |
| 强密码 | `MyPass@2026!` (12位) | ✅ 密码强度：中等 |
| 超强密码 | `MySecurePass@2026!` (18位) | ✅ 密码强度：强 |
| 向后兼容（旧要求） | `MyOldPassword@2024!` (20位) | ✅ 密码强度：强（验证 12+ 字符密码仍可用） |

### 回归测试

- [ ] 原有 12-15 位密码仍可正常使用
- [ ] 密码不匹配提示仍正常显示
- [ ] 显示/隐藏密码功能正常
- [ ] IPC 调用 `derive_master_key` 正常
- [ ] 设置成功后跳转到 `/files` 路由

## 实施步骤

1. **创建功能分支**: `feature/issue-36-password-length`
2. **Phase 1**: 修改密码验证逻辑 + 增强用户教育界面
3. **Phase 2**: 更新 ADR-004 文档
4. **测试**: 执行所有测试用例
5. **提交**: 创建 PR 并关联 Issue #36

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 用户选择弱密码（如 `Pass@123`） | 降低实际安全性 | 添加安全教育说明，引导用户选择强密码 |
| 前端验证绕过 | 无影响 | Rust 后端 Argon2id 保证加密强度，密码长度不影响 KDF 安全性 |
| 与现有密码不兼容 | 无影响 | 仅放宽限制，不影响已设置密码 |

## 参考资料

- [NIST SP 800-63B](https://pages.nist.gov/800-63-3/sp800-63b.html) - 推荐最小密码长度 8 位
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html) - Argon2id 推荐参数
- ADR-004: 加密方案选型
- VeraCrypt 密码策略（8 位最小长度）
- 1Password 密码要求（8 位最小长度）

## 实施时间估算

- Phase 1 (代码修改): 30 分钟
- Phase 2 (文档更新): 15 分钟
- 测试: 15 分钟
- **总计**: 约 1 小时

---

**状态**: Ready for implementation
**优先级**: P0
**里程碑**: MVP v1.0
