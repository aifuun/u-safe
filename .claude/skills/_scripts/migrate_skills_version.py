#!/usr/bin/env python3
"""为所有skills添加version字段到YAML frontmatter

根据ADR-008标准，为skills的YAML frontmatter添加version字段。
从Markdown中提取现有版本号，添加到YAML frontmatter（description后，argument-hint前）。
保留原Markdown版本号以实现向后兼容。
"""

import re
from pathlib import Path
from typing import Optional


def extract_markdown_version(content: str) -> Optional[str]:
    """从Markdown文本中提取版本号

    匹配格式：**Version:** 1.2.3
    """
    match = re.search(r'\*\*Version:\*\*\s+([0-9]+\.[0-9]+\.[0-9]+)', content)
    return match.group(1) if match else None


def has_yaml_version(content: str) -> bool:
    """检查YAML frontmatter是否已包含version字段"""
    # 检查YAML块中是否有version字段
    yaml_block_match = re.search(r'^---\n(.*?)\n---', content, re.MULTILINE | re.DOTALL)
    if yaml_block_match:
        yaml_content = yaml_block_match.group(1)
        return bool(re.search(r'^version:', yaml_content, re.MULTILINE))
    return False


def add_version_to_yaml(content: str, version: str) -> str:
    """在YAML frontmatter中添加version字段

    插入位置：description字段后，argument-hint字段前
    如果没有argument-hint，则插在YAML块末尾
    """
    # 查找YAML块
    yaml_pattern = r'^---\n(.*?)\n---'
    yaml_match = re.search(yaml_pattern, content, re.MULTILINE | re.DOTALL)

    if not yaml_match:
        # 没有YAML块，跳过
        return content

    yaml_content = yaml_match.group(1)

    # 查找description字段的结束位置
    # description可能是单行或多行（使用 | 或 >）
    desc_pattern = r'description:\s*[|>]?\n((?:  .*\n)*)'
    desc_match = re.search(desc_pattern, yaml_content)

    if desc_match:
        # 在description后插入version字段
        desc_end = desc_match.end()

        # 构建新的YAML内容
        yaml_before = yaml_content[:desc_end]
        yaml_after = yaml_content[desc_end:]

        # 添加version字段（与description同级缩进）
        new_yaml = f'{yaml_before}version: "{version}"\n{yaml_after}'

        # 替换原YAML块
        new_content = content[:yaml_match.start(1)] + new_yaml + content[yaml_match.end(1):]
        return new_content
    else:
        # 找不到description，在YAML块末尾添加
        yaml_before = yaml_content.rstrip()
        new_yaml = f'{yaml_before}\nversion: "{version}"\n'
        new_content = content[:yaml_match.start(1)] + new_yaml + content[yaml_match.end(1):]
        return new_content


def migrate_skill(skill_md: Path) -> bool:
    """迁移单个skill的版本号

    Returns:
        True if migrated successfully, False if skipped
    """
    content = skill_md.read_text(encoding='utf-8')

    # 检查是否已有YAML version字段
    if has_yaml_version(content):
        print(f"⏭️  {skill_md.parent.name}/SKILL.md: Already has YAML version field")
        return False

    # 提取Markdown版本号
    md_version = extract_markdown_version(content)

    if not md_version:
        print(f"⚠️  {skill_md.parent.name}/SKILL.md: No version found (needs manual assignment)")
        return False

    # 添加version字段到YAML
    new_content = add_version_to_yaml(content, md_version)

    if new_content == content:
        print(f"❌ {skill_md.parent.name}/SKILL.md: Failed to add version field")
        return False

    # 写回文件
    skill_md.write_text(new_content, encoding='utf-8')
    print(f"✅ {skill_md.parent.name}/SKILL.md: Added version {md_version}")
    return True


def main():
    """主函数：迁移所有skills"""
    skills_dir = Path('.claude/skills')

    if not skills_dir.exists():
        print(f"❌ Error: {skills_dir} not found")
        print("   Run this script from project root directory")
        return 1

    migrated_count = 0
    skipped_count = 0
    no_version_count = 0

    # 遍历所有skill目录
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue

        # 跳过特殊目录
        if skill_dir.name.startswith('.') or skill_dir.name.startswith('_'):
            continue

        skill_md = skill_dir / 'SKILL.md'
        if not skill_md.exists():
            continue

        result = migrate_skill(skill_md)

        if result:
            migrated_count += 1
        else:
            # 判断是跳过还是无版本号
            content = skill_md.read_text(encoding='utf-8')
            if has_yaml_version(content):
                skipped_count += 1
            else:
                no_version_count += 1

    # 打印总结
    print()
    print("=" * 60)
    print("Migration Summary")
    print("=" * 60)
    print(f"✅ Migrated: {migrated_count} skills")
    print(f"⏭️  Skipped (already has version): {skipped_count} skills")
    print(f"⚠️  No version found (manual assignment needed): {no_version_count} skills")
    print()

    if no_version_count > 0:
        print("Skills needing manual version assignment:")
        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir() or skill_dir.name.startswith(('.', '_')):
                continue
            skill_md = skill_dir / 'SKILL.md'
            if skill_md.exists():
                content = skill_md.read_text(encoding='utf-8')
                if not has_yaml_version(content) and not extract_markdown_version(content):
                    print(f"  - {skill_dir.name}")

    return 0


if __name__ == '__main__':
    exit(main())
