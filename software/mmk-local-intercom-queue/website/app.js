const API = "http://127.0.0.1:5056";

const form = document.getElementById("checkInForm");
const ticketResult = document.getElementById("ticketResult");
const queueList = document.getElementById("queueList");

async function loadQueue() {
    const response = await fetch(`${API}/api/queue`);
    const queue = await response.json();

    if (!queue.length) {
        queueList.textContent = "No patients in the queue.";
        return;
    }

    queueList.innerHTML = queue.map(patient => `
        <div class="queue-item">
            <strong>Queue #${patient.queue_number}</strong><br>
            ${patient.full_name}<br>
            ${patient.department}<br>
            Status: ${patient.status}
        </div>
    `).join("");
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const response = await fetch(`${API}/api/check-in`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            full_name: document.getElementById("fullName").value,
            phone: document.getElementById("phone").value,
            department: document.getElementById("department").value
        })
    });

    const result = await response.json();

    if (!result.ok) {
        ticketResult.textContent = result.error || "Check-in failed.";
        return;
    }

    ticketResult.textContent =
        `Patient checked in — Queue #${result.queue_number}`;

    form.reset();
    loadQueue();
});

loadQueue();
setInterval(loadQueue, 5000);
