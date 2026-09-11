const products = [
    {
        id: "MMK-001",
        name: "MMK Business Starter",
        category: "Digital Products",
        description: "Business starter resources for small businesses.",
        price: 99,
        currency: "ZAR"
    },
    {
        id: "MMK-002",
        name: "MMK Digital Template Pack",
        category: "Templates",
        description: "Reusable business and marketing templates.",
        price: 49,
        currency: "ZAR"
    },
    {
        id: "MMK-003",
        name: "MMK Grocery Starter",
        category: "Grocery",
        description: "Starter grocery ordering system.",
        price: 0,
        currency: "ZAR"
    }
];

const productList = document.getElementById("product-list");

products.forEach(product => {
    const card = document.createElement("div");
    card.className = "product-card";

    const price = product.price === 0
        ? "FREE"
        : `${product.currency} ${product.price}`;

    card.innerHTML = `
        <h3>${product.name}</h3>
        <p><strong>${product.category}</strong></p>
        <p>${product.description}</p>
        <p><strong>${price}</strong></p>
        <button onclick="viewProduct('${product.id}')">
            View Product
        </button>
    `;

    productList.appendChild(card);
});

function viewProduct(id) {
    alert("MMK Product ID: " + id);
}
