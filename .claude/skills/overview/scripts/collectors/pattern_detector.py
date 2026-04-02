#!/usr/bin/env python3
"""Code pattern detection module.

Detects architectural patterns, testing frameworks, and design patterns in the codebase.
Replaces detect-patterns.sh per ADR-003.

Example:
    >>> from collectors import pattern_detector
    >>> patterns = pattern_detector.detect_patterns()
    >>> print(', '.join(patterns))
    Clean Architecture, Jest Testing, Zustand State Management
"""

import sys
import subprocess
import re
from pathlib import Path
from typing import List, Set

# Add _scripts to path

from fs_utils import check_file_exists


def detect_patterns() -> List[str]:
    """
    Detect code patterns, frameworks, and architectural styles.

    Scans the codebase for common patterns using file structure,
    imports, and code content analysis.

    Returns:
        List of detected pattern names

    Example:
        >>> patterns = detect_patterns()
        >>> print(patterns)
        ['Clean Architecture', 'Jest Testing', 'TypeScript Nominal Types']
    """
    patterns: Set[str] = set()

    # Detect nominal types (TypeScript branded/nominal types)
    if _contains_in_src('unique symbol') or _contains_in_src('& { __brand:'):
        patterns.add('TypeScript Nominal Types')

    # Detect airlock validation pattern
    if _contains_in_src('airlock'):
        patterns.add('Airlock Validation')

    # Detect saga pattern
    if _contains_in_src('Saga') or _contains_in_src('compensation'):
        patterns.add('Saga Pattern')

    # Detect headless UI pattern
    if Path('src/headless').is_dir() or Path('packages/frontend/src/headless').is_dir():
        patterns.add('Headless UI')

    # Detect Clean Architecture
    if _has_clean_architecture_structure():
        patterns.add('Clean Architecture')

    # Detect testing frameworks
    test_patterns = _detect_testing_framework()
    patterns.update(test_patterns)

    # Detect state management
    state_patterns = _detect_state_management()
    patterns.update(state_patterns)

    # Detect Infrastructure as Code
    iac_patterns = _detect_iac()
    patterns.update(iac_patterns)

    # Detect frontend frameworks
    frontend_patterns = _detect_frontend_framework()
    patterns.update(frontend_patterns)

    return sorted(list(patterns))


def count_test_files() -> int:
    """
    Count test files in the project.

    Looks for files matching patterns: *.test.*, *.spec.*

    Returns:
        Number of test files

    Example:
        >>> count = count_test_files()
        >>> print(f"Test files: {count}")
        Test files: 42
    """
    count = 0
    test_dirs = ['tests', 'test', 'src']

    for test_dir in test_dirs:
        dir_path = Path(test_dir)
        if not dir_path.is_dir():
            continue

        # Find test files recursively
        for pattern in ['**/*.test.*', '**/*.spec.*']:
            count += len(list(dir_path.glob(pattern)))

    return count


def _contains_in_src(pattern: str) -> bool:
    """Check if pattern exists in src/ directory using grep."""
    try:
        if not Path('src').is_dir():
            return False

        result = subprocess.run(
            ['grep', '-r', '-q', pattern, 'src/'],
            capture_output=True
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.SubprocessError):
        return False


def _has_clean_architecture_structure() -> bool:
    """Detect Clean Architecture structure."""
    indicators = [
        Path('src/domain').is_dir(),
        Path('src/application').is_dir(),
        Path('src/infrastructure').is_dir(),
        Path('src/presentation').is_dir(),
        _contains_in_src('UseCase') or _contains_in_src('usecase'),
        _contains_in_src('Repository') and _contains_in_src('Entity')
    ]
    return sum(indicators) >= 2


def _detect_testing_framework() -> List[str]:
    """Detect testing framework(s) in use."""
    frameworks = []

    if check_file_exists('package.json'):
        try:
            import json
            with open('package.json', 'r') as f:
                pkg = json.load(f)
                deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}

                if 'jest' in deps:
                    frameworks.append('Jest Testing')
                if 'vitest' in deps:
                    frameworks.append('Vitest Testing')
                if 'mocha' in deps:
                    frameworks.append('Mocha Testing')
                if '@testing-library/react' in deps:
                    frameworks.append('React Testing Library')
                if 'cypress' in deps:
                    frameworks.append('Cypress E2E')
                if 'playwright' in deps:
                    frameworks.append('Playwright E2E')
        except (IOError, json.JSONDecodeError, KeyError):
            pass

    # Fallback: check for test files
    if not frameworks and count_test_files() > 0:
        frameworks.append('Testing Framework')

    return frameworks


def _detect_state_management() -> List[str]:
    """Detect state management solution(s)."""
    solutions = []

    if check_file_exists('package.json'):
        try:
            import json
            with open('package.json', 'r') as f:
                pkg = json.load(f)
                deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}

                if 'zustand' in deps:
                    solutions.append('Zustand State Management')
                if 'redux' in deps or '@reduxjs/toolkit' in deps:
                    solutions.append('Redux State Management')
                if 'mobx' in deps:
                    solutions.append('MobX State Management')
                if 'recoil' in deps:
                    solutions.append('Recoil State Management')
        except (IOError, json.JSONDecodeError, KeyError):
            pass

    return solutions


def _detect_iac() -> List[str]:
    """Detect Infrastructure as Code tools."""
    tools = []

    if Path('cdk').is_dir() or Path('infrastructure').is_dir():
        if check_file_exists('cdk.json'):
            tools.append('AWS CDK Infrastructure')
        elif check_file_exists('package.json'):
            try:
                import json
                with open('package.json', 'r') as f:
                    pkg = json.load(f)
                    deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                    if 'aws-cdk-lib' in deps:
                        tools.append('AWS CDK Infrastructure')
            except (IOError, json.JSONDecodeError, KeyError):
                pass

    if Path('terraform').is_dir() or check_file_exists('main.tf'):
        tools.append('Terraform Infrastructure')

    return tools


def _detect_frontend_framework() -> List[str]:
    """Detect frontend framework(s)."""
    frameworks = []

    if check_file_exists('package.json'):
        try:
            import json
            with open('package.json', 'r') as f:
                pkg = json.load(f)
                deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}

                if 'react' in deps:
                    frameworks.append('React Frontend')
                if 'vue' in deps:
                    frameworks.append('Vue Frontend')
                if 'angular' in deps or '@angular/core' in deps:
                    frameworks.append('Angular Frontend')
                if 'svelte' in deps:
                    frameworks.append('Svelte Frontend')
                if 'next' in deps:
                    frameworks.append('Next.js Framework')
        except (IOError, json.JSONDecodeError, KeyError):
            pass

    return frameworks


if __name__ == '__main__':
    # CLI interface for direct invocation
    import json

    if len(sys.argv) > 1 and sys.argv[1] == 'count-tests':
        # Print test file count
        count = count_test_files()
        print(json.dumps({'testCount': count}, indent=2))
    else:
        # Print detected patterns
        patterns = detect_patterns()
        print(json.dumps(patterns, indent=2))
