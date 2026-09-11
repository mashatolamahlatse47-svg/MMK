document.addEventListener("DOMContentLoaded", () => {
  const config = window.MMK_CONFIG || {
    businessName: "MMK",
    appName: "Stock & Profit Calculator",
    currency: "R"
  };

  const form = document.getElementById("calculatorForm");
  const productName = document.getElementById("productName");
  const costPrice = document.getElementById("costPrice");
  const sellingPrice = document.getElementById("sellingPrice");
  const quantity = document.getElementById("quantity");

  const resultProduct = document.getElementById("resultProduct");
  const totalCost = document.getElementById("totalCost");
  const totalSales = document.getElementById("totalSales");
  const profitPerItem = document.getElementById("profitPerItem");
  const totalProfit = document.getElementById("totalProfit");
  const status = document.getElementById("status");

  function money(value) {
    return `${config.currency}${Number(value).toFixed(2)}`;
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const name = productName.value.trim() || "Unnamed Product";
    const cost = Number(costPrice.value) || 0;
    const selling = Number(sellingPrice.value) || 0;
    const qty = Number(quantity.value) || 0;

    const costTotal = cost * qty;
    const salesTotal = selling * qty;
    const itemProfit = selling - cost;
    const profitTotal = itemProfit * qty;

    resultProduct.textContent = name;
    totalCost.textContent = money(costTotal);
    totalSales.textContent = money(salesTotal);
    profitPerItem.textContent = money(itemProfit);
    totalProfit.textContent = money(profitTotal);

    if (profitTotal > 0) {
      status.textContent = "PROFIT";
      status.className = "status profit";
    } else if (profitTotal < 0) {
      status.textContent = "LOSS";
      status.className = "status loss";
    } else {
      status.textContent = "BREAK-EVEN";
      status.className = "status break-even";
    }
  });
});
