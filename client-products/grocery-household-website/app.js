const STORAGE_KEY = "mmk_grocery_products";

const productGrid = document.getElementById("productGrid");

const activeProducts = (() => {
  const saved = localStorage.getItem(STORAGE_KEY);

  if (!saved) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(products));
    return [...products];
  }

  try {
    const parsed = JSON.parse(saved);
    return Array.isArray(parsed) ? parsed : [...products];
  } catch {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(products));
    return [...products];
  }
})();
const categoryFilters = document.getElementById("categoryFilters");
const whatsappOrder = document.getElementById("whatsappOrder");

let selectedCategory = "All";
const cart = new Map();

function formatPrice(price) {
  if (!price || Number(price) <= 0) {
    return "Price to be confirmed";
  }

  return `R${Number(price).toFixed(2)}`;
}

function renderFilters() {
  const categories = [
    "All",
    ...new Set(activeProducts.map(product => product.category))
  ];

  categoryFilters.innerHTML = categories
    .map(category => `
      <button
        class="filter-btn ${category === selectedCategory ? "active" : ""}"
        data-category="${category}">
        ${category}
      </button>
    `)
    .join("");

  document.querySelectorAll(".filter-btn").forEach(button => {
    button.addEventListener("click", () => {
      selectedCategory = button.dataset.category;
      renderFilters();
      renderProducts();
    });
  });
}

function renderProducts() {
  const visibleProducts = selectedCategory === "All"
    ? activeProducts
    : activeProducts.filter(product => product.category === selectedCategory);

  productGrid.innerHTML = visibleProducts
    .map(product => {
      const quantity = cart.get(product.id) || 0;

      return `
        <article class="product-card">
          <div class="product-image">
            ${
              product.image
                ? `<img src="${product.image}" alt="${product.name}" loading="lazy">`
                : `<div class="image-placeholder">📷<span>Add product photo</span></div>`
            }
          </div>

          <div class="product-info">
            <span class="category">${product.category}</span>
            <h3>${product.name}</h3>
            <p>${product.size}</p>
            <strong>${formatPrice(product.price)}</strong>
          </div>

          <div class="quantity-control">
            <button
              class="quantity-btn"
              data-action="minus"
              data-id="${product.id}">
              −
            </button>

            <span>${quantity}</span>

            <button
              class="quantity-btn"
              data-action="plus"
              data-id="${product.id}">
              +
            </button>
          </div>
        </article>
      `;
    })
    .join("");

  document.querySelectorAll(".quantity-btn").forEach(button => {
    button.addEventListener("click", () => {
      const id = Number(button.dataset.id);
      const action = button.dataset.action;
      const current = cart.get(id) || 0;

      if (action === "plus") {
        cart.set(id, current + 1);
      }

      if (action === "minus") {
        if (current <= 1) {
          cart.delete(id);
        } else {
          cart.set(id, current - 1);
        }
      }

      renderProducts();
      updateOrderButton();
    });
  });
}

function updateOrderButton() {
  const totalItems = [...cart.values()]
    .reduce((total, quantity) => total + quantity, 0);

  whatsappOrder.textContent =
    totalItems > 0
      ? `Send WhatsApp Order (${totalItems})`
      : "Send WhatsApp Order";
}

function createWhatsAppMessage() {
  if (cart.size === 0) {
    return "Hello Molebogeng, I would like to place an order. Please send me the available products and prices.";
  }

  let message = "Hello Molebogeng, I would like to place an order:%0A%0A";

  cart.forEach((quantity, id) => {
    const product = activeProducts.find(item => item.id === id);

    message += `${quantity} x ${product.name} (${product.size}) - ${formatPrice(product.price)}%0A`;
  });

  message += "%0APlease confirm availability and the final total. Thank you.";

  return message;
}

whatsappOrder.addEventListener("click", () => {
  const message = createWhatsAppMessage();
  const url = `https://wa.me/27715078355?text=${message}`;

  window.open(url, "_blank");
});

renderFilters();
renderProducts();
updateOrderButton();

console.log("[MMK] Grocery website app loaded successfully.");
