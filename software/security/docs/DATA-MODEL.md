# MMK Security Occurrence Book — Data Model v0.1

## Purpose

The MMK Security Occurrence Book (SOB) is a reusable security-management system for MMK and future clients.

The system records security occurrences, incidents, shifts, handovers, sites, and responsible users.

## Core Entities

### 1. Security Site

Represents a location protected by the security system.

Fields:
- id
- business_id
- name
- address
- status
- created_at
- updated_at

### 2. Security Occurrence

Represents an event recorded in the occurrence book.

Fields:
- id
- site_id
- user_id
- occurrence_date
- occurrence_time
- category
- description
- action_taken
- status
- created_at
- updated_at

### 3. Security Incident

Represents a serious event linked to an occurrence.

Fields:
- id
- occurrence_id
- severity
- description
- response
- resolution
- supervisor_id
- status
- created_at
- updated_at

### 4. Security Shift

Represents a guard or security team's working period.

Fields:
- id
- site_id
- supervisor_id
- shift_date
- start_time
- end_time
- status
- notes
- created_at
- updated_at

### 5. Security Handover

Represents information transferred between shifts.

Fields:
- id
- site_id
- from_user_id
- to_user_id
- shift_id
- handover_date
- notes
- outstanding_items
- status
- created_at
- updated_at

### 6. Security Report

Reports are generated from stored system data.

Initial report types:
- Daily occurrence report
- Shift report
- Incident report
- Handover report
- Monthly security report

Reports should initially be generated dynamically rather than stored as duplicate data.

## Relationships

Business
  |
  +-- Security Sites
        |
        +-- Security Occurrences
        |       |
        |       +-- Security Incidents
        |
        +-- Security Shifts
        |
        +-- Security Handovers

Users are connected to:
- occurrences
- incidents
- shifts
- handovers

## Status Principles

Records should support controlled statuses.

Examples:
- active
- inactive
- open
- closed
- pending
- resolved

The exact allowed values will be enforced by the database and application layer.

## Security Principles

1. Never use real client information during development.
2. Never store passwords in occurrence records.
3. Keep client data separated.
4. Record important system actions through audit logging.
5. Validate user input.
6. Use database constraints where appropriate.
7. Keep security records traceable.
8. Do not delete important records casually.
9. Use backups before major migrations.
10. Version database changes.

## Reuse Principle

The Security Occurrence Book is a reusable MMK software engine.

MMK should be able to configure the same engine for:

- MMK internal operations
- Security companies
- Estates
- Schools
- Businesses
- Construction sites
- Other organisations requiring structured security records

The reusable engine should remain separate from client-specific configuration.

## Version

Data Model Version: 0.1.0

Status: Development
