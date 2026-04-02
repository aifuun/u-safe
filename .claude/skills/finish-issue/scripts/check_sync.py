#!/usr/bin/env python3
"""Check if current branch is synced with origin/main.

Returns: "✅ Synced" or "⚠️ Need sync"
Exit codes: 0 = success
"""

import sys
from pathlib import Path

# Add _scripts to path

from utils.git import check_sync_status


def check_sync() -> int:
    """
    Check if current branch is synced with origin/main.

    Uses shared git_utils.check_sync_status() to verify
    whether origin/main is an ancestor of HEAD.

    Returns:
        0 if synced or check completed
        (Always returns 0 as this is informational)

    Example:
        >>> sys.exit(check_sync())
    """
    is_synced = check_sync_status()

    if is_synced:
        print('✅ Synced')
    else:
        print('⚠️ Need sync')

    return 0


if __name__ == '__main__':
    sys.exit(check_sync())
