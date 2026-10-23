document.addEventListener("DOMContentLoaded", () => {
    const productSection = document.querySelector("#products");
    const grid = productSection && productSection.querySelector(".grid");
    if (!grid) return;

    fetch("catalogue/products.json")
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        })
        .then(products => {
            if (!Array.isArray(products)) throw new Error("Product data is not a list.");
            grid.replaceChildren();

            products.slice(0, 4).forEach(product => {
                const card = document.createElement("article");
                card.className = "card";

                const category = document.createElement("p");
                category.className = "eyebrow";
                category.textContent = product.category || "MMK PRODUCT";
                card.appendChild(category);

                const title = document.createElement("h3");
                title.textContent = product.name || "MMK Product";
                card.appendChild(title);

                const description = document.createElement("p");
                description.textContent = product.description || "";
                card.appendChild(description);

                const price = document.createElement("p");
                if (product.priceLabel) {
                    price.textContent = product.priceLabel;
                } else if (Number(product.price) > 0) {
                    price.textContent = `${product.currency === "ZAR" ? "R" : (product.currency || "")}${Number(product.price).toFixed(2)}`;
                } else {
                    price.textContent = "Contact MMK for details";
                }
                card.appendChild(price);

                const link = document.createElement("a");
                link.className = "button primary";
                link.href = "catalogue/index.html";
                link.textContent = "View in Shop";
                card.appendChild(link);
                grid.appendChild(card);
            });
        })
        .catch(error => {
            console.error("MMK homepage products failed to load:", error);
        });
});
