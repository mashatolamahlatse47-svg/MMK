document.addEventListener("DOMContentLoaded", () => {
  const STORAGE_KEY = "mmk_stock_records";

  const form = document.getElementById("stockForm");
  const productName = document.getElementById("stockProductName");
  const costPrice = document.getElementById("stockCostPrice");
  const sellingPrice = document.getElementById("stockSellingPrice");
  const quantity = document.getElementById("stockQuantity");

  const tableBody = document.getElementById("stockTableBody");
  const recordCount = document.getElementById("recordCount");
  const totalStock = document.getElementById("totalStock");
  const stockValue = document.getElementById("stockValue");

  function loadRecords() {
    const saved = localStorage.getItem(STORAGE_KEY);

    if (saved) {
      return JSON.parse(saved);
    }

    return [];
  }

  function saveRecords(records) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
  }

  function money(value) {
    return `${(Number(value) || 0).toFixed(2)}`;
  }

  function render() {
    const records = loadRecords();

    tableBody.innerHTML = "";

    let stockTotal = 0;
    let valueTotal = 0;

    records.forEach((product) => {
      stockTotal += Number(product.stock);
      valueTotal += Number(product.cost) * Number(product.stock);

      const row = document.createElement("tr");

      const values = [
        product.name,
        `R${money(product.cost)}`,
        `R${money(product.price)}`,
        product.stock,
        `R${money(product.price - product.cost)}`
      ];

      values.forEach((value) => {
        const cell = document.createElement("td");
        cell.textContent = value;
        cell.style.padding = "8px";
        row.appendChild(cell);
      });

      const actionCell = document.createElement("td");
      actionCell.style.padding = "8px";

      const sellButton = document.createElement("button");
      sellButton.textContent = "Sell 1";
      sellButton.type = "button";
      sellButton.style.width = "auto";
      sellButton.style.margin = "0 4px 4px 0";
      sellButton.style.padding = "7px 10px";

      sellButton.addEventListener("click", () => {
        sellProduct(product.id);
      });

      const restockButton = document.createElement("button");
      restockButton.textContent = "Restock 1";
      restockButton.type = "button";
      restockButton.style.width = "auto";
      restockButton.style.margin = "0 4px 4px 0";
      restockButton.style.padding = "7px 10px";

      restockButton.addEventListener("click", () => {
        restockProduct(product.id);
      });

      const deleteButton = document.createElement("button");
      deleteButton.textContent = "Delete";
      deleteButton.type = "button";
      deleteButton.style.width = "auto";
      deleteButton.style.margin = "0";
      deleteButton.style.padding = "7px 10px";

      deleteButton.addEventListener("click", () => {
        deleteProduct(product.id);
      });

      actionCell.appendChild(sellButton);
      actionCell.appendChild(restockButton);
      actionCell.appendChild(deleteButton);

      row.appendChild(actionCell);
      tableBody.appendChild(row);
    });

    recordCount.textContent = records.length;
    totalStock.textContent = stockTotal;
    stockValue.textContent = `R${money(valueTotal)}`;
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const name = productName.value.trim();

    if (!name) {
      alert("Enter a product name.");
      return;
    }

    const cost = Number(costPrice.value);
    const price = Number(sellingPrice.value);
    const stock = Number(quantity.value);

    if (cost < 0 || price < 0 || stock < 0) {
      alert("Values cannot be negative.");
      return;
    }

    const records = loadRecords();

    const newProduct = {
      id: `MMK-${Date.now()}`,
      name,
      cost,
      price,
      stock
    };

    records.push(newProduct);
    saveRecords(records);

    form.reset();
    render();
  });

  function sellProduct(id) {
    const records = loadRecords();
    const product = records.find((item) => item.id === id);

    if (!product) {
      return;
    }

    if (Number(product.stock) <= 0) {
      alert("Not enough stock.");
      return;
    }

    product.stock = Number(product.stock) - 1;

    saveRecords(records);
    render();
  }

  function restockProduct(id) {
    const records = loadRecords();
    const product = records.find((item) => item.id === id);

    if (!product) {
      return;
    }

    product.stock = Number(product.stock) + 1;

    saveRecords(records);
    render();
  }

  function deleteProduct(id) {
    const confirmed = confirm("Delete this product?");

    if (!confirmed) {
      return;
    }

    const records = loadRecords();
    const updatedRecords = records.filter((item) => item.id !== id);

    saveRecords(updatedRecords);
    render();
  }

  async function initialiseStock() {
    const existing = localStorage.getItem(STORAGE_KEY);

    if (existing) {
      render();
      return;
    }

    try {
      const response = await fetch("products.json");

      if (!response.ok) {
        throw new Error("Could not load products.json");
      }

      const products = await response.json();

      saveRecords(products);
      render();
    } catch (error) {
      console.error(error);
      render();
    }
  }

  initialiseStock();
});
