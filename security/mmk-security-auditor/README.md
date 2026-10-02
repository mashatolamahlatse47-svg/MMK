# MMK Security Auditor

MMK Security Auditor is an authorization-first security assessment toolkit for MMK-owned systems and systems where the owner has explicitly authorized testing.

## Core Workflow

Authorization -> Scope -> Test -> Evidence -> Finding -> Report -> Review

Testing must not begin unless the target and activity are within the approved assessment scope.

## Current Training Lab

- Target: 127.0.0.1
- Authorized port: 8080
- Allowed activities: port discovery and service version detection

## Safety Rules

- No unauthorized access.
- No denial-of-service testing.
- No destructive testing.
- No data destruction.
- No testing outside approved scope.

## Findings

A finding must distinguish an observation from a confirmed vulnerability.

## Founder + AI Gate

AI may assist with analysis, documentation, code, and quality checks.

The MMK Founder remains responsible for authorization, scope approval, finding review, and final report approval.
