# MMK Security Auditor - Methodology

## 1. Authorization

Every assessment begins with documented authorization from the system owner or an authorized representative.

Authorization should identify the assessment, authorized representative, assessment period, targets, activities, and exclusions.

If authorization is missing or unclear, testing stops.

## 2. Scope

The assessment scope defines exactly what may be tested.

The scope gate must approve the requested target, port, and activity before the corresponding test executes.

## 3. Controlled Testing

Testing begins with the least intrusive activity appropriate to the approved assessment.

For the current MMK training lab, the approved activities are port discovery and service version detection.

Testing outside the approved activity list is denied.

## 4. Evidence Collection

Each test should produce evidence that can be reviewed later.

Evidence should include a timestamp, target, port or service, command, and tool output.

Historical evidence must be preserved and must not be silently overwritten.

## 5. Findings

A finding records an observed security condition.

Findings should contain a finding ID, severity, asset, observation, evidence references, risk, recommendation, and status.

An observed port or service does not by itself prove a vulnerability.

## 6. Validation

Findings must pass structural validation before report generation.

## 7. Reporting

Reports must clearly identify the assessment, target, finding, severity, observation, evidence, risk, and recommendation.

Reports must not claim more than the available evidence supports.

## 8. Human Review

The MMK Founder reviews assessment conclusions before a report is considered final.

AI assistance does not replace human authorization or review.

## 9. Stop Conditions

Testing stops when authorization cannot be verified, the target is outside scope, the activity is prohibited, scope cannot be loaded, or evidence cannot be safely preserved.
