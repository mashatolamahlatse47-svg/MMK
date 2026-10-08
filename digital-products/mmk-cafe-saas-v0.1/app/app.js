const workspace = document.getElementById("workspace");

const MENU_KEY = "mmkCafeMenu";
const ORDERS_KEY = "mmkCafeOrders";
const CUSTOMERS_KEY = "mmkCafeCustomers";
const CUSTOMER_CONFIG_KEY = "mmkCafeCustomerConfig";

let currentOrder = [];

const sections = {
  dashboard: {
    title: "Dashboard",
    render: renderDashboard
  },
  menu: {
    title: "Menu",
    render: renderMenu
  },
  orders: {
    title: "Orders",
    render: renderOrders
  },
  customers: {
    title: "Customers",
    render: renderCustomers
  },
  settings: {
    title: "Settings",
    render: renderSettings
  }
};


function startOfDay(date = new Date()) {
  const value = new Date(date);
  value.setHours(0, 0, 0, 0);
  return value;
}

function startOfWeek(date = new Date()) {
  const value = startOfDay(date);
  const day = value.getDay();
  const mondayOffset = day === 0 ? 6 : day - 1;
  value.setDate(value.getDate() - mondayOffset);
  return value;
}

function startOfMonth(date = new Date()) {
  const value = startOfDay(date);
  value.setDate(1);
  return value;
}

function orderDateValue(order) {
  const parsed = new Date(order.date);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function ordersSince(date) {
  const start = startOfDay(date);

  return getOrders().filter((order) => {
    const orderDate = orderDateValue(order);
    return orderDate && orderDate >= start;
  });
}

function ordersSinceDateTime(date) {
  const start = new Date(date);

  return getOrders().filter((order) => {
    const orderDate = orderDateValue(order);
    return orderDate && orderDate >= start;
  });
}

function sumOrderTotals(orders) {
  return orders.reduce(
    (sum, order) => sum + Number(order.total || 0),
    0
  );
}

function formatRand(value) {
  return `R${Number(value || 0).toFixed(2)}`;
}

function getDashboardStats() {
  const now = new Date();
  const allOrders = getOrders();

  const todayOrders = ordersSince(now);
  const yesterdayStart = startOfDay(now);
  yesterdayStart.setDate(yesterdayStart.getDate() - 1);

  const weekOrders = ordersSince(startOfWeek(now));
  const monthOrders = ordersSince(startOfMonth(now));

  const activeStatuses = ["NEW", "PREPARING", "READY"];

  const activeOrders = allOrders.filter((order) =>
    activeStatuses.includes(order.status)
  );

  const statusCounts = {
    NEW: 0,
    PREPARING: 0,
    READY: 0,
    COMPLETED: 0,
    CANCELLED: 0
  };

  allOrders.forEach((order) => {
    if (Object.prototype.hasOwnProperty.call(statusCounts, order.status)) {
      statusCounts[order.status] += 1;
    }
  });

  const yesterdayOrders = getOrders().filter((order) => {
    const orderDate = orderDateValue(order);
    if (!orderDate) return false;

    return (
      orderDate >= yesterdayStart &&
      orderDate < startOfDay(now)
    );
  });

  return {
    todaySales: sumOrderTotals(todayOrders),
    todayOrders: todayOrders.length,
    activeOrders: activeOrders.length,
    customers: getCustomers().length,
    weekSales: sumOrderTotals(weekOrders),
    monthSales: sumOrderTotals(monthOrders),
    yesterdaySales: sumOrderTotals(yesterdayOrders),
    statusCounts
  };
}

function getDashboardCustomerName(order) {
  if (!order.customerId) return "Walk-in";

  const customer = getCustomers().find(
    (entry) => entry.id === order.customerId
  );

  return customer ? customer.name : order.customerId;
}

function renderDashboard() {
  const stats = getDashboardStats();

  const recentOrders = [...getOrders()]
    .sort((a, b) => {
      const dateA = orderDateValue(a)?.getTime() || 0;
      const dateB = orderDateValue(b)?.getTime() || 0;
      return dateB - dateA;
    })
    .slice(0, 8);

  return `
    <p class="eyebrow">LIVE BUSINESS OVERVIEW</p>
    <h2>Café Dashboard</h2>
    <p class="muted">
      Monitor sales, orders, customers and café progress from one place.
    </p>

    <section class="dashboard-stats">
      <article class="stat-card">
        <span class="stat-label">Sales Today</span>
        <strong>${formatRand(stats.todaySales)}</strong>
      </article>

      <article class="stat-card">
        <span class="stat-label">Orders Today</span>
        <strong>${stats.todayOrders}</strong>
      </article>

      <article class="stat-card">
        <span class="stat-label">Active Orders</span>
        <strong>${stats.activeOrders}</strong>
      </article>

      <article class="stat-card">
        <span class="stat-label">Customers</span>
        <strong>${stats.customers}</strong>
      </article>
    </section>

    <section class="dashboard-panel">
      <div class="dashboard-panel-heading">
        <div>
          <p class="eyebrow">LIVE PROGRESS</p>
          <h3>Order Pipeline</h3>
        </div>
        <span class="live-indicator">LIVE</span>
      </div>

      <div class="progress-grid">
        ${["NEW", "PREPARING", "READY", "COMPLETED", "CANCELLED"]
          .map((status) => `
            <article class="progress-card">
              <span>${status}</span>
              <strong>${stats.statusCounts[status]}</strong>
            </article>
          `).join("")}
      </div>
    </section>

    <section class="dashboard-panel">
      <div class="dashboard-panel-heading">
        <div>
          <p class="eyebrow">RECENT ACTIVITY</p>
          <h3>Recent Orders</h3>
        </div>
      </div>

      ${
        recentOrders.length
          ? `<div class="dashboard-order-list">
              ${recentOrders.map((order) => `
                <article class="dashboard-order">
                  <div>
                    <strong>#${escapeHtml(order.id)}</strong>
                    <small>${escapeHtml(getDashboardCustomerName(order))}</small>
                  </div>

                  <div>
                    <strong>${formatRand(order.total)}</strong>
                    <small>${escapeHtml(order.status || "NEW")}</small>
                  </div>
                </article>
              `).join("")}
            </div>`
          : `<p class="muted">No orders recorded yet.</p>`
      }
    </section>

    <section class="dashboard-panel">
      <div class="dashboard-panel-heading">
        <div>
          <p class="eyebrow">SALES HISTORY</p>
          <h3>Revenue Overview</h3>
        </div>
      </div>

      <div class="history-grid">
        <article>
          <span>Today</span>
          <strong>${formatRand(stats.todaySales)}</strong>
        </article>

        <article>
          <span>Yesterday</span>
          <strong>${formatRand(stats.yesterdaySales)}</strong>
        </article>

        <article>
          <span>This Week</span>
          <strong>${formatRand(stats.weekSales)}</strong>
        </article>

        <article>
          <span>This Month</span>
          <strong>${formatRand(stats.monthSales)}</strong>
        </article>
      </div>

      <p class="muted dashboard-note">
        Revenue is calculated from saved orders. Profit will be added
        when reliable ingredient cost data is available.
      </p>
    </section>
  `;
}


const SETTINGS_KEY = "mmkCafeSettings";

function getSettings() {
  const defaults = {
    cafeName: "MMK Café",
    ownerName: "",
    phone: "",
    email: "",
    address: "",
    currency: "ZAR",
    defaultOrderStatus: "NEW",
    customerDefaultStatus: "ACTIVE",
    requireCustomerPhone: false,
    allowCustomerNotes: true,
    defaultProductAvailable: true,
    categories: ["Coffee", "Tea", "Food", "Cold Drinks", "Other"]
  };

  try {
    const saved = JSON.parse(localStorage.getItem(SETTINGS_KEY) || "{}");
    return { ...defaults, ...saved };
  } catch {
    return defaults;
  }
}

function saveSettings(settings) {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}

function renderSettings() {
  const settings = getSettings();

  return `
    <p class="eyebrow">SETTINGS</p>
    <h2>Café Settings</h2>
    <p class="muted">
      Configure the café workspace and save your business preferences locally.
    </p>

    <form id="settingsForm" class="settings-form">

      <section class="settings-panel">
        <div class="dashboard-panel-heading">
          <div>
            <p class="eyebrow">BUSINESS PROFILE</p>
            <h3>Business information</h3>
          </div>
        </div>

        <label>
          Café name
          <input
            id="cafeName"
            type="text"
            value="${escapeHtml(settings.cafeName)}"
            required
          >
        </label>

        <label>
          Owner name
          <input
            id="ownerName"
            type="text"
            value="${escapeHtml(settings.ownerName)}"
          >
        </label>

        <label>
          Phone
          <input
            id="businessPhone"
            type="tel"
            value="${escapeHtml(settings.phone)}"
          >
        </label>

        <label>
          Email
          <input
            id="businessEmail"
            type="email"
            value="${escapeHtml(settings.email)}"
          >
        </label>

        <label>
          Address
          <textarea id="businessAddress" rows="3">${escapeHtml(settings.address)}</textarea>
        </label>
      </section>

      <section class="settings-panel">
        <div class="dashboard-panel-heading">
          <div>
            <p class="eyebrow">BUSINESS SETTINGS</p>
            <h3>Workspace defaults</h3>
          </div>
        </div>

        <label>
          Currency
          <select id="currency">
            <option value="ZAR" ${settings.currency === "ZAR" ? "selected" : ""}>
              ZAR — South African Rand (R)
            </option>
          </select>
        </label>

        <label>
          Default order status
          <select id="defaultOrderStatus">
            <option value="NEW" ${settings.defaultOrderStatus === "NEW" ? "selected" : ""}>NEW</option>
            <option value="PREPARING" ${settings.defaultOrderStatus === "PREPARING" ? "selected" : ""}>PREPARING</option>
          </select>
        </label>
      </section>

      <section class="settings-panel">
        <div class="dashboard-panel-heading">
          <div>
            <p class="eyebrow">CUSTOMERS</p>
            <h3>Customer defaults</h3>
          </div>
        </div>

        <label>
          Default customer status
          <select id="customerDefaultStatus">
            <option value="ACTIVE" ${settings.customerDefaultStatus === "ACTIVE" ? "selected" : ""}>ACTIVE</option>
            <option value="INACTIVE" ${settings.customerDefaultStatus === "INACTIVE" ? "selected" : ""}>INACTIVE</option>
          </select>
        </label>

        <label class="settings-checkbox">
          <input
            id="requireCustomerPhone"
            type="checkbox"
            ${settings.requireCustomerPhone ? "checked" : ""}
          >
          <span>Require a customer phone number</span>
        </label>

        <label class="settings-checkbox">
          <input
            id="allowCustomerNotes"
            type="checkbox"
            ${settings.allowCustomerNotes ? "checked" : ""}
          >
          <span>Allow customer notes</span>
        </label>
      </section>

      <section class="settings-panel">
        <div class="dashboard-panel-heading">
          <div>
            <p class="eyebrow">MENU</p>
            <h3>Menu defaults</h3>
          </div>
        </div>

        <label class="settings-checkbox">
          <input
            id="defaultProductAvailable"
            type="checkbox"
            ${settings.defaultProductAvailable ? "checked" : ""}
          >
          <span>New products are available by default</span>
        </label>

        <label>
          Menu categories
          <textarea id="categories" rows="4">${escapeHtml(settings.categories.join(", "))}</textarea>
          <small class="muted">Separate categories with commas.</small>
        </label>
      </section>

      <section class="settings-panel">
        <div class="dashboard-panel-heading">
          <div>
            <p class="eyebrow">DATA</p>
            <h3>Local data</h3>
          </div>
        </div>

        <p class="muted">
          Café data is currently stored locally in this browser using localStorage.
        </p>

        <button type="button" class="secondary-button" id="exportCafeData">
          Export Café Data
        </button>
      </section>

      <div class="settings-actions">
        <button type="submit" class="primary-button">
          Save Settings
        </button>
      </div>

      <p id="settingsMessage" class="muted"></p>
    </form>
  `;
}

function bindSettingsEvents() {
  const form = document.getElementById("settingsForm");

  if (!form) return;

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const categories = document
      .getElementById("categories")
      .value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);

    const settings = {
      cafeName: document.getElementById("cafeName").value.trim(),
      ownerName: document.getElementById("ownerName").value.trim(),
      phone: document.getElementById("businessPhone").value.trim(),
      email: document.getElementById("businessEmail").value.trim(),
      address: document.getElementById("businessAddress").value.trim(),
      currency: document.getElementById("currency").value,
      defaultOrderStatus: document.getElementById("defaultOrderStatus").value,
      customerDefaultStatus: document.getElementById("customerDefaultStatus").value,
      requireCustomerPhone: document.getElementById("requireCustomerPhone").checked,
      allowCustomerNotes: document.getElementById("allowCustomerNotes").checked,
      defaultProductAvailable: document.getElementById("defaultProductAvailable").checked,
      categories
    };

    saveSettings(settings);

    const message = document.getElementById("settingsMessage");

    if (message) {
      message.textContent = "Settings saved successfully.";
    }
  });

  const exportButton = document.getElementById("exportCafeData");

  if (exportButton) {
    exportButton.addEventListener("click", () => {
      const data = {
        exportedAt: new Date().toISOString(),
        settings: getSettings(),
        menu: getMenu(),
        orders: getOrders(),
        customers: getCustomers()
      };

      const blob = new Blob(
        [JSON.stringify(data, null, 2)],
        { type: "application/json" }
      );

      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = url;
      link.download = "mmk-cafe-backup.json";
      link.click();

      URL.revokeObjectURL(url);
    });
  }
}

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

function getMenu() {
  try {
    const saved = JSON.parse(localStorage.getItem(MENU_KEY)) || [];

    return saved.map((item) => ({
      ...item,
      description: item.description || "",
      recipe: item.recipe || "",
      available: item.available !== false
    }));
  } catch {
    return [];
  }
}

function saveMenu(menu) {
  localStorage.setItem(MENU_KEY, JSON.stringify(menu));
}

function getOrders() {
  try {
    return JSON.parse(localStorage.getItem(ORDERS_KEY)) || [];
  } catch {
    return [];
  }
}

function saveOrders(orders) {
  localStorage.setItem(ORDERS_KEY, JSON.stringify(orders));
}

function renderMenu() {
  const menu = getMenu();

  return `
    <p class="eyebrow">MENU MANAGEMENT</p>
    <h2>Café Menu</h2>
    <p class="muted">
      Manage your products, prices, recipes and availability.
    </p>

    <form id="menuForm" class="menu-form">
      <input id="productName" type="text" placeholder="Product name" required>
      <input id="productCategory" type="text" placeholder="Category e.g. Coffee" required>
      <input id="productPrice" type="number" min="0" step="0.01" placeholder="Selling price (R)" required>

      <textarea
        id="productDescription"
        placeholder="Product description"
        rows="3"
      ></textarea>

      <textarea
        id="productRecipe"
        placeholder="Recipe / ingredients"
        rows="4"
      ></textarea>

      <label class="availability-check">
        <input id="productAvailable" type="checkbox" checked>
        Available for customers
      </label>

      <button type="submit">Add Product</button>
    </form>

    <section class="customer-menu">
      <p class="eyebrow">CUSTOMER MENU</p>
      <h2>Today's Menu</h2>

      ${
        menu.length
          ? renderCustomerMenu(menu)
          : `<p class="muted">No products added yet.</p>`
      }
    </section>

    <section class="menu-management">
      <p class="eyebrow">PRODUCTS</p>
      <h2>Manage Products</h2>

      ${
        menu.length
          ? menu.map(renderManagementItem).join("")
          : `<p class="muted">Add your first café product above.</p>`
      }
    </section>
  `;
}

function renderCustomerMenu(menu) {
  const available = menu.filter((item) => item.available);

  if (!available.length) {
    return `<p class="muted">No products are currently available.</p>`;
  }

  const categories = [
    ...new Set(available.map((item) => item.category.trim()))
  ];

  return categories.map((category) => {
    const products = available.filter(
      (item) => item.category.trim() === category
    );

    return `
      <div class="menu-category">
        <h3>${escapeHtml(category)}</h3>

        ${products.map((item) => `
          <article class="customer-menu-item">
            <div>
              <h4>${escapeHtml(item.name)}</h4>
              <p>${escapeHtml(item.description || "Freshly prepared café item.")}</p>
            </div>

            <strong>R${Number(item.price).toFixed(2)}</strong>
          </article>
        `).join("")}
      </div>
    `;
  }).join("");
}

function renderManagementItem(item) {
  return `
    <article class="menu-item">
      <div>
        <strong>${escapeHtml(item.name)}</strong>

        <span>
          ${escapeHtml(item.category)}
          • R${Number(item.price).toFixed(2)}
        </span>

        <p>${escapeHtml(item.description || "No description added.")}</p>

        <small>
          Recipe: ${escapeHtml(item.recipe || "No recipe recorded.")}
        </small>

        <small class="${item.available ? "status-available" : "status-unavailable"}">
          ${item.available ? "Available" : "Unavailable"}
        </small>
      </div>

      <div class="menu-item-right">
        <button class="toggle-menu" data-id="${item.id}" type="button">
          ${item.available ? "Disable" : "Enable"}
        </button>

        <button class="delete-menu" data-id="${item.id}" type="button">
          Remove
        </button>
      </div>
    </article>
  `;
}

function renderOrders() {
  const menu = getMenu().filter((item) => item.available);
  const orders = getOrders();

  return `
    <p class="eyebrow">ORDERS</p>
    <h2>Create Order</h2>
    <p class="muted">
      Select products, build the order and save it to the café history.
    </p>

    ${
      menu.length
        ? `
          <div class="order-products">
            ${menu.map((item) => `
              <article class="order-product">
                <div>
                  <strong>${escapeHtml(item.name)}</strong>
                  <span>R${Number(item.price).toFixed(2)}</span>
                </div>

                <button
                  class="add-order-item"
                  data-id="${item.id}"
                  type="button"
                >
                  Add
                </button>
              </article>
            `).join("")}
          </div>
        `
        : `<p class="muted">Add available products in Menu first.</p>`
    }

    <section class="order-cart">
      <p class="eyebrow">CURRENT ORDER</p>
      <h3>Order Cart</h3>

      <label class="order-customer-field">
        Customer
        <select id="orderCustomer">
          <option value="">Walk-in customer</option>
          ${getCustomers()
            .filter(customer => customer.status === "ACTIVE")
            .map(customer => `
              <option value="${escapeHtml(customer.id)}">
                ${escapeHtml(customer.id)} — ${escapeHtml(customer.name)}
              </option>
            `).join("")}
        </select>
      </label>

      <div id="orderCart">
        ${renderOrderCart()}
      </div>
    </section>

    <section class="order-history">
      <p class="eyebrow">HISTORY</p>
      <h3>Order History</h3>

      ${
        orders.length
          ? orders.slice().reverse().map(renderOrderHistory).join("")
          : `<p class="muted">No saved orders yet.</p>`
      }
    </section>
  `;
}

function renderOrderCart() {
  if (!currentOrder.length) {
    return `<p class="muted">No items in the current order.</p>`;
  }

  const total = currentOrder.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );

  return `
    ${currentOrder.map((item) => `
      <article class="cart-item">
        <div>
          <strong>${escapeHtml(item.name)}</strong>
          <span>
            R${Number(item.price).toFixed(2)} × ${item.quantity}
          </span>
        </div>

        <div class="cart-actions">
          <button class="change-quantity" data-id="${item.id}" data-change="-1" type="button">−</button>
          <strong>R${(item.price * item.quantity).toFixed(2)}</strong>
          <button class="change-quantity" data-id="${item.id}" data-change="1" type="button">+</button>
        </div>
      </article>
    `).join("")}

    <div class="order-total">
      <strong>Total</strong>
      <strong>R${total.toFixed(2)}</strong>
    </div>

    <button id="saveOrder" class="save-order" type="button">
      Save Order
    </button>

    <button id="clearOrder" class="clear-order" type="button">
      Clear Order
    </button>
  `;
}

function renderOrderHistory(order) {
  return `
    <article class="history-order">
      <div>
        <strong>Order #${escapeHtml(order.id)}</strong>
        <span>${escapeHtml(order.date)}</span>

        ${
          order.customerId
            ? (() => {
                const customer = getCustomers().find(
                  entry => entry.id === order.customerId
                );
                return customer
                  ? `<small>Customer: ${escapeHtml(customer.name)} (${escapeHtml(customer.id)})</small>`
                  : `<small>Customer: ${escapeHtml(order.customerId)}</small>`;
              })()
            : `<small>Customer: Walk-in</small>`
        }

        ${order.items.map((item) => `
          <small>
            ${item.quantity} × ${escapeHtml(item.name)}
          </small>
        `).join("")}
      </div>

      <div>
        <strong>R${Number(order.total).toFixed(2)}</strong>

        <select
          class="order-status"
          data-id="${order.id}"
        >
          ${["NEW", "PREPARING", "READY", "COMPLETED", "CANCELLED"]
            .map((status) => `
              <option
                value="${status}"
                ${order.status === status ? "selected" : ""}
              >
                ${status}
              </option>
            `).join("")}
        </select>
      </div>
    </article>
  `;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function showSection(name) {
  const section = sections[name];

  if (!section) return;

  workspace.innerHTML = section.render();

  bindMenuEvents();
  bindOrderEvents();

  if (name === "customers") {
    bindCustomerEvents();
  }

  if (name === "settings") {
    bindSettingsEvents();
  }
}

function bindMenuEvents() {
  const form = document.getElementById("menuForm");

  if (form) {
    form.addEventListener("submit", (event) => {
      event.preventDefault();

      const name = document.getElementById("productName").value.trim();
      const category = document.getElementById("productCategory").value.trim();
      const price = Number(document.getElementById("productPrice").value);
      const description = document.getElementById("productDescription").value.trim();
      const recipe = document.getElementById("productRecipe").value.trim();
      const available = document.getElementById("productAvailable").checked;

      if (!name || !category || !Number.isFinite(price) || price < 0) {
        return;
      }

      const menu = getMenu();

      menu.push({
        id: Date.now(),
        name,
        category,
        price,
        description,
        recipe,
        available
      });

      saveMenu(menu);
      showSection("menu");
    });
  }

  document.querySelectorAll(".delete-menu").forEach((button) => {
    button.addEventListener("click", () => {
      const id = Number(button.dataset.id);

      saveMenu(
        getMenu().filter((item) => item.id !== id)
      );

      showSection("menu");
    });
  });

  document.querySelectorAll(".toggle-menu").forEach((button) => {
    button.addEventListener("click", () => {
      const id = Number(button.dataset.id);

      const menu = getMenu().map((item) => {
        if (item.id === id) {
          return {
            ...item,
            available: !item.available
          };
        }

        return item;
      });

      saveMenu(menu);
      showSection("menu");
    });
  });
}

function bindOrderEvents() {
  document.querySelectorAll(".add-order-item").forEach((button) => {
    button.addEventListener("click", () => {
      const id = Number(button.dataset.id);
      const product = getMenu().find((item) => item.id === id);

      if (!product) return;

      const existing = currentOrder.find(
        (item) => item.id === id
      );

      if (existing) {
        existing.quantity += 1;
      } else {
        currentOrder.push({
          id: product.id,
          name: product.name,
          price: Number(product.price),
          quantity: 1
        });
      }

      showSection("orders");
    });
  });

  document.querySelectorAll(".change-quantity").forEach((button) => {
    button.addEventListener("click", () => {
      const id = Number(button.dataset.id);
      const change = Number(button.dataset.change);

      const item = currentOrder.find(
        (entry) => entry.id === id
      );

      if (!item) return;

      item.quantity += change;

      currentOrder = currentOrder.filter(
        (entry) => entry.quantity > 0
      );

      showSection("orders");
    });
  });

  const saveButton = document.getElementById("saveOrder");

  if (saveButton) {
    saveButton.addEventListener("click", () => {
      if (!currentOrder.length) return;

      const total = currentOrder.reduce(
        (sum, item) => sum + item.price * item.quantity,
        0
      );

      const customerSelect = document.getElementById("orderCustomer");

      const order = {
        id: Date.now().toString().slice(-6),
        date: new Date().toLocaleString(),
        customerId: customerSelect ? customerSelect.value || null : null,
        items: currentOrder.map((item) => ({ ...item })),
        total,
        status: "NEW"
      };

      const orders = getOrders();

      orders.push(order);
      saveOrders(orders);

      currentOrder = [];
      showSection("orders");
    });
  }

  const clearButton = document.getElementById("clearOrder");

  if (clearButton) {
    clearButton.addEventListener("click", () => {
      currentOrder = [];
      showSection("orders");
    });
  }

  document.querySelectorAll(".order-status").forEach((select) => {
    select.addEventListener("change", () => {
      const id = String(select.dataset.id);

      const orders = getOrders().map((order) => {
        if (String(order.id) === id) {
          return {
            ...order,
            status: select.value
          };
        }

        return order;
      });

      saveOrders(orders);
      showSection("orders");
    });
  });
}

document.querySelectorAll("[data-section]").forEach((button) => {
  button.addEventListener("click", () => {
    showSection(button.dataset.section);
  });
});
