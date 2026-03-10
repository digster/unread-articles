"""Git operations for committing and pushing URL changes."""

import subprocess
from datetime import datetime, timezone


def commit_and_push(files: list[str], message: str | None = None) -> None:
    """Stage specified files, commit with a message, and push to remote.

    Args:
        files: List of file paths to stage.
        message: Custom commit message. Defaults to "updated urls - YYYY-MM-DD".
    """
    if message is None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        message = f"updated urls - {date_str}"

    # Stage only the specified files
    subprocess.run(["git", "add", *files], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push"], check=True)
