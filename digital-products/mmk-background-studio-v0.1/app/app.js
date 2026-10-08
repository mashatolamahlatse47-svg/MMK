const imageInput = document.getElementById("imageInput");
const fileName = document.getElementById("fileName");
const previewArea = document.getElementById("previewArea");
const removeBgBtn = document.getElementById("removeBgBtn");
const resetBtn = document.getElementById("resetBtn");
const exportBtn = document.getElementById("exportBtn");

const status = document.getElementById("status");
const qualityStatus = document.getElementById("qualityStatus");

const dimensions = document.getElementById("dimensions");
const format = document.getElementById("format");
const transparency = document.getElementById("transparency");
const production = document.getElementById("production");

let currentImage = null;
let currentFile = null;

imageInput.addEventListener("change", () => {
  const file = imageInput.files[0];

  if (!file) return;

  currentFile = file;

  fileName.textContent = file.name;
  format.textContent = file.type || "Unknown";

  const reader = new FileReader();

  reader.onload = event => {
    previewArea.innerHTML = "";

    const img = document.createElement("img");
    img.src = event.target.result;

    img.onload = () => {
      currentImage = img;

      dimensions.textContent =
        `${img.naturalWidth} × ${img.naturalHeight}`;

      transparency.textContent =
        file.type === "image/png" ? "Possible" : "No";

      production.textContent = "IMPORTED";
      status.textContent = "IMPORTED";
      qualityStatus.textContent = "CHECK";

      removeBgBtn.disabled = false;
      resetBtn.disabled = false;
      exportBtn.disabled = false;

      previewArea.appendChild(img);
    };
  };

  reader.readAsDataURL(file);
});

removeBgBtn.addEventListener("click", () => {
  status.textContent = "NEXT STAGE";
  production.textContent = "AI REMOVAL REQUIRED";

  alert(
    "Background-removal engine is the next MMK build stage."
  );
});

resetBtn.addEventListener("click", () => {
  imageInput.value = "";
  currentImage = null;
  currentFile = null;

  fileName.textContent = "No artwork selected.";
  dimensions.textContent = "—";
  format.textContent = "—";
  transparency.textContent = "—";
  production.textContent = "WAITING";

  status.textContent = "WAITING";
  qualityStatus.textContent = "NOT READY";

  removeBgBtn.disabled = true;
  resetBtn.disabled = true;
  exportBtn.disabled = true;

  previewArea.innerHTML = `
    <div class="empty-state">
      <div class="empty-icon">🖼️</div>
      <p>Your artwork will appear here.</p>
    </div>
  `;
});

exportBtn.addEventListener("click", () => {
  if (!currentImage) return;

  const link = document.createElement("a");

  link.href = currentImage.src;
  link.download = "MMK-Artwork-Transparent.png";

  link.click();
});
