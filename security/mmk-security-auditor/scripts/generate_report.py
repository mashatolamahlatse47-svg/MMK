#!/usr/bin/env python3

import json
import sys
from datetime import datetime
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
FINDINGS_DIR = PROJECT_DIR / "findings"
REPORTS_DIR = PROJECT_DIR / "reports"


def load_finding(path: Path) -> dict:
    return json.loads(path.read_text())


def generate_report(finding: dict) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""# MMK Security Assessment Report

## Assessment

**Assessment ID:** MMK-LAB-001  
**Target:** {finding["asset"]}  
**Generated:** {timestamp}

## Finding {finding["finding_id"]}

**Severity:** {finding["severity"]}  
**Title:** {finding["title"]}  
**Status:** {finding["status"]}

### Observation

{finding["observation"]}

### Evidence

{chr(10).join(f"- `{item}`" for item in finding["evidence"])}

### Risk

{finding["risk"]}

### Recommendation

{finding["recommendation"]}

---

## Assessment Note

This report records observed evidence and documented assessment
conclusions. An observed service or open port must not be treated
as proof of a vulnerability without supporting evidence.

**MMK Security Auditor**
"""


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} FINDING.json")
        return 2

    finding_path = Path(sys.argv[1])

    if not finding_path.exists():
        print(f"ERROR: Finding not found: {finding_path}")
        return 1

    finding = load_finding(finding_path)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    report_name = f"report-{finding['finding_id']}.md"
    report_path = REPORTS_DIR / report_name

    report_path.write_text(generate_report(finding))

    print("REPORT GENERATED")
    print(f"Report: {report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
