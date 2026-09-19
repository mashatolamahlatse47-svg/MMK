# MMK Software Data Model

## Purpose

This document defines common data concepts used across MMK software
products.

The model is designed for reuse by MMK and configurable client systems.

---

## Core Entities

### Business

Represents the business or organization using an MMK software product.

Typical information:
- business ID
- business name
- contact information
- address
- configuration
- status

---

### User

Represents a person who can access a system.

Typical information:
- user ID
- name
- username
- role
- status
- authentication information

---

### Customer

Represents a customer or service recipient.

Typical information:
- customer ID
- name
- contact information
- address
- status

---

### Product

Represents a product or service offered by a business.

Typical information:
- product ID
- name
- description
- price
- stock
- status

---

### Order

Represents a customer request or purchase.

Typical information:
- order ID
- customer ID
- items
- total
- status
- created date
- updated date

---

## Security Domain Entities

### Occurrence

Represents an entry recorded in an occurrence book.

Typical information:
- occurrence ID
- site
- date
- time
- category
- description
- person involved
- action taken
- reporting user
- status

---

### Incident

Represents a security incident requiring additional attention.

Typical information:
- incident ID
- occurrence ID
- severity
- description
- response
- status
- supervisor
- resolution

---

### Report

Represents generated operational information.

Examples:
- daily report
- shift report
- incident report
- monthly report

---

## Audit Entity

### Audit Event

Records important system actions.

Typical information:
- event ID
- user ID
- action
- entity
- entity ID
- timestamp
- result

Audit events help with accountability and system security.

---

## Relationships

Business
  ↓
Users

Business
  ↓
Customers

Business
  ↓
Products

Customer
  ↓
Orders

Order
  ↓
Products

Security Site
  ↓
Occurrences

Occurrence
  ↓
Incidents

User
  ↓
Occurrences

User
  ↓
Audit Events

---

## Reuse Principle

Core entities should be reusable where appropriate.

Domain-specific entities should remain inside their respective
software domains.

For example:

User
Customer
Business
Audit Event

may be shared.

Occurrence and Incident belong primarily to security software.

Order belongs primarily to ordering software.

---

## Design Goal

The MMK data model must support:

- MMK internal systems
- reusable products
- configurable client systems
- future web applications
- future mobile applications
- future AI integrations

The model should evolve through controlled versioning.
