#!/usr/bin/env python3
"""
diagnose.py - CLCL System Diagnostics

Checks the health and configuration of the CLCL system.
Run this to verify setup before deploying.

Usage:
    python3 diagnose.py           # Run all checks
    python3 diagnose.py --quick   # Skip slow network tests
    python3 diagnose.py --fix     # Attempt to fix issues
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def ok(msg):
    print(f"  {GREEN}✓{RESET} {msg}")


def fail(msg):
    print(f"  {RED}✗{RESET} {msg}")


def warn(msg):
    print(f"  {YELLOW}!{RESET} {msg}")


def info(msg):
    print(f"  {BLUE}ℹ{RESET} {msg}")


def header(msg):
    print(f"\n{BOLD}{msg}{RESET}")


class DiagnosticResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def add_pass(self):
        self.passed += 1

    def add_fail(self):
        self.failed += 1

    def add_warn(self):
        self.warnings += 1

    def summary(self):
        total = self.passed + self.failed
        status = "PASS" if self.failed == 0 else "FAIL"
        color = GREEN if self.failed == 0 else RED
        print(f"\n{BOLD}Results:{RESET} {self.passed}/{total} checks passed", end="")
        if self.warnings:
            print(f", {self.warnings} warnings", end="")
        print(f" [{color}{status}{RESET}]")
        return self.failed == 0


def check_python_version(results):
    """Check Python version."""
    header("Python Environment")

    version = sys.version_info
    if version >= (3, 8):
        ok(f"Python {version.major}.{version.minor}.{version.micro}")
        results.add_pass()
    else:
        fail(f"Python {version.major}.{version.minor} (need 3.8+)")
        results.add_fail()


def check_dependencies(results):
    """Check required Python packages."""
    header("Dependencies")

    packages = {
        'imapclient': 'Required for IMAP IDLE listener',
    }

    for package, description in packages.items():
        try:
            __import__(package)
            ok(f"{package} - {description}")
            results.add_pass()
        except ImportError:
            fail(f"{package} - {description}")
            info(f"  Install with: pip install {package}")
            results.add_fail()


def check_file_structure(results):
    """Check that required files exist."""
    header("File Structure")

    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    required_files = [
        (script_dir / 'clcl_email_listener.py', 'Email listener script'),
        (script_dir / 'send_to_clcl.py', 'Send helper script'),
        (script_dir / 'com.era.clcl-listener.plist', 'launchd config'),
        (repo_root / '.github' / 'workflows' / 'clcl-wake.yml', 'GitHub Action'),
        (repo_root / 'clcl_outbox', 'Outbox directory'),
    ]

    for filepath, description in required_files:
        if filepath.exists():
            ok(f"{filepath.name} - {description}")
            results.add_pass()
        else:
            fail(f"{filepath.name} - {description}")
            results.add_fail()


def check_environment_variables(results):
    """Check environment variables."""
    header("Environment Variables")

    env_vars = {
        'CLCL_EMAIL': ('Email to monitor', 'claude@ecorestorationalliance.org'),
        'CLCL_APP_PASSWORD': ('Google App Password', None),
        'CLCL_INBOX_DIR': ('Inbox directory', '~/ERA_Admin/clcl_inbox'),
    }

    for var, (description, default) in env_vars.items():
        value = os.environ.get(var)
        if value:
            # Mask password
            display_value = '****' if 'PASSWORD' in var else value
            ok(f"{var}={display_value}")
            results.add_pass()
        elif default:
            warn(f"{var} not set (default: {default})")
            results.add_warn()
        else:
            fail(f"{var} not set - {description}")
            results.add_fail()


def check_git_status(results):
    """Check git repository status."""
    header("Git Repository")

    try:
        # Check if in a git repo
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            ok("Git repository detected")
            results.add_pass()
        else:
            fail("Not in a git repository")
            results.add_fail()
            return

        # Check current branch
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True, text=True
        )
        branch = result.stdout.strip()
        ok(f"Current branch: {branch}")
        results.add_pass()

        # Check remote
        result = subprocess.run(
            ['git', 'remote', '-v'],
            capture_output=True, text=True
        )
        if 'origin' in result.stdout:
            ok("Remote 'origin' configured")
            results.add_pass()
        else:
            warn("No 'origin' remote configured")
            results.add_warn()

    except FileNotFoundError:
        fail("git command not found")
        results.add_fail()


def check_github_action_syntax(results):
    """Validate GitHub Action YAML syntax."""
    header("GitHub Action Validation")

    script_dir = Path(__file__).parent
    workflow_file = script_dir.parent / '.github' / 'workflows' / 'clcl-wake.yml'

    if not workflow_file.exists():
        fail("Workflow file not found")
        results.add_fail()
        return

    try:
        import yaml
        with open(workflow_file) as f:
            workflow = yaml.safe_load(f)

        # Check required keys
        # Note: YAML parses 'on:' as boolean True
        if 'on' in workflow or True in workflow:
            ok("Trigger configuration present")
            results.add_pass()
        else:
            fail("Missing 'on' trigger configuration")
            results.add_fail()

        if 'jobs' in workflow:
            ok("Jobs configuration present")
            results.add_pass()
        else:
            fail("Missing 'jobs' configuration")
            results.add_fail()

        # Check for secrets usage
        content = workflow_file.read_text()
        if 'secrets.CLCL_SMTP' in content:
            ok("SMTP secrets referenced")
            results.add_pass()
        else:
            warn("SMTP secrets not found in workflow")
            results.add_warn()

    except ImportError:
        warn("PyYAML not installed, skipping YAML validation")
        info("Install with: pip install pyyaml")
        results.add_warn()
    except Exception as e:
        fail(f"YAML parse error: {e}")
        results.add_fail()


def check_imap_connectivity(results, quick=False):
    """Test IMAP connection (skipped in quick mode)."""
    header("IMAP Connectivity")

    if quick:
        info("Skipped in quick mode (use --full for network tests)")
        return

    email_addr = os.environ.get('CLCL_EMAIL')
    password = os.environ.get('CLCL_APP_PASSWORD')

    if not email_addr or not password:
        warn("Credentials not set, skipping IMAP test")
        results.add_warn()
        return

    try:
        from imapclient import IMAPClient

        info("Connecting to imap.gmail.com...")
        with IMAPClient('imap.gmail.com', ssl=True, timeout=10) as client:
            client.login(email_addr, password)
            ok("IMAP login successful")
            results.add_pass()

            client.select_folder('INBOX')
            ok("INBOX selected")
            results.add_pass()

            # Check IDLE capability
            capabilities = client.capabilities()
            if b'IDLE' in capabilities:
                ok("IDLE capability supported")
                results.add_pass()
            else:
                fail("IDLE capability not supported")
                results.add_fail()

    except ImportError:
        fail("imapclient not installed")
        results.add_fail()
    except Exception as e:
        fail(f"IMAP connection failed: {e}")
        results.add_fail()


def check_macos_specific(results):
    """Check macOS-specific components."""
    header("macOS Components")

    if sys.platform != 'darwin':
        info("Not on macOS, skipping platform-specific checks")
        return

    # Check launchd
    try:
        result = subprocess.run(
            ['launchctl', 'list'],
            capture_output=True, text=True
        )
        if 'clcl' in result.stdout.lower():
            ok("CLCL service is loaded")
            results.add_pass()
        else:
            warn("CLCL service not loaded")
            info("Load with: launchctl load ~/Library/LaunchAgents/com.era.clcl-listener.plist")
            results.add_warn()
    except FileNotFoundError:
        info("launchctl not available")

    # Check if plist is in LaunchAgents
    plist_path = Path.home() / 'Library' / 'LaunchAgents' / 'com.era.clcl-listener.plist'
    if plist_path.exists():
        ok("plist installed in LaunchAgents")
        results.add_pass()
    else:
        warn("plist not installed in LaunchAgents")
        results.add_warn()


def run_unit_tests(results):
    """Run unit tests."""
    header("Unit Tests")

    script_dir = Path(__file__).parent
    test_dir = script_dir / 'tests'

    if not test_dir.exists():
        warn("Test directory not found")
        results.add_warn()
        return

    # Try unittest (always available)
    result = subprocess.run(
        [sys.executable, '-m', 'unittest', 'discover', '-s', str(test_dir), '-v'],
        capture_output=True, text=True,
        cwd=str(script_dir)
    )

    if result.returncode == 0:
        # Count tests from output
        import re
        match = re.search(r'Ran (\d+) tests?', result.stderr)
        test_count = match.group(1) if match else '?'
        ok(f"All {test_count} unit tests passed")
        results.add_pass()
    else:
        fail("Some unit tests failed")
        print(result.stderr)
        results.add_fail()


def main():
    parser = argparse.ArgumentParser(description='CLCL System Diagnostics')
    parser.add_argument('--quick', '-q', action='store_true',
                        help='Skip slow network tests')
    parser.add_argument('--fix', '-f', action='store_true',
                        help='Attempt to fix issues (not yet implemented)')
    args = parser.parse_args()

    print(f"{BOLD}CLCL System Diagnostics{RESET}")
    print("=" * 40)

    results = DiagnosticResults()

    check_python_version(results)
    check_dependencies(results)
    check_file_structure(results)
    check_environment_variables(results)
    check_git_status(results)
    check_github_action_syntax(results)
    check_imap_connectivity(results, quick=args.quick)
    check_macos_specific(results)
    run_unit_tests(results)

    success = results.summary()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
