from pathlib import Path
from datetime import datetime
import subprocess

root = Path.home() / "MMK"
daily = root / "automation" / "daily"
out = daily / "TODAY.md"
state = (daily / "PROJECT-STATE.md").read_text().strip()

def git(cmd):
    return subprocess.getoutput("cd " + str(root) + " && " + cmd)

now = datetime.now()

content = f"""# MMK DAILY WORK PLAN

Date: {now:%Y-%m-%d}
Generated: {now:%H:%M}

## ACTIVE PROJECT STATE

{state}

## GIT STATE

Branch: {git("git branch --show-current")}

Latest commit: {git("git log -1 --oneline")}

Current changes:

{git("git status --short") or "Clean working tree."}

## TODAY

- [ ] Review active project
- [ ] Complete current task
- [ ] Run required tests
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
print("MMK DAILY PLANNER UPDATED")
