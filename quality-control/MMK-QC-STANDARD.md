# MMK Quality Control Standard

Version: 0.1.1
System: MMK-QC
Owner: MMK Founder

## Purpose

MMK-QC is the quality checkpoint between building an MMK project
and placing that project on the completed shelf or delivering it
to a customer.

No project should be treated as production-ready simply because
AI generated the code or because the application appears to run.

QC documentation may be located at the project root or one level
below it, such as `core/README.md`, when that structure is intentional.

## Core principle

AI + MMK Founder + Real Problem + Testing + Human Review

## Inspection gates

1. PROBLEM
   - Is the problem clearly defined?
   - Is there a real intended user/customer?
   - Is the proposed solution understandable?

2. FOUNDER CONTRIBUTION
   - What idea came from the MMK Founder?
   - What decisions were made by the Founder?
   - What was changed or improved by the Founder?
   - Is there evidence of human review?

3. PRODUCT
   - Does the product solve the stated problem?
   - Are the main features present?
   - Are unnecessary/random features avoided?

4. CODE
   - Does the code run?
   - Are obvious errors present?
   - Are tests available where appropriate?
   - Is the structure understandable?

5. SECURITY
   - No accidental secrets.
   - No obvious unsafe configuration.
   - No unnecessary exposure of private information.
   - No destructive changes without approval.

6. USER EXPERIENCE
   - Can the intended user understand it?
   - Can the main workflow be completed?
   - Does it work on the intended device?
   - Is the interface usable?

7. DOCUMENTATION
   - README exists.
   - Installation/use instructions exist where needed.
   - Customer documentation exists where needed.
   - Version information is recorded.

8. TESTING
   - Functional testing completed.
   - Important workflows tested.
   - Failures recorded.
   - Fixes retested.

9. INTELLECTUAL PROPERTY / ASSETS
   - MMK-owned assets identified.
   - Third-party assets identified where applicable.
   - Licences/permissions checked where applicable.
   - Product identity and version recorded.

10. CUSTOMER READINESS
   - Customer workflow tested.
   - Customer instructions ready.
   - Contact/support information ready.
   - Release package checked.

11. FOUNDER FINAL APPROVAL
   - Founder has personally reviewed the product.
   - Founder decides whether it is ready for release.

## Results

PASS
    All required gates satisfied.

PASS WITH WARNINGS
    Product works, but documented non-blocking issues remain.

FOUNDER REVIEW REQUIRED
    Technical checks may pass, but human/business/IP decisions remain.

NEEDS IMPROVEMENT
    Product requires additional work before release.

FAIL
    A blocking problem prevents release.

## Shelf rule

A product must not move to COMPLETED merely because an automated
inspection passes.

Automated inspection + human inspection + Founder approval are required.

## Principle

BUILD
CHECK
TEST
IMPROVE
CHECK AGAIN
RELEASE
PRESERVE
