"use strict";

const OB_STORAGE_KEY = "mmk_ob_occurrences";
const OB_LAST_OCCURRENCE_KEY = "mmk_ob_last_occurrence";
const OB_STORAGE_VERSION = 1;

function getStoredOccurrences() {
  try {
    const raw = localStorage.getItem(OB_STORAGE_KEY);

    if (!raw) {
      return [];
    }

    const parsed = JSON.parse(raw);

    if (!Array.isArray(parsed)) {
      throw new Error("Stored O.B. data must be an array.");
    }

    return sanitizeStoredRecords(parsed);
  } catch (error) {
    console.error("MMK O.B. storage read error:", error);
    throw new Error("Stored occurrence data is invalid or corrupted.");
  }
}

function saveStoredOccurrences(records) {
  if (!Array.isArray(records)) {
    throw new Error("O.B. records must be an array.");
  }

  const sanitized = sanitizeStoredRecords(records);

  localStorage.setItem(
    OB_STORAGE_KEY,
    JSON.stringify(sanitized)
  );

  return sanitized;
}

function saveLastOccurrence(record) {
  if (!record || typeof record !== "object") {
    throw new Error("Invalid last occurrence record.");
  }

  localStorage.setItem(
    OB_LAST_OCCURRENCE_KEY,
    JSON.stringify({
      ...record,
      storageVersion: OB_STORAGE_VERSION
    })
  );
}

function getLastOccurrence() {
  try {
    const raw = localStorage.getItem(OB_LAST_OCCURRENCE_KEY);

    if (!raw) {
      return null;
    }

    const parsed = JSON.parse(raw);

    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      throw new Error("Invalid last occurrence data.");
    }

    return parsed;
  } catch (error) {
    console.error("MMK O.B. last-occurrence read error:", error);
    return null;
  }
}

function clearStoredOccurrences() {
  localStorage.removeItem(OB_STORAGE_KEY);
  localStorage.removeItem(OB_LAST_OCCURRENCE_KEY);
}

function getStorageVersion() {
  return OB_STORAGE_VERSION;
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    OB_STORAGE_KEY,
    OB_LAST_OCCURRENCE_KEY,
    OB_STORAGE_VERSION,
    getStorageVersion,
    getStoredOccurrences,
    saveStoredOccurrences,
    saveLastOccurrence,
    getLastOccurrence,
    clearStoredOccurrences
  };
}

console.log("MMK O.B. STORAGE INTEGRITY v0.1.0: PASS");
