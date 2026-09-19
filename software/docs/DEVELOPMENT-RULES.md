# MMK Software Development Rules

## Rule 1 — Build Reusable Assets

Software should be designed for reuse whenever practical.

## Rule 2 — Do Not Destroy Existing Assets

Existing MMK projects must not be deleted, overwritten or moved
without first inspecting and protecting them.

## Rule 3 — Separate Engine From Product

Reusable engineering belongs under:

software/

Finished products belong under:

products/

Client-specific work belongs under:

clients/

## Rule 4 — Prototype Before Large Builds

Important interfaces and workflows should have a prototype before
large production implementations.

## Rule 5 — Test Before Release

Software should be tested before being marked as a release.

## Rule 6 — Version Everything

Products and important engines must have identifiable versions.

Example:

v0.1.0
v0.2.0
v1.0.0

## Rule 7 — Document Important Systems

Every major software product should explain:
- purpose
- installation
- usage
- architecture
- testing
- configuration
- version

## Rule 8 — Security By Design

Security should be considered during development, not added only
after the software is finished.

## Rule 9 — Keep Client Data Separate

Client-specific information must not be mixed into reusable
MMK source assets.

## Rule 10 — Backup Before Major Changes

Create or verify a backup before major structural changes.
