#!/usr/bin/env python3

from pathlib import Path
import argparse
import subprocess
import re
import sys


SKIP_DIRS = {
    ".git",
    ".venv",
    ".venv-design",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "BACKUPS",
    "backups",
}

SECRET_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
}

QC_SELF = Path("quality-control/scripts/mmk_qc.py")


def run(cmd, cwd):
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            text=True,
            capture_output=True
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as exc:
        return 1, "", str(exc)


def files_in(root):
    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if any(part in SKIP_DIRS for part in path.parts):
            continue

        yield path


def check_readme(root):
    names = {"README.md", "README.txt", "README"}

    # Check the project root first.
    if any(
        p.name in names
        for p in root.iterdir()
        if p.is_file()
    ):
        return True

    # Also allow one level of project structure, such as
    # core/README.md, without scanning unrelated nested projects.
    for directory in root.iterdir():
        if not directory.is_dir():
            continue

        if directory.name in SKIP_DIRS:
            continue

        if any(
            p.name in names
            for p in directory.iterdir()
            if p.is_file()
        ):
            return True

    return False


def check_tests(root):
    test_dirs = {"tests", "test"}

    return any(
        p.is_dir() and p.name in test_dirs
        for p in root.iterdir()
    )


def check_todos(root):
    matches = []

    pattern = re.compile(r"\b(TODO|FIXME|XXX)\b", re.I)

    for path in files_in(root):

        relative = path.relative_to(root)

        # Do not inspect the QC inspector itself.
        if (
            relative == Path("scripts/mmk_qc.py")
            or path.resolve() == QC_SELF.resolve()
        ):
            continue

        if path.suffix.lower() not in {
            ".py",
            ".js",
            ".html",
            ".css",
            ".md",
            ".json",
        }:
            continue

        try:
            text = path.read_text(errors="ignore")
        except Exception:
            continue

        if pattern.search(text):
            matches.append(str(relative))

    return matches


def check_secret_files(root):
    found = []

    for path in files_in(root):

        if path.name in SECRET_NAMES:
            found.append(str(path.relative_to(root)))

    return found


def check_python(root):
    failures = []

    for path in files_in(root):

        if path.suffix != ".py":
            continue

        code, _, err = run(
            [
                sys.executable,
                "-m",
                "py_compile",
                str(path),
            ],
            root,
        )

        if code != 0:
            failures.append({
                "file": str(path.relative_to(root)),
                "error": err,
            })

    return failures


def check_html(root):
    pages = []
    partials = []

    for path in files_in(root):

        if path.suffix.lower() != ".html":
            continue

        relative = path.relative_to(root)
        relative_text = str(relative).lower()

        # HTML fragments/components are not required to contain
        # <html> and <body>.
        if (
            "/components/" in relative_text
            or "/partials/" in relative_text
            or "/fragments/" in relative_text
            or path.name.startswith("_")
        ):
            partials.append(str(relative))
            continue

        # Explicit test HTML files may intentionally be fragments.
        if path.name.startswith("test"):
            partials.append(str(relative))
            continue

        pages.append(path)

    failures = []

    for path in pages:

        try:
            text = path.read_text(errors="ignore").lower()
        except Exception:
            continue

        relative = str(path.relative_to(root))

        if "<html" not in text:
            failures.append(
                f"{relative} [missing html element]"
            )

        if "<body" not in text:
            failures.append(
                f"{relative} [missing body]"
            )

    return failures, partials


def print_header(title):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def main():

    parser = argparse.ArgumentParser(
        description="MMK Quality Control Inspector"
    )

    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Project directory to inspect",
    )

    args = parser.parse_args()

    root = Path(args.target).resolve()

    print("=" * 60)
    print("MMK QUALITY CONTROL INSPECTOR")
    print("Version: 0.2.2")
    print("=" * 60)

    print(f"Target: {root}")

    if not root.exists():
        print()
        print("FAIL: Target does not exist.")
        return 1

    # ---------------------------------------------------------
    # GIT
    # ---------------------------------------------------------

    print_header("[1] GIT STATUS")

    code, output, error = run(
        ["git", "status", "--short", "--branch"],
        root,
    )

    if code == 0:
        print(output or "No Git output.")
    else:
        print("INFO: Git status unavailable for this target.")
        if error:
            print(error)

    # ---------------------------------------------------------
    # README
    # ---------------------------------------------------------

    print_header("[2] DOCUMENTATION")

    if check_readme(root):
        print("PASS: README found.")
    else:
        print("WARN: README not found.")

    # ---------------------------------------------------------
    # TESTS
    # ---------------------------------------------------------

    print_header("[3] TEST STRUCTURE")

    if check_tests(root):
        print("PASS: Test directory found.")
    else:
        print("WARN: No test directory detected.")

    # ---------------------------------------------------------
    # TODO
    # ---------------------------------------------------------

    print_header("[4] UNFINISHED MARKERS")

    todos = check_todos(root)

    if todos:
        print(
            f"WARN: {len(todos)} files contain "
            "TODO/FIXME/XXX markers."
        )

        for item in todos[:20]:
            print(f"  - {item}")

        if len(todos) > 20:
            print(
                f"  ... and {len(todos) - 20} more."
            )
    else:
        print("PASS: No TODO/FIXME/XXX markers detected.")

    # ---------------------------------------------------------
    # SECRET FILES
    # ---------------------------------------------------------

    print_header("[5] SECURITY FILE REVIEW")

    secrets = check_secret_files(root)

    if secrets:

        print(
            "REVIEW REQUIRED: Potential secret/config files found."
        )

        print(
            "IMPORTANT: File contents are NOT displayed by QC."
        )

        for item in secrets:
            print(f"  - {item}")

        print()
        print(
            "ACTION: Verify that secrets are not committed, "
            "published, or exposed."
        )

    else:

        print(
            "PASS: No common .env secret files detected."
        )

    # ---------------------------------------------------------
    # PYTHON
    # ---------------------------------------------------------

    print_header("[6] PYTHON SYNTAX")

    py_failures = check_python(root)

    if py_failures:

        print(
            "FAIL: Python syntax errors detected."
        )

        for item in py_failures:

            print(
                f"  - {item['file']}"
            )

            if item["error"]:
                print(
                    f"    {item['error']}"
                )

    else:

        print(
            "PASS: Python syntax check passed."
        )

    # ---------------------------------------------------------
    # HTML
    # ---------------------------------------------------------

    print_header("[7] HTML STRUCTURE")

    html_failures, partials = check_html(root)

    if html_failures:

        print(
            "WARN: HTML page structure issues detected:"
        )

        for item in html_failures[:20]:
            print(f"  - {item}")

    else:

        print(
            "PASS: Full HTML pages passed basic structure check."
        )

    if partials:

        print()
        print(
            f"INFO: {len(partials)} HTML fragments/test files "
            "were excluded from full-page validation."
        )

    # ---------------------------------------------------------
    # FOUNDER GATE
    # ---------------------------------------------------------

    print_header("[8] FOUNDER QUALITY GATE")

    print("Automated inspection is NOT final approval.")
    print()
    print("Founder must review:")
    print("  1. Real problem")
    print("  2. Target customer")
    print("  3. Founder contribution")
    print("  4. Product usefulness")
    print("  5. Real-world test")
    print("  6. Security")
    print("  7. IP/assets")
    print("  8. Documentation")
    print("  9. Release readiness")

    print()
    print(
        "FINAL STATUS: FOUNDER REVIEW REQUIRED"
    )

    print("=" * 60)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
