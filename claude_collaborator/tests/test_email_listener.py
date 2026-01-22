#!/usr/bin/env python3
"""
Tests for clcl_email_listener.py

These tests verify email parsing and task handling logic without
requiring actual IMAP connections.
"""

import email
import sys
import tempfile
import unittest
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from clcl_email_listener import (
    parse_clcl_command,
    decode_subject,
    get_body,
    write_task_file,
    WAKE_PREFIXES
)


def create_test_email(subject, body, from_addr='test@example.com'):
    """Helper to create test email messages."""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = 'claude@ecorestorationalliance.org'
    msg['Date'] = 'Thu, 22 Jan 2026 10:30:00 -0500'
    msg['Message-ID'] = '<test-123@example.com>'
    return msg


def create_multipart_email(subject, text_body, html_body=None, from_addr='test@example.com'):
    """Helper to create multipart test email."""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = 'claude@ecorestorationalliance.org'
    msg['Date'] = 'Thu, 22 Jan 2026 10:30:00 -0500'

    msg.attach(MIMEText(text_body, 'plain'))
    if html_body:
        msg.attach(MIMEText(html_body, 'html'))

    return msg


class TestDecodeSubject(unittest.TestCase):
    """Test email subject decoding."""

    def test_plain_subject(self):
        """Test plain ASCII subject."""
        result = decode_subject("Hello World")
        self.assertEqual(result, "Hello World")

    def test_empty_subject(self):
        """Test empty subject."""
        result = decode_subject("")
        self.assertEqual(result, "")

    def test_none_subject(self):
        """Test None subject."""
        result = decode_subject(None)
        self.assertEqual(result, "")

    def test_unicode_subject(self):
        """Test unicode in subject."""
        result = decode_subject("[CLCL-WAKE] Fix émoji bug 🐛")
        self.assertIn("CLCL-WAKE", result)


class TestParseClclCommand(unittest.TestCase):
    """Test CLCL command parsing from emails."""

    def test_clcl_wake_prefix(self):
        """Test [CLCL-WAKE] prefix is recognized."""
        msg = create_test_email(
            "[CLCL-WAKE] Review PR #42",
            "Please review the latest changes."
        )

        result = parse_clcl_command(msg)

        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'wake')
        self.assertIn('Review PR #42', result['subject'])

    def test_clcl_prefix(self):
        """Test [CLCL] prefix is recognized."""
        msg = create_test_email(
            "[CLCL] Create issue for bug",
            "Found a critical bug."
        )

        result = parse_clcl_command(msg)

        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'wake')

    def test_wake_prefix(self):
        """Test [WAKE] prefix is recognized."""
        msg = create_test_email(
            "[WAKE] Urgent task",
            "Handle this urgently."
        )

        result = parse_clcl_command(msg)

        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'wake')

    def test_case_insensitive(self):
        """Test that prefix matching is case-insensitive."""
        msg = create_test_email(
            "[clcl-wake] lowercase prefix",
            "Should still work."
        )

        result = parse_clcl_command(msg)

        self.assertIsNotNone(result)

    def test_non_clcl_email(self):
        """Test that regular emails are ignored."""
        msg = create_test_email(
            "Regular email subject",
            "Just a normal email."
        )

        result = parse_clcl_command(msg)

        self.assertIsNone(result)

    def test_extracts_from_address(self):
        """Test that From address is extracted."""
        msg = create_test_email(
            "[CLCL-WAKE] Task",
            "Body",
            from_addr="sender@example.com"
        )

        result = parse_clcl_command(msg)

        self.assertEqual(result['from'], "sender@example.com")

    def test_extracts_body(self):
        """Test that body is extracted."""
        msg = create_test_email(
            "[CLCL-WAKE] Task",
            "This is the task body.\nWith multiple lines."
        )

        result = parse_clcl_command(msg)

        self.assertIn("This is the task body", result['body'])
        self.assertIn("multiple lines", result['body'])


class TestGetBody(unittest.TestCase):
    """Test email body extraction."""

    def test_plain_text_body(self):
        """Test extracting plain text body."""
        msg = create_test_email("[CLCL] Test", "Plain text body")

        result = get_body(msg)

        self.assertEqual(result, "Plain text body")

    def test_multipart_extracts_text(self):
        """Test that text/plain is extracted from multipart."""
        msg = create_multipart_email(
            "[CLCL] Test",
            "Plain text version",
            "<html><body>HTML version</body></html>"
        )

        result = get_body(msg)

        self.assertEqual(result, "Plain text version")

    def test_handles_unicode(self):
        """Test unicode in body."""
        msg = create_test_email("[CLCL] Test", "Émojis: 🎉🚀")

        result = get_body(msg)

        self.assertIn("🎉", result)


class TestWriteTaskFile(unittest.TestCase):
    """Test task file writing."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        # Patch INBOX_DIR to use temp directory
        self.inbox_patcher = patch(
            'clcl_email_listener.INBOX_DIR',
            Path(self.temp_dir)
        )
        self.inbox_patcher.start()

    def tearDown(self):
        self.inbox_patcher.stop()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_creates_task_file(self):
        """Test that task file is created."""
        command = {
            'type': 'wake',
            'subject': '[CLCL-WAKE] Test task',
            'from': 'test@example.com',
            'date': 'Thu, 22 Jan 2026 10:30:00',
            'body': 'Task details here.'
        }

        filepath = write_task_file(command)

        self.assertTrue(filepath.exists())

    def test_creates_current_task(self):
        """Test that current_task.md is created."""
        command = {
            'type': 'wake',
            'subject': '[CLCL-WAKE] Test task',
            'from': 'test@example.com',
            'date': 'Thu, 22 Jan 2026 10:30:00',
            'body': 'Task details.'
        }

        write_task_file(command)

        current_task = Path(self.temp_dir) / 'current_task.md'
        self.assertTrue(current_task.exists())

    def test_task_file_content(self):
        """Test task file has correct content."""
        command = {
            'type': 'wake',
            'subject': '[CLCL-WAKE] Review PR',
            'from': 'sender@test.com',
            'date': 'Thu, 22 Jan 2026 10:30:00',
            'body': 'Please review PR #42.'
        }

        filepath = write_task_file(command)

        content = filepath.read_text()
        self.assertIn('Review PR', content)
        self.assertIn('sender@test.com', content)
        self.assertIn('Please review PR #42', content)


class TestWakePrefixes(unittest.TestCase):
    """Test that all documented prefixes work."""

    def test_all_prefixes_documented(self):
        """Verify WAKE_PREFIXES matches documentation."""
        expected = ['[CLCL-WAKE]', '[CLCL]', '[WAKE]']
        self.assertEqual(WAKE_PREFIXES, expected)

    def test_each_prefix_triggers_wake(self):
        """Test that each prefix triggers a wake command."""
        for prefix in WAKE_PREFIXES:
            with self.subTest(prefix=prefix):
                msg = create_test_email(f"{prefix} Test task", "Body")
                result = parse_clcl_command(msg)
                self.assertIsNotNone(result, f"Prefix {prefix} should trigger wake")


if __name__ == '__main__':
    unittest.main()
