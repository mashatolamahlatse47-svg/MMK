from pathlib import Path

root = Path(__file__).resolve().parents[1]
app = root / "app"

js = app / "app.js"
html = app / "index.html"
css = app / "style.css"

js_text = js.read_text()
html_text = html.read_text()
css_text = css.read_text()

js_text = js_text.replace(
'''const transaction = {
      id: Date.now().toString(),
      date: new Date().toLocaleDateString(),
      material,
      quantity,
      buyPrice,
      salePrice,
      profit: salePrice - buyPrice
    };''',
'''const purchaseQuantity = Number(
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
    };'''
)

js_text = js_text.replace(
'''<label>
          Weight / Quantity
          <input id="quantity" type="number" min="0" step="0.01" required placeholder="e.g. 25">
        </label>

        <label>
          Buying Price
          <input id="buyPrice" type="number" min="0" step="0.01" required placeholder="R0.00">
        </label>

        <label>
          Selling Price
          <input id="salePrice" type="number" min="0" step="0.01" required placeholder="R0.00">
        </label>''',
'''<h3>Purchase</h3>

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
        </label>'''
)

js_text = js_text.replace(
'''${escapeHtml(transaction.date)}
              • ${escapeHtml(transaction.quantity)} units
            </p>
            <p>
              Cost: ${money(transaction.buyPrice)}
              • Sale: ${money(transaction.salePrice)}
            </p>''',
'''${escapeHtml(transaction.date)}
            </p>
            <p>
              Purchase: ${escapeHtml(transaction.purchaseQuantity)}
              • Sale: ${escapeHtml(transaction.saleQuantity)}
            </p>
            <p>
              Cost: ${money(transaction.buyPrice)}
              • Income: ${money(transaction.salePrice)}
            </p>'''
)

js_text = js_text.replace(
'''const today = new Date().toLocaleDateString();

  const todayTransactions = transactions.filter(
    (transaction) => transaction.date === today
  );''',
'''const today = new Date().toLocaleDateString();

  const todayTransactions = transactions.filter((transaction) => {
    const transactionDate = new Date(transaction.date);
    return !Number.isNaN(transactionDate.getTime()) &&
      transactionDate.toLocaleDateString() === today;
  });'''
)

js.write_text(js_text)

css_text += '''

.transaction h3 {
  margin-bottom: 8px;
}

.transaction p {
  margin-bottom: 6px;
}
'''

css.write_text(css_text)

print("TRANSACTION V0.2 BUILD APPLIED")
