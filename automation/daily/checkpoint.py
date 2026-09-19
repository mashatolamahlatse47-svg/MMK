from pathlib import Path
from datetime import datetime
import subprocess

root = Path.home() / "MMK"
daily = root / "automation" / "daily"

today = daily / "TODAY.md"
checkpoint = daily / "CHECKPOINT.md"


def git(cmd):
    return subprocess.getoutput(
        "cd " + str(root) + " && " + cmd
    )


def ask(label, default=""):
    value = input(f"{label}: ").strip()
    return value if value else default


now = datetime.now()
today_text = today.read_text()

task = "Unknown"

for line in today_text.splitlines():
    if line.startswith("### "):
        task = line[4:].strip()
        break


print("================================")
print("MMK DAILY CHECKPOINT v1.4")
print("================================")
print(f"Task: {task}")
print()

status = ask(
    "Status (IN PROGRESS / COMPLETED / BLOCKED)",
    "IN PROGRESS"
)

work = ask(
    "Work completed",
    "No work recorded."
)

tests = ask(
    "Tests completed",
    "No tests recorded."
)

problems = ask(
    "Problems",
    "None."
)

lessons = ask(
    "Lessons",
    "None recorded."
)

next_action = ask(
    "Next action",
    "Continue the selected task."
)

commit = git("git log -1 --oneline")
changes = git("git status --short") or "Clean working tree."

content = f"""# MMK DAILY CHECKPOINT

Date: {now:%Y-%m-%d}
Generated: {now:%H:%M}

## MAIN TASK

Task: {task}

Status: {status.removeprefix("Status: ").strip()}

## WORK COMPLETED

- {work.removeprefix("Work completed: ").strip()}

## TESTS

- {tests.removeprefix("Tests completed: ").strip()}

## FILES CHANGED

Current repository state:

{changes}

## GIT

Latest commit: {commit}

## PROBLEMS

- {problems.removeprefix("Problems: ").strip()}

## LESSONS

- {lessons.removeprefix("Lessons: ").strip()}

## NEXT ACTION

{next_action.removeprefix("Next action: ").strip()}

## END OF DAY

Completed: {status == "COMPLETED"}

Blocked: {status == "BLOCKED"}

Next working session: {next_action.removeprefix("Next action: ").strip()}
"""

checkpoint.write_text(content)

print()
print("================================")
print("CHECKPOINT SAVED")
print("================================")
print("Task:", task)
print("Status:", status)
print("File:", checkpoint)
