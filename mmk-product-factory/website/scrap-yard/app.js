const workspace = document.getElementById("workspace");

const TRANSACTIONS_KEY = "mmkScrapYardTransactions";

function getTransactions() {
  try {
    return JSON.parse(
      localStorage.getItem(TRANSACTIONS_KEY) || "[]"
    );
  } catch {
    return [];
  }
}

function saveTransactions(transactions) {
  localStorage.setItem(
    TRANSACTIONS_KEY,
    JSON.stringify(transactions)
  );
}

function money(value) {
  return `R${Number(value || 0).toFixed(2)}`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function getDashboardStats() {
  const transactions = getTransactions();

  const today = new Date().toLocaleDateString();

  const todayTransactions = transactions.filter((transaction) => {
    const transactionDate = new Date(transaction.date);

    return (
      !Number.isNaN(transactionDate.getTime()) &&
      transactionDate.toLocaleDateString() === today
    );
  });

  const totals = (items) => {
    const sales = items.reduce(
      (sum, transaction) => sum + Number(transaction.salePrice || 0),
      0
    );

    const costs = items.reduce(
      (sum, transaction) => sum + Number(transaction.buyPrice || 0),
      0
    );

    return {
      sales,
      costs,
      profit: sales - costs,
      transactions: items.length
    };
  };

  return {
    today: totals(todayTransactions),
    all: totals(transactions),
    recent: transactions.slice(-5).reverse()
  };
}

function renderDashboard() {
  const stats = getDashboardStats();

  return `
    <section>
      <p class="eyebrow">DASHBOARD</p>
      <h2>Scrap Yard Overview</h2>

      <div class="grid">
        <article class="stat-card">
          <div class="stat-label">Today's Sales</div>
          <div class="stat-value">${money(stats.today.sales)}</div>
        </article>

        <article class="stat-card">
          <div class="stat-label">Today's Costs</div>
          <div class="stat-value">${money(stats.today.costs)}</div>
        </article>

        <article class="stat-card">
          <div class="stat-label">Today's Profit / Loss</div>
          <div class="stat-value ${
            stats.today.profit >= 0 ? "profit" : "loss"
          }">${money(stats.today.profit)}</div>
        </article>

        <article class="stat-card">
          <div class="stat-label">Today's Transactions</div>
          <div class="stat-value">${stats.today.transactions}</div>
        </article>
      </div>

      <div class="panel dashboard-panel">
        <p class="eyebrow">ALL TIME</p>
        <h3>Business Totals</h3>

        <div class="grid">
          <div>
            <div class="stat-label">Total Sales</div>
            <strong>${money(stats.all.sales)}</strong>
          </div>

          <div>
            <div class="stat-label">Total Costs</div>
            <strong>${money(stats.all.costs)}</strong>
          </div>

          <div>
            <div class="stat-label">Total Profit / Loss</div>
            <strong class="${
              stats.all.profit >= 0 ? "profit" : "loss"
            }">${money(stats.all.profit)}</strong>
          </div>

          <div>
            <div class="stat-label">Total Transactions</div>
            <strong>${stats.all.transactions}</strong>
          </div>
        </div>
      </div>

      <div class="panel dashboard-panel">
        <p class="eyebrow">RECENT ACTIVITY</p>
        <h3>Recent Transactions</h3>

        ${
          stats.recent.length
            ? stats.recent.map((transaction) => `
                <article class="transaction">
                  <strong>${escapeHtml(transaction.material)}</strong>
                  <p class="muted">${escapeHtml(transaction.date)}</p>
                  <p>
                    Sale: ${money(transaction.salePrice)}
                    • Cost: ${money(transaction.buyPrice)}
                  </p>
                  <p class="${
                    transaction.profit >= 0 ? "profit" : "loss"
                  }">
                    ${transaction.profit >= 0 ? "Profit" : "Loss"}:
                    ${money(Math.abs(transaction.profit))}
                  </p>
                </article>
              `).join("")
            : `<p class="muted">No transactions recorded yet.</p>`
        }
      </div>
    </section>

      <section class="panel premium-panel">
        <p class="eyebrow">PREMIUM SERVICE</p>
        <h2>Premium Personalization</h2>
        <p class="muted">
          Want this Scrap Yard system customized for your business?
          Request premium personalization from the MMK Founder.
        </p>

        <ul class="premium-list">
          <li>Custom business branding</li>
          <li>Business colors and logo</li>
          <li>Personalized layout and features</li>
          <li>Tailored business version</li>
        </ul>

        <div class="premium-contact">
          MASHATOLAMAHLATSE47@GMAIL.COM
        </div>

        <div class="actions">
          <a class="button primary" href="mailto:mashatolamahlatse47@gmail.com?subject=Scrap%20Yard%20Premium%20Personalization">
            Request by Email
          </a>
          <a class="button secondary" href="tel:0724422893">
            Call 072 442 2893
          </a>
          <a class="button secondary" href="tel:0828638858">
            Call 082 863 8858
          </a>
        </div>
      </section>

  `;
}

function renderRecord() {
  return `
    <section class="panel">
      <p class="eyebrow">RECORD TRANSACTION</p>
      <h2>Scrap Transaction</h2>

      <form id="transactionForm">
        <label>
          Material / Item
          <input id="material" required placeholder="e.g. Copper">
        </label>

        <h3>Purchase</h3>

        <label>
          Purchase Weight / Quantity
          <input id="purchaseQuantity" type="number" min="0" step="0.01" required placeholder="e.g. 25">
        </label>

        <label>
          Purchase Cost
          <input id="buyPrice" type="number" min="0" step="0.01" required placeholder="R0.00">
        </label>

        <h3>Sale</h3>

        <label>
          Sale Weight / Quantity
          <input id="saleQuantity" type="number" min="0" step="0.01" required placeholder="e.g. 25">
        </label>

        <label>
          Sale Income
          <input id="salePrice" type="number" min="0" step="0.01" required placeholder="R0.00">
        </label>

        <div class="actions">
          <button type="submit" class="primary">Save Transaction</button>
        </div>
      </form>
    </section>
  `;
}

function renderHistory() {
  const transactions = getTransactions();

  if (!transactions.length) {
    return `
      <section class="panel">
        <p class="eyebrow">HISTORY</p>
        <h2>Transaction History</h2>
        <p class="muted">No transactions recorded yet.</p>
      </section>
    `;
  }

  return `
    <section class="panel">
      <p class="eyebrow">HISTORY</p>
      <h2>Transaction History</h2>
      <p class="muted">Newest transactions appear first.</p>

      <div class="history-list">
        ${transactions
          .slice()
          .reverse()
          .map((transaction) => {
            const isProfit = Number(transaction.profit) >= 0;

            return `
              <article class="transaction history-card">
                <div class="history-header">
                  <div>
                    <strong>${escapeHtml(transaction.material)}</strong>
                    <p class="muted">${escapeHtml(transaction.date)}</p>
                  </div>
                  <span class="${isProfit ? "profit" : "loss"}">
                    ${isProfit ? "PROFIT" : "LOSS"}
                  </span>
                </div>

                <div class="history-grid">
                  <div>
                    <span class="muted">Purchase Qty</span>
                    <strong>${escapeHtml(transaction.purchaseQuantity)}</strong>
                  </div>

                  <div>
                    <span class="muted">Purchase Cost</span>
                    <strong>${money(transaction.buyPrice)}</strong>
                  </div>

                  <div>
                    <span class="muted">Sale Qty</span>
                    <strong>${escapeHtml(transaction.saleQuantity)}</strong>
                  </div>

                  <div>
                    <span class="muted">Sale Income</span>
                    <strong>${money(transaction.salePrice)}</strong>
                  </div>
                </div>

                <div class="history-result ${isProfit ? "profit-result" : "loss-result"}">
                  <span>${isProfit ? "Profit" : "Loss"}</span>
                  <strong>${money(Math.abs(Number(transaction.profit) || 0))}</strong>
                </div>

                <div class="history-actions">
                  <button
                    type="button"
                    class="danger delete-transaction"
                    data-id="${escapeHtml(transaction.id)}"
                  >
                    Delete Transaction
                  </button>
                </div>
              </article>
            `;
          })
          .join("")}
      </div>
    </section>
  `;
}

function bindHistoryEvents() {
  document.querySelectorAll(".delete-transaction").forEach((button) => {
    button.addEventListener("click", () => {
      const id = button.dataset.id;

      if (!id) return;

      const confirmed = window.confirm(
        "Delete this transaction? This action cannot be undone."
      );

      if (!confirmed) return;

      const transactions = getTransactions().filter(
        (transaction) => transaction.id !== id
      );

      saveTransactions(transactions);
      showSection("history");
    });
  });
}

const sections = {
  dashboard: renderDashboard,
  record: renderRecord,
  history: renderHistory
};

function showSection(name) {
  const render = sections[name];

  if (!render) return;

  workspace.innerHTML = render();

  document.querySelectorAll(".nav-button").forEach((button) => {
    button.classList.toggle(
      "active",
      button.dataset.section === name
    );
  });

  if (name === "record") {
    bindRecordEvents();
  }

  if (name === "history") {
    bindHistoryEvents();
  }
}

function bindRecordEvents() {
  const form = document.getElementById("transactionForm");

  if (!form) return;

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const material = document
      .getElementById("material")
      .value.trim();

    const buyPrice = Number(
      document.getElementById("buyPrice").value
    );

    const salePrice = Number(
      document.getElementById("salePrice").value
    );

    const purchaseQuantity = Number(
      document.getElementById("purchaseQuantity").value
    );

    const saleQuantity = Number(
      document.getElementById("saleQuantity").value
    );

    const transaction = {
      id: Date.now().toString(),
      date: new Date().toLocaleString(),
      material,
      purchaseQuantity,
      saleQuantity,
      buyPrice,
      salePrice,
      profit: salePrice - buyPrice
    };

    const transactions = getTransactions();

    transactions.push(transaction);
    saveTransactions(transactions);

    showSection("dashboard");
  });
}

document.querySelectorAll(".nav-button").forEach((button) => {
  button.addEventListener("click", () => {
    showSection(button.dataset.section);
  });
});

showSection("dashboard");
