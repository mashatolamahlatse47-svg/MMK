document.addEventListener("DOMContentLoaded", () => {
    console.log(`${MMK_SECURITY_CONFIG.productName} v${MMK_SECURITY_CONFIG.version}`);
    console.log(`Mode: ${MMK_SECURITY_CONFIG.mode}`);

    const navItems = document.querySelectorAll(".nav-item");

    navItems.forEach((item) => {
        item.addEventListener("click", () => {
            navItems.forEach((button) => button.classList.remove("active"));
            item.classList.add("active");

            console.log(`Prototype section: ${item.dataset.section}`);
        });
    });

    const recordButtons = [
        document.getElementById("recordButton"),
        document.getElementById("emptyRecordButton")
    ];

    recordButtons.forEach((button) => {
        if (button) {
            button.addEventListener("click", () => {
                alert("Occurrence recording will be connected to the MMK Security Service in a later step.");
            });
        }
    });
});
