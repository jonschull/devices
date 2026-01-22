#!/usr/bin/env python3
"""
clcl_email_listener.py - Push-based email listener for Claude Collaborator

Uses IMAP IDLE to receive immediate notification when emails arrive.
No polling - holds connection open and wakes on new mail.

Usage:
    python3 clcl_email_listener.py

Environment Variables:
    CLCL_EMAIL: Email address to monitor (default: claude@ecorestorationalliance.org)
    CLCL_APP_PASSWORD: Google App Password for authentication
    CLCL_INBOX_DIR: Directory to write incoming tasks (default: ~/ERA_Admin/clcl_inbox)
"""

import email
import os
import sys
import time
import subprocess
from datetime import datetime
from email.header import decode_header
from pathlib import Path

try:
    from imapclient import IMAPClient
except ImportError:
    print("Error: imapclient not installed. Run: pip install imapclient")
    sys.exit(1)


# Configuration
IMAP_HOST = 'imap.gmail.com'
EMAIL = os.environ.get('CLCL_EMAIL', 'claude@ecorestorationalliance.org')
APP_PASSWORD = os.environ.get('CLCL_APP_PASSWORD', '')
INBOX_DIR = Path(os.environ.get('CLCL_INBOX_DIR', os.path.expanduser('~/ERA_Admin/clcl_inbox')))
IDLE_TIMEOUT = 29 * 60  # Gmail drops IDLE after ~29 min, reconnect before that

# Command prefixes that trigger CLCL
WAKE_PREFIXES = ['[CLCL-WAKE]', '[CLCL]', '[WAKE]']


def decode_subject(subject):
    """Decode email subject, handling encoded headers."""
    if not subject:
        return ''
    decoded, encoding = decode_header(subject)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(encoding or 'utf-8', errors='ignore')
    return decoded


def get_body(msg):
    """Extract plain text body from email."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode('utf-8', errors='ignore')
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode('utf-8', errors='ignore')
    return ''


def parse_clcl_command(msg):
    """Extract CLCL command from email if present."""
    subject = decode_subject(msg.get('Subject', ''))

    # Check for CLCL wake command prefixes
    for prefix in WAKE_PREFIXES:
        if subject.upper().startswith(prefix):
            return {
                'type': 'wake',
                'subject': subject,
                'from': msg.get('From', 'unknown'),
                'to': msg.get('To', ''),
                'date': msg.get('Date', ''),
                'body': get_body(msg),
                'message_id': msg.get('Message-ID', '')
            }
    return None


def write_task_file(command):
    """Write incoming command to task file for Claude to read."""
    INBOX_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    task_file = INBOX_DIR / f'task_{timestamp}.md'

    with open(task_file, 'w') as f:
        f.write(f"# Incoming Task\n\n")
        f.write(f"**Received:** {datetime.now().isoformat()}\n")
        f.write(f"**From:** {command['from']}\n")
        f.write(f"**Subject:** {command['subject']}\n")
        f.write(f"**Date:** {command['date']}\n\n")
        f.write(f"## Task\n\n{command['body']}\n")

    # Also write to current_task.md for easy access
    current_task = INBOX_DIR / 'current_task.md'
    with open(current_task, 'w') as f:
        f.write(f"# Current Task\n\n")
        f.write(f"**Received:** {datetime.now().isoformat()}\n")
        f.write(f"**From:** {command['from']}\n")
        f.write(f"**Subject:** {command['subject']}\n\n")
        f.write(f"## Task\n\n{command['body']}\n")

    return task_file


def launch_claude():
    """Launch Claude Code via AppleScript (macOS only)."""
    if sys.platform != 'darwin':
        print("[CLCL] Not on macOS, skipping AppleScript launch")
        return False

    applescript = '''
    tell application "Terminal"
        activate
        do script "cd ~/ERA_Admin && claude 'Check clcl_inbox/current_task.md for your new task from email'"
    end tell
    '''

    try:
        subprocess.run(['osascript', '-e', applescript], check=True)
        print("[CLCL] Launched Claude Code in Terminal")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[CLCL] Failed to launch Claude: {e}")
        return False


def handle_command(command):
    """Process a CLCL command - write to inbox and launch Claude."""
    print(f"\n[CLCL] ========================================")
    print(f"[CLCL] WAKE COMMAND RECEIVED")
    print(f"[CLCL] From: {command['from']}")
    print(f"[CLCL] Subject: {command['subject']}")
    print(f"[CLCL] ========================================\n")

    # Write task to inbox
    task_file = write_task_file(command)
    print(f"[CLCL] Task written to: {task_file}")

    # Launch Claude Code
    launch_claude()


def listen():
    """Main IDLE loop - runs forever, reconnecting as needed."""
    if not APP_PASSWORD:
        print("[CLCL] ERROR: CLCL_APP_PASSWORD environment variable not set")
        print("[CLCL] Generate an App Password at: Google Account -> Security -> App Passwords")
        sys.exit(1)

    print(f"[CLCL] Claude Collaborator Email Listener")
    print(f"[CLCL] Monitoring: {EMAIL}")
    print(f"[CLCL] Inbox dir: {INBOX_DIR}")
    print(f"[CLCL] Wake prefixes: {WAKE_PREFIXES}")
    print()

    while True:
        try:
            print(f"[CLCL] Connecting to {IMAP_HOST}...")

            with IMAPClient(IMAP_HOST, ssl=True) as client:
                client.login(EMAIL, APP_PASSWORD)
                client.select_folder('INBOX')

                print("[CLCL] Connected. Entering IDLE mode (push-based, not polling)...")
                print("[CLCL] Waiting for emails...\n")

                while True:
                    # Enter IDLE mode - blocks until new mail or timeout
                    client.idle()

                    # Wait for response (new mail or timeout)
                    responses = client.idle_check(timeout=IDLE_TIMEOUT)
                    client.idle_done()

                    if responses:
                        print(f"[CLCL] Activity detected: {responses}")

                        # Fetch new/unseen messages
                        messages = client.search(['UNSEEN'])

                        for uid in messages:
                            raw = client.fetch([uid], ['RFC822'])[uid][b'RFC822']
                            msg = email.message_from_bytes(raw)

                            command = parse_clcl_command(msg)
                            if command:
                                handle_command(command)
                                # Mark as seen
                                client.set_flags([uid], ['\\Seen'])
                            else:
                                subject = decode_subject(msg.get('Subject', ''))
                                print(f"[CLCL] Ignoring non-CLCL email: {subject[:50]}")
                    else:
                        # Timeout - re-enter IDLE (keeps connection alive)
                        print(f"[CLCL] IDLE refresh at {datetime.now().strftime('%H:%M:%S')}")

        except KeyboardInterrupt:
            print("\n[CLCL] Shutting down...")
            break
        except Exception as e:
            print(f"[CLCL] Connection error: {e}")
            print("[CLCL] Reconnecting in 10 seconds...")
            time.sleep(10)


if __name__ == '__main__':
    listen()
