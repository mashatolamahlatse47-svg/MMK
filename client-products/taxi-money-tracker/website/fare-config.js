"use strict";

window.MMKTaxiFareConfig = {
  currency: "ZAR",

  fares: [
    {
      id: "local",
      name: "Local",
      fare: 17.00
    },
    {
      id: "cbd",
      name: "CBD",
      fare: 28.00
    }
  ],

  getFare(routeId) {
    const route = this.fares.find(item => item.id === routeId);
    return route ? Number(route.fare) : 0;
  },

  getRoute(routeId) {
    return this.fares.find(item => item.id === routeId) || null;
  }
};
