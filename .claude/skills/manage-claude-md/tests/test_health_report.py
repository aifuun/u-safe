#!/usr/bin/env python3
"""
单元测试: health_report.py
"""

import sys
from pathlib import Path
import tempfile

# 添加 scripts/ 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from health_report import check_skills_health, check_docs_health


def test_check_skills_health():
    """测试 skills 健康度检查"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        skills_dir = project_root / ".claude" / "skills"
        skills_dir.mkdir(parents=True)

        # 创建一些 skills
        for i in range(5):
            skill_dir = skills_dir / f"skill-{i}"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").touch()

        # 创建 README
        (skills_dir / "README.md").touch()

        # 测试
        score, details = check_skills_health(project_root)

        # 验证
        assert score > 0, "应该有正分数"
        assert "skills_dir" in details
        assert details["skills_dir"] == "✅ 存在"

    print("✅ test_check_skills_health 通过")


def test_check_docs_health():
    """测试 docs 健康度检查"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # 创建文档
        (project_root / "CLAUDE.md").touch()
        (project_root / "README.md").touch()

        adrs_dir = project_root / "docs" / "ADRs"
        adrs_dir.mkdir(parents=True)
        (adrs_dir / "001-test.md").touch()

        # 测试
        score, details = check_docs_health(project_root)

        # 验证
        assert score > 0, "应该有正分数"
        assert "claude_md" in details
        assert details["claude_md"] == "✅ 存在"

    print("✅ test_check_docs_health 通过")


if __name__ == "__main__":
    test_check_skills_health()
    test_check_docs_health()
    print("\n✅ 所有测试通过")
