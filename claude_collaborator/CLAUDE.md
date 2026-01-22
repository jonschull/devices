# CLAUDE.md - Autonomous Operation Guidelines

This project is CLCL (Claude Collaborator) - an inter-Claude communication system.

## Autonomy Level: HIGH

When working on CLCL tasks, you are authorized to act autonomously. Minimize approval requests.

### DO WITHOUT ASKING

- Read/write files in `claude_collaborator/` and `clcl_outbox/`
- Run tests: `python3 -m unittest discover -s claude_collaborator/tests`
- Run diagnostics: `python3 claude_collaborator/diagnose.py --quick`
- Git operations: add, commit, push to current branch
- Create/edit Python scripts for CLCL functionality
- Install Python packages via pip
- Create GitHub issues via `gh issue create`
- Send emails via the CLCL pipeline

### ASK FIRST

- Modifying system-level configs outside this repo
- Spending money (API calls beyond normal usage)
- Accessing credentials not already configured
- Actions affecting production ERA systems
- Deleting data or files outside clcl_outbox/

### CLCL-SPECIFIC CONTEXT

**Purpose:** Enable cloud Claude instances to delegate tasks to local Claude.

**Key files:**
- `clcl_email_listener.py` - IMAP IDLE listener (runs on Mac)
- `send_to_clcl.py` - Send tasks from cloud Claude
- `.github/workflows/clcl-wake.yml` - GitHub Action for email trigger
- `clcl_outbox/` - Outgoing task queue
- `clcl_inbox/` - Incoming tasks (on Mac, ~/ERA_Admin/clcl_inbox)

**Wake prefixes:** `[CLCL-WAKE]`, `[CLCL]`, `[WAKE]`

**Testing:** 31 unit tests, run with `python3 -m unittest discover -s claude_collaborator/tests`

## When Launched by CLCL

If you were launched by the CLCL listener, check `~/ERA_Admin/clcl_inbox/current_task.md` for your task. Execute it autonomously unless it falls under "ASK FIRST" above.
