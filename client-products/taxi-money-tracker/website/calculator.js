(function () {
  "use strict";

  function money(value) {
    const number = Number(value) || 0;
    return Math.round((number + Number.EPSILON) * 100) / 100;
  }

  function calculateLoad(passengers, fare) {
    return money(Number(passengers) * Number(fare));
  }

  function calculateRouteLoad(routeId, passengers) {
    if (
      !window.MMKTaxiFareConfig ||
      typeof window.MMKTaxiFareConfig.getFare !== "function"
    ) {
      throw new Error("MMK Taxi fare configuration is not loaded.");
    }

    const fare = window.MMKTaxiFareConfig.getFare(routeId);

    if (fare <= 0) {
      throw new Error("Unknown or invalid taxi route.");
    }

    return {
      routeId: routeId,
      passengers: Number(passengers),
      fare: money(fare),
      income: calculateLoad(passengers, fare)
    };
  }

  function calculateGrossIncome(loads) {
    return money((loads || []).reduce(
      (total, load) =>
        total + calculateLoad(load.passengers, load.fare),
      0
    ));
  }

  function calculateDistance(start, end) {
    return money(Math.max(
      0,
      Number(end || 0) - Number(start || 0)
    ));
  }

  function calculateFuelCost(litres, price) {
    return money(Number(litres) * Number(price));
  }

  function calculateMaintenanceReserve(distance, rate) {
    return money(Number(distance) * Number(rate));
  }

  function calculateDay(data) {
    const loads = data.loads || [];
    const grossIncome = calculateGrossIncome(loads);

    const passengers = loads.reduce(
      (total, load) => total + (Number(load.passengers) || 0),
      0
    );

    const distance = calculateDistance(
      data.startOdometer,
      data.endOdometer
    );

    const fuelCost = calculateFuelCost(
      data.fuelLitres,
      data.fuelPricePerLitre
    );

    const otherExpenses = money(data.otherExpenses);

    const maintenanceReserve = calculateMaintenanceReserve(
      distance,
      data.maintenanceReservePerKm
    );

    const operatingResult = money(
      grossIncome -
      fuelCost -
      otherExpenses -
      maintenanceReserve
    );

    const ownerTarget = money(data.ownerTarget);
    const ownerContribution = money(data.ownerContribution);

    const ownerShortfall = money(
      Math.max(0, ownerTarget - ownerContribution)
    );

    const driverBalance = money(
      Math.max(0, operatingResult - ownerContribution)
    );

    return {
      totalLoads: loads.length,
      totalPassengers: passengers,
      grossIncome,
      distance,
      fuelCost,
      otherExpenses,
      maintenanceReserve,
      operatingResult,
      ownerTarget,
      ownerContribution,
      ownerShortfall,
      driverBalance,
      targetReached: ownerContribution >= ownerTarget
    };
  }

  window.MMKTaxiCalculator = {
    money,
    calculateLoad,
    calculateRouteLoad,
    calculateGrossIncome,
    calculateDistance,
    calculateFuelCost,
    calculateMaintenanceReserve,
    calculateDay
  };
})();
