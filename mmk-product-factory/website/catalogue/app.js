const productList = document.getElementById("product-list");

if (!productList) {
    throw new Error("MMK catalogue: product list element not found.");
}

productList.innerHTML = "<p>Loading MMK products...</p>";

fetch("./products.json")
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return response.json();
    })
    .then(products => {
        productList.innerHTML = "";

        products.forEach(product => {
            const card = document.createElement("article");
            card.className = "product-card";

            const price = Number(product.price);

            let priceLabel = "Coming Soon";

            if (product.available && price > 0) {
                priceLabel = `${product.currency} ${price.toFixed(2)}`;
            } else if (product.available && price === 0) {
                priceLabel = "Free / Demo";
            }

            card.innerHTML = `
                <h3>${product.name}</h3>
                <p><strong>${product.category}</strong></p>
                <p>${product.description}</p>
                <p><strong>${priceLabel}</strong></p>
            `;

            if (product.link) {
                const link = document.createElement("a");

                link.href = product.link;
                link.className = "catalogue-button";
                link.textContent = "Open Product";

                card.appendChild(link);
            } else {
                const status = document.createElement("p");

                status.textContent = product.available
                    ? "Product information available"
                    : "Coming Soon";

                card.appendChild(status);
            }

            productList.appendChild(card);
        });
    })
    .catch(error => {
        console.error("MMK catalogue loading failed:", error);

        productList.innerHTML = `
            <p>
                The MMK product catalogue could not be loaded.
                Please try again later.
            </p>
        `;
    });
