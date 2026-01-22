# CLCL Quick Start

**Total time: ~10 minutes**

---

## Step 1: On Your Mac (5 min)

```bash
cd ~/ERA_Admin  # or wherever you clone this
git clone <this-repo>
cd claude_collaborator
chmod +x setup.sh
./setup.sh
```

The script will:
- Install `imapclient`
- Create directories
- Ask for your Google App Password
- Start the listener

---

## Step 2: GitHub Secrets (3 min)

Go to your repo → Settings → Secrets → Actions

Add these two secrets:

| Name | Value |
|------|-------|
| `CLCL_SMTP_USERNAME` | Your Gmail address |
| `CLCL_SMTP_PASSWORD` | App password for that Gmail |

---

## Step 3: Test It (2 min)

Send an email to `claude@ecorestorationalliance.org`:

```
Subject: [CLCL-WAKE] Test from Jon
Body: Just testing the wake-up system
```

Your Mac should:
1. Receive the email instantly (IMAP IDLE)
2. Open Terminal
3. Launch Claude Code with the task

---

## Done!

Now any cloud Claude can wake your local Claude by:

1. Writing to `clcl_outbox/task_*.json`
2. Git push
3. GitHub Action sends email
4. Your Mac wakes up

---

## Troubleshooting

```bash
# Check if listener is running
launchctl list | grep clcl

# View logs
tail -f ~/ERA_Admin/claude_collaborator/clcl_listener.log

# Restart listener
launchctl unload ~/Library/LaunchAgents/com.era.clcl-listener.plist
launchctl load ~/Library/LaunchAgents/com.era.clcl-listener.plist

# Run diagnostics
python3 claude_collaborator/diagnose.py
```
