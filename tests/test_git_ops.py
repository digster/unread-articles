"""Tests for git operations (commit and push)."""

import subprocess
from unittest.mock import call, patch

import pytest

from unread_articles.git_ops import commit_and_push


class TestCommitAndPush:
    """Tests for commit_and_push with mocked subprocess calls."""

    @patch("unread_articles.git_ops.subprocess.run")
    def test_commits_and_pushes_when_changes_exist(self, mock_run):
        """Returns True and runs commit + push when staged changes exist."""
        # git add succeeds, git diff --cached --quiet exits 1 (changes exist),
        # git commit and git push succeed
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0),  # git add
            subprocess.CompletedProcess(args=[], returncode=1),  # git diff --cached --quiet
            subprocess.CompletedProcess(args=[], returncode=0),  # git commit
            subprocess.CompletedProcess(args=[], returncode=0),  # git push
        ]

        result = commit_and_push(files=["urls.txt"], message="test commit")

        assert result is True
        assert mock_run.call_count == 4
        mock_run.assert_any_call(["git", "add", "urls.txt"], check=True)
        mock_run.assert_any_call(["git", "diff", "--cached", "--quiet"])
        mock_run.assert_any_call(["git", "commit", "-m", "test commit"], check=True)
        mock_run.assert_any_call(["git", "push"], check=True)

    @patch("unread_articles.git_ops.subprocess.run")
    def test_skips_commit_when_no_changes(self, mock_run):
        """Returns False and skips commit/push when no staged changes."""
        # git add succeeds, git diff --cached --quiet exits 0 (no changes)
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0),  # git add
            subprocess.CompletedProcess(args=[], returncode=0),  # git diff --cached --quiet
        ]

        result = commit_and_push(files=["urls.txt"])

        assert result is False
        # Only git add and git diff should be called — no commit or push
        assert mock_run.call_count == 2

    @patch("unread_articles.git_ops.subprocess.run")
    def test_default_commit_message(self, mock_run):
        """Uses date-based default message when none is provided."""
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0),  # git add
            subprocess.CompletedProcess(args=[], returncode=1),  # git diff --cached --quiet
            subprocess.CompletedProcess(args=[], returncode=0),  # git commit
            subprocess.CompletedProcess(args=[], returncode=0),  # git push
        ]

        commit_and_push(files=["urls.txt"])

        # The commit message should start with "updated urls - "
        commit_call = mock_run.call_args_list[2]
        commit_msg = commit_call[0][0][3]  # ["git", "commit", "-m", <message>]
        assert commit_msg.startswith("updated urls - ")
