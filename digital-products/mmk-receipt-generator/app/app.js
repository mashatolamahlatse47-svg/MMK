const itemsContainer = document.getElementById("items");

function addItem(name = "", quantity = 1, price = 0) {
  const row = document.createElement("div");
  row.className = "item-row";

  row.innerHTML = `
    <input class="item-name" type="text" placeholder="Item / Service" value="${name}">
    <input class="item-qty" type="number" min="1" step="1" value="${quantity}">
    <input class="item-price" type="number" min="0" step="0.01" value="${price}">
    <button type="button" class="remove">Remove</button>
  `;

  row.querySelector(".remove").addEventListener("click", () => {
    row.remove();
    generateReceipt();
  });

  row.querySelectorAll("input").forEach(input => {
    input.addEventListener("input", generateReceipt);
    input.addEventListener("change", generateReceipt);
  });

  itemsContainer.appendChild(row);
}

function money(value) {
  return Number(value).toFixed(2);
}

function generateReceipt() {
  const business = document.getElementById("businessName").value.trim();
  const phone = document.getElementById("businessPhone").value.trim();
  const number = document.getElementById("receiptNumber").value.trim();
  const date = document.getElementById("receiptDate").value;
  const customer = document.getElementById("customerName").value.trim();
  const payment = document.getElementById("paymentMethod").value;
  const reference = document.getElementById("paymentReference").value.trim();
  const discount = Math.max(
    0,
    Number(document.getElementById("discount").value) || 0
  );
  const amountPaid = Math.max(
    0,
    Number(document.getElementById("amountPaid").value) || 0
  );

  document.getElementById("outBusiness").textContent =
    business || "Your Business";

  document.getElementById("outPhone").textContent = phone;
  document.getElementById("outNumber").textContent = number || "REC-0001";
  document.getElementById("outDate").textContent = date || "";
  document.getElementById("outCustomer").textContent = customer || "Walk-in Customer";
  document.getElementById("outPayment").textContent = payment;
  document.getElementById("outReference").textContent = reference;

  const output = document.getElementById("outItems");
  output.innerHTML = "";

  let subtotal = 0;

  document.querySelectorAll(".item-row").forEach(row => {
    const name = row.querySelector(".item-name").value.trim() || "Item";
    const quantity = Number(row.querySelector(".item-qty").value) || 0;
    const price = Number(row.querySelector(".item-price").value) || 0;
    const total = quantity * price;

    subtotal += total;

    const tr = document.createElement("tr");

    [name, quantity, `R${money(price)}`, `R${money(total)}`]
      .forEach(value => {
        const td = document.createElement("td");
        td.textContent = value;
        tr.appendChild(td);
      });

    output.appendChild(tr);
  });

  const amountDue = Math.max(0, subtotal - discount);
  const change = Math.max(0, amountPaid - amountDue);
  const amountOwing = Math.max(0, amountDue - amountPaid);

  document.getElementById("outSubtotal").textContent = money(subtotal);
  document.getElementById("outDiscount").textContent = money(discount);
  document.getElementById("outTotal").textContent = money(amountDue);
  document.getElementById("outAmountPaid").textContent = money(amountPaid);
  document.getElementById("outChange").textContent = money(change);
  document.getElementById("outAmountOwing").textContent = money(amountOwing);
}

document.getElementById("addItem").addEventListener("click", () => {
  addItem();
});

document.getElementById("generate").addEventListener("click", generateReceipt);

[
  "businessName",
  "businessPhone",
  "receiptNumber",
  "receiptDate",
  "customerName",
  "paymentMethod",
  "paymentReference",
  "discount",
  "amountPaid"
].forEach(id => {
  const field = document.getElementById(id);
  field.addEventListener("input", generateReceipt);
  field.addEventListener("change", generateReceipt);
});

document.getElementById("print").addEventListener("click", () => {
  generateReceipt();
  window.print();
});

addItem();
addItem();
addItem();

document.getElementById("receiptDate").value =
  new Date().toISOString().split("T")[0];

generateReceipt();
