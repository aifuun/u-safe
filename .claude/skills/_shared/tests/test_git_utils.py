#!/usr/bin/env python3
"""Unit tests for git_utils module."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from git_utils import (
    run_git_command,
    get_current_branch,
    check_sync_status,
    get_commit_info,
    get_branch_commits
)
from test_utils import mock_git_repo
import subprocess


class TestRunGitCommand:
    """Tests for run_git_command function."""

    def test_successful_command(self):
        """Test running a successful git command."""
        code, stdout, stderr = run_git_command(['--version'])
        assert code == 0
        assert 'git version' in stdout.lower()
        assert stderr == ''

    def test_invalid_command(self):
        """Test running an invalid git command."""
        code, stdout, stderr = run_git_command(['invalid-command'])
        assert code != 0
        assert stderr != ''

    def test_returns_tuple(self):
        """Test that function returns a 3-tuple."""
        result = run_git_command(['--version'])
        assert isinstance(result, tuple)
        assert len(result) == 3
        code, stdout, stderr = result
        assert isinstance(code, int)
        assert isinstance(stdout, str)
        assert isinstance(stderr, str)


class TestGetCurrentBranch:
    """Tests for get_current_branch function."""

    def test_get_branch_in_repo(self):
        """Test getting branch name in a git repository."""
        with mock_git_repo() as repo:
            # Change to repo directory and get branch
            import os
            original_dir = os.getcwd()
            try:
                os.chdir(repo)
                branch = get_current_branch()
                # Git init creates 'main' or 'master' depending on config
                assert branch in ('main', 'master')
            finally:
                os.chdir(original_dir)

    def test_error_outside_repo(self):
        """Test error when not in a git repository."""
        import tempfile
        import os
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                with pytest.raises(RuntimeError):
                    get_current_branch()
            finally:
                os.chdir(original_dir)

    def test_branch_name_format(self):
        """Test that branch name is properly formatted."""
        with mock_git_repo() as repo:
            import os
            original_dir = os.getcwd()
            try:
                os.chdir(repo)
                # Create a feature branch
                subprocess.run(['git', 'checkout', '-b', 'feature/test-branch'],
                             cwd=repo, check=True, capture_output=True)
                branch = get_current_branch()
                assert branch == 'feature/test-branch'
            finally:
                os.chdir(original_dir)


class TestCheckSyncStatus:
    """Tests for check_sync_status function."""

    def test_synced_branch(self):
        """Test checking sync status when branch is synced."""
        # This test requires being in an actual repo with remotes
        # For now, we'll test that it returns a boolean
        with mock_git_repo() as repo:
            import os
            original_dir = os.getcwd()
            try:
                os.chdir(repo)
                result = check_sync_status()
                assert isinstance(result, bool)
            finally:
                os.chdir(original_dir)


class TestGetCommitInfo:
    """Tests for get_commit_info function."""

    def test_get_head_commit(self):
        """Test getting HEAD commit info."""
        with mock_git_repo() as repo:
            import os
            original_dir = os.getcwd()
            try:
                os.chdir(repo)
                info = get_commit_info('HEAD')
                assert isinstance(info, dict)
                assert 'hash' in info
                assert 'author' in info
                assert 'date' in info
                assert 'message' in info
                assert info['message'] == 'Initial commit'
                assert info['author'] == 'Test User'
            finally:
                os.chdir(original_dir)

    def test_commit_info_structure(self):
        """Test that commit info has correct structure."""
        with mock_git_repo() as repo:
            import os
            original_dir = os.getcwd()
            try:
                os.chdir(repo)
                info = get_commit_info()
                # Check all required fields exist
                required_fields = ['hash', 'author', 'date', 'message']
                for field in required_fields:
                    assert field in info
                    assert isinstance(info[field], str)
                    assert len(info[field]) > 0
            finally:
                os.chdir(original_dir)

    def test_invalid_ref(self):
        """Test error when ref doesn't exist."""
        with mock_git_repo() as repo:
            import os
            original_dir = os.getcwd()
            try:
                os.chdir(repo)
                with pytest.raises(RuntimeError):
                    get_commit_info('nonexistent-ref')
            finally:
                os.chdir(original_dir)


class TestGetBranchCommits:
    """Tests for get_branch_commits function."""

    def test_empty_range(self):
        """Test getting commits when range is empty."""
        with mock_git_repo() as repo:
            import os
            original_dir = os.getcwd()
            try:
                os.chdir(repo)
                # HEAD and HEAD should be same, so empty range
                commits = get_branch_commits('HEAD', 'HEAD')
                assert isinstance(commits, list)
                assert len(commits) == 0
            finally:
                os.chdir(original_dir)

    def test_branch_with_commits(self):
        """Test getting commits from a branch with new commits."""
        with mock_git_repo() as repo:
            import os
            original_dir = os.getcwd()
            try:
                os.chdir(repo)
                # Create a new branch
                subprocess.run(['git', 'checkout', '-b', 'feature/test'],
                             cwd=repo, check=True, capture_output=True)

                # Add some commits
                for i in range(3):
                    test_file = repo / f'test{i}.txt'
                    test_file.write_text(f'content {i}')
                    subprocess.run(['git', 'add', '.'], cwd=repo,
                                 check=True, capture_output=True)
                    subprocess.run(['git', 'commit', '-m', f'commit {i}'],
                                 cwd=repo, check=True, capture_output=True)

                # Get commits since main/master
                base_branch = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD~3'],
                                            cwd=repo, capture_output=True, text=True).stdout.strip()
                if not base_branch:
                    # Fallback: use initial commit
                    base_ref = subprocess.run(['git', 'rev-list', '--max-parents=0', 'HEAD'],
                                             cwd=repo, capture_output=True, text=True).stdout.strip()
                else:
                    base_ref = 'HEAD~3'

                commits = get_branch_commits(base_ref, 'HEAD')
                assert isinstance(commits, list)
                assert len(commits) == 3
                for commit in commits:
                    assert 'hash' in commit
                    assert 'author' in commit
                    assert 'message' in commit
            finally:
                os.chdir(original_dir)

    def test_commit_list_structure(self):
        """Test that commit list has correct structure."""
        with mock_git_repo() as repo:
            import os
            original_dir = os.getcwd()
            try:
                os.chdir(repo)
                # Get all commits (from root to HEAD)
                root_commit = subprocess.run(
                    ['git', 'rev-list', '--max-parents=0', 'HEAD'],
                    cwd=repo, capture_output=True, text=True
                ).stdout.strip()

                commits = get_branch_commits(f'{root_commit}~0', 'HEAD')
                assert isinstance(commits, list)
                if len(commits) > 0:
                    commit = commits[0]
                    assert isinstance(commit, dict)
                    required_fields = ['hash', 'author', 'date', 'message']
                    for field in required_fields:
                        assert field in commit
            finally:
                os.chdir(original_dir)
