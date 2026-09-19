from pathlib import Path
from datetime import datetime
import re
import subprocess

root = Path.home() / "MMK"
daily = root / "automation" / "daily"

queue_file = daily / "TASK-QUEUE.md"
state_file = daily / "PROJECT-STATE.md"
today_file = daily / "TODAY.md"
checkpoint_file = daily / "CHECKPOINT.md"
planner_file = daily / "generate_today.py"


def clean(value):
    return value.strip()


queue = queue_file.read_text()
today = today_file.read_text()

task_name = "Unknown"

for line in today.splitlines():
    if line.startswith("### "):
        task_name = line[4:].strip()
        break

if task_name == "Unknown":
    raise SystemExit("ERROR: No selected task found in TODAY.md.")

pattern = (
    r"(### Task \d+\n"
    r"Name: " + re.escape(task_name) +
    r"\nPriority: [^\n]+\n"
    r"Status: )ACTIVE"
)

updated_queue, count = re.subn(
    pattern,
    r"\1COMPLETED",
    queue,
    count=1
)

if count != 1:
    raise SystemExit(
        f"ERROR: ACTIVE task '{task_name}' was not found in TASK-QUEUE.md."
    )

# Promote the next WAITING task to ACTIVE.
promoted_queue, promoted = re.subn(
    r"(### Task \d+\nName: [^\n]+\nPriority: [^\n]+\nStatus: )WAITING",
    r"\1ACTIVE",
    updated_queue,
    count=1
)

if promoted != 1:
    raise SystemExit("ERROR: No next WAITING task available to activate.")

queue_file.write_text(promoted_queue)

state = state_file.read_text()

state = state.replace(
    "## Version\n\nv1.3",
    "## Version\n\nv1.5",
    1
)

state = state.replace(
    "## Current Task\n\nBuild reliable completion recording for the daily checkpoint system.",
    "## Current Task\n\nMaintain daily completion recording and task-state synchronization.",
    1
)

state = state.replace(
    "## Next Task\n\nBuild reliable completion recording.",
    "## Next Task\n\nBuild weekly review system.",
    1
)

state_file.write_text(state)

subprocess.run(
    ["python", str(planner_file)],
    cwd=root,
    check=True
)

now = datetime.now()

checkpoint = f"""# MMK DAILY CHECKPOINT

Date: {now:%Y-%m-%d}
Generated: {now:%H:%M}

## MAIN TASK

Task: {task_name}

Status: COMPLETED

## COMPLETION RECORDED

The selected ACTIVE task was marked COMPLETED in TASK-QUEUE.md.

## PROJECT STATE

PROJECT-STATE.md advanced to v1.5.

## NEXT ACTION

Build weekly review system.

## FILES UPDATED

- automation/daily/TASK-QUEUE.md
- automation/daily/PROJECT-STATE.md
- automation/daily/TODAY.md
- automation/daily/CHECKPOINT.md
"""

checkpoint_file.write_text(checkpoint)

print("================================")
print("MMK TASK COMPLETION RECORDER v1.5")
print("================================")
print("COMPLETED:", task_name)
print("TASK QUEUE: UPDATED")
print("PROJECT STATE: UPDATED")
print("CHECKPOINT: SAVED")
print("================================")
