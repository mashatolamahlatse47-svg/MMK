from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app" / "app.js"
BACKUP = ROOT / "backups" / "history-before-v0.2"

source = APP.read_text()

start = source.index("function renderHistory() {")
end = source.index("\nconst sections =", start)

old = source[start:end]

new = r'''function renderHistory() {
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
              </article>
            `;
          })
          .join("")}
      </div>
    </section>
  `;
}
'''

if old not in source:
    raise SystemExit("ERROR: Expected renderHistory block was not found. No changes made.")

BACKUP.mkdir(parents=True, exist_ok=True)
(BACKUP / "app.js").write_text(source)
APP.write_text(source.replace(old, new))

CSS = ROOT / "app" / "style.css"
css = CSS.read_text()

css_addition = r'''
.history-list {
  display: grid;
  gap: 12px;
  margin-top: 16px;
}

.history-card {
  padding: 14px;
}

.history-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.history-header strong {
  font-size: 1.05rem;
}

.history-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}

.history-grid div {
  display: grid;
  gap: 3px;
}

.history-grid strong {
  font-size: 0.95rem;
}

.history-result {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.history-result strong {
  font-size: 1.05rem;
}

.profit-result {
  border-radius: 10px;
}

.loss-result {
  border-radius: 10px;
}
'''

if ".history-list {" not in css:
    CSS.write_text(css.rstrip() + "\n" + css_addition)

print("HISTORY V0.2 BUILD APPLIED")
