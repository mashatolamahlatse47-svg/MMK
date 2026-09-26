"use strict";

const loads = [];

function updateLoadIncome() {
  const routeId = document.getElementById("route").value;
  const passengers = Number(document.getElementById("passengers").value) || 0;
  const result = window.MMKTaxiCalculator.calculateRouteLoad(routeId, passengers);
  document.getElementById("load-income").textContent = "R" + result.income.toFixed(2);
}

document.getElementById("route").addEventListener("change", updateLoadIncome);
document.getElementById("passengers").addEventListener("input", updateLoadIncome);

document.getElementById("add-load").addEventListener("click", function () {
  const routeId = document.getElementById("route").value;
  const passengers = Number(document.getElementById("passengers").value) || 0;
  if (passengers < 1) return;
  const result = window.MMKTaxiCalculator.calculateRouteLoad(routeId, passengers);
  loads.push(result);
  document.getElementById("load-list").innerHTML = loads.map(function(load, index) {
    return "<p>Load " + (index + 1) + ": " + load.passengers + " passengers × R" + load.fare.toFixed(2) + " = <strong>R" + load.income.toFixed(2) + "</strong></p>";
  }).join("");
  const summary = window.MMKTaxiCalculator.calculateGrossIncome(loads);
  document.getElementById("gross-income").textContent = "R" + summary.toFixed(2);
  document.getElementById("total-passengers").textContent = loads.reduce(function(total, load) { return total + load.passengers; }, 0);
  document.getElementById("total-loads").textContent = loads.length;
  updateLoadIncome();
});

updateLoadIncome();
