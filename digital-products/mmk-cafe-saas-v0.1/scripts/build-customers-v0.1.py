from pathlib import Path

app = Path("app/app.js")
css = Path("app/style.css")

s = app.read_text()

if 'const CUSTOMERS_KEY = "mmkCafeCustomers";' in s:
    raise SystemExit("STOP: Customers build already exists.")

s = s.replace(
    'const ORDERS_KEY = "mmkCafeOrders";',
    'const ORDERS_KEY = "mmkCafeOrders";\nconst CUSTOMERS_KEY = "mmkCafeCustomers";\nconst CUSTOMER_CONFIG_KEY = "mmkCafeCustomerConfig";'
)

placeholder = '''  customers: {
    title: "Customers",
    render: () => `
      <p class="eyebrow">CUSTOMERS</p>
      <h2>Customers</h2>
      <p class="muted">Customer records will be managed here.</p>
    `
  },'''

replacement = '''  customers: {
    title: "Customers",
    render: renderCustomers
  },'''

if placeholder not in s:
    raise SystemExit("ERROR: Customers placeholder not found.")

s = s.replace(placeholder, replacement)

marker = "function getMenu() {"

module = r'''
function getCustomers() {
  try {
    const data = JSON.parse(localStorage.getItem(CUSTOMERS_KEY) || "[]");
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}

function saveCustomers(customers) {
  localStorage.setItem(CUSTOMERS_KEY, JSON.stringify(customers));
}

function getCustomerConfig() {
  try {
    const data = JSON.parse(localStorage.getItem(CUSTOMER_CONFIG_KEY) || "{}");
    return {
      defaultStatus: data.defaultStatus || "ACTIVE",
      emailOptional: data.emailOptional !== false,
      notesOptional: data.notesOptional !== false
    };
  } catch {
    return {
      defaultStatus: "ACTIVE",
      emailOptional: true,
      notesOptional: true
    };
  }
}

function saveCustomerConfig(config) {
  localStorage.setItem(CUSTOMER_CONFIG_KEY, JSON.stringify(config));
}

function createCustomerId(customers) {
  const numbers = customers
    .map(c => Number(String(c.id || "").replace("CUS-", "")))
    .filter(Number.isFinite);

  const next = numbers.length ? Math.max(...numbers) + 1 : 1;
  return `CUS-${String(next).padStart(4, "0")}`;
}

function getCustomerStats(customerId) {
  const orders = getOrders().filter(order => order.customerId === customerId);

  return {
    orderCount: orders.length,
    totalSpent: orders.reduce((sum, order) => sum + Number(order.total || 0), 0)
  };
}

function escapeCustomerText(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function renderCustomers() {
  const customers = getCustomers();
  const config = getCustomerConfig();

  return `
    <p class="eyebrow">CUSTOMERS</p>
    <h2>Customer Management</h2>
    <p class="muted">Manage customers and their café relationship.</p>

    <div class="card-panel customer-config">
      <h3>Customer Configuration</h3>

      <div class="form-grid">
        <label>
          Default Status
          <select id="customer-default-status">
            <option value="ACTIVE" ${config.defaultStatus === "ACTIVE" ? "selected" : ""}>Active</option>
            <option value="INACTIVE" ${config.defaultStatus === "INACTIVE" ? "selected" : ""}>Inactive</option>
          </select>
        </label>

        <label class="checkbox-row">
          <input id="customer-email-optional" type="checkbox" ${config.emailOptional ? "checked" : ""}>
          Email optional
        </label>

        <label class="checkbox-row">
          <input id="customer-notes-optional" type="checkbox" ${config.notesOptional ? "checked" : ""}>
          Notes optional
        </label>
      </div>

      <button class="primary-button" id="save-customer-config" type="button">
        Save Customer Configuration
      </button>
    </div>

    <div class="card-panel">
      <h3 id="customer-form-title">Add Customer</h3>

      <form id="customer-form">
        <input id="customer-id" type="hidden">

        <div class="form-grid">
          <label>
            Name *
            <input id="customer-name" type="text" required placeholder="Customer name">
          </label>

          <label>
            Phone *
            <input id="customer-phone" type="tel" required placeholder="Phone number">
          </label>

          <label>
            Email
            <input id="customer-email" type="email" placeholder="customer@example.com">
          </label>

          <label>
            Status
            <select id="customer-status">
              <option value="ACTIVE">Active</option>
              <option value="INACTIVE">Inactive</option>
            </select>
          </label>

          <label class="full-width">
            Notes
            <textarea id="customer-notes" rows="3" placeholder="Optional notes"></textarea>
          </label>
        </div>

        <div class="form-actions">
          <button class="primary-button" type="submit">Save Customer</button>
          <button class="secondary-button" id="cancel-customer-edit" type="button" hidden>
            Cancel Edit
          </button>
        </div>
      </form>
    </div>

    <div class="customer-list-header">
      <h3>Customers (${customers.length})</h3>
      <input id="customer-search" type="search" placeholder="Search customers...">
    </div>

    <div id="customer-list" class="customer-list">
      ${renderCustomerList(customers)}
    </div>
  `;
}

function renderCustomerList(customers) {
  if (!customers.length) {
    return `<p class="muted">No customers recorded yet.</p>`;
  }

  return customers.map(customer => {
    const stats = getCustomerStats(customer.id);

    return `
      <article class="customer-card" data-search="${escapeCustomerText(
        `${customer.id} ${customer.name} ${customer.phone} ${customer.email || ""}`
      ).toLowerCase()}">

        <div class="customer-card-main">
          <div>
            <p class="eyebrow">${escapeCustomerText(customer.id)}</p>
            <h3>${escapeCustomerText(customer.name)}</h3>
            <p>${escapeCustomerText(customer.phone)}</p>
            ${customer.email ? `<p>${escapeCustomerText(customer.email)}</p>` : ""}
            ${customer.notes ? `<p class="muted">${escapeCustomerText(customer.notes)}</p>` : ""}
          </div>

          <span class="customer-status">
            ${escapeCustomerText(customer.status)}
          </span>
        </div>

        <div class="customer-stats">
          <span>Orders: <strong>${stats.orderCount}</strong></span>
          <span>Spent: <strong>R${stats.totalSpent.toFixed(2)}</strong></span>
        </div>

        <div class="customer-actions">
          <button class="secondary-button edit-customer" data-id="${escapeCustomerText(customer.id)}">
            Edit
          </button>

          <button class="danger-button delete-customer" data-id="${escapeCustomerText(customer.id)}">
            Delete
          </button>
        </div>
      </article>
    `;
  }).join("");
}

function bindCustomerEvents() {
  const form = document.getElementById("customer-form");
  const list = document.getElementById("customer-list");
  const search = document.getElementById("customer-search");
  const configButton = document.getElementById("save-customer-config");
  const cancelButton = document.getElementById("cancel-customer-edit");

  if (!form || !list) return;

  document.getElementById("customer-status").value =
    getCustomerConfig().defaultStatus;

  form.addEventListener("submit", event => {
    event.preventDefault();

    const customers = getCustomers();
    const id = document.getElementById("customer-id").value.trim();

    const customer = {
      id: id || createCustomerId(customers),
      name: document.getElementById("customer-name").value.trim(),
      phone: document.getElementById("customer-phone").value.trim(),
      email: document.getElementById("customer-email").value.trim(),
      status: document.getElementById("customer-status").value,
      notes: document.getElementById("customer-notes").value.trim(),
      updatedAt: new Date().toISOString()
    };

    if (!customer.name || !customer.phone) return;

    const index = customers.findIndex(c => c.id === customer.id);

    if (index >= 0) {
      customer.createdAt = customers[index].createdAt;
      customers[index] = customer;
    } else {
      customer.createdAt = new Date().toISOString();
      customers.push(customer);
    }

    saveCustomers(customers);
    showSection("customers");
  });

  cancelButton.addEventListener("click", () => {
    showSection("customers");
  });

  search.addEventListener("input", () => {
    const query = search.value.trim().toLowerCase();

    list.querySelectorAll(".customer-card").forEach(card => {
      card.hidden = query && !card.dataset.search.includes(query);
    });
  });

  list.addEventListener("click", event => {
    const edit = event.target.closest(".edit-customer");
    const remove = event.target.closest(".delete-customer");

    if (edit) {
      const customer = getCustomers().find(c => c.id === edit.dataset.id);
      if (!customer) return;

      document.getElementById("customer-id").value = customer.id;
      document.getElementById("customer-name").value = customer.name;
      document.getElementById("customer-phone").value = customer.phone;
      document.getElementById("customer-email").value = customer.email || "";
      document.getElementById("customer-status").value = customer.status;
      document.getElementById("customer-notes").value = customer.notes || "";

      document.getElementById("customer-form-title").textContent = "Edit Customer";
      cancelButton.hidden = false;

      document.getElementById("customer-name").focus();
    }

    if (remove) {
      const id = remove.dataset.id;
      const stats = getCustomerStats(id);

      if (stats.orderCount > 0) {
        alert("This customer has saved orders. Set them to INACTIVE instead of deleting them.");
        return;
      }

      const customer = getCustomers().find(c => c.id === id);

      if (customer && confirm(`Delete ${customer.name}?`)) {
        saveCustomers(getCustomers().filter(c => c.id !== id));
        showSection("customers");
      }
    }
  });

  configButton.addEventListener("click", () => {
    saveCustomerConfig({
      defaultStatus: document.getElementById("customer-default-status").value,
      emailOptional: document.getElementById("customer-email-optional").checked,
      notesOptional: document.getElementById("customer-notes-optional").checked
    });

    document.getElementById("customer-status").value =
      getCustomerConfig().defaultStatus;
  });
}

'''

if marker not in s:
    raise SystemExit("ERROR: getMenu marker not found.")

s = s.replace(marker, module + marker, 1)

old_show = """  workspace.innerHTML = section.render();

  bindMenuEvents();
  bindOrderEvents();
}"""

new_show = '''  workspace.innerHTML = section.render();

  if (name === "customers") {
    bindCustomerEvents();
  }
}'''

if old_show not in s:
    raise SystemExit("ERROR: showSection target not found.")

s = s.replace(old_show, new_show, 1)

app.write_text(s)

css_text = css.read_text()

if "/* Customers V0.1 */" not in css_text:
    css.write_text(css_text + r'''

/* Customers V0.1 */
.card-panel {
  margin-top: 18px;
  padding: 18px;
  border-radius: 14px;
}

.form-grid {
  display: grid;
  gap: 14px;
  margin: 16px 0;
}

.form-grid label {
  display: grid;
  gap: 7px;
}

.form-grid input,
.form-grid select,
.form-grid textarea,
#customer-search {
  width: 100%;
  box-sizing: border-box;
}

.full-width {
  grid-column: 1 / -1;
}

.checkbox-row {
  display: flex !important;
  align-items: center;
  gap: 8px !important;
}

.checkbox-row input {
  width: auto;
}

.form-actions,
.customer-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.customer-list-header {
  display: grid;
  gap: 12px;
  margin: 24px 0 14px;
}

.customer-list {
  display: grid;
  gap: 14px;
}

.customer-card {
  padding: 16px;
  border-radius: 14px;
}

.customer-card-main {
  display: flex;
  justify-content: space-between;
  gap: 14px;
}

.customer-status {
  font-size: 0.78rem;
  font-weight: 700;
  white-space: nowrap;
}

.customer-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  margin: 14px 0;
  padding-top: 12px;
  border-top: 1px solid rgba(255,255,255,0.08);
}

@media (min-width: 700px) {
  .form-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .customer-list-header {
    grid-template-columns: 1fr minmax(220px, 320px);
    align-items: center;
  }
}
''')

print("CUSTOMERS BUILD APPLIED")
