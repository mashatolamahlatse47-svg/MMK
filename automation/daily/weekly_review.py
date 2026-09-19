from pathlib import Path
from datetime import datetime, timedelta
import re

root = Path.home() / "MMK"
daily = root / "automation" / "daily"

queue_file = daily / "TASK-QUEUE.md"
history_dir = daily / "history"
review_file = daily / "WEEKLY-REVIEW.md"


def checkpoint_status(text):
    match = re.search(r"Status: ([^\n]+)", text)
    return match.group(1).strip() if match else "UNKNOWN"


def checkpoint_task(text):
    match = re.search(r"Task: ([^\n]+)", text)
    return match.group(1).strip() if match else "Unknown task"


def checkpoint_next_action(text):
    match = re.search(r"## NEXT ACTION\n\n(.+)", text)
    return match.group(1).strip() if match else "No next action recorded."


queue = queue_file.read_text()

today = datetime.now()
week_start = today - timedelta(days=6)

records = []

if history_dir.exists():
    for file in sorted(history_dir.glob("*.md")):
        try:
            record_date = datetime.strptime(file.stem, "%Y-%m-%d")
        except ValueError:
            continue

        if week_start.date() <= record_date.date() <= today.date():
            text = file.read_text()

            records.append({
                "date": record_date.strftime("%Y-%m-%d"),
                "status": checkpoint_status(text),
                "task": checkpoint_task(text),
                "next": checkpoint_next_action(text),
            })

completed = sum(r["status"] == "COMPLETED" for r in records)
blocked = sum(r["status"] == "BLOCKED" for r in records)
in_progress = sum(r["status"] == "IN PROGRESS" for r in records)

next_task = "No ACTIVE task found."

for match in re.finditer(
    r"### Task (\d+)\n"
    r"Name: ([^\n]+)\n"
    r"Priority: ([^\n]+)\n"
    r"Status: ([^\n]+)\n"
    r"Area: ([^\n]+)\n"
    r"Next: ([^\n]+)\n"
    r"Test: ([^\n]+)",
    queue
):
    if match.group(4).strip() == "ACTIVE":
        next_task = (
            f"{match.group(2).strip()} — "
            f"{match.group(6).strip()}"
        )
        break

if records:
    history_lines = "\n".join(
        f"- {r['date']} — {r['task']} — {r['status']}"
        for r in records
    )
else:
    history_lines = "- No checkpoint history recorded for this period."

content = f"""# MMK WEEKLY REVIEW

Review period:
{week_start:%Y-%m-%d} to {today:%Y-%m-%d}

Generated:
{today:%Y-%m-%d %H:%M}

## SUMMARY

Checkpoint records: {len(records)}
Completed: {completed}
Blocked: {blocked}
In-progress: {in_progress}

## CHECKPOINT HISTORY

{history_lines}

## CURRENT ACTIVE TASK

{next_task}

## NEXT WEEK FOCUS

Continue the current ACTIVE task before starting unrelated MMK work.

## REVIEW STATUS

Weekly review generated successfully.
"""

review_file.write_text(content)

print("================================")
print("MMK WEEKLY REVIEW v1.6")
print("================================")
print("Review:", f"{week_start:%Y-%m-%d} to {today:%Y-%m-%d}")
print("Records:", len(records))
print("Completed:", completed)
print("Blocked:", blocked)
print("In progress:", in_progress)
print("Next:", next_task)
print("File:", review_file)
print("================================")
