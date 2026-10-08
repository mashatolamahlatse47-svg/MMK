from pathlib import Path

app = Path("app/app.js")
s = app.read_text()

if "function renderDashboard()" in s:
    raise SystemExit("STOP: Dashboard build already exists.")

# 1. Add Dashboard to sections.
old_sections = """const sections = {
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
  settings:"""

new_sections = """const sections = {
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
  settings:"""

if old_sections not in s:
    raise SystemExit("STOP: sections target not found.")

s = s.replace(old_sections, new_sections, 1)

# 2. Insert dashboard functions before getCustomers().
marker = "function getCustomers() {"

dashboard_code = r'''function startOfDay(date = new Date()) {
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

'''

if marker not in s:
    raise SystemExit("STOP: customer function marker not found.")

s = s.replace(marker, dashboard_code + marker, 1)

app.write_text(s)

# 3. Add Dashboard navigation.
index = Path("app/index.html")
html = index.read_text()

if 'data-section="dashboard"' in html:
    raise SystemExit("STOP: Dashboard navigation already exists.")

old_nav = """    <section class="dashboard-grid">
      <button class="card" data-section="menu">"""

new_nav = """    <section class="dashboard-grid">
      <button class="card" data-section="dashboard">
        <span class="card-icon">📊</span>
        <strong>Dashboard</strong>
        <span>View live café performance.</span>
      </button>

      <button class="card" data-section="menu">"""

if old_nav not in html:
    raise SystemExit("STOP: navigation target not found.")

html = html.replace(old_nav, new_nav, 1)
index.write_text(html)

# 4. Add dashboard styling.
css = Path("app/style.css")
css_text = css.read_text()

if "/* Dashboard V0.1 */" not in css_text:
    css_text += """

/* Dashboard V0.1 */
.dashboard-stats,
.progress-grid,
.history-grid {
  display: grid;
  gap: 12px;
}

.dashboard-stats {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin: 24px 0;
}

.stat-card,
.progress-card,
.history-grid article {
  padding: 16px;
  border: 1px solid var(--border, #333);
  border-radius: 14px;
  background: var(--surface, #151515);
}

.stat-card {
  display: grid;
  gap: 8px;
}

.stat-label,
.progress-card span,
.history-grid span {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  opacity: 0.7;
}

.stat-card strong {
  font-size: 1.35rem;
}

.dashboard-panel {
  margin-top: 20px;
  padding: 18px;
  border: 1px solid var(--border, #333);
  border-radius: 16px;
  background: var(--surface, #151515);
}

.dashboard-panel-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.dashboard-panel-heading h3 {
  margin: 4px 0 0;
}

.live-indicator {
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  font-weight: 700;
}

.progress-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.progress-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.progress-card strong {
  font-size: 1.2rem;
}

.dashboard-order-list {
  display: grid;
  gap: 10px;
}

.dashboard-order {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border, #333);
}

.dashboard-order:last-child {
  border-bottom: 0;
}

.dashboard-order div {
  display: grid;
  gap: 4px;
}

.dashboard-order div:last-child {
  text-align: right;
}

.dashboard-order small {
  opacity: 0.7;
}

.history-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.history-grid article {
  display: grid;
  gap: 8px;
}

.dashboard-note {
  margin: 16px 0 0;
  font-size: 0.85rem;
}

@media (min-width: 700px) {
  .dashboard-stats,
  .progress-grid,
  .history-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .progress-grid {
    grid-template-columns: repeat(5, minmax(0, 1fr));
  }
}
"""
    css.write_text(css_text)

print("DASHBOARD V0.1 BUILD APPLIED")
