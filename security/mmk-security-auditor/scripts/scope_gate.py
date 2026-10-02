#!/usr/bin/env python3

import json
import pathlib
import sys


PROJECT_DIR = pathlib.Path(__file__).resolve().parents[1]
SCOPE_FILE = PROJECT_DIR / "config" / "lab-scope.json"


def load_scope():
    try:
        with SCOPE_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as error:
        print(f"ERROR: Cannot load authorization scope: {error}")
        return None


def is_authorized(target, port, activity):
    scope = load_scope()

    if scope is None:
        return False

    if scope.get("status") != "AUTHORIZED":
        return False

    if activity not in scope.get("allowed_activities", []):
        return False

    for authorized_target in scope.get("targets", []):
        if authorized_target.get("host") != target:
            continue

        requested_ports = [item.strip() for item in str(port).split(",") if item.strip()]
        authorized_ports = {
            str(item) for item in authorized_target.get("ports", [])
        }

        if requested_ports and all(item in authorized_ports for item in requested_ports):
            return True

    return False


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: scope_gate.py <target> <port> <activity>"
        )
        return 2

    target = sys.argv[1]
    port = sys.argv[2]
    activity = sys.argv[3]

    if is_authorized(target, port, activity):
        print("AUTHORIZED")
        print(f"Target: {target}")
        print(f"Port: {port}")
        print(f"Activity: {activity}")
        return 0

    print("DENIED")
    print(f"Target: {target}")
    print(f"Port: {port}")
    print(f"Activity: {activity}")
    print("Reason: Request is outside the authorized assessment scope.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
