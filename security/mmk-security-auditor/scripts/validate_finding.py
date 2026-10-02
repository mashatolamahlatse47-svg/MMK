#!/usr/bin/env python3

import json
import sys
from pathlib import Path

REQUIRED_FIELDS = [
    "finding_id",
    "severity",
    "title",
    "asset",
    "observation",
    "evidence",
    "risk",
    "recommendation",
    "status",
]

ALLOWED_SEVERITIES = {
    "INFO",
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
}

def validate_finding(path: Path) -> bool:
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: {exc}")
        return False

    missing = [field for field in REQUIRED_FIELDS if field not in data]

    if missing:
        print("INVALID")
        print("Missing fields:", ", ".join(missing))
        return False

    if data["severity"] not in ALLOWED_SEVERITIES:
        print("INVALID")
        print("Invalid severity:", data["severity"])
        return False

    if not isinstance(data["evidence"], list):
        print("INVALID")
        print("Evidence must be a list.")
        return False

    print("VALID")
    print("Finding:", data["finding_id"])
    print("Severity:", data["severity"])
    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} FINDING.json")
        raise SystemExit(2)

    raise SystemExit(
        0 if validate_finding(Path(sys.argv[1])) else 1
    )
