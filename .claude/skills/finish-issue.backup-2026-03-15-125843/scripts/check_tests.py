#!/usr/bin/env python3
"""Check test status for finish-issue skill.

Returns: "✅ Passing", "⚠️ Failing", or "No tests"
Exit codes: 0 = success/no tests, 1 = tests failed
"""

import sys
import subprocess
from pathlib import Path


def check_tests() -> int:
    """
    Check if npm tests pass.

    Looks for package.json to determine if tests exist.
    If found, runs npm test and reports status.

    Returns:
        0 if tests pass or no tests exist
        1 if tests fail

    Example:
        >>> sys.exit(check_tests())
    """
    if not Path('package.json').exists():
        print('No tests')
        return 0

    result = subprocess.run(
        ['npm', 'test'],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print('✅ Passing')
        return 0
    else:
        print('⚠️ Failing')
        return 1


if __name__ == '__main__':
    sys.exit(check_tests())
