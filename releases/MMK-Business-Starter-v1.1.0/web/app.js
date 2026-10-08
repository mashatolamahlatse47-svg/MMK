const workspace = document.getElementById("workspace");

const sections = {
  business: {
    title: "Business Information",
    render() {
      return `
        <h2>Business Information</h2>
        <form id="business-form">
          <label>
            Business Name
            <input name="businessName" type="text" required>
          </label>

          <label>
            Owner Name
            <input name="ownerName" type="text">
          </label>

          <label>
            Phone / WhatsApp
            <input name="phone" type="tel">
          </label>

          <label>
            Email
            <input name="email" type="email">
          </label>

          <label>
            Website
            <input name="website" type="url" placeholder="https://">
          </label>

          <label>
            Business Category
            <input name="category" type="text">
          </label>

          <div class="form-actions">
            <button type="submit">Save Business Information</button>
            <button type="button" id="clear-business" class="secondary">
              Clear Saved Information
            </button>
          </div>

          <p id="save-message" class="message"></p>
        </form>
      `;
    }
  },

  products: {
    title: "Products",

    render() {
      return `
        <h2>Products</h2>

        <form id="product-form">
          <label>
            Product Name
            <input name="name" type="text" required>
          </label>

          <label>
            Category
            <input name="category" type="text">
          </label>

          <label>
            Selling Price (R)
            <input name="sellingPrice" type="number" min="0" step="0.01" required>
          </label>

          <label>
            Cost Price (R)
            <input name="costPrice" type="number" min="0" step="0.01" required>
          </label>

          <label>
            Stock Quantity
            <input name="stock" type="number" min="0" step="1" required>
          </label>

          <div class="form-actions">
            <button type="submit">Add Product</button>
            <button type="button" id="clear-products" class="secondary">
              Clear All Products
            </button>
          </div>

          <p id="product-message" class="message"></p>
        </form>

        <div id="product-list"></div>
      `;
    }
  },

  customers: {
    title: "Customers",

    render() {
      return `
        <h2>Customers</h2>

        <form id="customer-form">
          <label>
            Customer Name
            <input name="name" type="text" required>
          </label>

          <label>
            Money Owed (R)
            <input name="moneyOwed" type="number" min="0" step="0.01" required>
          </label>

          <label>
            Notes
            <textarea name="notes" rows="3" placeholder="Optional customer notes"></textarea>
          </label>

          <div class="form-actions">
            <button type="submit">Add Customer</button>
            <button type="button" id="clear-customers" class="secondary">
              Clear All Customers
            </button>
          </div>

          <p id="customer-message" class="message"></p>
        </form>

        <div id="customer-list"></div>
      `;
    }
  },

  sales: {
    title: "Sales",

    render() {
      const products = getProducts();
      const customers = getCustomers();

      const productOptions = products.length
        ? products.map((product, index) =>
            `<option value="${index}">${product.name} — R${Number(product.sellingPrice).toFixed(2)} — Stock: ${product.stock}</option>`
          ).join("")
        : '<option value="">No products available</option>';

      const customerOptions = customers.length
        ? customers.map((customer, index) =>
            `<option value="${index}">${customer.name}</option>`
          ).join("")
        : '<option value="">No customers available</option>';

      return `
        <h2>Sales</h2>

        <form id="sales-form">
          <label>
            Date
            <input name="date" type="date" required>
          </label>

          <label>
            Customer
            <select name="customerIndex" required>
              <option value="">Select Customer</option>
              ${customerOptions}
            </select>
          </label>

          <div class="sales-products-panel">
            <div class="sales-products-header">
              <div>
                <h3>Products</h3>
                <p>Select a product to calculate stock, cost and profit automatically.</p>
              </div>
              <button type="button" id="add-product-from-sales" class="secondary">Add Product</button>
            </div>

            <div id="sales-product-list" class="sales-product-list">
              ${
                products.length
                  ? products.map((product, index) => `
                      <button type="button" class="sales-product-item" data-product-index="${index}">
                        <strong>${product.name}</strong>
                        <span>Sell: R${Number(product.sellingPrice).toFixed(2)}</span>
                        <span>Cost: R${Number(product.costPrice).toFixed(2)}</span>
                        <span>Stock: ${Number(product.stock)}</span>
                      </button>
                    `).join("")
                  : "<p>No products available. Add a product to begin a sale.</p>"
              }
            </div>
          </div>

          <label>
            Product
            <select name="productIndex" required>
              <option value="">Select Product</option>
              ${productOptions}
            </select>
          </label>

          <label>
            Quantity
            <input name="quantity" type="number" min="1" step="1" required>
          </label>

          <label>
            Payment Type
            <select name="paymentType" required>
              <option value="">Select Payment Type</option>
              <option value="cash">Cash</option>
              <option value="credit">Credit</option>
              <option value="partial">Partial Payment</option>
            </select>
          </label>

          <label>
            Amount Paid (R)
            <input name="amountPaid" type="number" min="0" step="0.01" value="0">
          </label>

          <div id="sale-summary">
            <p>Sales Total: R0.00</p>
            <p>Cost Total: R0.00</p>
            <p>Total Profit: R0.00</p>
            <p>Stock Remaining: 0</p>
            <p>Amount Owed: R0.00</p>
          </div>

          <div class="form-actions">
            <button type="submit">Record Sale</button>
            <button type="button" id="clear-sales" class="secondary">
              Clear Sales
            </button>
          </div>

          <p id="sales-message" class="message"></p>
        </form>

        <div id="sales-list"></div>
      `;
    }
  },

  reports: {
    title: "Reports",

    render() {
      return `
        <h2>Reports</h2>

        <section class="report-section">
          <h3>Business Summary</h3>
          <div id="reports-summary"></div>
        </section>

        <section class="report-section">
          <h3>Sales History</h3>
          <div id="reports-sales-history"></div>
        </section>

        <section class="report-section">
          <h3>Customer Debt Report</h3>
          <div id="reports-debt"></div>
        </section>

        <section class="report-section">
          <h3>Product & Stock Report</h3>
          <div id="reports-products"></div>
        </section>
      `;
    }
  }
};

function loadBusinessInformation() {
  const saved = localStorage.getItem("mmkBusinessInformation");

  if (!saved) {
    return;
  }

  const data = JSON.parse(saved);

  Object.entries(data).forEach(([name, value]) => {
    const field = document.querySelector(`[name="${name}"]`);

    if (field) {
      field.value = value;
    }
  });
}

function setupBusinessForm() {
  const form = document.getElementById("business-form");

  if (!form) {
    return;
  }

  loadBusinessInformation();

  document.querySelectorAll(".sales-product-item").forEach((button) => {
    button.addEventListener("click", () => {
      const productIndex = button.dataset.productIndex;
      productSelect.value = productIndex;
      quantityInput.focus();
      calculateSale();
    });
  });

  const addProductButton = document.getElementById("add-product-from-sales");

  if (addProductButton) {
    addProductButton.addEventListener("click", () => {
      const productsButton = document.querySelector('[data-section="products"]');

      if (productsButton) {
        productsButton.click();
      }
    });
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const data = Object.fromEntries(new FormData(form));

    localStorage.setItem(
      "mmkBusinessInformation",
      JSON.stringify(data)
    );

    document.getElementById("save-message").textContent =
      "Business information saved on this device.";
  });

  document.getElementById("clear-business").addEventListener("click", () => {
    localStorage.removeItem("mmkBusinessInformation");
    form.reset();

    document.getElementById("save-message").textContent =
      "Saved business information cleared.";
  });
}

function getCustomers() {
  const saved = localStorage.getItem("mmkCustomers");

  if (!saved) {
    return [];
  }

  try {
    return JSON.parse(saved);
  } catch {
    return [];
  }
}

function saveCustomers(customers) {
  localStorage.setItem("mmkCustomers", JSON.stringify(customers));
}

function renderCustomers() {
  const list = document.getElementById("customer-list");

  if (!list) {
    return;
  }

  const customers = getCustomers();

  if (customers.length === 0) {
    list.innerHTML = "<p>No customers saved yet.</p>";
    return;
  }

  list.innerHTML = customers.map((customer, index) => {
    const moneyOwed = Number(customer.moneyOwed || 0);

    return `
      <article class="customer-card">
        <h3>${customer.name}</h3>
        <p>Money Owed: R${moneyOwed.toFixed(2)}</p>

        <h4>Debt History</h4>
        <p>No debt transactions recorded yet.</p>
        <p>Date Taken will be recorded when a credit sale is added.</p>

        <h4>Notes</h4>
        <p>${customer.notes || "No notes recorded."}</p>

        <button type="button" class="secondary delete-customer" data-index="${index}">
          Delete
        </button>
      </article>
    `;
  }).join("");

  document.querySelectorAll(".delete-customer").forEach((button) => {
    button.addEventListener("click", () => {
      const index = Number(button.dataset.index);
      const customers = getCustomers();

      customers.splice(index, 1);
      saveCustomers(customers);
      renderCustomers();
    });
  });
}

function setupCustomersForm() {
  const form = document.getElementById("customer-form");

  if (!form) {
    return;
  }

  renderCustomers();

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const formData = Object.fromEntries(new FormData(form));

    const customer = {
      name: formData.name.trim(),
      moneyOwed: Number(formData.moneyOwed || 0),
      debtHistory: [],
      notes: formData.notes.trim()
    };

    const customers = getCustomers();
    customers.push(customer);

    saveCustomers(customers);
    form.reset();
    renderCustomers();

    document.getElementById("customer-message").textContent =
      "Customer added successfully on this device.";
  });

  document.getElementById("clear-customers").addEventListener("click", () => {
    localStorage.removeItem("mmkCustomers");
    renderCustomers();

    document.getElementById("customer-message").textContent =
      "All customers cleared on this device.";
  });
}

function getSales() {
  const saved = localStorage.getItem("mmkSales");

  if (!saved) {
    return [];
  }

  try {
    return JSON.parse(saved);
  } catch {
    return [];
  }
}

function saveSales(sales) {
  localStorage.setItem("mmkSales", JSON.stringify(sales));
}

function renderSales() {
  const list = document.getElementById("sales-list");

  if (!list) {
    return;
  }

  const sales = getSales();

  if (sales.length === 0) {
    list.innerHTML = "<p>No sales recorded yet.</p>";
    return;
  }

  list.innerHTML = sales.map((sale) => `
    <article class="customer-card">
      <h3>${sale.productName}</h3>
      <p>Date: ${sale.date}</p>
      <p>Customer: ${sale.customerName}</p>
      <p>Quantity: ${sale.quantity}</p>
      <p>Sales Total: R${sale.salesTotal.toFixed(2)}</p>
      <p>Cost Total: R${sale.costTotal.toFixed(2)}</p>
      <p>Total Profit: R${sale.profit.toFixed(2)}</p>
      <p>Payment: ${sale.paymentType}</p>
      <p>Amount Paid: R${sale.amountPaid.toFixed(2)}</p>
      <p>Amount Owed: R${sale.amountOwed.toFixed(2)}</p>
    </article>
  `).join("");
}

function setupSalesForm() {
  const form = document.getElementById("sales-form");

  if (!form) {
    return;
  }

  const dateField = form.elements.date;

  if (!dateField.value) {
    dateField.value = new Date().toISOString().split("T")[0];
  }

  const summary = document.getElementById("sale-summary");

  function calculateSale() {
    const products = getProducts();
    const productIndex = Number(form.elements.productIndex.value);
    const quantity = Number(form.elements.quantity.value || 0);
    const paymentType = form.elements.paymentType.value;
    const amountPaid = Number(form.elements.amountPaid.value || 0);

    const product = products[productIndex];

    if (!product || quantity <= 0) {
      summary.innerHTML = `
        <p>Sales Total: R0.00</p>
        <p>Cost Total: R0.00</p>
        <p>Total Profit: R0.00</p>
        <p>Amount Owed: R0.00</p>
      `;
      return;
    }

    const salesTotal = Number(product.sellingPrice) * quantity;
    const costTotal = Number(product.costPrice) * quantity;
    const profit = salesTotal - costTotal;
    const stockRemaining = Number(product.stock) - quantity;

    let amountOwed = 0;

    if (paymentType === "credit") {
      amountOwed = salesTotal;
    } else if (paymentType === "partial") {
      amountOwed = Math.max(0, salesTotal - amountPaid);
    }

    summary.innerHTML = `
      <p>Sales Total: R${salesTotal.toFixed(2)}</p>
      <p>Cost Total: R${costTotal.toFixed(2)}</p>
      <p>Total Profit: R${profit.toFixed(2)}</p>
      <p>Stock Remaining: ${stockRemaining}</p>
      <p>Amount Owed: R${amountOwed.toFixed(2)}</p>
    `;
  }

  form.elements.productIndex.addEventListener("change", calculateSale);
  form.elements.quantity.addEventListener("input", calculateSale);
  form.elements.paymentType.addEventListener("change", calculateSale);
  form.elements.amountPaid.addEventListener("input", calculateSale);

  calculateSale();

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const products = getProducts();
    const customers = getCustomers();

    const productIndex = Number(form.elements.productIndex.value);
    const customerIndex = Number(form.elements.customerIndex.value);
    const quantity = Number(form.elements.quantity.value);
    const paymentType = form.elements.paymentType.value;
    const amountPaid = Number(form.elements.amountPaid.value || 0);

    const product = products[productIndex];
    const customer = customers[customerIndex];

    if (!product || !customer) {
      document.getElementById("sales-message").textContent =
        "Select a valid customer and product.";
      return;
    }

    if (quantity <= 0) {
      document.getElementById("sales-message").textContent =
        "Quantity must be at least 1.";
      return;
    }

    if (quantity > Number(product.stock)) {
      document.getElementById("sales-message").textContent =
        "Not enough stock available.";
      return;
    }

    const salesTotal = Number(product.sellingPrice) * quantity;
    const costTotal = Number(product.costPrice) * quantity;
    const profit = salesTotal - costTotal;

    let finalAmountPaid = amountPaid;

    if (paymentType === "cash") {
      finalAmountPaid = salesTotal;
    }

    if (paymentType === "credit") {
      finalAmountPaid = 0;
    }

    finalAmountPaid = Math.min(finalAmountPaid, salesTotal);

    const amountOwed = Math.max(0, salesTotal - finalAmountPaid);

    product.stock = Number(product.stock) - quantity;
    saveProducts(products);

    const sale = {
      date: form.elements.date.value,
      customerName: customer.name,
      productName: product.name,
      quantity,
      salesTotal,
      costTotal,
      profit,
      paymentType,
      amountPaid: finalAmountPaid,
      amountOwed
    };

    const sales = getSales();
    sales.push(sale);
    saveSales(sales);

    if (amountOwed > 0) {
      customer.moneyOwed =
        Number(customer.moneyOwed || 0) + amountOwed;

      customer.debtHistory = customer.debtHistory || [];

      customer.debtHistory.push({
        date: form.elements.date.value,
        product: product.name,
        quantity,
        amount: salesTotal,
        amountPaid: finalAmountPaid,
        balance: amountOwed
      });

      saveCustomers(customers);
    }

    form.reset();
    dateField.value = new Date().toISOString().split("T")[0];

    renderSales();

    document.getElementById("sales-message").textContent =
      "Sale recorded successfully on this device.";

    calculateSale();
  });

  document.getElementById("clear-sales").addEventListener("click", () => {
    localStorage.removeItem("mmkSales");
    renderSales();

    document.getElementById("sales-message").textContent =
      "All saved sales cleared.";
  });

  renderSales();
}

function getProducts() {
  const saved = localStorage.getItem("mmkProducts");

  if (!saved) {
    return [];
  }

  try {
    return JSON.parse(saved);
  } catch {
    return [];
  }
}

function saveProducts(products) {
  localStorage.setItem("mmkProducts", JSON.stringify(products));
}

function renderProducts() {
  const list = document.getElementById("product-list");

  if (!list) {
    return;
  }

  const products = getProducts();

  if (products.length === 0) {
    list.innerHTML = "<p>No products saved yet.</p>";
    return;
  }

  list.innerHTML = products.map((product, index) => {
    const profit = product.sellingPrice - product.costPrice;

    return `
      <article class="product-card">
        <h3>${product.name}</h3>
        <p>Category: ${product.category || "Not specified"}</p>
        <p>Selling Price: R${product.sellingPrice.toFixed(2)}</p>
        <p>Cost Price: R${product.costPrice.toFixed(2)}</p>
        <p>Profit per Unit: R${profit.toFixed(2)}</p>
        <p>Stock: ${product.stock}</p>
        <button type="button" class="secondary delete-product" data-index="${index}">
          Delete
        </button>
      </article>
    `;
  }).join("");

  document.querySelectorAll(".delete-product").forEach((button) => {
    button.addEventListener("click", () => {
      const index = Number(button.dataset.index);
      const products = getProducts();

      products.splice(index, 1);
      saveProducts(products);
      renderProducts();
    });
  });
}

function setupProductsForm() {
  const form = document.getElementById("product-form");

  if (!form) {
    return;
  }

  renderProducts();

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const formData = Object.fromEntries(new FormData(form));

    const product = {
      name: formData.name.trim(),
      category: formData.category.trim(),
      sellingPrice: Number(formData.sellingPrice),
      costPrice: Number(formData.costPrice),
      stock: Number(formData.stock)
    };

    const products = getProducts();
    products.push(product);

    saveProducts(products);
    form.reset();
    renderProducts();

    document.getElementById("product-message").textContent =
      "Product added successfully on this device.";
  });

  document.getElementById("clear-products").addEventListener("click", () => {
    localStorage.removeItem("mmkProducts");
    renderProducts();

    document.getElementById("product-message").textContent =
      "All saved products cleared.";
  });
}

document.querySelectorAll("[data-section]").forEach((button) => {
  button.addEventListener("click", () => {
    const section = sections[button.dataset.section];

    if (section.render) {
      workspace.innerHTML = section.render();

      if (button.dataset.section === "business") {
        setupBusinessForm();
      }

      if (button.dataset.section === "products") {
        setupProductsForm();
      }

      if (button.dataset.section === "customers") {
        setupCustomersForm();
      }

      if (button.dataset.section === "sales") {
        setupSalesForm();
      }

      if (button.dataset.section === "reports") {
        renderReports();
      }

      return;
    }

    workspace.innerHTML = `
      <h2>${section.title}</h2>
      <p>${section.text}</p>
      <p><strong>Web module v0.1</strong></p>
    `;
  });
});
