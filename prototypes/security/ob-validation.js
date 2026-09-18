"use strict";

const OB_OCCURRENCE_TYPES = [
  "Theft",
  "Incident",
  "Accident",
  "Access Control",
  "Suspicious Activity",
  "Maintenance",
  "Other"
];

const OB_STATUSES = [
  "Open",
  "Under Review",
  "Resolved",
  "Closed"
];

function isValidDate(value) {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return false;
  }

  const date = new Date(value + "T00:00:00");

  return (
    !Number.isNaN(date.getTime()) &&
    date.getFullYear() === Number(value.slice(0, 4)) &&
    date.getMonth() + 1 === Number(value.slice(5, 7)) &&
    date.getDate() === Number(value.slice(8, 10))
  );
}

function isValidTime(value) {
  return (
    typeof value === "string" &&
    /^([01]\d|2[0-3]):[0-5]\d$/.test(value)
  );
}

function normalizeRecord(record) {
  if (!record || typeof record !== "object" || Array.isArray(record)) {
    return null;
  }

  return {
    occurrenceNumber: String(record.occurrenceNumber || "").trim(),
    date: String(record.date || "").trim(),
    time: String(record.time || "").trim(),
    location: String(record.location || "").trim(),
    type: String(record.type || "").trim(),
    description: String(record.description || "").trim(),
    personInvolved: String(record.personInvolved || "").trim(),
    officer: String(record.officer || "").trim(),
    actionTaken: String(record.actionTaken || "").trim(),
    status: String(record.status || "").trim()
  };
}

function validateOccurrence(record, existingRecords = []) {
  const errors = [];

  const normalized = normalizeRecord(record);

  if (!normalized) {
    return {
      valid: false,
      errors: ["Invalid occurrence record."]
    };
  }

  const requiredFields = [
    ["occurrenceNumber", "Occurrence number"],
    ["date", "Date"],
    ["time", "Time"],
    ["location", "Location"],
    ["type", "Occurrence type"],
    ["description", "Description"],
    ["officer", "Security officer"],
    ["actionTaken", "Action taken"],
    ["status", "Status"]
  ];

  requiredFields.forEach(function ([field, label]) {
    if (!normalized[field]) {
      errors.push(label + " is required.");
    }
  });

  if (
    normalized.occurrenceNumber &&
    normalized.occurrenceNumber.length > 100
  ) {
    errors.push("Occurrence number is too long.");
  }

  if (normalized.date && !isValidDate(normalized.date)) {
    errors.push("Date is invalid.");
  }

  if (normalized.time && !isValidTime(normalized.time)) {
    errors.push("Time is invalid.");
  }

  if (
    normalized.type &&
    !OB_OCCURRENCE_TYPES.includes(normalized.type)
  ) {
    errors.push("Occurrence type is not allowed.");
  }

  if (
    normalized.status &&
    !OB_STATUSES.includes(normalized.status)
  ) {
    errors.push("Status is not allowed.");
  }

  const duplicate = existingRecords.some(function (existing) {
    return (
      existing &&
      String(existing.occurrenceNumber || "").trim() ===
        normalized.occurrenceNumber
    );
  });

  if (normalized.occurrenceNumber && duplicate) {
    errors.push("Occurrence number already exists.");
  }

  return {
    valid: errors.length === 0,
    errors,
    record: normalized
  };
}

function createRecordMetadata() {
  const now = new Date().toISOString();

  return {
    id:
      "OB-" +
      Date.now().toString(36).toUpperCase() +
      "-" +
      Math.random().toString(36).slice(2, 8).toUpperCase(),
    createdAt: now,
    updatedAt: now,
    recordVersion: 1
  };
}

function sanitizeStoredRecords(records) {
  if (!Array.isArray(records)) {
    return [];
  }

  return records
    .filter(function (record) {
      return record && typeof record === "object" && !Array.isArray(record);
    })
    .map(function (record) {
      return {
        ...record,
        occurrenceNumber: String(record.occurrenceNumber || "").trim(),
        date: String(record.date || "").trim(),
        time: String(record.time || "").trim(),
        location: String(record.location || "").trim(),
        type: String(record.type || "").trim(),
        description: String(record.description || "").trim(),
        personInvolved: String(record.personInvolved || "").trim(),
        officer: String(record.officer || "").trim(),
        actionTaken: String(record.actionTaken || "").trim(),
        status: String(record.status || "").trim()
      };
    });
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    OB_OCCURRENCE_TYPES,
    OB_STATUSES,
    isValidDate,
    isValidTime,
    normalizeRecord,
    validateOccurrence,
    createRecordMetadata,
    sanitizeStoredRecords
  };
}
