const productList = document.getElementById("product-list");

function makeText(tag, className, value) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    element.textContent = value == null ? "" : String(value);
    return element;
}

function renderProduct(product) {
    const card = document.createElement("article");
    card.className = "product-card";
    card.appendChild(makeText("p", "product-category", product.category));
    card.appendChild(makeText("h3", "", product.name));
    card.appendChild(makeText("p", "product-description", product.description));

    let priceLabel = product.priceLabel;
    if (!priceLabel) {
        const price = Number(product.price);
        priceLabel = product.available && price > 0
            ? `${product.currency || "R"} ${price.toFixed(2)}`
            : (product.available ? "Contact MMK for details" : "Coming soon");
    }
    card.appendChild(makeText("p", "product-price", priceLabel));

    if (product.status) {
        card.appendChild(makeText("p", "product-status", product.status));
    }

    const link = document.createElement("a");
    link.className = "catalogue-button";
    link.textContent = product.buttonLabel || (product.link ? "Open Product" : "Enquire with MMK");
    link.href = product.link ||
        `mailto:mashatolamahlatse47@gmail.com?subject=${encodeURIComponent("MMK product enquiry: " + product.name)}`;

    if (/^https:\/\//i.test(link.href)) {
        link.target = "_blank";
        link.rel = "noopener noreferrer";
    }

    card.appendChild(link);
    return card;
}

if (!productList) {
    console.error("MMK Shop: product list element not found.");
} else {
    fetch("./products.json")
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        })
        .then(products => {
            if (!Array.isArray(products)) throw new Error("Product data is not a list.");
            productList.replaceChildren();
            products.forEach(product => productList.appendChild(renderProduct(product)));
            if (products.length === 0) {
                productList.appendChild(makeText("p", "", "Products will be listed here soon."));
            }
        })
        .catch(error => {
            console.error("MMK Shop loading failed:", error);
            productList.replaceChildren(
                makeText("p", "", "The catalogue could not load. Please contact MMK for product information.")
            );
        });
}
