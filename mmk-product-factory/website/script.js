document.addEventListener("DOMContentLoaded", () => {
    const productSection = document.querySelector("#products");

    if (!productSection) return;

    const grid = productSection.querySelector(".grid");

    if (!grid) return;

    fetch("../data/products.json")
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(products => {
            grid.innerHTML = "";

            products.forEach(product => {
                const card = document.createElement("article");
                card.className = "card";

                const price = Number(product.price);

                card.innerHTML = `
                    <span class="eyebrow">${product.category}</span>
                    <h3>${product.name}</h3>
                    <p>${product.description}</p>
                    <p><strong>${price > 0 ? `R${price.toFixed(2)}` : "Coming Soon"}</strong></p>
                    ${
                        product.id === "MMK-004"
                            ? `<a href="stock-calculator/index.html" class="button primary">Open Calculator</a>`
                            : ""
                    }
                `;

                grid.appendChild(card);
            });
        })
        .catch(error => {
            console.error("Catalogue loading failed:", error);
        });
});
