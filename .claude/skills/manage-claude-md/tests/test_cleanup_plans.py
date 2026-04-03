#!/usr/bin/env python3
"""
单元测试: cleanup_plans.py
"""

import sys
from pathlib import Path
import tempfile

# 添加 scripts/ 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from cleanup_plans import extract_issue_number


def test_extract_issue_number_from_filename():
    """测试从文件名提取 issue 编号"""
    test_file = Path("issue-123-plan.md")
    result = extract_issue_number(test_file)

    assert result == 123
    print("✅ test_extract_issue_number_from_filename 通过")


def test_extract_issue_number_from_content():
    """测试从文件内容提取 issue 编号"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("**GitHub**: https://github.com/user/repo/issues/456\n")
        temp_path = Path(f.name)

    try:
        result = extract_issue_number(temp_path)
        assert result == 456
        print("✅ test_extract_issue_number_from_content 通过")
    finally:
        temp_path.unlink()


def test_extract_issue_number_none():
    """测试无法提取时返回 None"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("No issue number here\n")
        temp_path = Path(f.name)

    try:
        result = extract_issue_number(temp_path)
        assert result is None
        print("✅ test_extract_issue_number_none 通过")
    finally:
        temp_path.unlink()


if __name__ == "__main__":
    test_extract_issue_number_from_filename()
    test_extract_issue_number_from_content()
    test_extract_issue_number_none()
    print("\n✅ 所有测试通过")
