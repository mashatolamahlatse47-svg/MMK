"use strict";

const assert = require("assert");

const {
  isValidDate,
  isValidTime,
  validateOccurrence,
  createRecordMetadata,
  sanitizeStoredRecords
} = require("../ob-validation.js");

const validRecord = {
  occurrenceNumber: "OB-0001",
  date: "2026-09-18",
  time: "20:30",
  location: "Main Gate",
  type: "Incident",
  description: "Test occurrence",
  personInvolved: "None",
  officer: "Test Officer",
  actionTaken: "Occurrence recorded",
  status: "Open"
};

console.log("================================");
console.log("MMK O.B. 8.11 VALIDATION TESTS");
console.log("================================");

assert.strictEqual(isValidDate("2026-09-18"), true);
assert.strictEqual(isValidDate("2026-02-30"), false);
assert.strictEqual(isValidDate("bad-date"), false);
console.log("Date validation: PASS");

assert.strictEqual(isValidTime("20:30"), true);
assert.strictEqual(isValidTime("25:99"), false);
assert.strictEqual(isValidTime("bad-time"), false);
console.log("Time validation: PASS");

const validResult = validateOccurrence(validRecord, []);
assert.strictEqual(validResult.valid, true);
console.log("Valid occurrence: PASS");

const missingResult = validateOccurrence(
  {
    ...validRecord,
    location: ""
  },
  []
);

assert.strictEqual(missingResult.valid, false);
assert.ok(
  missingResult.errors.some(error => error.includes("Location"))
);
console.log("Required-field protection: PASS");

const duplicateResult = validateOccurrence(
  validRecord,
  [validRecord]
);

assert.strictEqual(duplicateResult.valid, false);
assert.ok(
  duplicateResult.errors.some(error =>
    error.includes("already exists")
  )
);
console.log("Duplicate occurrence protection: PASS");

const invalidTypeResult = validateOccurrence(
  {
    ...validRecord,
    type: "INVALID TYPE"
  },
  []
);

assert.strictEqual(invalidTypeResult.valid, false);
console.log("Occurrence-type protection: PASS");

const invalidStatusResult = validateOccurrence(
  {
    ...validRecord,
    status: "INVALID STATUS"
  },
  []
);

assert.strictEqual(invalidStatusResult.valid, false);
console.log("Status protection: PASS");

const metadata = createRecordMetadata();

assert.ok(metadata.id.startsWith("OB-"));
assert.ok(metadata.createdAt);
assert.ok(metadata.updatedAt);
assert.strictEqual(metadata.recordVersion, 1);
console.log("Record metadata: PASS");

const sanitized = sanitizeStoredRecords([
  validRecord,
  null,
  "malformed",
  {
    ...validRecord,
    location: "  Main Gate  "
  }
]);

assert.strictEqual(sanitized.length, 2);
assert.strictEqual(sanitized[1].location, "Main Gate");
console.log("Stored-record sanitization: PASS");

console.log("================================");
console.log("ALL O.B. 8.11 TESTS: PASS");
console.log("================================");
