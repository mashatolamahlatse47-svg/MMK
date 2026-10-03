const API_BASE = "http://127.0.0.1:8090";

const state = {
  business: {
    name: "Loading...",
    currency: "ZAR"
  },
  stock: 0,
  revenue: 0,
  owing: 0,
  expenses: 0,
  profit: 0
};

const money = (cents) =>
  new Intl.NumberFormat("en-ZA", {
    style: "currency",
    currency: state.business.currency
  }).format(cents / 100);

function renderDashboard() {
  document.getElementById("stock").textContent = state.stock;
  document.getElementById("sales").textContent = money(state.revenue);
  document.getElementById("owing").textContent = money(state.owing);
  document.getElementById("profit").textContent = money(state.profit);
}

async function loadDashboard() {
  try {
    const response = await fetch(`${API_BASE}/api/dashboard`);

    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }

    const data = await response.json();

    if (!data.business) {
      throw new Error("No business data found");
    }

    state.business.name = data.business.name;
    state.business.currency = data.business.currency;
    state.stock = data.stock_units;
    state.revenue = data.revenue_cents;
    state.owing = data.outstanding_credit_cents;
    state.expenses = data.expenses_cents;

    // Use the backend ReportsEngine result so COGS is included.
    state.profit = data.net_profit_cents;

    renderDashboard();
  } catch (error) {
    console.error("Dashboard loading failed:", error);
    document.getElementById("stock").textContent = "—";
    document.getElementById("sales").textContent = "API error";
    document.getElementById("owing").textContent = "—";
    document.getElementById("profit").textContent = "—";
  }
}

function selectSection(name) {
  document.querySelectorAll(".menu button").forEach((button) => {
    button.classList.toggle(
      "active",
      button.textContent.trim().toLowerCase() === name.toLowerCase()
    );
  });
}

document.querySelectorAll(".menu button").forEach((button) => {
  button.addEventListener("click", () => {
    selectSection(button.textContent.trim());
  });
});

loadDashboard();


async function loadStock() {
  const section = document.getElementById("stockSection");
  const list = document.getElementById("stockList");
  const business = document.getElementById("stockBusiness");

  if (!section || !list || !business) return;

  section.style.display = "block";
  list.innerHTML = "<p>Loading stock...</p>";

  try {
    const response = await fetch(`${API_BASE}/api/stock`);
    if (!response.ok) throw new Error(`API returned ${response.status}`);

    const data = await response.json();

    business.textContent = data.business.name;

    if (!data.products.length) {
      list.innerHTML = "<p>No stock products recorded.</p>";
      return;
    }

    list.innerHTML = data.products.map(product => `
      <div class="stock-card">
        <strong>${product.name}</strong>
        <div>Unit: ${product.unit}</div>
        <div>Selling price: ${money(product.selling_price_cents)}</div>
        <div>Stock remaining: <strong>${product.quantity_on_hand}</strong></div>
      </div>
    `).join("");
  } catch (error) {
    console.error("Stock loading failed:", error);
    list.innerHTML = "<p>Stock API error.</p>";
  }
}

document.querySelectorAll("button").forEach(button => {
  if (button.textContent.trim().toLowerCase() === "stock") {
    button.addEventListener("click", loadStock);
  }
});
