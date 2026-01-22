# Claude Collaborator (CLCL)

**Inter-Claude communication system** that enables cloud Claude instances (sandboxed VMs) to delegate tasks to a local CLCL instance (full system access).

## Why This Exists

Cloud Claudes run in restricted VMs:
- No email sending
- No `gh` CLI
- No local file access
- No API credentials

CLCL runs on your Mac with full access. This system lets cloud Claudes **delegate tasks** to CLCL through a controlled channel.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CLOUD CLAUDE → CLCL                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐     git push      ┌──────────────────┐                │
│  │  Cloud Claude   │ ───────────────▶  │  GitHub Actions  │                │
│  │  (sandboxed VM) │  clcl_outbox/     │                  │                │
│  └─────────────────┘                   └────────┬─────────┘                │
│                                                 │                           │
│                                           sends email                       │
│                                        [CLCL-WAKE] ...                      │
│                                                 │                           │
│                                                 ▼                           │
│                                        ┌──────────────┐                    │
│                                        │    Gmail     │                    │
│                                        │   (inbox)    │                    │
│                                        └──────┬───────┘                    │
│                                               │                             │
│                                         IMAP IDLE                           │
│                                        (push, ~1-3s)                        │
│                                               │                             │
│                                               ▼                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        YOUR MAC                                      │   │
│  │  ┌──────────────────┐      ┌─────────────┐      ┌────────────────┐  │   │
│  │  │ clcl_email_      │ ───▶ │ clcl_inbox/ │ ───▶ │  Claude Code   │  │   │
│  │  │ listener.py      │      │             │      │  (launched)    │  │   │
│  │  │ (launchd svc)    │      └─────────────┘      └────────────────┘  │   │
│  │  └──────────────────┘                                                │   │
│  │                                                                      │   │
│  │  CLCL can now:                                                       │   │
│  │  • Send emails          • Run gh CLI        • Access local files    │   │
│  │  • Use Airtable API     • Run Fathom        • Browser automation    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Components

| File | Purpose |
|------|---------|
| `clcl_email_listener.py` | IMAP IDLE listener (runs on Mac) |
| `send_to_clcl.py` | Helper for cloud Claudes to send tasks |
| `com.era.clcl-listener.plist` | launchd config for persistent service |
| `.github/workflows/clcl-wake.yml` | GitHub Action that sends wake emails |
| `clcl_outbox/` | Where cloud Claudes drop task files |
| `clcl_inbox/` | Where CLCL receives tasks (on Mac) |

## Setup

### Part 1: GitHub Action (enables cloud Claudes to trigger CLCL)

Add these secrets to your GitHub repo (Settings → Secrets → Actions):

| Secret | Value |
|--------|-------|
| `CLCL_SMTP_USERNAME` | Email to send from (e.g., `your-email@gmail.com`) |
| `CLCL_SMTP_PASSWORD` | App password for that email |

### Part 2: CLCL Listener (runs on your Mac)

```bash
# 1. Install dependency
pip install imapclient

# 2. Create directories
mkdir -p ~/ERA_Admin/clcl_inbox

# 3. Generate App Password for claude@ecorestorationalliance.org
#    Google Account → Security → App Passwords

# 4. Test manually
export CLCL_EMAIL="claude@ecorestorationalliance.org"
export CLCL_APP_PASSWORD="your-16-char-app-password"
python3 clcl_email_listener.py

# 5. Install as service
# Edit com.era.clcl-listener.plist with your App Password
cp com.era.clcl-listener.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.era.clcl-listener.plist
```

## Usage

### From a Cloud Claude

**Option A: Use the helper script**
```bash
python3 claude_collaborator/send_to_clcl.py "Create GitHub issue for the bug we discussed"
python3 claude_collaborator/send_to_clcl.py --urgent "Production alert - check logs"
```

**Option B: Manual (if helper not available)**
```bash
# Create task file
cat > clcl_outbox/task_$(date +%Y%m%d_%H%M%S).json << 'EOF'
{
  "task": "Create GitHub issue #174 for CLCL architecture",
  "priority": "normal",
  "from": "cloud-claude",
  "context": "Discussed in session, needs tracking"
}
EOF

# Commit and push
git add clcl_outbox/
git commit -m "[CLCL-WAKE] Create GitHub issue"
git push
```

**What happens:**
1. Push triggers GitHub Action
2. Action emails `claude@ecorestorationalliance.org`
3. CLCL listener receives (IMAP IDLE, ~1-3s)
4. Claude Code launches with the task

### Capability Delegation

| Cloud Claude can't... | ...but can ask CLCL to: |
|----------------------|-------------------------|
| Send email | Send via Gmail |
| Create GitHub issues | Run `gh issue create` |
| Access Airtable | Run ERA integration scripts |
| Read local files | Access `~/ERA_Admin/*` |
| Run browser automation | Use Playwright with sessions |

## Security Model

**You control the boundaries:**

1. **You decide** what credentials CLCL has access to
2. **Email prefix filter** - only `[CLCL-WAKE]`, `[CLCL]`, `[WAKE]` trigger
3. **CLCL follows AI_HANDOFF_GUIDE** - asks permission for sensitive actions
4. **Audit trail** - every task logged in email + task files
5. **Kill switch** - stop launchd service anytime

This is **delegation with human-controlled permissions**, not privilege escalation.

## Logs & Debugging

```bash
# View listener logs
tail -f ~/ERA_Admin/claude_collaborator/clcl_listener.log

# Check service status
launchctl list | grep clcl

# View GitHub Action runs
# Go to: https://github.com/YOUR_REPO/actions
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

## Related

- [Issue #173](https://github.com/jonschull/ERA_Admin/issues/173) - Claude Collaborator feature request
- [ERA_Admin](https://github.com/jonschull/ERA_Admin) - Parent project
- [AI_HANDOFF_GUIDE.md](https://github.com/jonschull/ERA_Admin/blob/main/AI_HANDOFF_GUIDE.md) - AI collaboration protocols
