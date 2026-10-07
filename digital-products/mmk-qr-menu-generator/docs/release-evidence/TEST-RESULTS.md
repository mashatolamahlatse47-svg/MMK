# MMK QR Menu Generator — Test Evidence

## Current Status

TESTED DEVELOPMENT / LAB PRODUCT

Not yet customer-released.

## Automated Tests

Command: .venv/bin/python -m pytest -q

Result: 3 passed

## Python Syntax

Command: .venv/bin/python -m py_compile app/*.py tests/*.py

Result: OK: Python syntax valid.

## Local HTTP Verification

Homepage: GET / → 200 OK
Demo: GET /menu/demo → 302 → PDF 200 OK
Demo Cafe: GET /menu/demo-cafe → 302 → PDF 200 OK
Mama's Kitchen: GET /menu/mamas-kitchen → 302 → PDF 200 OK
Invalid menu: GET /menu/does-not-exist → 404 NOT FOUND

## Customer URL Workflow

Custom base URL generation is covered by an automated test.

## Release Limitation

The default local URL is http://127.0.0.1:8060.
This is suitable for local testing only.
A public HTTPS deployment and real-phone QR scan have not been completed.

## Decision

Keep product in TESTED DEVELOPMENT / LAB status.
Do not mark customer release complete until public deployment and real-phone scanning are verified.
