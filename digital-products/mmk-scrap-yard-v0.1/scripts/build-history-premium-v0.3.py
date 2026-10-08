from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app" / "app.js"
CSS = ROOT / "app" / "style.css"
BACKUP = ROOT / "backups" / "history-premium-before-v0.3"

app = APP.read_text()
css = CSS.read_text()

history_start = app.index("function renderHistory() {")
history_end = app.index("\nconst sections =", history_start)

old_history = app[history_start:history_end]

new_history = r'''function renderHistory() {
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
'''

if old_history not in app:
    raise SystemExit("ERROR: Expected History section not found. No changes made.")

premium_marker = '      <section class="panel premium-panel">'
if premium_marker not in app:
    dashboard_marker = 'function renderRecord() {'
    dashboard_start = app.index("function renderDashboard() {")
    record_start = app.index(dashboard_marker)

    dashboard_block = app[dashboard_start:record_start]

    premium = r'''
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

'''

    dashboard_end = dashboard_block.rfind("  `;")
    if dashboard_end == -1:
        raise SystemExit("ERROR: Dashboard template closing not found. No changes made.")

    insert_at = dashboard_start + dashboard_end
    app = app[:insert_at] + premium + app[insert_at:]

app = app.replace(
    '  if (name === "record") {\n    bindRecordEvents();\n  }',
    '''  if (name === "record") {
    bindRecordEvents();
  }

  if (name === "history") {
    bindHistoryEvents();
  }'''
)

app = app.replace(old_history, new_history, 1)

BACKUP.mkdir(parents=True, exist_ok=True)
(BACKUP / "app.js").write_text(APP.read_text())
(BACKUP / "style.css").write_text(CSS.read_text())

APP.write_text(app)

css_addition = r'''
.history-actions {
  margin-top: 12px;
}

.danger {
  width: 100%;
}

.premium-panel {
  margin-top: 16px;
}

.premium-list {
  margin: 14px 0;
  padding-left: 20px;
}

.premium-list li {
  margin-bottom: 7px;
}

.premium-panel .actions {
  display: grid;
  gap: 8px;
}

.premium-panel .button {
  display: block;
  text-align: center;
  text-decoration: none;
}
'''

if ".history-actions {" not in css:
    CSS.write_text(css.rstrip() + "\n" + css_addition)

print("HISTORY DELETE + PREMIUM V0.3 BUILD APPLIED")
