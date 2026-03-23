#!/bin/bash
#
# 安装 Git Hooks
#
# 用途: 设置 pre-commit hook 确保代码质量
# 使用: ./scripts/install-hooks.sh
#

set -e

HOOKS_DIR=".git/hooks"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🔧 安装 Git Hooks..."
echo ""

# 检查 .git 目录是否存在
if [ ! -d ".git" ]; then
  echo "❌ 错误: 未找到 .git 目录"
  echo "   请在项目根目录运行此脚本"
  exit 1
fi

# 创建 pre-commit hook
echo "📝 创建 pre-commit hook..."
cat > "$HOOKS_DIR/pre-commit" << 'EOF'
#!/bin/sh
#
# Pre-commit hook: 确保代码可以编译
#
# 自动生成于: Issue #52 - 配置路径别名和 TypeScript 设置
# 目的: 防止提交不可编译的代码到版本控制
#

echo "🔍 运行 pre-commit 检查..."
echo ""

# 1. TypeScript 编译检查
echo "📝 检查 TypeScript 编译..."
if ! npx tsc --noEmit; then
  echo ""
  echo "❌ TypeScript 编译失败！"
  echo ""
  echo "请修复上述错误后再提交。"
  echo ""
  echo "💡 如果你确定要跳过检查（不推荐），可以使用："
  echo "   git commit --no-verify -m \"your message\""
  echo ""
  exit 1
fi

echo "✅ TypeScript 编译通过"
echo ""
echo "✅ 所有检查通过，继续提交..."
echo ""

exit 0
EOF

# 设置可执行权限
chmod +x "$HOOKS_DIR/pre-commit"

echo "✅ pre-commit hook 已安装"
echo ""
echo "📋 Hook 功能:"
echo "   - 提交前自动运行 TypeScript 编译检查"
echo "   - 如果编译失败，拒绝提交"
echo "   - 使用 --no-verify 可以跳过检查（不推荐）"
echo ""
echo "🎉 Git Hooks 安装完成！"
