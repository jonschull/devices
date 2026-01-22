# Claude Collaborator (CLCL) - Email Listener

Push-based email listener that enables cloud Claude instances to wake up and communicate with a local CLCL instance.

## How It Works

```
Cloud Claude → sends email → Gmail → IMAP IDLE push → clcl_email_listener.py → launches Claude Code
```

1. **Cloud Claude** sends email to `claude@ecorestorationalliance.org` with subject starting with `[CLCL-WAKE]`
2. **Gmail** receives the email
3. **IMAP IDLE** (push, not polling) immediately notifies the listener
4. **clcl_email_listener.py** parses the command and writes to `clcl_inbox/`
5. **AppleScript** launches Claude Code in Terminal with the task

**Latency:** ~1-3 seconds (push-based, not polling)

## Setup

### 1. Install Dependencies

```bash
pip install imapclient
```

### 2. Generate Google App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Factor Authentication if not already
3. Go to "App Passwords"
4. Generate a new password for "Mail"
5. Copy the 16-character password

### 3. Create Inbox Directory

```bash
mkdir -p ~/ERA_Admin/clcl_inbox
```

### 4. Test Manually

```bash
export CLCL_EMAIL="claude@ecorestorationalliance.org"
export CLCL_APP_PASSWORD="your-16-char-app-password"
export CLCL_INBOX_DIR="$HOME/ERA_Admin/clcl_inbox"

python3 clcl_email_listener.py
```

### 5. Install as launchd Service

```bash
# Edit the plist to add your App Password
nano com.era.clcl-listener.plist

# Copy to LaunchAgents
cp com.era.clcl-listener.plist ~/Library/LaunchAgents/

# Load the service
launchctl load ~/Library/LaunchAgents/com.era.clcl-listener.plist

# Check status
launchctl list | grep clcl
```

## Usage

### Sending a Wake Command

From any Claude instance (or any email client):

```
To: claude@ecorestorationalliance.org
Subject: [CLCL-WAKE] Review the latest PR
Body: Please review PR #42 in the ERA_Admin repo and provide feedback.
```

Valid subject prefixes:
- `[CLCL-WAKE]`
- `[CLCL]`
- `[WAKE]`

### Task Files

Incoming tasks are written to:
- `clcl_inbox/current_task.md` - Always contains the latest task
- `clcl_inbox/task_YYYYMMDD_HHMMSS.md` - Archived copy with timestamp

## Logs

```bash
# View live logs
tail -f ~/ERA_Admin/claude_collaborator/clcl_listener.log

# View errors
tail -f ~/ERA_Admin/claude_collaborator/clcl_listener_error.log
```

## Managing the Service

```bash
# Stop
launchctl unload ~/Library/LaunchAgents/com.era.clcl-listener.plist

# Start
launchctl load ~/Library/LaunchAgents/com.era.clcl-listener.plist

# Restart
launchctl unload ~/Library/LaunchAgents/com.era.clcl-listener.plist && \
launchctl load ~/Library/LaunchAgents/com.era.clcl-listener.plist
```

## Security Notes

- **App Password**: Never commit your App Password to git. The plist contains a placeholder.
- **Email Scope**: Only emails with specific prefixes trigger actions
- **Local Only**: Commands only launch Claude Code on the local Mac

## Architecture

```
┌─────────────────┐     email      ┌─────────────┐
│  Cloud Claude   │ ──────────────▶│    Gmail    │
│  (ephemeral)    │  [CLCL-WAKE]   │             │
└─────────────────┘                └──────┬──────┘
                                          │
                                    IMAP IDLE
                                    (push, ~1-3s)
                                          │
                                          ▼
                                   ┌──────────────┐
                                   │ clcl_email_  │
                                   │ listener.py  │
                                   └──────┬───────┘
                                          │
                              ┌───────────┴───────────┐
                              │                       │
                              ▼                       ▼
                     ┌────────────────┐     ┌─────────────────┐
                     │  clcl_inbox/   │     │   AppleScript   │
                     │ current_task.md│     │ launches Claude │
                     └────────────────┘     └─────────────────┘
```

## Related

- [Issue #173](https://github.com/jonschull/ERA_Admin/issues/173) - Claude Collaborator feature request
- [ERA_Admin](https://github.com/jonschull/ERA_Admin) - Parent project
