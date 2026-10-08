from pathlib import Path

APP = Path("app/app.js")
HTML = Path("app/index.html")
CSS = Path("app/style.css")

app = APP.read_text()
html = HTML.read_text()
css = CSS.read_text()

settings_block = r'''
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
'''

if "const SETTINGS_KEY = " not in app:
    marker = 'function getCustomers() {'
    if marker not in app:
        raise SystemExit("Could not find getCustomers marker.")
    app = app.replace(marker, settings_block + "\n" + marker, 1)

old_show = '''  bindMenuEvents();
  bindOrderEvents();

  if (name === "customers") {
    bindCustomerEvents();
  }
'''

new_show = '''  bindMenuEvents();
  bindOrderEvents();

  if (name === "customers") {
    bindCustomerEvents();
  }

  if (name === "settings") {
    bindSettingsEvents();
  }
'''

if old_show not in app:
    raise SystemExit("Could not find showSection binding block.")

app = app.replace(old_show, new_show, 1)

if "/* Settings V0.1 */" not in css:
    css += r'''

/* Settings V0.1 */

.settings-form {
  display: grid;
  gap: 16px;
}

.settings-panel {
  display: grid;
  gap: 14px;
  padding: 18px;
  border: 1px solid var(--border, #333);
  border-radius: 14px;
  background: var(--surface, #151515);
}

.settings-panel label {
  display: grid;
  gap: 7px;
  font-weight: 600;
}

.settings-panel input,
.settings-panel select,
.settings-panel textarea {
  width: 100%;
  box-sizing: border-box;
}

.settings-checkbox {
  display: flex !important;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: 10px !important;
}

.settings-checkbox input {
  width: auto;
}

.settings-actions {
  display: flex;
  justify-content: flex-end;
}

.settings-actions button,
.settings-panel button {
  min-height: 44px;
}

.settings-panel h3 {
  margin: 0;
}
'''

APP.write_text(app)
CSS.write_text(css)

print("SETTINGS V0.1 BUILD APPLIED")
