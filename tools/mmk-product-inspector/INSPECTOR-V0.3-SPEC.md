# MMK PRODUCT INSPECTOR
## Version 0.3.1 Specification

### 1. PURPOSE

MMK Product Inspector is a read-only inspection tool that checks
MMK products against the requirements applicable to their product type.

The Inspector reports the current structural state of a product.
It does not decide product direction and does not automatically fix
products.

### 2. CORE PRINCIPLE

PRODUCT
→ IDENTIFY TYPE
→ LOAD APPLICABLE REQUIREMENTS
→ INSPECT
→ REPORT EVIDENCE
→ OWNER DECIDES WHAT TO CHANGE

### 3. READ-ONLY RULE

The Inspector must never:

- Delete files
- Move files
- Modify product files
- Create product files
- Install software
- Commit changes
- Push changes
- Change product direction

### 4. PRODUCT TYPES

The Inspector must support:

- SOFTWARE
- DIGITAL PRODUCT
- ART
- CLOTHING
- COURSE / EDUCATION
- SERVICE
- EVENT / CULTURE
- OTHER

### 5. PRODUCT TYPE DETECTION

The Inspector should determine product type from an explicit,
machine-readable product identity/configuration where available.

If product type cannot be confidently determined:

PRODUCT TYPE = REVIEW

The Inspector must not guess silently.

### 6. UNIVERSAL CHECKS

Every product should be checked for:

- Identity
- Product type
- Version
- Documentation

The Inspector should report whether each requirement is:

- PASS
- REVIEW
- MISSING
- ERROR
- NOT APPLICABLE

### 7. SOFTWARE CHECKS

Software checks may include:

- Application/runtime
- Backend/server where applicable
- Website/UI where applicable
- Database/data where applicable
- Tests
- Security documentation
- Customer documentation
- Installation/deployment information where applicable

The Inspector must not require every possible software component.

### 8. DIGITAL PRODUCT CHECKS

Digital product checks may include:

- Master/source asset
- Release/export asset
- Documentation
- Version
- Licensing/ownership information

### 9. ART CHECKS

Art product checks may include:

- Master artwork
- High-resolution/export asset
- Catalogue information
- Ownership/IP information

### 10. CLOTHING CHECKS

Clothing product checks may include:

- Master design
- Product specification
- Mockup/sample
- Catalogue/product information

### 11. COURSE / EDUCATION CHECKS

Course checks may include:

- Course identity
- Learning objectives
- Lessons/material
- Resources
- Exercises
- Assessment where applicable
- Access model

### 12. SERVICE CHECKS

Service checks may include:

- Service identity
- Scope
- Deliverables
- Delivery process
- Support
- Feedback/improvement process

### 13. EVENT / CULTURE CHECKS

Event/culture checks may include:

- Event identity
- Event materials
- Delivery information
- Documentation
- Customer/participant information where applicable

### 14. OTHER

OTHER products must not automatically inherit the full SOFTWARE
checklist.

They should receive universal checks and be marked REVIEW for
requirements requiring human determination.

### 15. APPLICABILITY

The Inspector must distinguish:

PASS
Requirement exists and is verified.

REVIEW
Requirement exists or can be partially identified but requires
human review.

MISSING
An applicable expected requirement was not found.

ERROR
Inspection could not be completed correctly.

NOT APPLICABLE
The requirement does not apply to this product.

### 16. TESTING

The existence of a tests directory does not mean tests pass.

The Inspector may verify that test files exist, but actual test
execution must be separately reported.

Example:

TEST STRUCTURE = REVIEW
TEST EXECUTION = NOT VERIFIED

### 17. EVIDENCE

Inspection results should identify what was checked.

Where practical, reports should include:

- Requirement
- Status
- Evidence
- Product type
- Product version
- Inspector version

### 18. VERSIONING

Inspector source and VERSION file must contain the same Inspector
version.

Current baseline:

Inspector = 0.2.0

Target implementation:

Inspector = 0.3.0

### 19. PRODUCT CONTRACT

The Inspector v0.3 design is based on:

PRODUCT-CONTRACT.md

Contract version:

1.0.0

The Product Contract defines the broader MMK production rules.
The Inspector implements structural/read-only checks derived from
those rules.

### 20. REAL MMK PRODUCT COMPATIBILITY

The Inspector must support different legitimate product structures.

Examples observed in MMK include:

software/mmk-pre-order-system
software/mmk-local-intercom-queue
software/event-ticketing-qr-pass
products/stock-profit-calculator-record

The Inspector must not assume every product contains:

- website/
- backend/
- database/
- tests/
- CUSTOMER-GUIDE.md
- SECURITY.md

unless those requirements are applicable to the product type and
product stage.

### 21. SOURCE VS RELEASE PACKAGE

The Inspector must distinguish between:

SOURCE PRODUCT
and
CUSTOMER RELEASE PACKAGE

A development/source directory should not automatically fail because
customer-facing release-package files are absent.

### 22. REPORTING

The report should clearly show:

MMK PRODUCT INSPECTOR
Inspector Version
Product
Path
Product Type
Product Version

Then applicable checks and their statuses.

Overall result:

ERROR
if an inspection error exists.

REVIEW
if applicable requirements are missing or require review.

PASS
if all applicable checks are verified.

### 23. OWNER CONTROL

The Inspector provides evidence.

It does not make final product decisions.

The Owner decides:

- Whether a missing item is actually required
- Whether a product is ready
- Whether a product should be changed
- Whether a product should be released
- Whether a requirement should be marked not applicable

### 24. FUTURE EXTENSIONS

Future versions may add:

- Machine-readable product manifests
- Product stage awareness
- Release-package inspection
- Test-result ingestion
- Security-result ingestion
- Ownership/IP metadata inspection
- JSON reports
- HTML reports
- Release-gate support

These are outside the initial v0.3 implementation unless explicitly
approved by the Owner.

END OF INSPECTOR V0.3 SPECIFICATION
