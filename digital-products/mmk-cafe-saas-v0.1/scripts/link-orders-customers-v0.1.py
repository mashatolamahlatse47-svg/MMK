from pathlib import Path

app = Path("app/app.js")
s = app.read_text()

if 'id="orderCustomer"' in s:
    raise SystemExit("STOP: Customer selector already exists.")

# 1. Restore event binding inside showSection.
old_show = """  workspace.innerHTML = section.render();

  if (name === "customers") {
    bindCustomerEvents();
  }
}"""

new_show = """  workspace.innerHTML = section.render();

  bindMenuEvents();
  bindOrderEvents();

  if (name === "customers") {
    bindCustomerEvents();
  }
}"""

if old_show not in s:
    raise SystemExit("STOP: showSection target not found.")

s = s.replace(old_show, new_show, 1)

# 2. Add customer selector to the current order area.
old_cart = """    <section class="order-cart">
      <p class="eyebrow">CURRENT ORDER</p>
      <h3>Order Cart</h3>

      <div id="orderCart">
        ${renderOrderCart()}
      </div>
    </section>"""

new_cart = """    <section class="order-cart">
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
    </section>"""

if old_cart not in s:
    raise SystemExit("STOP: order cart target not found.")

s = s.replace(old_cart, new_cart, 1)

# 3. Preserve the selected customer while the cart re-renders.
old_save = """      const order = {
        id: Date.now().toString().slice(-6),
        date: new Date().toLocaleString(),
        items: currentOrder.map((item) => ({ ...item })),
        total,
        status: "NEW"
      };"""

new_save = """      const customerSelect = document.getElementById("orderCustomer");

      const order = {
        id: Date.now().toString().slice(-6),
        date: new Date().toLocaleString(),
        customerId: customerSelect ? customerSelect.value || null : null,
        items: currentOrder.map((item) => ({ ...item })),
        total,
        status: "NEW"
      };"""

if old_save not in s:
    raise SystemExit("STOP: save order target not found.")

s = s.replace(old_save, new_save, 1)

# 4. Show customer on order history when linked.
old_history = """        <span>${escapeHtml(order.date)}</span>

        ${order.items.map((item) => `"""

new_history = """        <span>${escapeHtml(order.date)}</span>

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

        ${order.items.map((item) => `"""

if old_history not in s:
    raise SystemExit("STOP: order history target not found.")

s = s.replace(old_history, new_history, 1)

app.write_text(s)

css = Path("app/style.css")
css_text = css.read_text()

if "/* Customer ↔ Orders V0.1 */" not in css_text:
    css.write_text(css_text + """

/* Customer ↔ Orders V0.1 */
.order-customer-field {
  display: grid;
  gap: 7px;
  margin: 0 0 16px;
}

.order-customer-field select {
  width: 100%;
  box-sizing: border-box;
}
""")

print("CUSTOMER ↔ ORDERS PATCH APPLIED")
