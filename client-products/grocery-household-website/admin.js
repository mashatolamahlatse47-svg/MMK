const STORAGE_KEY = "mmk_grocery_products";

function loadAdminProducts() {
  const saved = localStorage.getItem(STORAGE_KEY);

  if (!saved) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(products));
    return [...products];
  }

  try {
    return JSON.parse(saved);
  } catch {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(products));
    return [...products];
  }
}

let adminProducts = loadAdminProducts();

function saveAdminProducts() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(adminProducts));
}


function createImagePicker(product, index) {
  const wrapper = document.createElement("div");
  wrapper.className = "image-manager";

  wrapper.innerHTML = `
    <label class="admin-label">Product Picture</label>

    <div class="admin-image-preview">
      ${
        product.image
          ? `<img src="${product.image}" alt="${product.name || "Product"}">`
          : `<div class="admin-image-empty">📷<span>No picture selected</span></div>`
      }
    </div>

    <input
      type="file"
      class="admin-image-input"
      accept="image/*"
      data-image-index="${index}"
    />

    <small class="admin-help">
      Choose a picture from your phone. It will be saved with this product.
    </small>
  `;

  const input = wrapper.querySelector(".admin-image-input");

  input.addEventListener("change", function () {
    const file = this.files && this.files[0];

    if (!file) return;

    if (!file.type.startsWith("image/")) {
      alert("Please choose an image file.");
      this.value = "";
      return;
    }

    const reader = new FileReader();

    reader.onload = function (event) {
      adminProducts[index].image = event.target.result;
      saveAdminProducts();

      renderAdminProducts();

      alert("Product picture selected and saved.");
    };

    reader.readAsDataURL(file);
  });

  return wrapper;
}

function renderAdminProducts() {
  const container = document.getElementById("adminProducts");

  if (!container) return;

  container.innerHTML = "";

  adminProducts.forEach((product, index) => {
    const card = document.createElement("div");
    card.className = "admin-product";

    card.innerHTML = `
      <div class="admin-product-info">
        <strong>${product.name}</strong>
        <small>${product.category} • ${product.size}</small>
      </div>

      <div class="admin-price-row">
        <label>Price (R)</label>
        <input
          type="number"
          min="0"
          step="0.01"
          value="${product.price || 0}"
          data-price-id="${product.id}"
        >

        <button
          class="admin-save"
          data-save-id="${product.id}">
          Save Price
        </button>
      </div>
    `;

    const imagePicker = createImagePicker(product, index);
    card.appendChild(imagePicker);

    container.appendChild(card);
  });

  document.querySelectorAll("[data-save-id]").forEach(button => {
    button.addEventListener("click", () => {
      const id = Number(button.dataset.saveId);
      const input = document.querySelector(`[data-price-id="${id}"]`);
      const product = adminProducts.find(item => item.id === id);

      if (!product || !input) return;

      product.price = Number(input.value) || 0;
      saveAdminProducts();

      alert(`${product.name} price saved.`);
    });
  });
}

const addProductButton = document.getElementById("addProduct");

if (addProductButton) {
  addProductButton.addEventListener("click", () => {
    const name = document.getElementById("adminName").value.trim();
    const size = document.getElementById("adminSize").value.trim();
    const category = document.getElementById("adminCategory").value.trim();
    const price = Number(document.getElementById("adminPrice").value) || 0;

    if (!name || !size || !category) {
      alert("Please enter product name, size and category.");
      return;
    }

    const nextId = adminProducts.length
      ? Math.max(...adminProducts.map(item => item.id)) + 1
      : 1;

    adminProducts.push({
      id: nextId,
      category,
      name,
      size,
      price
    });

    saveAdminProducts();
    renderAdminProducts();

    document.getElementById("adminName").value = "";
    document.getElementById("adminSize").value = "";
    document.getElementById("adminCategory").value = "";
    document.getElementById("adminPrice").value = "";

    alert("Product added successfully.");
  });
}

renderAdminProducts();

console.log("[MMK] Admin price manager loaded.");
