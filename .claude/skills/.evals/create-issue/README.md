# create-issue Skill Evaluations

评估测试套件，用于验证 create-issue 技能的核心功能。

## 测试覆盖

| 测试文件 | 功能 | 测试数量 | 状态 |
|----------|------|----------|------|
| `test-size-validation.md` | 尺寸验证和建议 | 5 | ✅ 100% |
| `test-template-support.md` | 模板加载和应用 | 4 | ✅ 100% |
| `test-deduplication.md` | 去重检测 | 5 | ✅ 100% (2 模拟) |

**总计**: 14 个测试用例，100% 通过率

## 运行测试

### 1. 尺寸验证测试

```bash
# 测试理想尺寸
python3 .claude/skills/create-issue/scripts/size_validator.py

# 测试特定场景
python3 .claude/skills/create-issue/scripts/create.py \
  --estimate-only \
  --title "Add login" \
  --body "$(cat test-data/ideal-size.md)"
```

### 2. 模板测试

```bash
# 测试 bug 模板
python3 .claude/skills/create-issue/scripts/create.py \
  --estimate-only \
  --template bug \
  --title "Login crashes"

# 测试 feature 模板
python3 .claude/skills/create-issue/scripts/create.py \
  --estimate-only \
  --template feature \
  --title "Add dark mode"

# 测试 enhancement 模板
python3 .claude/skills/create-issue/scripts/create.py \
  --estimate-only \
  --template enhancement \
  --title "Optimize queries"
```

### 3. 去重测试

**注意**: 去重测试需要在真实仓库中运行

```bash
# 检查去重（需要 gh CLI 认证）
python3 .claude/skills/create-issue/scripts/create.py \
  --check-duplicate \
  --title "Your issue title"

# 创建时自动检查去重
python3 .claude/skills/create-issue/scripts/create.py \
  --dry-run \
  --title "Add authentication" \
  --body "Implement JWT auth"
```

## 测试数据

### 理想尺寸 (PASS)

```markdown
## Tasks
1. Create component
2. Add validation
3. Integrate API
4. Add tests
```

### 警告尺寸 (WARN)

```markdown
## Tasks
1. Task 1
2. Task 2
3. Task 3
4. Task 4
5. Task 5
6. Task 6
7. Task 7
8. Task 8
```

### 阻止尺寸 (BLOCK)

```markdown
## Tasks
1-16. (16 个任务)
```

## 成功标准

### 尺寸验证

- ✅ 正确识别理想尺寸 (3-5 任务 → PASS)
- ✅ 警告偏大尺寸 (6-8 任务 → WARN)
- ✅ 阻止过大尺寸 (>15 任务 → BLOCK)
- ✅ 根据复杂度调整估算
- ✅ 提供拆分建议

### 模板支持

- ✅ 加载所有内置模板 (bug, feature, enhancement)
- ✅ 模板内容包含正确的任务数量
- ✅ 错误处理缺失的模板

### 去重检测

- ✅ 高相似度 (>90%) 阻止创建
- ✅ 中等相似度 (80-90%) 警告用户
- ✅ 低相似度 (<60%) 允许创建
- ✅ gh CLI 失败时跳过检测

## 已知限制

1. **去重检测**: 仅检查前 100 个 open issues（性能考虑）
2. **相似度算法**: 基于词汇重叠（未来可用语义分析增强）
3. **批量创建**: 测试需要实际的 markdown 文件

## Phase 2 测试计划

待实现功能的测试：

- [ ] 批量创建测试
- [ ] 自动拆分测试
- [ ] 模板变量替换测试
- [ ] 智能标签建议测试
- [ ] 与 work-issue 集成测试

## 维护

更新测试时：

1. 修改相应的 `test-*.md` 文件
2. 更新本 README 的测试数量统计
3. 运行所有测试验证
4. 更新通过率
