const fallback = {
    business: {
        name: "YOUR BUSINESS NAME",
        tagline: "Useful work for your customers.",
        description: "Add a clear description of the business here.",
        founder: "OWNER / FOUNDER NAME"
    },
    contact: {
        phone: "",
        whatsapp: "",
        email: "",
        location: "",
        hours: ""
    },
    services: [],
    products: [],
    gallery: [],
    projects: []
};

function safeText(value, fallbackValue = "") {
    return value && String(value).trim()
        ? String(value).trim()
        : fallbackValue;
}

function renderServices(services) {
    const container = document.getElementById("services-list");

    container.innerHTML = services.map(service => `
        <article class="card">
            <span class="icon">🛠️</span>
            <h3>${safeText(service.title, "Service")}</h3>
            <p>${safeText(service.description)}</p>
        </article>
    `).join("");
}

function renderProducts(products) {
    const container = document.getElementById("products-list");

    container.innerHTML = products.map(product => `
        <article class="card">
            <span class="icon">📦</span>
            <h3>${safeText(product.name, "Product")}</h3>
            <p>${safeText(product.description)}</p>
            <span class="status">${safeText(product.status, "Available")}</span>
        </article>
    `).join("");
}

function renderProjects(projects) {
    const container = document.getElementById("projects-list");

    container.innerHTML = projects.map(project => `
        <article class="card">
            <span class="icon">📁</span>
            <h3>${safeText(project.name, "Project")}</h3>
            <p>${safeText(project.description)}</p>
        </article>
    `).join("");
}

function renderGallery(gallery) {
    const container = document.getElementById("gallery-list");

    if (!gallery || gallery.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                Gallery images can be added during customization.
            </div>
        `;
        return;
    }

    container.innerHTML = gallery.map(image => `
        <figure class="gallery-item">
            <img src="${image.src}" alt="${safeText(image.alt, "Business gallery image")}">
        </figure>
    `).join("");
}

function renderContact(contact) {
    const phone = safeText(contact.phone);
    const whatsapp = safeText(contact.whatsapp);
    const email = safeText(contact.email);

    document.getElementById("contact-phone").textContent =
        phone || "Not provided";

    document.getElementById("contact-whatsapp").textContent =
        whatsapp || "Not provided";

    document.getElementById("contact-email").textContent =
        email || "Not provided";

    document.getElementById("contact-location").textContent =
        safeText(contact.location, "Not provided");

    document.getElementById("contact-hours").textContent =
        safeText(contact.hours, "Not provided");

    const phoneLink = document.getElementById("phone-link");
    const whatsappLink = document.getElementById("whatsapp-link");
    const emailLink = document.getElementById("email-link");
    const button = document.getElementById("contact-button");

    if (phone) {
        phoneLink.href = `tel:${phone.replace(/\s+/g, "")}`;
    } else {
        phoneLink.removeAttribute("href");
    }

    if (whatsapp) {
        const whatsappNumber = whatsapp.replace(/\D/g, "");
        whatsappLink.href = `https://wa.me/${whatsappNumber}`;
    } else {
        whatsappLink.removeAttribute("href");
    }

    if (email) {
        emailLink.href = `mailto:${email}`;
        button.href = `mailto:${email}`;
    } else {
        emailLink.removeAttribute("href");
        button.href = "#contact";
    }
}

function renderSite(site) {
    const business = site.business || fallback.business;
    const contact = site.contact || fallback.contact;

    document.title = safeText(business.name, fallback.business.name);

    document.getElementById("business-logo").textContent =
        safeText(business.name, fallback.business.name);

    document.querySelector(".hero .eyebrow").textContent =
        safeText(business.name, fallback.business.name);

    document.getElementById("hero-title").textContent =
        safeText(business.tagline, fallback.business.tagline);

    document.getElementById("hero-description").textContent =
        safeText(business.description, fallback.business.description);

    document.getElementById("about-description").textContent =
        safeText(business.description, fallback.business.description);

    document.getElementById("founder-name").textContent =
        safeText(business.founder, fallback.business.founder);

    document.getElementById("footer-business-name").textContent =
        safeText(business.name, fallback.business.name);

    renderServices(site.services || fallback.services);
    renderProducts(site.products || fallback.products);
    renderProjects(site.projects || fallback.projects);
    renderGallery(site.gallery || fallback.gallery);
    renderContact(contact);

    document.getElementById("footer-year").textContent =
        new Date().getFullYear();
}

async function loadSite() {
    try {
        const response = await fetch("./data/site.json", {
            cache: "no-store"
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const site = await response.json();
        renderSite(site);

    } catch (error) {
        console.error("Website configuration could not be loaded:", error);
        renderSite(fallback);
    }
}

loadSite();
