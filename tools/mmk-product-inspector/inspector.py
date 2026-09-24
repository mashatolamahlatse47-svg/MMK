#!/usr/bin/env python3

from pathlib import Path
import sys

VERSION = "0.3.1"

PRODUCT_TYPES = {
    "SOFTWARE",
    "DIGITAL PRODUCT",
    "ART",
    "CLOTHING",
    "COURSE / EDUCATION",
    "SERVICE",
    "EVENT / CULTURE",
    "OTHER",
}

STAGES = {
    "IDEA",
    "PROTOTYPE",
    "DEVELOPMENT",
    "TESTING",
    "REVIEW",
    "RELEASE CANDIDATE",
    "RELEASED",
    "MAINTENANCE",
    "RETIRED / ARCHIVED",
}


def status(label, result, evidence=""):
    return {
        "requirement": label,
        "status": result,
        "evidence": evidence,
    }


def file_exists(path):
    return path.is_file()


def directory_exists(path):
    return path.is_dir()


def read_text(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def read_version(product_path):
    for name in ("VERSION", "VERSION.txt"):
        path = product_path / name
        if path.is_file():
            value = read_text(path).strip()
            if value:
                return status(
                    "VERSION",
                    "PASS",
                    f"{name}: {value}",
                )
            return status(
                "VERSION",
                "REVIEW",
                f"{name} exists but is empty",
            )

    return status(
        "VERSION",
        "MISSING",
        "No VERSION or VERSION.txt found",
    )


def detect_product_type(product_path):
    """
    Determine product type only from an explicit product declaration.

    The generic PRODUCT-CONTRACT.md defines allowed product types; it must
    never be used as evidence for the actual type of a product.
    """
    declaration_files = [
        product_path / "PRODUCT-TYPE",
        product_path / "PRODUCT-TYPE.txt",
        product_path / "PRODUCT-TYPE.md",
    ]

    for declaration in declaration_files:
        if not declaration.is_file():
            continue

        text = read_text(declaration).strip().upper()

        for product_type in PRODUCT_TYPES:
            patterns = [
                rf"^PRODUCT[ -]?TYPE\\s*[:=]\\s*{re.escape(product_type)}\\s*$",
                rf"^TYPE\\s*[:=]\\s*{re.escape(product_type)}\\s*$",
                rf"^{re.escape(product_type)}$",
            ]

            if any(re.search(pattern, text, re.MULTILINE) for pattern in patterns):
                return status(
                    "PRODUCT TYPE",
                    "PASS",
                    f"Explicit declaration from {declaration.name}: {product_type}",
                )

        return status(
            "PRODUCT TYPE",
            "REVIEW",
            f"Explicit product-type declaration found in {declaration.name}, "
            "but no valid MMK product type was declared",
        )

    return status(
        "PRODUCT TYPE",
        "REVIEW",
        "No explicit product-type declaration found; Inspector will not guess",
    )

def documentation_status(product_path):
    readme = product_path / "README.md"

    if readme.is_file() and readme.stat().st_size > 0:
        return status(
            "DOCUMENTATION",
            "PASS",
            "README.md exists and is non-empty",
        )

    return status(
        "DOCUMENTATION",
        "MISSING",
        "README.md missing or empty",
    )


def customer_guide_status(product_path, product_type):
    if product_type in {"SOFTWARE", "DIGITAL PRODUCT", "COURSE / EDUCATION"}:
        candidates = [
            "CUSTOMER-GUIDE.md",
            "USER-GUIDE.md",
            "GUIDE.md",
        ]

        for name in candidates:
            path = product_path / name
            if path.is_file() and path.stat().st_size > 0:
                return status(
                    "CUSTOMER GUIDE",
                    "PASS",
                    f"{name} exists and is non-empty",
                )

        return status(
            "CUSTOMER GUIDE",
            "REVIEW",
            "Customer-facing guide not found",
        )

    return status(
        "CUSTOMER GUIDE",
        "NOT APPLICABLE",
        f"Not required by Inspector for {product_type}",
    )


def security_status(product_path):
    candidates = [
        "SECURITY.md",
        "security",
        "SECURITY",
    ]

    for name in candidates:
        path = product_path / name
        if path.is_file() or path.is_dir():
            return status(
                "SECURITY",
                "PASS",
                f"Security evidence found: {name}",
            )

    return status(
        "SECURITY",
        "REVIEW",
        "No explicit security evidence found",
    )


def test_status(product_path):
    tests = product_path / "tests"

    if not tests.is_dir():
        return (
            status(
                "TEST STRUCTURE",
                "MISSING",
                "tests directory not found",
            ),
            status(
                "TEST EXECUTION",
                "REVIEW",
                "No test execution evidence supplied",
            ),
        )

    files = [
        p for p in tests.rglob("*")
        if p.is_file()
        and (
            p.name.startswith("test_")
            or p.name.endswith("_test.py")
            or p.name.endswith(".test.js")
            or p.name.endswith(".spec.js")
        )
    ]

    if not files:
        return (
            status(
                "TEST STRUCTURE",
                "MISSING",
                "tests directory exists but no recognized test files were found",
            ),
            status(
                "TEST EXECUTION",
                "REVIEW",
                "No test execution evidence supplied",
            ),
        )

    return (
        status(
            "TEST STRUCTURE",
            "PASS",
            f"{len(files)} recognized test file(s) found",
        ),
        status(
            "TEST EXECUTION",
            "REVIEW",
            "Test files exist; presence does not prove tests passed",
        ),
    )


def software_checks(product_path):
    results = []

    website = product_path / "website"

    software_evidence = [
        product_path / "app.py",
        product_path / "main.py",
        product_path / "package.json",
        product_path / "requirements.txt",
        product_path / "src",
        product_path / "backend",
        product_path / "server",
        product_path / "website",
    ]

    found = [item for item in software_evidence if item.exists()]

    results.append(
        status(
            "SOFTWARE WEBSITE / UI",
            "PASS" if website.is_dir() else "REVIEW",
            str(website) if website.is_dir()
            else "website directory not found; software may be non-web",
        )
    )

    results.append(
        status(
            "SOFTWARE BACKEND / APP",
            "PASS" if found else "MISSING",
            "Recognized software structure: "
            + ", ".join(item.name for item in found)
            if found
            else "No recognized software application structure found",
        )
    )

    return results

def digital_product_checks(product_path):
    return [
        status(
            "DIGITAL PRODUCT PACKAGE",
            "PASS" if any(
                (product_path / name).exists()
                for name in (
                    "README.md",
                    "PRODUCT.md",
                    "CUSTOMER-GUIDE.md",
                    "package.json",
                )
            ) else "REVIEW",
            "Digital-product documentation/package evidence inspected",
        )
    ]


def art_checks(product_path):
    candidates = [
        "ART.md",
        "art",
        "artwork",
        "gallery",
        "assets",
    ]

    found = [name for name in candidates if (product_path / name).exists()]

    return [
        status(
            "ART ASSETS",
            "PASS" if found else "REVIEW",
            ", ".join(found) if found else "No explicit art/gallery asset structure found",
        )
    ]


def clothing_checks(product_path):
    candidates = [
        "CLOTHING.md",
        "clothing",
        "designs",
        "products",
        "catalogue",
    ]

    found = [name for name in candidates if (product_path / name).exists()]

    return [
        status(
            "CLOTHING STRUCTURE",
            "PASS" if found else "REVIEW",
            ", ".join(found) if found else "No explicit clothing structure found",
        )
    ]


def course_checks(product_path):
    candidates = [
        "COURSE.md",
        "course",
        "lessons",
        "modules",
        "curriculum",
    ]

    found = [name for name in candidates if (product_path / name).exists()]

    return [
        status(
            "COURSE STRUCTURE",
            "PASS" if found else "REVIEW",
            ", ".join(found) if found else "No explicit course structure found",
        )
    ]


def service_checks(product_path):
    candidates = [
        "SERVICE.md",
        "services",
        "pricing",
        "SCOPE.md",
    ]

    found = [name for name in candidates if (product_path / name).exists()]

    return [
        status(
            "SERVICE STRUCTURE",
            "PASS" if found else "REVIEW",
            ", ".join(found) if found else "No explicit service structure found",
        )
    ]


def event_checks(product_path):
    candidates = [
        "EVENT.md",
        "event",
        "tickets",
        "checkin",
        "sales",
    ]

    found = [name for name in candidates if (product_path / name).exists()]

    return [
        status(
            "EVENT / CULTURE STRUCTURE",
            "PASS" if found else "REVIEW",
            ", ".join(found) if found else "No explicit event/culture structure found",
        )
    ]


def database_status(product_path):
    databases = list(product_path.rglob("*.db"))

    if databases:
        return status(
            "DATABASE",
            "PASS",
            f"{len(databases)} database file(s) found",
        )

    return status(
        "DATABASE",
        "NOT APPLICABLE",
        "No SQLite database detected",
    )


def ownership_status(product_path):
    candidates = [
        "LICENSE.md",
        "LICENCE.md",
        "IP.md",
        "OWNERSHIP.md",
        "COPYRIGHT.md",
    ]

    found = [name for name in candidates if (product_path / name).exists()]

    if found:
        return status(
            "OWNERSHIP / IP",
            "PASS",
            ", ".join(found),
        )

    return status(
        "OWNERSHIP / IP",
        "REVIEW",
        "No explicit ownership/IP record found",
    )


def release_status(product_path):
    candidates = [
        "RELEASE.md",
        "RELEASE-NOTES.md",
        "CHANGELOG.md",
        "SALES-SHEET.md",
        "CUSTOMER-GUIDE.md",
    ]

    found = [name for name in candidates if (product_path / name).exists()]

    if found:
        return status(
            "RELEASE EVIDENCE",
            "PASS",
            ", ".join(found),
        )

    return status(
        "RELEASE EVIDENCE",
        "REVIEW",
        "No explicit release evidence found",
    )


def inspect_product(product_path):
    results = []

    type_result = detect_product_type(product_path)
    results.append(type_result)

    product_type = None

    if type_result["status"] in {"PASS", "REVIEW"}:
        evidence = type_result["evidence"]
        for candidate in PRODUCT_TYPES:
            if candidate in evidence:
                product_type = candidate
                break

    results.append(read_version(product_path))
    results.append(documentation_status(product_path))

    if product_type:
        results.append(customer_guide_status(product_path, product_type))
    else:
        results.append(
            status(
                "CUSTOMER GUIDE",
                "REVIEW",
                "Product type unresolved; applicability cannot be confirmed",
            )
        )

    results.append(security_status(product_path))

    test_structure, test_execution = test_status(product_path)
    results.append(test_structure)
    results.append(test_execution)

    if product_type == "SOFTWARE":
        results.extend(software_checks(product_path))
    elif product_type == "DIGITAL PRODUCT":
        results.extend(digital_product_checks(product_path))
    elif product_type == "ART":
        results.extend(art_checks(product_path))
    elif product_type == "CLOTHING":
        results.extend(clothing_checks(product_path))
    elif product_type == "COURSE / EDUCATION":
        results.extend(course_checks(product_path))
    elif product_type == "SERVICE":
        results.extend(service_checks(product_path))
    elif product_type == "EVENT / CULTURE":
        results.extend(event_checks(product_path))
    else:
        results.append(
            status(
                "PRODUCT-SPECIFIC STRUCTURE",
                "NOT APPLICABLE",
                "No product-specific structure check selected",
            )
        )

    results.append(database_status(product_path))
    results.append(ownership_status(product_path))
    results.append(release_status(product_path))

    return results, product_type


def print_report(product_path, results, product_type):
    print("\n=== MMK PRODUCT INSPECTOR ===")
    print(f"Inspector version: {VERSION}")
    print(f"Product: {product_path}")
    print(f"Product type: {product_type or 'UNRESOLVED'}")
    print()

    for item in results:
        print(f"[{item['status']}] {item['requirement']}")
        print(f"  Evidence: {item['evidence']}")

    statuses = {item["status"] for item in results}

    if "ERROR" in statuses:
        overall = "ERROR"
    elif "MISSING" in statuses or "REVIEW" in statuses:
        overall = "REVIEW"
    else:
        overall = "PASS"

    print()
    print(f"OVERALL: {overall}")
    print("READ-ONLY: Inspector does not modify the inspected product.")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <product-directory>")
        return 2

    product_path = Path(sys.argv[1]).expanduser().resolve()

    if not product_path.is_dir():
        print(f"ERROR: Product directory not found: {product_path}")
        return 2

    results, product_type = inspect_product(product_path)
    print_report(product_path, results, product_type)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
