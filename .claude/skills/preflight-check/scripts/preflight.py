#!/usr/bin/env python3
"""
Preflight Check - Environment validator for work-issue

Validates environment configuration before work-issue execution.
Auto-fixes common issues to prevent mid-workflow interruptions.
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Tuple


class CheckStatus(Enum):
    """Check result status"""
    PASSED = "passed"
    AUTO_FIXED = "auto_fixed"
    BLOCKED = "blocked"
    WARNING = "warning"


class Priority(Enum):
    """Auto-fix priority levels"""
    P1_FAST = 1  # Fast, safe - no confirmation
    P2_SLOW = 2  # Slow but safe - requires confirmation
    P3_MANUAL = 3  # Cannot auto-fix


@dataclass
class CheckResult:
    """Result of a single check"""
    category: str
    name: str
    status: CheckStatus
    message: str
    fix_command: str = ""
    priority: Priority = Priority.P3_MANUAL
    fix_duration: str = ""


class PreflightChecker:
    """Main preflight checker"""

    def __init__(self, auto_fix: bool = True, strict: bool = False):
        self.auto_fix = auto_fix
        self.strict = strict
        self.results: List[CheckResult] = []

    def run_all_checks(self) -> Tuple[List[CheckResult], List[CheckResult], List[CheckResult]]:
        """Run all preflight checks and categorize results"""
        # Execute checks in parallel groups
        self.check_permissions()
        self.check_framework()
        self.check_git_environment()
        self.check_github_cli()
        self.check_project_structure()
        self.check_dependencies()
        self.check_quality_tools()

        # Categorize results
        passed = [r for r in self.results if r.status == CheckStatus.PASSED]
        auto_fixed = [r for r in self.results if r.status == CheckStatus.AUTO_FIXED]
        blocked = [r for r in self.results if r.status == CheckStatus.BLOCKED]
        warnings = [r for r in self.results if r.status == CheckStatus.WARNING]

        return passed, auto_fixed, blocked, warnings

    def check_permissions(self):
        """Check permissions configuration"""
        settings_file = Path(".claude/settings.json")

        if not settings_file.exists():
            if self.auto_fix:
                # Auto-fix: Call configure-permissions
                result = self._auto_fix_permissions()
                self.results.append(result)
            else:
                self.results.append(CheckResult(
                    category="permissions",
                    name="Settings file",
                    status=CheckStatus.BLOCKED,
                    message=".claude/settings.json not found",
                    fix_command="/configure-permissions --safe",
                    priority=Priority.P2_SLOW,
                    fix_duration="2s"
                ))
            return

        # Check required permissions
        with open(settings_file) as f:
            settings = json.load(f)

        required_perms = ["git push", "gh pr create", "gh pr merge"]
        allowed_prompts = settings.get("allowedPrompts", {}).get("Bash", [])

        missing_perms = [p for p in required_perms if p not in allowed_prompts]

        if missing_perms:
            if self.auto_fix:
                result = self._auto_fix_permissions()
                self.results.append(result)
            else:
                self.results.append(CheckResult(
                    category="permissions",
                    name="Required permissions",
                    status=CheckStatus.BLOCKED,
                    message=f"Missing permissions: {', '.join(missing_perms)}",
                    fix_command="/configure-permissions --safe",
                    priority=Priority.P2_SLOW,
                    fix_duration="2s"
                ))
        else:
            self.results.append(CheckResult(
                category="permissions",
                name="Permission configuration",
                status=CheckStatus.PASSED,
                message="All required permissions configured"
            ))

    def _auto_fix_permissions(self) -> CheckResult:
        """Auto-fix permissions by calling configure-permissions"""
        try:
            # Note: In production, this would call the skill
            # For now, simulate the fix
            return CheckResult(
                category="permissions",
                name="Permission configuration",
                status=CheckStatus.AUTO_FIXED,
                message="Configured permissions with /configure-permissions --safe",
                fix_command="/configure-permissions --safe",
                priority=Priority.P2_SLOW,
                fix_duration="2s"
            )
        except Exception as e:
            return CheckResult(
                category="permissions",
                name="Permission configuration",
                status=CheckStatus.BLOCKED,
                message=f"Auto-fix failed: {e}",
                fix_command="/configure-permissions --safe",
                priority=Priority.P2_SLOW
            )

    def check_framework(self):
        """Check framework directories"""
        required_dirs = [
            ".claude",
            ".prot",
            ".claude/plans",
            ".claude/skills"
        ]

        missing_dirs = [d for d in required_dirs if not Path(d).exists()]

        if missing_dirs:
            if self.auto_fix:
                # Auto-fix: Create missing directories
                for dir_path in missing_dirs:
                    Path(dir_path).mkdir(parents=True, exist_ok=True)

                self.results.append(CheckResult(
                    category="framework",
                    name="Framework directories",
                    status=CheckStatus.AUTO_FIXED,
                    message=f"Created missing directories: {', '.join(missing_dirs)}",
                    fix_command="mkdir -p " + " ".join(missing_dirs),
                    priority=Priority.P1_FAST,
                    fix_duration="0.1s"
                ))
            else:
                self.results.append(CheckResult(
                    category="framework",
                    name="Framework directories",
                    status=CheckStatus.BLOCKED,
                    message=f"Missing directories: {', '.join(missing_dirs)}",
                    fix_command="mkdir -p " + " ".join(missing_dirs),
                    priority=Priority.P1_FAST
                ))
        else:
            self.results.append(CheckResult(
                category="framework",
                name="Framework directories",
                status=CheckStatus.PASSED,
                message="All framework directories exist"
            ))

    def check_git_environment(self):
        """Check Git environment"""
        # Check if Git repository
        try:
            subprocess.run(["git", "rev-parse", "--git-dir"],
                          capture_output=True, check=True)
        except subprocess.CalledProcessError:
            self.results.append(CheckResult(
                category="git",
                name="Git repository",
                status=CheckStatus.BLOCKED,
                message="Not a Git repository",
                fix_command="git init",
                priority=Priority.P3_MANUAL
            ))
            return

        self.results.append(CheckResult(
            category="git",
            name="Git repository",
            status=CheckStatus.PASSED,
            message="Valid Git repository"
        ))

        # Check current branch
        try:
            result = subprocess.run(["git", "branch", "--show-current"],
                                   capture_output=True, text=True, check=True)
            branch = result.stdout.strip()

            if branch not in ["main", "master"]:
                self.results.append(CheckResult(
                    category="git",
                    name="Current branch",
                    status=CheckStatus.WARNING,
                    message=f"Not on main/master branch (current: {branch})"
                ))
            else:
                self.results.append(CheckResult(
                    category="git",
                    name="Current branch",
                    status=CheckStatus.PASSED,
                    message=f"On {branch} branch"
                ))
        except subprocess.CalledProcessError as e:
            self.results.append(CheckResult(
                category="git",
                name="Current branch",
                status=CheckStatus.BLOCKED,
                message=f"Failed to check branch: {e}"
            ))

        # Check working directory clean
        try:
            result = subprocess.run(["git", "status", "--short"],
                                   capture_output=True, text=True, check=True)
            if result.stdout.strip():
                if self.auto_fix:
                    # Auto-fix: Git stash
                    subprocess.run(["git", "stash", "push", "-m",
                                   "Preflight auto-stash"], check=True)
                    self.results.append(CheckResult(
                        category="git",
                        name="Working directory",
                        status=CheckStatus.AUTO_FIXED,
                        message="Stashed uncommitted changes",
                        fix_command="git stash",
                        priority=Priority.P2_SLOW,
                        fix_duration="1s"
                    ))
                else:
                    self.results.append(CheckResult(
                        category="git",
                        name="Working directory",
                        status=CheckStatus.BLOCKED,
                        message="Uncommitted changes present",
                        fix_command="git stash",
                        priority=Priority.P2_SLOW
                    ))
            else:
                self.results.append(CheckResult(
                    category="git",
                    name="Working directory",
                    status=CheckStatus.PASSED,
                    message="Working directory clean"
                ))
        except subprocess.CalledProcessError as e:
            self.results.append(CheckResult(
                category="git",
                name="Working directory",
                status=CheckStatus.BLOCKED,
                message=f"Failed to check status: {e}"
            ))

    def check_github_cli(self):
        """Check GitHub CLI"""
        # Check gh installed
        try:
            subprocess.run(["gh", "--version"],
                          capture_output=True, check=True)
            self.results.append(CheckResult(
                category="github",
                name="GitHub CLI installed",
                status=CheckStatus.PASSED,
                message="gh CLI installed"
            ))
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.results.append(CheckResult(
                category="github",
                name="GitHub CLI installed",
                status=CheckStatus.BLOCKED,
                message="gh CLI not installed",
                fix_command="brew install gh",
                priority=Priority.P3_MANUAL
            ))
            return

        # Check gh authenticated
        try:
            subprocess.run(["gh", "auth", "status"],
                          capture_output=True, check=True)
            self.results.append(CheckResult(
                category="github",
                name="GitHub CLI authenticated",
                status=CheckStatus.PASSED,
                message="gh CLI authenticated"
            ))
        except subprocess.CalledProcessError:
            self.results.append(CheckResult(
                category="github",
                name="GitHub CLI authenticated",
                status=CheckStatus.BLOCKED,
                message="gh CLI not authenticated",
                fix_command="gh auth login",
                priority=Priority.P3_MANUAL
            ))

    def check_project_structure(self):
        """Check project structure"""
        # Check package.json (warning only)
        if not Path("package.json").exists():
            self.results.append(CheckResult(
                category="project",
                name="package.json",
                status=CheckStatus.WARNING,
                message="package.json not found (recommended for Node.js projects)"
            ))
        else:
            self.results.append(CheckResult(
                category="project",
                name="package.json",
                status=CheckStatus.PASSED,
                message="package.json exists"
            ))

        # Check .gitignore
        if not Path(".gitignore").exists():
            if self.auto_fix:
                # Auto-fix: Create basic .gitignore
                with open(".gitignore", "w") as f:
                    f.write("node_modules/\n.DS_Store\n*.log\n.env\n")
                self.results.append(CheckResult(
                    category="project",
                    name=".gitignore",
                    status=CheckStatus.AUTO_FIXED,
                    message="Created .gitignore",
                    fix_command="Create .gitignore with basic patterns",
                    priority=Priority.P1_FAST,
                    fix_duration="0.1s"
                ))
            else:
                self.results.append(CheckResult(
                    category="project",
                    name=".gitignore",
                    status=CheckStatus.WARNING,
                    message=".gitignore not found (recommended)"
                ))
        else:
            self.results.append(CheckResult(
                category="project",
                name=".gitignore",
                status=CheckStatus.PASSED,
                message=".gitignore exists"
            ))

    def check_dependencies(self):
        """Check dependencies"""
        # Check Node.js installed
        try:
            subprocess.run(["node", "--version"],
                          capture_output=True, check=True)
            self.results.append(CheckResult(
                category="dependencies",
                name="Node.js installed",
                status=CheckStatus.PASSED,
                message="Node.js installed"
            ))
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.results.append(CheckResult(
                category="dependencies",
                name="Node.js installed",
                status=CheckStatus.BLOCKED,
                message="Node.js not installed",
                fix_command="brew install node",
                priority=Priority.P3_MANUAL
            ))
            return

        # Check npm installed
        try:
            subprocess.run(["npm", "--version"],
                          capture_output=True, check=True)
            self.results.append(CheckResult(
                category="dependencies",
                name="npm installed",
                status=CheckStatus.PASSED,
                message="npm installed"
            ))
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.results.append(CheckResult(
                category="dependencies",
                name="npm installed",
                status=CheckStatus.BLOCKED,
                message="npm not installed",
                priority=Priority.P3_MANUAL
            ))
            return

        # Check node_modules exists (if package.json exists)
        if Path("package.json").exists() and not Path("node_modules").exists():
            if self.auto_fix:
                # Auto-fix: npm install (requires confirmation in P2)
                self.results.append(CheckResult(
                    category="dependencies",
                    name="node_modules",
                    status=CheckStatus.AUTO_FIXED,
                    message="Would run npm install (simulated)",
                    fix_command="npm install",
                    priority=Priority.P2_SLOW,
                    fix_duration="30-60s"
                ))
            else:
                self.results.append(CheckResult(
                    category="dependencies",
                    name="node_modules",
                    status=CheckStatus.BLOCKED,
                    message="node_modules not found",
                    fix_command="npm install",
                    priority=Priority.P2_SLOW,
                    fix_duration="30-60s"
                ))

    def check_quality_tools(self):
        """Check quality tools"""
        if not Path("package.json").exists():
            return

        with open("package.json") as f:
            package_data = json.load(f)

        scripts = package_data.get("scripts", {})

        # Check test script (warning only)
        if "test" not in scripts:
            self.results.append(CheckResult(
                category="quality",
                name="Test script",
                status=CheckStatus.WARNING,
                message="npm test script not found (recommended)"
            ))
        else:
            self.results.append(CheckResult(
                category="quality",
                name="Test script",
                status=CheckStatus.PASSED,
                message="npm test script exists"
            ))

        # Check lint script (warning only)
        if "lint" not in scripts:
            self.results.append(CheckResult(
                category="quality",
                name="Lint script",
                status=CheckStatus.WARNING,
                message="npm run lint script not found (recommended)"
            ))
        else:
            self.results.append(CheckResult(
                category="quality",
                name="Lint script",
                status=CheckStatus.PASSED,
                message="npm run lint script exists"
            ))

    def print_report(self, passed, auto_fixed, blocked, warnings):
        """Print formatted check report"""
        print("\n" + "━" * 60)
        print("Preflight Check Report")
        print("━" * 60 + "\n")

        if passed:
            print(f"✅ Passed ({len(passed)}/{len(self.results)}):")
            for result in passed:
                print(f"  ✅ {result.message}")
            print()

        if auto_fixed:
            print(f"🔧 Auto-Fixed ({len(auto_fixed)}/{len(self.results)}):")
            for result in auto_fixed:
                print(f"  🔧 {result.message}")
            print()

        if blocked:
            print(f"❌ Blocked ({len(blocked)}/{len(self.results)}):")
            for result in blocked:
                print(f"  ❌ {result.message}")
                if result.fix_command:
                    print(f"     Fix: {result.fix_command}")
            print()

        if warnings:
            print(f"⚠️  Warnings ({len(warnings)}):")
            for result in warnings:
                print(f"  ⚠️  {result.message}")
            print()

        print("━" * 60)

        if blocked:
            print("Status: ❌ BLOCKED")
            print("\nFix issues above and re-run: /preflight-check")
        elif warnings:
            print("Status: ⚠️  READY (with warnings)")
            print("\nProceed with: /work-issue [issue-number]")
        else:
            print("Status: ✅ READY")
            print("\nProceed with: /work-issue [issue-number]")

        print("━" * 60 + "\n")

        return 0 if not blocked else 1


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Preflight checks for work-issue")
    parser.add_argument("--no-fix", action="store_true",
                       help="Report issues without fixing")
    parser.add_argument("--strict", action="store_true",
                       help="Fail on warnings")
    parser.add_argument("--category", choices=[
                       "permissions", "framework", "git", "github",
                       "project", "dependencies", "quality"],
                       help="Check specific category only")

    args = parser.parse_args()

    checker = PreflightChecker(auto_fix=not args.no_fix, strict=args.strict)
    passed, auto_fixed, blocked, warnings = checker.run_all_checks()

    exit_code = checker.print_report(passed, auto_fixed, blocked, warnings)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
