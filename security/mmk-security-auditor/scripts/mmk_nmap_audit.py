#!/usr/bin/env python3

import argparse
import datetime
import pathlib
import subprocess
import sys


PROJECT_DIR = pathlib.Path(__file__).resolve().parents[1]
EVIDENCE_DIR = PROJECT_DIR / "evidence"
SCOPE_GATE = PROJECT_DIR / "scripts" / "scope_gate.py"


def check_authorization(target: str, port: str, activity: str) -> bool:
    result = subprocess.run(
        [
            sys.executable,
            str(SCOPE_GATE),
            target,
            port,
            activity,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    print(result.stdout, end="")

    if result.returncode != 0:
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")
        return False

    return True


def run_scan(target: str, ports: str) -> int:
    if not check_authorization(
        target,
        ports,
        "service_version_detection",
    ):
        print("MMK Security Auditor: scan blocked.")
        return 1

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    evidence_file = EVIDENCE_DIR / f"nmap-{target.replace('/', '_')}-{timestamp}.txt"

    command = [
        "nmap",
        "-sV",
        "-p",
        ports,
        target,
    ]

    print("MMK Security Auditor")
    print("====================")
    print(f"Target: {target}")
    print(f"Ports:  {ports}")
    print()
    print("Running:", " ".join(command))
    print()

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        print("ERROR: nmap is not installed or not available.")
        return 1

    evidence = (
        "MMK SECURITY AUDITOR — NMAP EVIDENCE\n"
        f"Timestamp: {timestamp}\n"
        f"Target: {target}\n"
        f"Ports: {ports}\n"
        f"Command: {' '.join(command)}\n"
        "\n"
        "----- NMAP OUTPUT -----\n"
        f"{result.stdout}"
        f"{result.stderr}"
    )

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text(evidence, encoding="utf-8")

    print(result.stdout)

    if result.returncode != 0:
        print("Nmap returned an error.")
        return result.returncode

    print(f"Evidence saved: {evidence_file}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="MMK Security Auditor — controlled Nmap service audit"
    )
    parser.add_argument("target", help="Authorized target, e.g. 127.0.0.1")
    parser.add_argument(
        "--ports",
        default="8080",
        help="Authorized TCP ports, default: 8080",
    )

    args = parser.parse_args()

    return run_scan(args.target, args.ports)


if __name__ == "__main__":
    sys.exit(main())
