(function () {
  "use strict";

  function getData() {
    if (!window.MMKOffline) {
      throw new Error("Business data is not ready. Reload the calculator and try again.");
    }
    const data = window.MMKOffline.load();
    return {
      products: Array.isArray(data.products) ? data.products : [],
      sales: Array.isArray(data.sales) ? data.sales : [],
      settings: data.settings || { businessName: "MMK" }
    };
  }

  function money(value) {
    return "R" + (Number(value) || 0).toLocaleString("en-ZA", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (c) {
      return ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;",
        '"': "&quot;", "'": "&#39;"
      })[c];
    });
  }

  function download(content, type, filename) {
    const blob = new Blob([content], { type: type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1500);
  }

  function makeTable(headers, rows) {
    return "<table><thead><tr>" +
      headers.map(function (h) {
        return "<th>" + escapeHtml(h) + "</th>";
      }).join("") +
      "</tr></thead><tbody>" +
      (rows.length ? rows.map(function (row) {
        return "<tr>" + row.map(function (v) {
          return "<td>" + escapeHtml(v) + "</td>";
        }).join("") + "</tr>";
      }).join("") : '<tr><td colspan="' + headers.length +
        '">No records available.</td></tr>') +
      "</tbody></table>";
  }

  function exportReport() {
    const data = getData();
    const products = data.products;
    const sales = data.sales;
    const business = data.settings.businessName || "MMK";
    const now = new Date();
    const dateText = now.toLocaleString("en-ZA");
    const fileDate = now.toISOString().slice(0, 10);

    const stockCount = products.reduce(function (n, p) {
      return n + (Number(p.stock) || 0);
    }, 0);
    const stockValue = products.reduce(function (n, p) {
      return n + (Number(p.cost) || 0) * (Number(p.stock) || 0);
    }, 0);
    const revenue = sales.reduce(function (n, s) {
      return n + (Number(s.revenue) || 0);
    }, 0);
    const profit = sales.reduce(function (n, s) {
      return n + (Number(s.profit) || 0);
    }, 0);

    const productRows = products.map(function (p) {
      const cost = Number(p.cost) || 0;
      const price = Number(p.price) || 0;
      const qty = Number(p.stock) || 0;
      return [
        p.name || "Unnamed product",
        money(cost),
        money(price),
        String(qty),
        money(price - cost),
        money(cost * qty)
      ];
    });

    const salesRows = sales.slice().reverse().map(function (s) {
      let date = s.date || "";
      if (date) {
        const parsed = new Date(date);
        if (!isNaN(parsed.getTime())) date = parsed.toLocaleString("en-ZA");
      }
      return [
        date,
        s.productName || "Unnamed product",
        String(Number(s.quantity) || 0),
        money(s.revenue),
        money(s.profit)
      ];
    });

    const html = '<!doctype html><html lang="en"><head><meta charset="utf-8">' +
      '<meta name="viewport" content="width=device-width,initial-scale=1">' +
      '<title>' + escapeHtml(business) + ' Business Report</title>' +
      '<style>' +
      '*{box-sizing:border-box}body{margin:0;background:#f1f4f2;color:#1b2922;' +
      'font:16px/1.5 Arial,sans-serif}.page{max-width:1000px;margin:24px auto;' +
      'padding:24px;background:#fff;border-radius:14px}.brand{background:#173d32;' +
      'color:#fff;padding:26px;border-radius:10px}.brand h1{margin:0 0 8px;' +
      'font-size:28px}.muted{color:#637168}.brand .muted{color:#d5e5dc}' +
      '.stats{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;' +
      'margin:20px 0}.stat{padding:16px;border:1px solid #d9e3dc;border-radius:9px}' +
      '.stat span{display:block;color:#52655a;font-size:13px}.stat strong{' +
      'display:block;font-size:22px;overflow-wrap:anywhere}h2{margin-top:28px;' +
      'font-size:20px} .tablewrap{overflow-x:auto}table{width:100%;border-collapse:' +
      'collapse;font-size:14px}th{background:#e6eee8;text-align:left}td,th{' +
      'padding:10px 8px;border-bottom:1px solid #dce4de}td{overflow-wrap:anywhere}' +
      '.actions{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}' +
      'button{border:0;border-radius:8px;padding:12px 16px;background:#173d32;' +
      'color:#fff;font-size:15px}footer{margin-top:30px;border-top:1px solid #ddd;' +
      'padding-top:15px;color:#637168;font-size:12px}' +
      '@media(max-width:600px){.page{margin:0;padding:14px;border-radius:0}' +
      '.brand{padding:18px}.brand h1{font-size:23px}.stat strong{font-size:18px}' +
      'table{font-size:12px}td,th{padding:8px 6px}}' +
      '@media print{body{background:#fff;font-size:11px}.page{margin:0;padding:0;' +
      'max-width:none}.actions{display:none}.brand{print-color-adjust:exact;' +
      '-webkit-print-color-adjust:exact}.stats{grid-template-columns:repeat(4,1fr)}' +
      'h2{break-after:avoid}tr{break-inside:avoid}table{font-size:10px}}' +
      '</style></head><body><main class="page">' +
      '<header class="brand"><h1>' + escapeHtml(business) +
      '</h1><div>STOCK, SALES &amp; PROFIT REPORT</div>' +
      '<p class="muted">Generated: ' + escapeHtml(dateText) +
      '<br>Currency: South African rand (ZAR)</p></header>' +
      '<div class="actions"><button onclick="window.print()">Print / Save as PDF</button>' +
      '<button onclick="window.scrollTo({top:0,behavior:\'smooth\'})">Back to top</button></div>' +
      '<section class="stats">' +
      '<div class="stat"><span>Products listed</span><strong>' + products.length + '</strong></div>' +
      '<div class="stat"><span>Units in stock</span><strong>' + stockCount + '</strong></div>' +
      '<div class="stat"><span>Stock cost value</span><strong>' + money(stockValue) + '</strong></div>' +
      '<div class="stat"><span>Recorded sales</span><strong>' + sales.length + '</strong></div>' +
      '<div class="stat"><span>Recorded revenue</span><strong>' + money(revenue) + '</strong></div>' +
      '<div class="stat"><span>Recorded profit</span><strong>' + money(profit) + '</strong></div>' +
      '</section><h2>Stock Inventory</h2><div class="tablewrap">' +
      makeTable(["Product", "Unit cost", "Selling price", "Quantity", "Profit per unit", "Stock cost value"], productRows) +
      '</div><h2>Sales History</h2><div class="tablewrap">' +
      makeTable(["Date", "Product", "Quantity", "Revenue", "Profit"], salesRows) +
      '</div><footer>Prepared using ' + escapeHtml(business) +
      ' Stock &amp; Profit Calculator. Figures are based on locally saved records. ' +
      'Profit does not include expenses that have not been entered into the calculator.</footer>' +
      '</main></body></html>';

    download(html, "text/html;charset=utf-8", "MMK-Business-Report-" + fileDate + ".html");
  }

  function csvCell(value) {
    let s = String(value == null ? "" : value);
    if (/^[\s]*[=+\-@]/.test(s)) s = "'" + s;
    return '"' + s.replace(/"/g, '""') + '"';
  }

  function exportCsv(kind) {
    const data = getData();
    let rows;
    let filename;

    if (kind === "stock") {
      rows = [["Product", "Unit cost (ZAR)", "Selling price (ZAR)", "Quantity in stock", "Profit per unit (ZAR)", "Stock cost value (ZAR)"]];
      data.products.forEach(function (p) {
        const cost = Number(p.cost) || 0;
        const price = Number(p.price) || 0;
        const qty = Number(p.stock) || 0;
        rows.push([p.name || "", cost.toFixed(2), price.toFixed(2), qty, (price - cost).toFixed(2), (cost * qty).toFixed(2)]);
      });
      filename = "MMK-Stock-Inventory-" + new Date().toISOString().slice(0, 10) + ".csv";
    } else {
      rows = [["Date", "Product", "Quantity", "Revenue (ZAR)", "Profit (ZAR)"]];
      data.sales.forEach(function (s) {
        rows.push([s.date || "", s.productName || "", Number(s.quantity) || 0, (Number(s.revenue) || 0).toFixed(2), (Number(s.profit) || 0).toFixed(2)]);
      });
      filename = "MMK-Sales-History-" + new Date().toISOString().slice(0, 10) + ".csv";
    }

    const csv = "\uFEFF" + rows.map(function (row) {
      return row.map(csvCell).join(",");
    }).join("\r\n");
    download(csv, "text/csv;charset=utf-8", filename);
  }

  document.addEventListener("DOMContentLoaded", function () {
    const actions = [
      ["exportReportButton", exportReport],
      ["exportStockCsvButton", function () { exportCsv("stock"); }],
      ["exportSalesCsvButton", function () { exportCsv("sales"); }]
    ];

    actions.forEach(function (entry) {
      const button = document.getElementById(entry[0]);
      if (button) button.addEventListener("click", function () {
        try {
          entry[1]();
        } catch (error) {
          console.error("MMK export failed:", error);
          alert("Export could not be completed. Reload the calculator and try again.");
        }
      });
    });
  });
})();
