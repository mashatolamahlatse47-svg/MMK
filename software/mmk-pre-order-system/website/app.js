const API_BASE = "http://127.0.0.1:5050";

let menu = [];
let cart = {};

async function loadMenu() {
    const response = await fetch(`${API_BASE}/api/menu`);
    if (!response.ok) {
        throw new Error("Could not load menu.");
    }

    menu = await response.json();
    renderMenu();
}

function renderMenu() {
    const container = document.getElementById("menu");
    const categories = [...new Set(menu.map(item => item.category))];

    container.innerHTML = categories.map(category => {
        const items = menu.filter(item => item.category === category);

        return `
            <section class="category">
                <h3>${category}</h3>
                <div class="menu-grid">
                    ${items.map(item => `
                        <article class="menu-item">
                            <h4>${item.name}</h4>
                            <div class="price">R${Number(item.price).toFixed(2)}</div>
                            <button class="add" onclick="addToCart(${item.id})">
                                ADD
                            </button>
                        </article>
                    `).join("")}
                </div>
            </section>
        `;
    }).join("");
}

function addToCart(id) {
    cart[id] = (cart[id] || 0) + 1;
    renderCart();
}

function renderCart() {
    const container = document.getElementById("cart");

    const entries = Object.entries(cart)
        .filter(([, quantity]) => quantity > 0)
        .map(([id, quantity]) => {
            const item = menu.find(menuItem => menuItem.id === Number(id));
            return { item, quantity };
        });

    if (!entries.length) {
        container.innerHTML = "<p>Your order is empty.</p>";
    } else {
        container.innerHTML = entries.map(({ item, quantity }) => `
            <div class="cart-item">
                <span>${item.name} × ${quantity}</span>
                <strong>R${(item.price * quantity).toFixed(2)}</strong>
            </div>
        `).join("");
    }

    const total = entries.reduce(
        (sum, entry) => sum + entry.item.price * entry.quantity,
        0
    );

    document.getElementById("total").textContent = `R${total.toFixed(2)}`;
}

document.getElementById("confirmOrder").addEventListener("click", () => {
    const entries = Object.entries(cart)
        .filter(([, quantity]) => quantity > 0);

    const name = document.getElementById("customerName").value.trim();
    const collection = document.getElementById("collectionTime").value;

    if (!entries.length) {
        alert("Please add an item to your order.");
        return;
    }

    if (!name) {
        alert("Please enter your name.");
        return;
    }

    if (!collection) {
        alert("Please select a collection time.");
        return;
    }

    const orderNumber = `MMK-${Date.now().toString().slice(-6)}`;

    const confirmation = document.getElementById("confirmation");
    confirmation.classList.remove("hidden");
    confirmation.innerHTML = `
        <strong>ORDER CONFIRMED ✅</strong>
        <p>Order: <strong>${orderNumber}</strong></p>
        <p>Collection: <strong>${collection}</strong></p>
        <p>Thank you for supporting local business.</p>
    `;
});

const WHATSAPP_NUMBER = "27724422893";

document.getElementById("whatsappOrder").addEventListener("click", () => {
    const entries = Object.entries(cart)
        .filter(([, quantity]) => quantity > 0)
        .map(([id, quantity]) => {
            const item = menu.find(menuItem => menuItem.id === Number(id));
            return { item, quantity };
        });

    const name = document.getElementById("customerName").value.trim();
    const reference = document.getElementById("customerReference").value.trim();
    const collection = document.getElementById("collectionTime").value;

    if (!entries.length) {
        alert("Please add an item to your order.");
        return;
    }

    if (!name) {
        alert("Please enter your name.");
        return;
    }

    if (!collection) {
        alert("Please select a collection time.");
        return;
    }

    const total = entries.reduce(
        (sum, entry) => sum + entry.item.price * entry.quantity,
        0
    );

    const orderNumber = `MMK-${Date.now().toString().slice(-6)}`;

    const itemsText = entries
        .map(({ item, quantity }) =>
            `• ${item.name} × ${quantity} — R${(item.price * quantity).toFixed(2)}`
        )
        .join("\n");

    const message = [
        "🛒 MMK PRE-ORDER",
        "",
        `Order: ${orderNumber}`,
        `Name: ${name}`,
        `Class / Reference: ${reference || "N/A"}`,
        `Collection Time: ${collection}`,
        "",
        "ORDER ITEMS:",
        itemsText,
        "",
        `TOTAL: R${total.toFixed(2)}`,
        "",
        "Please confirm my order. Thank you."
    ].join("\n");

    const whatsappUrl =
        `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(message)}`;

    window.open(whatsappUrl, "_blank");
});

renderCart();

loadMenu().catch(error => {
    document.getElementById("menu").innerHTML =
        `<p>Menu unavailable. Start the MMK backend first.</p>`;
    console.error(error);
});
