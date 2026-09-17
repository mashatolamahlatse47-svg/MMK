from pathlib import Path
from datetime import datetime

root = Path.home() / "MMK"
out = root / "automation/daily/TODAY.md"
date = datetime.now().strftime("%Y-%m-%d")
time = datetime.now().strftime("%H:%M")

out.write_text(f"# MMK DAILY WORK PLAN\n\nDate: {date}\nGenerated: {time}\n\n## TODAY\n\n- [ ] Main MMK task\n- [ ] Test the work\n- [ ] Save the work\n- [ ] Record progress\n\n## NOTES\n\n\n## NEXT ACTION\n\n")
print(f"MMK daily plan generated: {out}")
