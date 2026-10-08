from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"

js_path = APP / "app.js"
css_path = APP / "style.css"

js = js_path.read_text()
css = css_path.read_text()

start = js.index("function getDashboardStats() {")
end = js.index("\nfunction renderRecord()", start)

dashboard = r'''function getDashboardStats() {
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
  `;
}
'''

js = js[:start] + dashboard + js[end:]

css += '''

.dashboard-panel {
  margin-top: 12px;
}

.dashboard-panel strong {
  font-size: 18px;
}
'''

js_path.write_text(js)
css_path.write_text(css)

print("DASHBOARD V0.2 BUILD APPLIED")
