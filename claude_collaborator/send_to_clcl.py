#!/usr/bin/env python3
"""
send_to_clcl.py - Send a task to CLCL from a cloud Claude instance

This script creates a task file in clcl_outbox/, commits, and pushes.
A GitHub Action then emails CLCL to wake it up.

Usage:
    python3 send_to_clcl.py "Review PR #42 and provide feedback"
    python3 send_to_clcl.py --urgent "Production is down, check logs"
    python3 send_to_clcl.py --task "Create issue" --context "Need to track the CLCL feature"

Environment:
    Must be run from within a git repository with push access.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_repo_root():
    """Find the git repository root."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True, check=True
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        print("Error: Not in a git repository")
        sys.exit(1)


def get_session_id():
    """Try to get a session identifier."""
    # Check for Claude Code session ID in common locations
    session_id = os.environ.get('CLAUDE_SESSION_ID', '')
    if not session_id:
        # Generate a short unique ID
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    return session_id


def create_task_file(repo_root, task, priority='normal', context=''):
    """Create a task file in clcl_outbox/."""
    outbox = repo_root / 'clcl_outbox'
    outbox.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')  # Include microseconds
    session_id = get_session_id()
    filename = f"task_{timestamp}_{session_id[:8]}.json"
    filepath = outbox / filename

    task_data = {
        'task': task,
        'priority': priority,
        'from': f'cloud-claude-{session_id}',
        'timestamp': datetime.now().isoformat(),
        'context': context
    }

    with open(filepath, 'w') as f:
        json.dump(task_data, f, indent=2)

    return filepath


def git_commit_and_push(filepath, task):
    """Commit the task file and push."""
    try:
        # Add the file
        subprocess.run(['git', 'add', str(filepath)], check=True)

        # Commit with CLCL-WAKE prefix
        commit_msg = f"[CLCL-WAKE] {task[:50]}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)

        # Push
        result = subprocess.run(
            ['git', 'push'],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            # Try with upstream set
            branch = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True, text=True
            ).stdout.strip()

            subprocess.run(
                ['git', 'push', '-u', 'origin', branch],
                check=True
            )

        return True

    except subprocess.CalledProcessError as e:
        print(f"Git error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Send a task to CLCL (Claude Collaborator)'
    )
    parser.add_argument(
        'task',
        nargs='?',
        help='The task description (can also use --task)'
    )
    parser.add_argument(
        '--task', '-t',
        dest='task_flag',
        help='The task description'
    )
    parser.add_argument(
        '--urgent', '-u',
        action='store_true',
        help='Mark as urgent priority'
    )
    parser.add_argument(
        '--context', '-c',
        default='',
        help='Additional context for the task'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Create file but do not commit/push'
    )

    args = parser.parse_args()

    # Get task from either positional or flag
    task = args.task or args.task_flag
    if not task:
        parser.print_help()
        print("\nError: Task description required")
        sys.exit(1)

    priority = 'urgent' if args.urgent else 'normal'
    repo_root = get_repo_root()

    print(f"📤 Sending task to CLCL...")
    print(f"   Task: {task}")
    print(f"   Priority: {priority}")

    # Create task file
    filepath = create_task_file(repo_root, task, priority, args.context)
    print(f"   File: {filepath.relative_to(repo_root)}")

    if args.dry_run:
        print("\n🔍 Dry run - file created but not pushed")
        print(f"   To send: git add {filepath} && git commit -m '[CLCL-WAKE] {task[:30]}' && git push")
        return

    # Commit and push
    print("   Pushing to trigger GitHub Action...")

    if git_commit_and_push(filepath, task):
        print("\n✅ Task sent to CLCL!")
        print("   GitHub Action will email CLCL shortly.")
        print("   CLCL will wake up and process the task.")
    else:
        print("\n❌ Failed to push. Check git configuration.")
        sys.exit(1)


if __name__ == '__main__':
    main()
