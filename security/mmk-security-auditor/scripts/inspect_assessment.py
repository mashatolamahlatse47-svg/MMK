#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
AUTHORIZATION_FILE = PROJECT_DIR / "AUTHORIZATION.md"
CHECKLIST_FILE = PROJECT_DIR / "CHECKLIST.md"
SCOPE_FILE = PROJECT_DIR / "config" / "lab-scope.json"
FINDINGS_DIR = PROJECT_DIR / "findings"
REPORTS_DIR = PROJECT_DIR / "reports"
VALIDATOR = PROJECT_DIR / "scripts" / "validate_finding.py"


def check_file(path: Path, label: str) -> bool:
    if path.is_file():
        print(f"PASS  {label}")
        return True

    print(f"FAIL  {label} — missing: {path}")
    return False


def check_scope() -> bool:
    try:
        scope = json.loads(SCOPE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"FAIL  Scope configuration — {error}")
        return False

    checks = [
        ("Scope status is AUTHORIZED", scope.get("status") == "AUTHORIZED"),
        ("Scope owner exists", bool(scope.get("owner"))),
        ("Scope purpose exists", bool(scope.get("purpose"))),
        ("Authorized targets exist", bool(scope.get("targets"))),
        ("Allowed activities exist", bool(scope.get("allowed_activities"))),
    ]

    passed = True

    for label, result in checks:
        if result:
            print(f"PASS  {label}")
        else:
            print(f"FAIL  {label}")
            passed = False

    return passed


def validate_findings() -> bool:
    finding_files = sorted(FINDINGS_DIR.glob("*.json"))

    if not finding_files:
        print("FAIL  Findings — no JSON findings found")
        return False

    passed = True

    for finding_file in finding_files:
        result = subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                str(finding_file),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            print(f"PASS  Finding validation — {finding_file.name}")
        else:
            print(f"FAIL  Finding validation — {finding_file.name}")
            passed = False

    return passed


def check_finding_evidence() -> bool:
    passed = True

    for finding_file in sorted(FINDINGS_DIR.glob("*.json")):
        try:
            finding = json.loads(
                finding_file.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            print(f"FAIL  Finding JSON — {finding_file.name}")
            passed = False
            continue

        for evidence in finding.get("evidence", []):
            evidence_path = PROJECT_DIR / evidence

            if evidence_path.is_file():
                print(
                    f"PASS  Evidence exists — "
                    f"{finding_file.name}: {evidence}"
                )
            else:
                print(
                    f"FAIL  Evidence missing — "
                    f"{finding_file.name}: {evidence}"
                )
                passed = False

    return passed


def check_reports() -> bool:
    passed = True

    for finding_file in sorted(FINDINGS_DIR.glob("*.json")):
        try:
            finding = json.loads(
                finding_file.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            passed = False
            continue

        finding_id = finding.get("finding_id")

        if not finding_id:
            print(f"FAIL  Report check — {finding_file.name}")
            passed = False
            continue

        report = REPORTS_DIR / f"report-{finding_id}.md"

        if report.is_file():
            print(f"PASS  Report exists — {report.name}")
        else:
            print(f"FAIL  Report missing — {report}")
            passed = False

    return passed


def main() -> int:
    print("MMK SECURITY AUDITOR — ASSESSMENT INSPECTOR")
    print("==========================================")
    print()

    results = [
        check_file(AUTHORIZATION_FILE, "Authorization document"),
        check_file(CHECKLIST_FILE, "Assessment checklist"),
        check_file(SCOPE_FILE, "Scope configuration"),
        check_scope(),
        validate_findings(),
        check_finding_evidence(),
        check_reports(),
    ]

    print()
    print("==========================================")

    if all(results):
        print("INSPECTION: PASS")
        print("Assessment package is internally consistent.")
        print("Founder review is still required before final approval.")
        return 0

    print("INSPECTION: FAIL")
    print("Assessment package requires correction before final review.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
