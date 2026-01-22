#!/usr/bin/env python3
"""
Tests for send_to_clcl.py

These tests verify the task file creation logic without requiring
git push or network access.
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from send_to_clcl import create_task_file, get_session_id


class TestCreateTaskFile(unittest.TestCase):
    """Test task file creation."""

    def setUp(self):
        """Create a temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_creates_outbox_directory(self):
        """Test that clcl_outbox directory is created if missing."""
        outbox = self.repo_root / 'clcl_outbox'
        self.assertFalse(outbox.exists())

        create_task_file(self.repo_root, "Test task")

        self.assertTrue(outbox.exists())
        self.assertTrue(outbox.is_dir())

    def test_creates_json_file(self):
        """Test that a JSON task file is created."""
        filepath = create_task_file(self.repo_root, "Test task")

        self.assertTrue(filepath.exists())
        self.assertEqual(filepath.suffix, '.json')

    def test_json_structure(self):
        """Test that the JSON has correct structure."""
        filepath = create_task_file(
            self.repo_root,
            "Review PR #42",
            priority='urgent',
            context='Found a bug'
        )

        with open(filepath) as f:
            data = json.load(f)

        self.assertEqual(data['task'], "Review PR #42")
        self.assertEqual(data['priority'], 'urgent')
        self.assertEqual(data['context'], 'Found a bug')
        self.assertIn('from', data)
        self.assertIn('timestamp', data)

    def test_default_priority(self):
        """Test that default priority is 'normal'."""
        filepath = create_task_file(self.repo_root, "Test task")

        with open(filepath) as f:
            data = json.load(f)

        self.assertEqual(data['priority'], 'normal')

    def test_timestamp_format(self):
        """Test that timestamp is ISO format."""
        filepath = create_task_file(self.repo_root, "Test task")

        with open(filepath) as f:
            data = json.load(f)

        # Should parse without error
        datetime.fromisoformat(data['timestamp'])

    def test_unique_filenames(self):
        """Test that multiple calls create unique files."""
        files = set()
        for i in range(5):
            filepath = create_task_file(self.repo_root, f"Task {i}")
            files.add(filepath.name)

        self.assertEqual(len(files), 5)


class TestGetSessionId(unittest.TestCase):
    """Test session ID generation."""

    def test_returns_string(self):
        """Test that session ID is a string."""
        session_id = get_session_id()
        self.assertIsInstance(session_id, str)

    def test_non_empty(self):
        """Test that session ID is not empty."""
        session_id = get_session_id()
        self.assertTrue(len(session_id) > 0)

    def test_uses_env_var_if_set(self):
        """Test that CLAUDE_SESSION_ID env var is used if set."""
        with patch.dict(os.environ, {'CLAUDE_SESSION_ID': 'test-session-123'}):
            session_id = get_session_id()
            self.assertEqual(session_id, 'test-session-123')


class TestTaskFileContent(unittest.TestCase):
    """Test task file content edge cases."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_unicode_task(self):
        """Test handling of unicode characters in task."""
        filepath = create_task_file(self.repo_root, "Fix bug with émojis 🐛")

        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)

        self.assertEqual(data['task'], "Fix bug with émojis 🐛")

    def test_multiline_context(self):
        """Test multiline context is preserved."""
        context = """Line 1
Line 2
Line 3"""
        filepath = create_task_file(self.repo_root, "Task", context=context)

        with open(filepath) as f:
            data = json.load(f)

        self.assertEqual(data['context'], context)

    def test_special_characters(self):
        """Test JSON special characters are escaped."""
        task = 'Task with "quotes" and \\backslashes\\'
        filepath = create_task_file(self.repo_root, task)

        with open(filepath) as f:
            data = json.load(f)

        self.assertEqual(data['task'], task)


if __name__ == '__main__':
    unittest.main()
