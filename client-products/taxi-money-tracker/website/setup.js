
document.getElementById("save-setup").addEventListener("click", function () {
  const setup = {
    vehicle: document.getElementById("vehicle").value.trim(),
    driver: document.getElementById("driver").value.trim(),
    ownerTarget: Number(document.getElementById("owner-target").value) || 0,
    reservePerKm: Number(document.getElementById("reserve-per-km").value) || 0,
    startOdometer: Number(document.getElementById("start-odometer").value) || 0
  };
  localStorage.setItem("mmkTaxiDailySetup", JSON.stringify(setup));
  document.getElementById("setup-status").textContent = "Daily setup saved."; 
});
