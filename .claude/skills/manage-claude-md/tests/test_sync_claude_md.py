#!/usr/bin/env python3
"""
单元测试: sync_claude_md.py
"""

import sys
from pathlib import Path
import tempfile
import shutil

# 添加 scripts/ 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from sync_claude_md import scan_skills, generate_skills_table


def test_scan_skills():
    """测试扫描 skills 目录"""
    # 创建临时 skills 目录
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / ".claude" / "skills"
        skills_dir.mkdir(parents=True)

        # 创建几个测试 skill
        (skills_dir / "test-skill-1").mkdir()
        (skills_dir / "test-skill-2").mkdir()
        (skills_dir / "_internal").mkdir()  # 应该被忽略

        # 扫描
        result = scan_skills(skills_dir)

        # 验证
        assert isinstance(result, dict)
        # 至少有一个分类包含 skills
        assert any(len(skills) > 0 for skills in result.values())

    print("✅ test_scan_skills 通过")


def test_generate_skills_table():
    """测试生成 Markdown 表格"""
    test_data = {
        "Test Category": ["skill-1", "skill-2"],
        "Another Category": ["skill-3"]
    }

    table = generate_skills_table(test_data)

    # 验证表格格式
    assert "| Category | Key Skills | Purpose |" in table
    assert "Test Category" in table
    assert "skill-1" in table

    print("✅ test_generate_skills_table 通过")


if __name__ == "__main__":
    test_scan_skills()
    test_generate_skills_table()
    print("\n✅ 所有测试通过")
