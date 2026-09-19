from pathlib import Path
from datetime import datetime
import subprocess
import re

root = Path.home() / "MMK"
daily = root / "automation" / "daily"
out = daily / "TODAY.md"
state_file = daily / "PROJECT-STATE.md"
queue_file = daily / "TASK-QUEUE.md"

state = state_file.read_text().strip()
queue = queue_file.read_text().splitlines()

def git(cmd):
    return subprocess.getoutput("cd " + str(root) + " && " + cmd)

active = []
task = {}

for line in queue:
    if line.startswith("### Task "):
        if task:
            active.append(task)
        task = {"number": line.replace("### Task ", "").strip()}
    elif line.startswith("Name: "):
        task["name"] = line[6:]
    elif line.startswith("Priority: "):
        task["priority"] = line[10:]
    elif line.startswith("Status: "):
        task["status"] = line[8:]
    elif line.startswith("Area: "):
        task["area"] = line[6:]
    elif line.startswith("Next: "):
        task["next"] = line[6:]
    elif line.startswith("Test: "):
        task["test"] = line[6:]

if task:
    active.append(task)

selected = next(
    (t for t in active if t.get("status") == "ACTIVE"),
    None
)

now = datetime.now()
changes = git("git status --short") or "Clean working tree."

if selected:
    today_task = f"""### {selected["name"]}

Priority: {selected["priority"]}
Area: {selected["area"]}
Next action: {selected["next"]}
Required test: {selected["test"]}"""
else:
    today_task = "No ACTIVE task found."

content = f"""# MMK DAILY WORK PLAN

Date: {now:%Y-%m-%d}
Generated: {now:%H:%M}

## ACTIVE PROJECT STATE

{state}

## SELECTED TASK

{today_task}

## GIT STATE

Branch: {git("git branch --show-current")}

Latest commit: {git("git log -1 --oneline")}

Current changes:

{changes}

## TODAY

- [ ] Complete the selected task
- [ ] Run the required test
- [ ] Save and document the result
- [ ] Create focused Git commit
- [ ] Push completed commit to GitHub
- [ ] Record checkpoint

## WHAT SHOULD WAIT

- WhatsApp automation
- Large AI automation
- New unrelated products
- Major business-system expansion

## END-OF-DAY CHECKPOINT

Main task completed:

Tests completed:

Problems found:

Files changed:

Commit:

GitHub push:

Next action:
"""

out.write_text(content)
print("MMK DAILY PLANNER v1.1 UPDATED")
print("SELECTED:", selected["name"] if selected else "NONE")