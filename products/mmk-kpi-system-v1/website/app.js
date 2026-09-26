"use strict";

const kpis = {
    revenue: 0,
    profit: 0,
    salesCount: 0,
    stock: 0,
    credit: 0,
    expectedMoney: 0
};

document.getElementById("revenue").textContent =
    `R${kpis.revenue.toFixed(2)}`;

document.getElementById("profit").textContent =
    `R${kpis.profit.toFixed(2)}`;

document.getElementById("sales-count").textContent =
    kpis.salesCount;

document.getElementById("stock").textContent =
    kpis.stock;

document.getElementById("credit").textContent =
    `R${kpis.credit.toFixed(2)}`;

document.getElementById("expected-money").textContent =
    `R${kpis.expectedMoney.toFixed(2)}`;
