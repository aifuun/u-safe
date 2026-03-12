#!/usr/bin/env python3
"""Audit all skills for ADR compliance.

Checks:
- ADR-001: YAML frontmatter, TRIGGER/DO NOT TRIGGER, structure
- ADR-003: Python-only scripts, type hints, docstrings
- WORKFLOW_PATTERNS: TaskCreate/TaskUpdate for workflow skills
- Skills README: Proper documentation

Usage:
    python audit_skills.py
    python audit_skills.py --skill finish-issue
    python audit_skills.py --verbose
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Workflow skills that MUST follow WORKFLOW_PATTERNS
WORKFLOW_SKILLS = {
    'start-issue',
    'execute-plan',
    'finish-issue',
    'sync',
    'work-issue',
    'eval-plan',
    'review'
}


class SkillAuditor:
    """Audits a single skill for compliance."""

    def __init__(self, skill_path: Path):
        """Initialize auditor for a skill.

        Args:
            skill_path: Path to skill directory
        """
        self.skill_path = skill_path
        self.skill_name = skill_path.name
        self.skill_md = skill_path / "SKILL.md"
        self.scripts_dir = skill_path / "scripts"
        self.issues: List[Dict] = []
        self.warnings: List[Dict] = []
        self.passed: List[str] = []

    def audit(self) -> Dict:
        """Run all compliance checks.

        Returns:
            Audit report dict
        """
        if not self.skill_md.exists():
            self.issues.append({
                'category': 'structure',
                'severity': 'critical',
                'message': 'SKILL.md missing'
            })
            return self._generate_report()

        # Read SKILL.md
        with open(self.skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # ADR-001 checks
        self._check_yaml_frontmatter(content)
        self._check_trigger_conditions(content)
        self._check_file_structure()

        # ADR-003 checks
        self._check_python_scripts()

        # WORKFLOW_PATTERNS checks
        if self.skill_name in WORKFLOW_SKILLS:
            self._check_workflow_patterns(content)

        return self._generate_report()

    def _check_yaml_frontmatter(self, content: str) -> None:
        """Check YAML frontmatter exists and is valid."""
        if not content.startswith('---'):
            self.issues.append({
                'category': 'ADR-001',
                'severity': 'critical',
                'message': 'Missing YAML frontmatter (should start with ---)'
            })
            return

        # Extract frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            self.issues.append({
                'category': 'ADR-001',
                'severity': 'critical',
                'message': 'Invalid YAML frontmatter (missing closing ---)'
            })
            return

        frontmatter = parts[1]

        # Check required fields
        required = ['name', 'description']
        for field in required:
            if f'{field}:' not in frontmatter:
                self.issues.append({
                    'category': 'ADR-001',
                    'severity': 'critical',
                    'message': f'Missing required field: {field}'
                })
        else:
            self.passed.append('YAML frontmatter structure')

        # Check name matches directory
        name_match = re.search(r'name:\s*(\S+)', frontmatter)
        if name_match:
            yaml_name = name_match.group(1)
            if yaml_name != self.skill_name:
                self.warnings.append({
                    'category': 'ADR-001',
                    'severity': 'medium',
                    'message': f'Name mismatch: {yaml_name} != {self.skill_name}'
                })

    def _check_trigger_conditions(self, content: str) -> None:
        """Check TRIGGER and DO NOT TRIGGER conditions."""
        has_trigger = 'TRIGGER when:' in content
        has_no_trigger = 'DO NOT TRIGGER when:' in content

        if not has_trigger:
            self.issues.append({
                'category': 'ADR-001',
                'severity': 'high',
                'message': 'Missing "TRIGGER when:" in description'
            })

        if not has_no_trigger:
            self.warnings.append({
                'category': 'ADR-001',
                'severity': 'medium',
                'message': 'Missing "DO NOT TRIGGER when:" in description'
            })

        if has_trigger and has_no_trigger:
            self.passed.append('TRIGGER conditions defined')

    def _check_file_structure(self) -> None:
        """Check directory structure follows ADR-001."""
        expected = ['SKILL.md']
        optional = ['scripts/', 'LICENSE.txt', 'README.md', 'evals.json']

        # Check SKILL.md exists (already checked)
        self.passed.append('SKILL.md exists')

        # Check for unexpected files
        for item in self.skill_path.iterdir():
            if item.name not in expected + optional and not item.name.startswith('.'):
                if item.is_file():
                    self.warnings.append({
                        'category': 'structure',
                        'severity': 'low',
                        'message': f'Unexpected file: {item.name}'
                    })

    def _check_python_scripts(self) -> None:
        """Check scripts follow ADR-003 (Python-only, type hints)."""
        if not self.scripts_dir.exists():
            # Scripts are optional
            return

        bash_scripts = list(self.scripts_dir.glob('*.sh'))
        if bash_scripts:
            for script in bash_scripts:
                self.issues.append({
                    'category': 'ADR-003',
                    'severity': 'critical',
                    'message': f'Bash script found: {script.name} (Python-only policy)'
                })

        python_scripts = list(self.scripts_dir.glob('*.py'))
        if not python_scripts and bash_scripts:
            self.issues.append({
                'category': 'ADR-003',
                'severity': 'high',
                'message': 'No Python scripts found, but Bash scripts exist'
            })
            return

        # Check each Python script
        for script in python_scripts:
            self._check_python_file(script)

    def _check_python_file(self, script_path: Path) -> None:
        """Check individual Python file for compliance."""
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Skip checks for __init__.py (can be intentionally empty)
        if script_path.name == '__init__.py':
            if content.strip():  # Only check if not empty
                # Check for docstring if file has content
                if not re.search(r'"""[\s\S]+?"""', content):
                    self.warnings.append({
                        'category': 'ADR-003',
                        'severity': 'low',
                        'message': f'{script_path.name}: Missing module docstring'
                    })
            return  # Skip shebang check for __init__.py

        # Check shebang
        if not content.startswith('#!/usr/bin/env python3'):
            self.warnings.append({
                'category': 'ADR-003',
                'severity': 'low',
                'message': f'{script_path.name}: Missing shebang'
            })

        # Check module docstring (allow optional shebang before docstring)
        if not re.search(r'^(?:#!/[^\n]*\n)?"""[\s\S]+?"""', content):
            self.warnings.append({
                'category': 'ADR-003',
                'severity': 'medium',
                'message': f'{script_path.name}: Missing module docstring'
            })

        # Check for type hints in function definitions
        functions = re.findall(r'def\s+(\w+)\s*\([^)]*\)\s*(?:->)?', content)
        typed_functions = re.findall(r'def\s+\w+\s*\([^)]*\)\s*->', content)

        if functions and len(typed_functions) < len(functions):
            missing = len(functions) - len(typed_functions)
            self.warnings.append({
                'category': 'ADR-003',
                'severity': 'medium',
                'message': f'{script_path.name}: {missing} functions missing type hints'
            })
        elif functions:
            self.passed.append(f'{script_path.name}: Type hints present')

    def _check_workflow_patterns(self, content: str) -> None:
        """Check workflow skill follows WORKFLOW_PATTERNS."""
        # Check for TaskCreate mention
        has_task_create = 'TaskCreate' in content
        has_task_update = 'TaskUpdate' in content
        has_checklist = '- [ ]' in content

        if not has_task_create:
            self.issues.append({
                'category': 'WORKFLOW_PATTERNS',
                'severity': 'high',
                'message': 'Workflow skill missing TaskCreate documentation'
            })

        if not has_task_update:
            self.issues.append({
                'category': 'WORKFLOW_PATTERNS',
                'severity': 'high',
                'message': 'Workflow skill missing TaskUpdate documentation'
            })

        if not has_checklist:
            self.warnings.append({
                'category': 'WORKFLOW_PATTERNS',
                'severity': 'medium',
                'message': 'Missing progress checklist (- [ ] items)'
            })

        if has_task_create and has_task_update:
            self.passed.append('WORKFLOW_PATTERNS compliance')

    def _generate_report(self) -> Dict:
        """Generate audit report."""
        score = 100

        # Deduct points for issues
        for issue in self.issues:
            if issue['severity'] == 'critical':
                score -= 20
            elif issue['severity'] == 'high':
                score -= 10
            elif issue['severity'] == 'medium':
                score -= 5

        # Deduct points for warnings
        for warning in self.warnings:
            if warning['severity'] == 'medium':
                score -= 3
            elif warning['severity'] == 'low':
                score -= 1

        score = max(0, score)

        # Determine status
        if score >= 90:
            status = 'pass'
        elif score >= 70:
            status = 'needs_improvement'
        else:
            status = 'fail'

        return {
            'skill': self.skill_name,
            'status': status,
            'score': score,
            'is_workflow': self.skill_name in WORKFLOW_SKILLS,
            'issues': self.issues,
            'warnings': self.warnings,
            'passed': self.passed
        }


def audit_all_skills(skills_dir: Path, verbose: bool = False) -> List[Dict]:
    """Audit all skills in directory.

    Args:
        skills_dir: Path to .claude/skills directory
        verbose: Print detailed output

    Returns:
        List of audit reports
    """
    reports = []

    # Get all skill directories
    skill_dirs = [
        d for d in skills_dir.iterdir()
        if d.is_dir() and not d.name.startswith('_') and not d.name.startswith('.')
    ]

    for skill_dir in sorted(skill_dirs):
        if verbose:
            print(f"\n🔍 Auditing {skill_dir.name}...")

        auditor = SkillAuditor(skill_dir)
        report = auditor.audit()
        reports.append(report)

        if verbose:
            print_report(report)

    return reports


def print_report(report: Dict) -> None:
    """Print single skill report."""
    skill = report['skill']
    status = report['status']
    score = report['score']

    # Status emoji
    status_emoji = {
        'pass': '✅',
        'needs_improvement': '⚠️',
        'fail': '❌'
    }[status]

    print(f"{status_emoji} {skill}: {score}/100")

    if report['is_workflow']:
        print("   📋 Workflow skill")

    # Print issues
    for issue in report['issues']:
        severity_emoji = {
            'critical': '🔴',
            'high': '⚠️',
            'medium': '💛',
            'low': '💙'
        }[issue['severity']]
        print(f"   {severity_emoji} {issue['category']}: {issue['message']}")

    # Print warnings
    for warning in report['warnings']:
        print(f"   💛 {warning['category']}: {warning['message']}")

    # Print passed checks
    if report['passed']:
        print(f"   ✅ Passed: {', '.join(report['passed'][:3])}")


def print_summary(reports: List[Dict]) -> None:
    """Print audit summary."""
    total = len(reports)
    passed = sum(1 for r in reports if r['status'] == 'pass')
    needs_improvement = sum(1 for r in reports if r['status'] == 'needs_improvement')
    failed = sum(1 for r in reports if r['status'] == 'fail')

    avg_score = sum(r['score'] for r in reports) / total if total > 0 else 0

    print("\n" + "="*60)
    print("📊 AUDIT SUMMARY")
    print("="*60)
    print(f"Total skills: {total}")
    print(f"✅ Passed (≥90): {passed}")
    print(f"⚠️  Needs improvement (70-89): {needs_improvement}")
    print(f"❌ Failed (<70): {failed}")
    print(f"📈 Average score: {avg_score:.1f}/100")
    print()

    # Group by status
    if failed > 0:
        print("❌ Failed skills:")
        for r in reports:
            if r['status'] == 'fail':
                print(f"   - {r['skill']} ({r['score']}/100)")
        print()

    if needs_improvement > 0:
        print("⚠️  Needs improvement:")
        for r in reports:
            if r['status'] == 'needs_improvement':
                print(f"   - {r['skill']} ({r['score']}/100)")
        print()

    # Top issues across all skills
    all_issues = []
    for r in reports:
        all_issues.extend(r['issues'])

    if all_issues:
        print("🔥 Top issues by category:")
        categories = {}
        for issue in all_issues:
            cat = issue['category']
            categories[cat] = categories.get(cat, 0) + 1

        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            print(f"   - {cat}: {count} occurrences")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Audit skills for ADR compliance"
    )
    parser.add_argument(
        '--skill',
        help='Audit specific skill only'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output JSON report'
    )

    args = parser.parse_args()

    # Find skills directory
    skills_dir = Path('.claude/skills')
    if not skills_dir.exists():
        print("❌ Error: .claude/skills directory not found", file=sys.stderr)
        return 1

    # Audit
    if args.skill:
        skill_path = skills_dir / args.skill
        if not skill_path.exists():
            print(f"❌ Error: Skill '{args.skill}' not found", file=sys.stderr)
            return 1

        auditor = SkillAuditor(skill_path)
        report = auditor.audit()
        reports = [report]

        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print_report(report)
    else:
        reports = audit_all_skills(skills_dir, verbose=args.verbose)

        if args.json:
            print(json.dumps(reports, indent=2))
        else:
            if not args.verbose:
                # Print compact summary
                for report in reports:
                    print_report(report)
            print_summary(reports)

    return 0


if __name__ == '__main__':
    sys.exit(main())
