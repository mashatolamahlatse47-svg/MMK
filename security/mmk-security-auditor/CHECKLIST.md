# MMK Security Auditor - Assessment Checklist

## A. Authorization
- [ ] Authorization document exists.
- [ ] Authorized representative is identified.
- [ ] Assessment period is defined.
- [ ] Authorized targets are identified.
- [ ] Authorized activities are identified.
- [ ] Exclusions are documented.

## B. Scope Gate
- [ ] Scope configuration loads successfully.
- [ ] Assessment status is AUTHORIZED.
- [ ] Target matches an authorized target.
- [ ] Port matches an authorized port.
- [ ] Activity is explicitly allowed.
- [ ] Unauthorized requests are denied.
- [ ] Denied requests do not proceed to testing.

## C. Controlled Testing
- [ ] Test is within the authorized scope.
- [ ] Test is appropriate to the approved purpose.
- [ ] Test is non-destructive.
- [ ] No denial-of-service activity is performed.
- [ ] No unauthorized access is attempted.

## D. Evidence
- [ ] Evidence contains a timestamp.
- [ ] Evidence identifies the target.
- [ ] Evidence identifies the port or service.
- [ ] Evidence records the command or test.
- [ ] Tool output is preserved.
- [ ] Historical evidence is not overwritten.
- [ ] Evidence referenced by findings exists.

## E. Findings
- [ ] Finding has a unique ID.
- [ ] Severity is valid.
- [ ] Asset is identified.
- [ ] Observation is factual.
- [ ] Evidence is referenced.
- [ ] Risk is documented.
- [ ] Recommendation is documented.
- [ ] Status is documented.
- [ ] Finding does not claim a vulnerability without supporting evidence.

## F. Report
- [ ] Finding validation passes.
- [ ] Report identifies the assessment.
- [ ] Report identifies the target.
- [ ] Report includes the finding.
- [ ] Report includes evidence references.
- [ ] Report distinguishes observation from vulnerability.
- [ ] Report does not exceed the available evidence.

## G. Founder + AI Review
- [ ] MMK Founder defined the assessment purpose.
- [ ] MMK Founder confirmed authorization.
- [ ] MMK Founder reviewed scope.
- [ ] AI-assisted analysis was reviewed by a human.
- [ ] Findings were reviewed before finalization.
- [ ] Final report received human approval.

## H. Preservation
- [ ] Authorization is preserved.
- [ ] Scope configuration is preserved.
- [ ] Evidence is preserved.
- [ ] Findings are preserved.
- [ ] Reports are preserved.
- [ ] Changes are reviewed before Git commit.
