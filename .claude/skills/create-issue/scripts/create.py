#!/usr/bin/env python3
"""
create-issue: 智能 GitHub Issue 创建工具

功能:
- 尺寸验证和建议
- 去重检测
- 模板支持
- 批量创建
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 导入尺寸验证模块
from size_validator import (
    SizeValidator,
    SizeResult,
    SizeRecommendation,
    parse_tasks_from_body,
    estimate_complexity
)


class IssueCreator:
    """GitHub Issue 创建工具"""

    def __init__(self, repo: Optional[str] = None):
        """
        初始化 Issue 创建工具

        Args:
            repo: GitHub 仓库路径（格式: owner/repo），None 表示使用当前仓库
        """
        self.repo = repo
        self.validator = SizeValidator()
        self.templates_dir = Path(".claude/issue-templates")

    def create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        force: bool = False,
        dry_run: bool = False
    ) -> Dict:
        """
        创建单个 GitHub issue

        Args:
            title: Issue 标题
            body: Issue 内容
            labels: 标签列表
            force: 是否跳过尺寸检查
            dry_run: 是否仅预览不创建

        Returns:
            创建结果字典
        """
        # 1. 尺寸验证
        if not force:
            size_result = self.validator.validate_size(title, body)

            if size_result.recommendation == SizeRecommendation.BLOCK:
                return {
                    "success": False,
                    "error": "尺寸超限，必须拆分",
                    "size_result": size_result
                }

            if size_result.recommendation == SizeRecommendation.WARN:
                print(f"\n⚠️  警告: {size_result.message}")
                print(f"   建议拆分: {size_result.split_suggestions}")

        # 2. 去重检测
        duplicate = self._check_duplicate(title, body)
        if duplicate:
            similarity = duplicate["similarity"]
            if similarity > 90:
                return {
                    "success": False,
                    "error": f"与 #{duplicate['number']} 高度重复（相似度 {similarity}%）",
                    "duplicate": duplicate
                }
            elif similarity > 80:
                print(f"\n⚠️  发现相似 issue: #{duplicate['number']} (相似度 {similarity}%)")
                print(f"   {duplicate['title']}")
                print(f"   {duplicate['url']}")

                response = input("\n是否继续创建? [y/N]: ")
                if response.lower() != 'y':
                    return {
                        "success": False,
                        "error": "用户取消创建",
                        "duplicate": duplicate
                    }

        # 3. 预览模式
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "preview": {
                    "title": title,
                    "body": body,
                    "labels": labels or [],
                    "size_result": size_result if not force else None
                }
            }

        # 4. 调用 gh CLI 创建 issue
        try:
            issue_url = self._create_with_gh_cli(title, body, labels)
            issue_number = self._extract_issue_number(issue_url)

            return {
                "success": True,
                "issue_number": issue_number,
                "issue_url": issue_url,
                "size_result": size_result if not force else None
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"创建失败: {e.stderr}",
                "gh_error": str(e)
            }

    def _create_with_gh_cli(
        self,
        title: str,
        body: str,
        labels: Optional[List[str]] = None
    ) -> str:
        """
        使用 gh CLI 创建 issue

        Args:
            title: Issue 标题
            body: Issue 内容
            labels: 标签列表

        Returns:
            Issue URL
        """
        cmd = ["gh", "issue", "create", "--title", title, "--body", body]

        if self.repo:
            cmd.extend(["--repo", self.repo])

        if labels:
            cmd.extend(["--label", ",".join(labels)])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        # gh issue create 返回 issue URL
        return result.stdout.strip()

    def _extract_issue_number(self, issue_url: str) -> int:
        """从 issue URL 提取 issue 编号"""
        match = re.search(r'/issues/(\d+)$', issue_url)
        if match:
            return int(match.group(1))
        raise ValueError(f"无法从 URL 提取 issue 编号: {issue_url}")

    def _check_duplicate(self, title: str, body: str) -> Optional[Dict]:
        """
        检测重复 issue

        Args:
            title: 新 issue 标题
            body: 新 issue 内容

        Returns:
            相似 issue 信息，如果没有则返回 None
        """
        try:
            # 获取所有 open issues
            cmd = ["gh", "issue", "list", "--limit", "100", "--json", "number,title,body,url"]
            if self.repo:
                cmd.extend(["--repo", self.repo])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            issues = json.loads(result.stdout)

            # 计算相似度
            max_similarity = 0
            most_similar = None

            for issue in issues:
                similarity = self._calculate_similarity(
                    title, body,
                    issue["title"], issue.get("body", "")
                )

                if similarity > max_similarity:
                    max_similarity = similarity
                    most_similar = {
                        "number": issue["number"],
                        "title": issue["title"],
                        "url": issue["url"],
                        "similarity": similarity
                    }

            # 只返回相似度 > 60% 的结果
            if most_similar and most_similar["similarity"] > 60:
                return most_similar

            return None

        except subprocess.CalledProcessError:
            # gh CLI 失败时跳过去重检测
            return None

    def _calculate_similarity(
        self,
        title1: str,
        body1: str,
        title2: str,
        body2: str
    ) -> float:
        """
        计算两个 issue 的相似度（0-100）

        使用简化的相似度算法:
        - 标题相似度（权重 60%）: 基于共同词汇
        - 内容相似度（权重 40%）: 基于共同词汇

        Args:
            title1, body1: 第一个 issue
            title2, body2: 第二个 issue

        Returns:
            相似度分数（0-100）
        """
        # 标题相似度
        title1_words = set(self._tokenize(title1.lower()))
        title2_words = set(self._tokenize(title2.lower()))

        if not title1_words or not title2_words:
            title_sim = 0
        else:
            title_sim = len(title1_words & title2_words) / len(title1_words | title2_words)

        # 内容相似度
        body1_words = set(self._tokenize(body1.lower()))
        body2_words = set(self._tokenize(body2.lower()))

        if not body1_words or not body2_words:
            body_sim = 0
        else:
            body_sim = len(body1_words & body2_words) / len(body1_words | body2_words)

        # 加权平均
        total_similarity = title_sim * 0.6 + body_sim * 0.4

        return total_similarity * 100

    def _tokenize(self, text: str) -> List[str]:
        """将文本分词（简单实现）"""
        # 移除标点符号，按空格分词
        words = re.findall(r'\w+', text)
        # 过滤停用词和短词
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        return [w for w in words if len(w) > 2 and w not in stop_words]

    def load_template(self, template_name: str) -> str:
        """
        加载 issue 模板

        Args:
            template_name: 模板名称（不含 .md 扩展名）

        Returns:
            模板内容
        """
        template_path = self.templates_dir / f"{template_name}.md"

        if not template_path.exists():
            raise FileNotFoundError(f"模板不存在: {template_path}")

        return template_path.read_text()

    def create_from_template(
        self,
        template_name: str,
        title: str,
        variables: Optional[Dict[str, str]] = None,
        labels: Optional[List[str]] = None,
        force: bool = False,
        dry_run: bool = False
    ) -> Dict:
        """
        使用模板创建 issue

        Args:
            template_name: 模板名称
            title: Issue 标题
            variables: 模板变量字典
            labels: 标签列表
            force: 是否跳过尺寸检查
            dry_run: 是否仅预览

        Returns:
            创建结果
        """
        # 加载模板
        template = self.load_template(template_name)

        # 替换变量
        if variables:
            for key, value in variables.items():
                template = template.replace(f"{{{key}}}", value)

        # 创建 issue
        return self.create_issue(title, template, labels, force, dry_run)

    def batch_create(
        self,
        issues_file: Path,
        auto_split: bool = False,
        dry_run: bool = False
    ) -> Dict:
        """
        批量创建 issues

        Args:
            issues_file: 包含多个 issue 的 markdown 文件
            auto_split: 是否自动拆分过大的 issues
            dry_run: 是否仅预览

        Returns:
            批量创建结果
        """
        # 解析文件
        issues = self._parse_issues_file(issues_file)

        results = {
            "total": len(issues),
            "created": [],
            "skipped": [],
            "failed": []
        }

        for issue_data in issues:
            result = self.create_issue(
                title=issue_data["title"],
                body=issue_data["body"],
                labels=issue_data.get("labels", []),
                force=auto_split,  # 如果 auto_split，跳过尺寸检查
                dry_run=dry_run
            )

            if result["success"]:
                results["created"].append(result)
            elif "duplicate" in result:
                results["skipped"].append(result)
            else:
                results["failed"].append(result)

        return results

    def _parse_issues_file(self, file_path: Path) -> List[Dict]:
        """
        解析批量创建文件

        文件格式:
        ---
        title: Issue 标题
        labels: label1, label2
        ---

        Issue 内容...

        ---
        title: 下一个 Issue
        ---

        下一个内容...

        Returns:
            Issue 数据列表
        """
        content = file_path.read_text()
        issue_sections = re.split(r'^---\s*$', content, flags=re.MULTILINE)

        issues = []
        i = 1  # 跳过第一个空段
        while i < len(issue_sections):
            # 解析 frontmatter
            frontmatter = issue_sections[i].strip()
            if not frontmatter:
                i += 1
                continue

            # 提取元数据
            metadata = {}
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()

            # 提取内容
            body = issue_sections[i + 1].strip() if i + 1 < len(issue_sections) else ""

            # 解析标签
            labels = []
            if "labels" in metadata:
                labels = [l.strip() for l in metadata["labels"].split(',')]

            issues.append({
                "title": metadata.get("title", "Untitled"),
                "body": body,
                "labels": labels
            })

            i += 2

        return issues


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="创建 GitHub issues with intelligent size validation"
    )

    # 基础参数
    parser.add_argument("--title", help="Issue 标题")
    parser.add_argument("--body", help="Issue 内容")
    parser.add_argument("--labels", help="标签（逗号分隔）")
    parser.add_argument("--repo", help="目标仓库（owner/repo）")

    # 模板参数
    parser.add_argument("--template", help="使用模板")

    # 批量创建
    parser.add_argument("--from", dest="from_file", help="从文件批量创建")

    # 尺寸控制
    parser.add_argument("--force", action="store_true", help="跳过尺寸检查")
    parser.add_argument("--auto-split", action="store_true", help="自动拆分过大的 issues")
    parser.add_argument("--estimate-only", action="store_true", help="仅估算尺寸")

    # 其他选项
    parser.add_argument("--check-duplicate", action="store_true", help="仅检查去重")
    parser.add_argument("--dry-run", action="store_true", help="预览不创建")

    args = parser.parse_args()

    # 创建 IssueCreator 实例
    creator = IssueCreator(repo=args.repo)

    # 批量创建模式
    if args.from_file:
        file_path = Path(args.from_file)
        if not file_path.exists():
            print(f"❌ 文件不存在: {file_path}", file=sys.stderr)
            sys.exit(1)

        results = creator.batch_create(
            file_path,
            auto_split=args.auto_split,
            dry_run=args.dry_run
        )

        # 打印结果
        print(f"\n📊 批量创建报告")
        print(f"\n总计: {results['total']} 个 issues")
        print(f"✅ 成功: {len(results['created'])} 个")
        print(f"⚠️  跳过: {len(results['skipped'])} 个")
        print(f"❌ 失败: {len(results['failed'])} 个")

        if results['created']:
            print("\n创建的 issues:")
            for r in results['created']:
                if r.get('dry_run'):
                    print(f"  [预览] {r['preview']['title']}")
                else:
                    print(f"  #{r['issue_number']}: {r.get('preview', {}).get('title', 'N/A')}")

        sys.exit(0)

    # 单个 issue 创建模式
    if not args.title:
        print("❌ 请提供 --title 参数", file=sys.stderr)
        sys.exit(1)

    # 确定 body
    if args.template:
        try:
            body = creator.load_template(args.template)
        except FileNotFoundError as e:
            print(f"❌ {e}", file=sys.stderr)
            sys.exit(1)
    elif args.body:
        body = args.body
    else:
        body = ""

    # 解析标签
    labels = args.labels.split(',') if args.labels else None

    # 仅估算模式
    if args.estimate_only:
        size_result = creator.validator.validate_size(args.title, body)
        print(f"\n📏 尺寸估算")
        print(f"   任务数: {size_result.tasks_count}")
        print(f"   估算时间: {size_result.estimated_hours} 小时")
        print(f"   建议: {size_result.recommendation.name}")
        print(f"   {size_result.message}")
        sys.exit(0)

    # 仅去重检测
    if args.check_duplicate:
        duplicate = creator._check_duplicate(args.title, body)
        if duplicate:
            print(f"\n🔍 发现相似 issue:")
            print(f"   #{duplicate['number']}: {duplicate['title']}")
            print(f"   相似度: {duplicate['similarity']:.1f}%")
            print(f"   {duplicate['url']}")
        else:
            print("\n✅ 未发现相似 issue")
        sys.exit(0)

    # 创建 issue
    result = creator.create_issue(
        title=args.title,
        body=body,
        labels=labels,
        force=args.force,
        dry_run=args.dry_run
    )

    # 打印结果
    if result["success"]:
        if result.get("dry_run"):
            print("\n📋 预览模式")
            print(f"   标题: {result['preview']['title']}")
            print(f"   标签: {', '.join(result['preview']['labels'])}")
        else:
            print(f"\n✅ Issue 创建成功")
            print(f"   #{result['issue_number']}: {args.title}")
            print(f"   {result['issue_url']}")

            if result.get('size_result'):
                sr = result['size_result']
                print(f"\n📏 尺寸信息")
                print(f"   任务数: {sr.tasks_count}")
                print(f"   估算时间: {sr.estimated_hours} 小时")
                print(f"   建议: {sr.recommendation.name}")
    else:
        print(f"\n❌ 创建失败: {result['error']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
