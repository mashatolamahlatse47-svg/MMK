# MMK PROJECT REGISTER

## Purpose

The MMK Project Register records the lifecycle state of MMK projects.

The four shelves are:

- ACTIVE
- INCOMPLETE
- PARKED
- COMPLETED

This register is a management/control record.

It does NOT automatically move, delete, rename, or modify project source files.

---

# ACTIVE

## 1. MMK Small Business Engine

Location: software/mmk-small-business-engine
Version: 0.1.0
Stage: Foundation
Status: Active

Next focus:
Continue reusable business-engine development, testing and productisation.

---

## 2. MMK Local Intercom & Queue

Location: software/mmk-local-intercom-queue
Version: 0.1.0
Stage: Foundation
Status: Active

Next focus:
Continue roadmap development toward v1.0.0 production release.

---

## 3. MMK Pre-Order System

Location: software/mmk-pre-order-system
Version: 0.1.0
Stage: Foundation
Status: Active

Next focus:
Continue implementation and testing.

---

## 4. MMK KPI System v1

Location: products/mmk-kpi-system-v1
Stage: Build started
Status: Active

Next focus:
Inspect implementation and continue development.

---

## 5. MMK Local Services Coordinator

Location: products/local-services-coordinator
Version: 0.1.0
Stage: Foundation
Status: Active

Next focus:
Continue workflow, testing and product development.

---

## 6. Grocery Household Website

Location: client-products/grocery-household-website
Stage: Development
Status: Active development

Next focus:
Inspect current working state and remaining product/client work.

---

# INCOMPLETE

## 1. Taxi Money Tracker

Location: client-products/taxi-money-tracker
Version: 1.0.0
Status: Existing product; release-gate verification required.

---

## 2. MMK Digital Security System

Location: products/digital-security-system
Status: Development

Next focus:
Inspect implementation, testing and release readiness.

---

## 3. MMK Ordering System

Location: products/ordering-system
Status: Development

Next focus:
Inspect implementation, testing and release readiness.

---

## 4. MMK Website System

Location: products/website-system
Status: Development

Next focus:
Inspect implementation, testing and release readiness.

---

## 5. MMK KPI System

Location: products/kpi-system
Status: Development

Next focus:
Compare with MMK KPI System v1 and determine relationship.

---

## 6. MMK API Lab

Location: software/mmk-api-lab
Status: Development laboratory

Next focus:
Inspect implementation and determine whether it remains a laboratory or becomes a product.

---

## 7. MMK Business Starter

Location: digital-products/mmk-business-starter
Version: 1.2.0
Stage: Release verified
Status: Completed

Release:
releases/MMK-Business-Starter-v1.2.0

Package:
releases/MMK-Business-Starter-v1.2.0-release-verified.zip

Historical original package:
releases/MMK-Business-Starter-v1.2.0.zip

Evidence:
Working product, browser testing, persistent Activity History testing, README, CUSTOMER-GUIDE, RELEASE-NOTES, TEST-RESULTS, VERSION, clean release package, backup preservation and ZIP integrity verification.

Founder Final Approval:
APPROVED

Next focus:
Publish v1.2.0 when the planned release window begins.

---

## 8. MMK Business Starter Pack

Location: digital-products/MMK-Business-Starter-Pack
Version: 1.0
Status: Product work exists; release evidence incomplete.

---

## 9. Business Starter Pack

Location: digital-products/business-starter-pack
Version: 1.0
Status: Product work exists; release evidence incomplete.

---

## 10. MMK Art Gallery Pack

Location: digital-products/art-gallery-pack
Status: Development container

---

## 11. MMK Clothing Store

Location: digital-products/clothing-store
Status: Development container

---

## 12. MMK Grocery System

Location: digital-products/grocery-system
Status: Development container

---

## 13. MMK Invoice Pack

Location: digital-products/invoice-pack
Status: Development container

---

## 14. MMK Social Media Pack

Location: digital-products/social-media-pack
Status: Development container

---

# PARKED

## 1. MMK Business Starter — Before Email Cleanup

Location: digital-products/mmk-business-starter-before-email-cleanup
Status: Historical development copy

Rule:
Preserve this work. Do not delete it simply because a newer working copy exists.

---

# COMPLETED

## 1. MMK Stock Profit Calculator

Source:
products/stock-profit-calculator-record

Release:
releases/MMK-Stock-Profit-Calculator-v1.0.0

Package:
releases/MMK-Stock-Profit-Calculator-v1.0.0.zip

Version:
1.0.0

Evidence:
Release directory, ZIP package, README, CUSTOMER-GUIDE and VERSION.txt.

Status:
Release verified.

---

## 2. MMK Event Ticketing & QR Pass

Location:
software/event-ticketing-qr-pass

Version:
1.0.0

Evidence:
README, CUSTOMER-GUIDE, SALES-SHEET, SECURITY documentation, VERSION, application, website and automated tests.

Status:
Release evidence verified.

Security note:
The project contains local runtime data and a ticket secret. These must remain protected and must not be committed as production secrets.

---

# RELEASE GATE

A project should only enter COMPLETED when the specific version has appropriate evidence for:

1. Working product
2. Testing
3. Documentation
4. Security review where applicable
5. Version
6. Packaging/release artifact where applicable
7. Preservation/backup
8. Customer-ready state where applicable

A VERSION file alone does not prove completion.

---

# PROJECT MOVEMENT RULE

Do not physically move project folders simply because their shelf changes.

Shelf changes are management changes first.

If physical movement becomes necessary:

INSPECT
→ BACKUP
→ CHECK
→ MOVE ONLY IF NECESSARY
→ VERIFY
→ PRESERVE

---

# VERSION RULE

If a COMPLETED product enters new development:

COMPLETED v1.x
→ ACTIVE next development cycle
→ TEST
→ RELEASE
→ COMPLETED new version

---

# SAFETY RULE

Never use the four-shelf system as a reason to delete unfinished work.

Historical, experimental and abandoned-looking work must be inspected before any deletion decision.


---

## 3. MMK Business Website

Source:
templates/mmk-business-website

Release:
releases/MMK-Business-Website-v1.0.0

Package:
releases/MMK-Business-Website-v1.0.0.zip

Version:
1.0.0

Evidence:
Reusable generic website template, MMK_WORKSHOP working demo, README, CUSTOMER-GUIDE, VERSION, automated template tests, browser/mobile testing, clean release package and verified ZIP integrity.

Status:
Release verified; Founder Final Approval: APPROVED.

---

