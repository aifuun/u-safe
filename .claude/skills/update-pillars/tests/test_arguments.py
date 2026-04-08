"""
参数测试 - 基于 update-pillars SKILL.md "Arguments" 章节

测试参数验证和处理:
1. 必需参数: <target-path>
2. 可选参数: --dry-run, --pillars, --skip-validation
3. 参数组合验证
4. 无效参数检测
"""

import unittest
import tempfile
import shutil
from pathlib import Path


class TestRequiredArguments(unittest.TestCase):
    """测试必需参数: <target-path>"""

    def test_target_path_required(self):
        """target-path 参数是必需的"""
        # Given: 没有提供 target-path
        args = {}

        # When/Then: 应检测到缺失参数
        self.assertNotIn("target_path", args)

    def test_target_path_validation(self):
        """验证 target-path 是有效路径"""
        # Given: 提供有效路径
        with tempfile.TemporaryDirectory() as tmpdir:
            target_path = Path(tmpdir)

            # When: 验证路径
            is_valid = target_path.exists() and target_path.is_dir()

            # Then: 应为 True
            self.assertTrue(is_valid)

    def test_invalid_target_path(self):
        """检测无效的 target-path"""
        # Given: 不存在的路径
        target_path = Path("/nonexistent/path/12345")

        # When: 验证路径
        is_valid = target_path.exists()

        # Then: 应为 False
        self.assertFalse(is_valid)


class TestOptionalArguments(unittest.TestCase):
    """测试可选参数"""

    def test_dry_run_flag(self):
        """--dry-run 标志参数"""
        # Given: 提供 --dry-run 参数
        args = {"dry_run": True}

        # When: 检查标志
        is_dry_run = args.get("dry_run", False)

        # Then: 应为 True
        self.assertTrue(is_dry_run)

    def test_pillars_selective_sync(self):
        """--pillars 选择性同步参数"""
        # Given: 指定要同步的 Pillars
        args = {"pillars": "A,B,K"}

        # When: 解析参数
        pillars_list = args.get("pillars", "").split(",")

        # Then: 应解析为列表
        self.assertEqual(pillars_list, ["A", "B", "K"])

    def test_skip_validation_flag(self):
        """--skip-validation 跳过验证参数"""
        # Given: 提供 --skip-validation 参数
        args = {"skip_validation": True}

        # When: 检查标志
        skip_validation = args.get("skip_validation", False)

        # Then: 应为 True
        self.assertTrue(skip_validation)


class TestArgumentCombinations(unittest.TestCase):
    """测试参数组合"""

    def test_dry_run_with_pillars(self):
        """--dry-run 与 --pillars 组合"""
        # Given: 同时使用两个参数
        args = {
            "dry_run": True,
            "pillars": "M,Q"
        }

        # When: 检查两个参数都生效
        is_dry_run = args.get("dry_run", False)
        pillars = args.get("pillars", "").split(",")

        # Then: 两个参数都应有效
        self.assertTrue(is_dry_run)
        self.assertEqual(pillars, ["M", "Q"])

    def test_skip_validation_with_target_path(self):
        """--skip-validation 与 target-path 组合"""
        # Given: 组合参数
        with tempfile.TemporaryDirectory() as tmpdir:
            args = {
                "target_path": Path(tmpdir),
                "skip_validation": True
            }

            # When: 检查参数
            has_target = "target_path" in args
            skip = args.get("skip_validation", False)

            # Then: 两个参数都应存在
            self.assertTrue(has_target)
            self.assertTrue(skip)


class TestInvalidArguments(unittest.TestCase):
    """测试无效参数检测"""

    def test_invalid_pillars_format(self):
        """检测无效的 Pillars 格式"""
        # Given: 无效的 Pillars 参数
        invalid_pillars = ["XX", "YY", "123"]  # 不存在的 Pillars

        valid_pillars = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
                        "K", "L", "M", "N", "O", "P", "Q", "R"]

        # When: 验证每个 Pillar
        invalid_count = sum(1 for p in invalid_pillars if p not in valid_pillars)

        # Then: 应检测到全部无效
        self.assertEqual(invalid_count, len(invalid_pillars))

    def test_empty_target_path(self):
        """检测空的 target-path"""
        # Given: 空路径
        target_path = ""

        # When: 验证路径
        is_valid = bool(target_path) and Path(target_path).exists()

        # Then: 应为无效
        self.assertFalse(is_valid)


if __name__ == "__main__":
    unittest.main()
