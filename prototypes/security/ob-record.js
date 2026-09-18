"use strict";

const form = document.getElementById("occurrenceForm");
const result = document.getElementById("result");

form.addEventListener("submit", function (event) {
  event.preventDefault();

  const occurrence = {
    occurrenceNumber: document.getElementById("occurrenceNumber").value.trim(),
    date: document.getElementById("occurrenceDate").value,
    time: document.getElementById("occurrenceTime").value,
    location: document.getElementById("location").value.trim(),
    type: document.getElementById("occurrenceType").value,
    description: document.getElementById("description").value.trim(),
    personInvolved: document.getElementById("personInvolved").value.trim(),
    officer: document.getElementById("officer").value.trim(),
    actionTaken: document.getElementById("actionTaken").value.trim(),
    status: document.getElementById("status").value
  };

  let records = [];

  try {
    records = getStoredOccurrences();
  } catch (error) {
    result.textContent =
      "Stored occurrence data is invalid. No record was saved.";
    result.dataset.status = "error";
    console.error("MMK O.B. storage validation error:", error);
    return;
  }

  const validation = validateOccurrence(occurrence, records);

  if (!validation.valid) {
    result.textContent =
      "Occurrence not saved: " + validation.errors.join(" ");
    result.dataset.status = "error";
    return;
  }

  const protectedOccurrence = {
    ...validation.record,
    ...createRecordMetadata()
  };

  records.push(protectedOccurrence);

  saveStoredOccurrences(records);
  saveLastOccurrence(protectedOccurrence);

  result.textContent =
    "Occurrence " +
    protectedOccurrence.occurrenceNumber +
    " saved successfully.";
  result.dataset.status = "success";

  form.reset();

  renderOccurrences();
});

console.log("MMK O.B. RECORD OCCURRENCE v0.1.0: PASS");


function renderOccurrences() {
  const records = getStoredOccurrences();

  let history = document.getElementById("occurrenceHistory");

  if (!history) {
    history = document.createElement("section");
    history.id = "occurrenceHistory";
    form.parentNode.appendChild(history);
  }

  history.innerHTML = "<h2>Occurrence History</h2>";

  if (records.length === 0) {
    history.innerHTML += "<p>No occurrences recorded.</p>";
    return;
  }

  records.slice().reverse().forEach(function (record, index) {
    const article = document.createElement("article");

    article.innerHTML = `
      <h3>Occurrence ${escapeHtml(record.occurrenceNumber)}</h3>
      <p><strong>Date:</strong> ${escapeHtml(record.date)}</p>
      <p><strong>Time:</strong> ${escapeHtml(record.time)}</p>
      <p><strong>Location:</strong> ${escapeHtml(record.location)}</p>
      <p><strong>Type:</strong> ${escapeHtml(record.type)}</p>
      <p><strong>Description:</strong> ${escapeHtml(record.description)}</p>
      <p><strong>Person Involved:</strong> ${escapeHtml(record.personInvolved || "None recorded")}</p>
      <p><strong>Officer:</strong> ${escapeHtml(record.officer)}</p>
      <p><strong>Action Taken:</strong> ${escapeHtml(record.actionTaken)}</p>
      <p><strong>Status:</strong> ${escapeHtml(record.status)}</p>
      <button type="button" data-index="${records.length - 1 - index}">
        Delete Record
      </button>
      <hr>
    `;

    history.appendChild(article);
  });

  history.querySelectorAll("button[data-index]").forEach(function (button) {
    button.addEventListener("click", function () {
      const records = getStoredOccurrences();

      records.splice(Number(button.dataset.index), 1);

      saveStoredOccurrences(records);

      renderOccurrences();
    });
  });
}


function filterOccurrences() {
  const records = getStoredOccurrences();

  const search = (
    document.getElementById("obSearch")?.value || ""
  ).toLowerCase();

  const type = document.getElementById("obTypeFilter")?.value || "";
  const status = document.getElementById("obStatusFilter")?.value || "";

  const filtered = records.filter(function (record) {
    const searchable = [
      record.occurrenceNumber,
      record.date,
      record.location,
      record.type,
      record.description,
      record.personInvolved,
      record.officer,
      record.actionTaken,
      record.status
    ].join(" ").toLowerCase();

    return (
      searchable.includes(search) &&
      (!type || record.type === type) &&
      (!status || record.status === status)
    );
  });

  renderFilteredOccurrences(filtered);
}

function renderFilteredOccurrences(records) {
  let history = document.getElementById("occurrenceHistory");

  if (!history) {
    history = document.createElement("section");
    history.id = "occurrenceHistory";
    form.parentNode.appendChild(history);
  }

  history.innerHTML = `
    <h2>Occurrence History</h2>
    <label>
      Search
      <input id="obSearch" type="search" placeholder="Search occurrences...">
    </label>

    <label>
      Type
      <select id="obTypeFilter">
        <option value="">All Types</option>
        <option>Theft</option>
        <option>Incident</option>
        <option>Accident</option>
        <option>Access Control</option>
        <option>Suspicious Activity</option>
        <option>Maintenance</option>
        <option>Other</option>
      </select>
    </label>

    <label>
      Status
      <select id="obStatusFilter">
        <option value="">All Statuses</option>
        <option>Open</option>
        <option>Under Review</option>
        <option>Resolved</option>
        <option>Closed</option>
      </select>
    </label>
  `;

  if (records.length === 0) {
    history.innerHTML += "<p>No matching occurrences.</p>";
  }

  records.slice().reverse().forEach(function (record) {
    const article = document.createElement("article");

    article.innerHTML = `
      <h3>Occurrence ${escapeHtml(record.occurrenceNumber)}</h3>
      <p><strong>${escapeHtml(record.date)}</strong> at ${escapeHtml(record.time)}</p>
      <p><strong>Location:</strong> ${escapeHtml(record.location)}</p>
      <p><strong>Type:</strong> ${escapeHtml(record.type)}</p>
      <p><strong>Status:</strong> ${escapeHtml(record.status)}</p>
      <p>${escapeHtml(record.description)}</p>
    `;

    history.appendChild(article);
  });

  document.getElementById("obSearch").addEventListener(
    "input",
    filterOccurrences
  );

  document.getElementById("obTypeFilter").addEventListener(
    "change",
    filterOccurrences
  );

  document.getElementById("obStatusFilter").addEventListener(
    "change",
    filterOccurrences
  );
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

renderOccurrences();

function renderDashboard() {
  const records = getStoredOccurrences();

  let dashboard = document.getElementById("obDashboard");

  if (!dashboard) {
    dashboard = document.createElement("section");
    dashboard.id = "obDashboard";
    document.body.prepend(dashboard);
  }

  const counts = {
    total: records.length,
    open: records.filter(r => r.status === "Open").length,
    review: records.filter(r => r.status === "Under Review").length,
    resolved: records.filter(r => r.status === "Resolved").length,
    closed: records.filter(r => r.status === "Closed").length
  };

  const types = {};

  records.forEach(function (record) {
    types[record.type] = (types[record.type] || 0) + 1;
  });

  dashboard.innerHTML = `
    <h2>O.B. Operational Dashboard</h2>
    <div class="ob-summary">
      <p><strong>Total:</strong> ${counts.total}</p>
      <p><strong>Open:</strong> ${counts.open}</p>
      <p><strong>Under Review:</strong> ${counts.review}</p>
      <p><strong>Resolved:</strong> ${counts.resolved}</p>
      <p><strong>Closed:</strong> ${counts.closed}</p>
    </div>
    <h3>Occurrence Types</h3>
  `;

  const typeList = document.createElement("ul");

  Object.entries(types).forEach(function ([type, count]) {
    const item = document.createElement("li");
    item.textContent = type + ": " + count;
    typeList.appendChild(item);
  });

  if (Object.keys(types).length === 0) {
    const item = document.createElement("li");
    item.textContent = "No occurrences recorded.";
    typeList.appendChild(item);
  }

  dashboard.appendChild(typeList);
}

const originalRenderOccurrences = renderOccurrences;

renderOccurrences = function () {
  originalRenderOccurrences();
  renderDashboard();
};

renderDashboard();

function exportOccurrences() {
  const records = getStoredOccurrences();

  if (records.length === 0) {
    result.textContent = "No occurrences available for export.";
    result.dataset.status = "warning";
    return;
  }

  const lines = [];

  lines.push("MMK SECURITY O.B. REPORT");
  lines.push("========================");
  lines.push("Generated: " + new Date().toISOString());
  lines.push("Total Occurrences: " + records.length);
  lines.push("");

  records.forEach(function (record, index) {
    lines.push("OCCURRENCE " + (index + 1));
    lines.push("------------------------");
    lines.push("Occurrence Number: " + record.occurrenceNumber);
    lines.push("Date: " + record.date);
    lines.push("Time: " + record.time);
    lines.push("Location: " + record.location);
    lines.push("Type: " + record.type);
    lines.push("Description: " + record.description);
    lines.push("Person Involved: " + (record.personInvolved || "None recorded"));
    lines.push("Security Officer: " + record.officer);
    lines.push("Action Taken: " + record.actionTaken);
    lines.push("Status: " + record.status);
    lines.push("");
  });

  const report = lines.join("\n");
  const blob = new Blob([report], { type: "text/plain" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = "mmk-ob-report-" + Date.now() + ".txt";
  link.click();

  URL.revokeObjectURL(url);

  result.textContent = "O.B. report exported successfully.";
  result.dataset.status = "success";
}

function addExportButton() {
  if (document.getElementById("exportObButton")) {
    return;
  }

  const button = document.createElement("button");
  button.id = "exportObButton";
  button.type = "button";
  button.textContent = "Export O.B. Report";

  button.addEventListener("click", exportOccurrences);

  form.parentNode.insertBefore(button, form);
}

addExportButton();
