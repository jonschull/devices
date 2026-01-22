#!/usr/bin/env python3
"""
CLCL Unified Listener - Multi-channel message monitoring

Monitors multiple channels for [CLCL] commands:
- Email (IMAP IDLE) - all platforms
- WhatsApp (Playwright) - all platforms
- iMessage (SQLite) - macOS only

Usage:
    python3 clcl_unified_listener.py
    python3 clcl_unified_listener.py --channels email,whatsapp
    python3 clcl_unified_listener.py --list-channels
"""

import asyncio
import os
import sys
import subprocess
import argparse
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Configuration
INBOX_DIR = Path(os.environ.get('CLCL_INBOX_DIR', os.path.expanduser('~/ERA_Admin/clcl_inbox')))
WAKE_PREFIXES = ['[CLCL-WAKE]', '[CLCL]', '[WAKE]']


class CLCLCommand:
    """Represents a parsed CLCL command from any channel."""

    def __init__(self,
                 channel: str,
                 sender: str,
                 subject: str,
                 body: str,
                 timestamp: datetime = None,
                 metadata: Dict[str, Any] = None):
        self.channel = channel
        self.sender = sender
        self.subject = subject
        self.body = body
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}

    def __repr__(self):
        return f"CLCLCommand(channel={self.channel}, sender={self.sender}, subject={self.subject[:30]}...)"


class ChannelListener(ABC):
    """Abstract base class for channel listeners."""

    name: str = "base"
    platforms: List[str] = ["darwin", "linux", "win32"]  # Supported platforms

    @classmethod
    def is_available(cls) -> bool:
        """Check if this channel is available on current platform."""
        return sys.platform in cls.platforms

    @abstractmethod
    async def start(self):
        """Start listening for messages."""
        pass

    @abstractmethod
    async def stop(self):
        """Stop listening."""
        pass

    @abstractmethod
    def check_dependencies(self) -> tuple[bool, str]:
        """Check if dependencies are installed. Returns (ok, message)."""
        pass

    def parse_command(self, text: str) -> Optional[str]:
        """Check if text starts with a CLCL prefix. Returns the prefix or None."""
        text_upper = text.upper().strip()
        for prefix in WAKE_PREFIXES:
            if text_upper.startswith(prefix):
                return prefix
        return None


def write_task_file(command: CLCLCommand) -> Path:
    """Write incoming command to task file for Claude to read."""
    INBOX_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    task_file = INBOX_DIR / f'task_{timestamp}_{command.channel}.md'

    with open(task_file, 'w') as f:
        f.write(f"# Incoming Task\n\n")
        f.write(f"**Channel:** {command.channel}\n")
        f.write(f"**Received:** {command.timestamp.isoformat()}\n")
        f.write(f"**From:** {command.sender}\n")
        f.write(f"**Subject:** {command.subject}\n\n")
        f.write(f"## Task\n\n{command.body}\n")
        if command.metadata:
            f.write(f"\n## Metadata\n\n```json\n{command.metadata}\n```\n")

    # Also write to current_task.md for easy access
    current_task = INBOX_DIR / 'current_task.md'
    with open(current_task, 'w') as f:
        f.write(f"# Current Task ({command.channel})\n\n")
        f.write(f"**From:** {command.sender}\n")
        f.write(f"**Subject:** {command.subject}\n\n")
        f.write(f"## Task\n\n{command.body}\n")

    return task_file


def launch_claude(task_file: Path):
    """Launch Claude Code - cross-platform."""

    print(f"[CLCL] Launching Claude Code...")

    if sys.platform == 'darwin':
        # macOS - use AppleScript
        script = f'''
        tell application "Terminal"
            activate
            do script "cd ~/ERA_Admin && claude 'Check {task_file} for your new task'"
        end tell
        '''
        subprocess.run(['osascript', '-e', script])

    elif sys.platform == 'linux':
        # Linux - try common terminals
        terminals = [
            ['gnome-terminal', '--', 'bash', '-c', f'cd ~/ERA_Admin && claude "Check {task_file}"'],
            ['xterm', '-e', f'cd ~/ERA_Admin && claude "Check {task_file}"'],
            ['konsole', '-e', f'cd ~/ERA_Admin && claude "Check {task_file}"'],
        ]
        for cmd in terminals:
            try:
                subprocess.run(cmd, check=True)
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

    elif sys.platform == 'win32':
        # Windows
        subprocess.run([
            'wt', 'cmd', '/k',
            f'cd %USERPROFILE%\\ERA_Admin && claude "Check {task_file}"'
        ])

    print(f"[CLCL] Claude Code launched")


async def handle_command(command: CLCLCommand):
    """Process a CLCL command from any channel."""
    print(f"\n[CLCL] ========================================")
    print(f"[CLCL] WAKE COMMAND RECEIVED")
    print(f"[CLCL] Channel: {command.channel}")
    print(f"[CLCL] From: {command.sender}")
    print(f"[CLCL] Subject: {command.subject}")
    print(f"[CLCL] ========================================\n")

    task_file = write_task_file(command)
    print(f"[CLCL] Task written to: {task_file}")

    launch_claude(task_file)


class UnifiedListener:
    """Coordinates multiple channel listeners."""

    def __init__(self, channels: List[str] = None):
        self.listeners: List[ChannelListener] = []
        self.running = False

        # Import available listeners
        available = self._get_available_listeners()

        if channels:
            # Use specified channels
            for name in channels:
                if name in available:
                    self.listeners.append(available[name]())
                else:
                    print(f"[CLCL] Warning: Channel '{name}' not available")
        else:
            # Use all available channels
            for name, cls in available.items():
                self.listeners.append(cls())

    def _get_available_listeners(self) -> Dict[str, type]:
        """Get all available listener classes for this platform."""
        from clcl_email_listener import EmailChannelListener
        from clcl_whatsapp_listener import WhatsAppChannelListener

        available = {}

        # Email - always available
        available['email'] = EmailChannelListener

        # WhatsApp - always available (Playwright is cross-platform)
        available['whatsapp'] = WhatsAppChannelListener

        # iMessage - macOS only
        if sys.platform == 'darwin':
            from clcl_imessage_listener import iMessageChannelListener
            available['imessage'] = iMessageChannelListener

        return available

    def check_dependencies(self):
        """Check all listener dependencies."""
        print("[CLCL] Checking dependencies...\n")
        all_ok = True

        for listener in self.listeners:
            ok, msg = listener.check_dependencies()
            status = "✓" if ok else "✗"
            print(f"  {status} {listener.name}: {msg}")
            if not ok:
                all_ok = False

        print()
        return all_ok

    async def start(self):
        """Start all listeners."""
        if not self.listeners:
            print("[CLCL] No listeners configured")
            return

        print(f"[CLCL] Starting {len(self.listeners)} channel(s)...")
        for listener in self.listeners:
            print(f"  - {listener.name}")
        print()

        self.running = True

        # Start all listeners concurrently
        tasks = [listener.start() for listener in self.listeners]
        await asyncio.gather(*tasks)

    async def stop(self):
        """Stop all listeners."""
        self.running = False
        for listener in self.listeners:
            await listener.stop()


def list_channels():
    """List all available channels."""
    print("Available channels:\n")

    channels = [
        ("email", "Email via IMAP IDLE", ["darwin", "linux", "win32"]),
        ("whatsapp", "WhatsApp via Playwright", ["darwin", "linux", "win32"]),
        ("imessage", "iMessage via SQLite", ["darwin"]),
    ]

    for name, desc, platforms in channels:
        available = sys.platform in platforms
        status = "✓" if available else "✗"
        platform_str = ", ".join(platforms)
        print(f"  {status} {name:12} - {desc} ({platform_str})")

    print(f"\nCurrent platform: {sys.platform}")


def main():
    parser = argparse.ArgumentParser(description='CLCL Unified Listener')
    parser.add_argument('--channels', '-c',
                        help='Comma-separated list of channels (email,whatsapp,imessage)')
    parser.add_argument('--list-channels', '-l', action='store_true',
                        help='List available channels')
    parser.add_argument('--check', action='store_true',
                        help='Check dependencies without starting')
    args = parser.parse_args()

    if args.list_channels:
        list_channels()
        return

    channels = args.channels.split(',') if args.channels else None
    listener = UnifiedListener(channels)

    if args.check:
        listener.check_dependencies()
        return

    print("[CLCL] Claude Collaborator Unified Listener")
    print(f"[CLCL] Platform: {sys.platform}")
    print(f"[CLCL] Inbox: {INBOX_DIR}")
    print()

    if not listener.check_dependencies():
        print("[CLCL] Some dependencies missing. Install them and retry.")
        sys.exit(1)

    try:
        asyncio.run(listener.start())
    except KeyboardInterrupt:
        print("\n[CLCL] Shutting down...")
        asyncio.run(listener.stop())


if __name__ == '__main__':
    main()
