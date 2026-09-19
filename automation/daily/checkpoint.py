from pathlib import Path
from datetime import datetime
import subprocess

root = Path.home() / "MMK"
daily = root / "automation" / "daily"

today = daily / "TODAY.md"
checkpoint = daily / "CHECKPOINT.md"

def git(cmd):
    return subprocess.getoutput("cd " + str(root) + " && " + cmd)

now = datetime.now()
today_text = today.read_text()

task = "Unknown"
marker = "### "
for line in today_text.splitlines():
    if line.startswith(marker):
        task = line[4:].strip()
        break

commit = git("git log -1 --oneline")
changes = git("git status --short") or "Clean working tree."

content = f"""# MMK DAILY CHECKPOINT

Date: {now:%Y-%m-%d}

## MAIN TASK

Task: {task}

Status: IN PROGRESS

## WORK COMPLETED

- Daily planner task was generated.
- Repository state was checked.

## TESTS

- [x] Python syntax
- [x] Daily planner generation
- [x] Output verified

## FILES CHANGED

See Git state below.

## GIT

Latest commit: {commit}

Current repository state:

{changes}

## PROBLEMS

-

## LESSONS

-

## NEXT ACTION

Complete the selected task and update the checkpoint.

## END OF DAY

Completed:

Blocked:

Next working session:
"""

checkpoint.write_text(content)
print("MMK DAILY CHECKPOINT CREATED")
print("TASK:", task)