const workspace = document.getElementById("workspace");
const patternEl = document.getElementById("pattern");
const projectNameEl = document.getElementById("projectName");
const bpmEl = document.getElementById("bpm");
const canvas = document.getElementById("waveform");

let audioContext = null;
let beatTimer = null;
let currentStep = -1;
let mediaRecorder = null;
let recordingChunks = [];
let sampleUrls = [];
let history = [];
let autosaveEnabled = true;
let timeline = {
  beat: Array(16).fill(1),
  sample: Array(16).fill(0),
  voice: Array(16).fill(0)
};

let project = {
  name: "My First Beat",
  bpm: 90,
  lyrics: "",
  samples: [],
  recordings: []
};

let pattern = {
  kick:  [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
  snare: [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
  hat:   [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]
};

function getAudioContext() {
  if (!audioContext) audioContext = new (window.AudioContext || window.webkitAudioContext)();
  if (audioContext.state === "suspended") audioContext.resume();
  return audioContext;
}

function playTone(freq, duration, type="sine", volume=0.08) {
  const ctx = getAudioContext();
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = type;
  osc.frequency.value = freq;
  gain.gain.setValueAtTime(volume, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
  osc.connect(gain);
  gain.connect(ctx.destination);
  osc.start();
  osc.stop(ctx.currentTime + duration);
}

function playKick() {
  const ctx = getAudioContext();
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = "sine";
  osc.frequency.setValueAtTime(150, ctx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(48, ctx.currentTime + 0.16);
  gain.gain.setValueAtTime(0.55, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.22);
  osc.connect(gain);
  gain.connect(ctx.destination);
  osc.start();
  osc.stop(ctx.currentTime + 0.22);
}

function noise(duration, highpass, volume) {
  const ctx = getAudioContext();
  const buffer = ctx.createBuffer(1, ctx.sampleRate * duration, ctx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < data.length; i++) data[i] = Math.random() * 2 - 1;

  const source = ctx.createBufferSource();
  const filter = ctx.createBiquadFilter();
  const gain = ctx.createGain();

  source.buffer = buffer;
  filter.type = "highpass";
  filter.frequency.value = highpass;
  gain.gain.setValueAtTime(volume, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);

  source.connect(filter);
  filter.connect(gain);
  gain.connect(ctx.destination);
  source.start();
}

function playSnare() { noise(0.18, 900, 0.18); }
function playHat() { noise(0.055, 5000, 0.07); }

function playStep(step) {
  currentStep = step;
  document.querySelectorAll(".step").forEach(b => b.classList.remove("current"));
  document.querySelectorAll(`.step[data-step="${step}"]`).forEach(b => b.classList.add("current"));

  if (pattern.kick[step]) playKick();
  if (pattern.snare[step]) playSnare();
  if (pattern.hat[step]) playHat();
}

function startBeat() {
  stopBeat();
  getAudioContext();
  const bpm = Math.max(40, Math.min(220, Number(bpmEl.value) || 90));
  project.bpm = bpm;
  let step = 0;
  const interval = 60000 / bpm / 4;
  playStep(step);
  beatTimer = setInterval(() => {
    step = (step + 1) % 16;
    playStep(step);
  }, interval);
}

function stopBeat() {
  if (beatTimer) clearInterval(beatTimer);
  beatTimer = null;
  currentStep = -1;
  document.querySelectorAll(".step").forEach(b => b.classList.remove("current"));
}

function renderPattern() {
  patternEl.innerHTML = "";
  ["kick","snare","hat"].forEach(name => {
    const row = document.createElement("div");
    row.className = "pattern-row";

    const label = document.createElement("strong");
    label.textContent = name.toUpperCase();
    row.appendChild(label);

    const steps = document.createElement("div");
    steps.className = "steps";

    pattern[name].forEach((active, i) => {
      const button = document.createElement("button");
      button.className = "step" + (active ? " active" : "");
      button.dataset.step = i;
      button.textContent = i + 1;
      button.onclick = () => {
        pushHistory();
        pattern[name][i] = pattern[name][i] ? 0 : 1;
        button.classList.toggle("active");
        playStep(i);
      };
      steps.appendChild(button);
    });

    row.appendChild(steps);
    patternEl.appendChild(row);
  });
}

function randomBeat() {
  pushHistory();
  pattern.kick = Array.from({length:16}, (_,i) => i % 4 === 0 || (Math.random() < 0.18 ? 1 : 0));
  pattern.snare = Array.from({length:16}, (_,i) => i === 4 || i === 12 || (Math.random() < 0.08 ? 1 : 0));
  pattern.hat = Array.from({length:16}, () => Math.random() < 0.68 ? 1 : 0);
  renderPattern();
  drawWaveform();
}

function drawWaveform(audioData = null) {
  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0,0,w,h);

  ctx.strokeStyle = "#b8860b";
  ctx.lineWidth = 2;
  ctx.beginPath();

  if (audioData) {
    const step = Math.max(1, Math.floor(audioData.length / w));
    for (let x=0; x<w; x++) {
      const index = Math.min(audioData.length-1, x*step);
      const amp = Math.abs(audioData[index] || 0);
      const y = h/2 - amp*h*0.45;
      if (x === 0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    }
  } else {
    for (let x=0; x<w; x++) {
      const y = h/2 + Math.sin(x*0.055)*22 + Math.sin(x*0.17)*10;
      if (x === 0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    }
  }

  ctx.stroke();

  ctx.strokeStyle = "#444";
  ctx.beginPath();
  ctx.moveTo(0,h/2);
  ctx.lineTo(w,h/2);
  ctx.stroke();
}

function showSamples() {
  workspace.innerHTML = `
    <h3>🎵 SAMPLE BANK</h3>
    <p>Use audio already on your phone. Later we can add a legal sample-download catalogue.</p>
    <input id="sampleInput" type="file" accept="audio/*" multiple>
    <div id="sampleList"></div>
    <p class="tip">Tip: keep samples organised in samples/drums, samples/bass, samples/melodies, etc.</p>
  `;

  document.getElementById("sampleInput").onchange = e => {
    const files = [...e.target.files];
    const list = document.getElementById("sampleList");

    files.forEach(file => {
      const url = URL.createObjectURL(file);
      sampleUrls.push(url);
      project.samples.push(file.name);

      const box = document.createElement("div");
      box.className = "sample-item";
      box.innerHTML = `<strong>${escapeHtml(file.name)}</strong>`;

      const audio = document.createElement("audio");
      audio.controls = true;
      audio.src = url;

      const add = document.createElement("button");
      add.textContent = "＋ ADD TO PROJECT";
      add.onclick = () => {
        project.samples.push(file.name);
        saveProject(false);
        alert("Sample added to this project.");
      };

      box.append(audio, add);
      list.appendChild(box);

      audio.onplay = async () => {
        try {
          const buffer = await getAudioContext().decodeAudioData(await file.arrayBuffer());
          drawWaveform(buffer.getChannelData(0));
        } catch (_) {}
      };
    });
  };
}

async function recordAudio() {
  workspace.innerHTML = `
    <h3>🎙️ RECORD</h3>
    <p>Allow microphone access, then record your idea.</p>
    <button id="recordStart" class="primary">🔴 START RECORDING</button>
    <button id="recordStop" disabled>■ STOP</button>
    <div id="recordingList"></div>
  `;

  const start = document.getElementById("recordStart");
  const stop = document.getElementById("recordStop");
  const list = document.getElementById("recordingList");

  start.onclick = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({audio:true});
      recordingChunks = [];
      mediaRecorder = new MediaRecorder(stream);

      mediaRecorder.ondataavailable = e => recordingChunks.push(e.data);

      mediaRecorder.onstop = () => {
        stream.getTracks().forEach(t => t.stop());
        const blob = new Blob(recordingChunks, {type:"audio/webm"});
        const url = URL.createObjectURL(blob);
        project.recordings.push("Recording " + (project.recordings.length + 1));

        const audio = document.createElement("audio");
        audio.controls = true;
        audio.src = url;

        const link = document.createElement("a");
        link.href = url;
        link.download = `${safeName(project.name)}-recording-${project.recordings.length}.webm`;
        link.textContent = "⬇ DOWNLOAD RECORDING";
        link.className = "download-button";

        const box = document.createElement("div");
        box.className = "recording-box";
        box.append(audio, link);
        list.appendChild(box);

        drawWaveform();
        saveProject(false);
      };

      mediaRecorder.start();
      start.disabled = true;
      stop.disabled = false;
      start.textContent = "🔴 RECORDING...";
    } catch (err) {
      alert("Microphone access was not available. Check browser microphone permission.");
    }
  };

  stop.onclick = () => {
    if (mediaRecorder && mediaRecorder.state !== "inactive") mediaRecorder.stop();
    start.disabled = false;
    stop.disabled = true;
    start.textContent = "🔴 START RECORDING";
  };
}

function showLyrics() {
  workspace.innerHTML = `
    <h3>✍️ LYRICS</h3>
    <textarea id="lyrics" rows="12" placeholder="Write your lyrics here...">${escapeHtml(project.lyrics)}</textarea>
    <button id="lyricsSave" class="primary">SAVE LYRICS</button>
  `;
  document.getElementById("lyricsSave").onclick = () => {
    project.lyrics = document.getElementById("lyrics").value;
    saveProject(false);
    alert("Lyrics saved.");
  };
}

function getStudioSnapshot() {
  project.name = projectNameEl.textContent.trim() || "Untitled MMK Project";
  project.bpm = Number(bpmEl.value) || 90;

  return {
    mmkStudio: "MMK Studio",
    version: "0.4.1",
    savedAt: new Date().toISOString(),
    project: JSON.parse(JSON.stringify(project)),
    pattern: JSON.parse(JSON.stringify(pattern)),
    timeline: JSON.parse(JSON.stringify(timeline)),
    clips: typeof clips !== "undefined"
      ? clips.map(c => ({
          name: c.name,
          start: Number(c.start) || 0,
          duration: Number(c.duration) || 4,
          trimStart: Number(c.trimStart) || 0,
          trimEnd: Number(c.trimEnd) || Number(c.duration) || 4
        }))
      : []
  };
}

function getProjectLibrary() {
  try {
    const raw = localStorage.getItem("mmkStudioLibrary");
    const library = raw ? JSON.parse(raw) : { projects: [], drafts: [] };

    return {
      projects: Array.isArray(library.projects) ? library.projects : [],
      drafts: Array.isArray(library.drafts) ? library.drafts : []
    };
  } catch (_) {
    return { projects: [], drafts: [] };
  }
}

function saveProjectToLibrary(type="project", showMessage=true) {
  const snapshot = getStudioSnapshot();
  const library = getProjectLibrary();

  const collection = type === "draft" ? library.drafts : library.projects;
  const existingId = project.libraryId || null;

  if (existingId) {
    const index = collection.findIndex(item => item.id === existingId);

    if (index >= 0) {
      collection[index] = {
        ...collection[index],
        ...snapshot,
        id: existingId,
        type
      };
    } else {
      collection.unshift({
        ...snapshot,
        id: existingId,
        type
      });
    }
  } else {
    const id = "mmk-" + Date.now() + "-" + Math.random().toString(36).slice(2, 8);

    project.libraryId = id;

    collection.unshift({
      ...snapshot,
      project: JSON.parse(JSON.stringify(project)),
      id,
      type
    });
  }

  localStorage.setItem("mmkStudioLibrary", JSON.stringify(library));

  // Keep the latest project available for compatibility and recovery.
  localStorage.setItem("mmkStudioProject", JSON.stringify(snapshot));

  if (showMessage) {
    document.getElementById("timelineStatus").textContent =
      type === "draft" ? "Draft saved" : "Project saved";

    alert(
      type === "draft"
        ? "MMK draft saved on this device."
        : "MMK project saved to your project library."
    );
  }
}

function saveDraft(showMessage=true) {
  saveProjectToLibrary("draft", showMessage);
}

function saveProject(showMessage=true) {
  saveProjectToLibrary("project", showMessage);
}

function pushHistory() {
  history.push(JSON.stringify({
    project,
    pattern,
    timeline
  }));

  if (history.length > 20) history.shift();
}

function undo() {
  if (!history.length) {
    alert("Nothing to undo yet.");
    return;
  }

  const previous = JSON.parse(history.pop());
  project = previous.project;
  pattern = previous.pattern;
  timeline = previous.timeline;

  projectNameEl.textContent = project.name;
  bpmEl.value = project.bpm;
  renderPattern();
  renderTimeline();
  drawWaveform();
}

function autoSave() {
  if (!autosaveEnabled) return;
  saveProject(false);
  const status = document.getElementById("timelineStatus");
  status.textContent = "Auto-saved";
  status.classList.add("autosave-on");
}

function renderTimeline() {
  ["beat","sample","voice"].forEach(type => {
    const target = document.getElementById(type + "Track");
    if (!target) return;

    target.innerHTML = "";

    timeline[type].forEach((active, i) => {
      const cell = document.createElement("button");
      cell.className = "timeline-cell" + (active ? " active" : "");
      cell.title = type.toUpperCase() + " step " + (i + 1);
      cell.onclick = () => {
        pushHistory();
        timeline[type][i] = timeline[type][i] ? 0 : 1;
        cell.classList.toggle("active");
        autoSave();
      };
      target.appendChild(cell);
    });
  });
}

async function exportProject() {
  saveProject(false);

  const saved = localStorage.getItem("mmkStudioProject");

  if (!saved) {
    alert("Nothing to export yet. Save the project first.");
    return;
  }

  try {
    const data = JSON.parse(saved);

    const projectData = JSON.stringify({
      ...data,
      mmkStudio: "MMK Studio",
      version: "0.4.1",
      exportedAt: new Date().toISOString()
    }, null, 2);

    const fileName =
      safeName(project.name) + "-MMK-Studio-project.mmkstudio";

    const blob = new Blob([projectData], {
      type: "application/octet-stream"
    });

    /*
     * MOBILE-FIRST EXPORT
     * Try Android/browser Share first.
     * Fall back to normal file download when sharing
     * is not supported.
     */
    if (
      typeof navigator.share === "function" &&
      typeof navigator.canShare === "function" &&
      typeof File !== "undefined"
    ) {
      const file = new File(
        [blob],
        fileName,
        { type: "application/octet-stream" }
      );

      if (navigator.canShare({ files: [file] })) {
        try {
          await navigator.share({
            title: "MMK Studio Project",
            text: "MMK Studio project: " + (project.name || "Untitled"),
            files: [file]
          });

          document.getElementById("timelineStatus").textContent = "Shared";
          return;
        } catch (error) {
          if (error && error.name === "AbortError") {
            document.getElementById("timelineStatus").textContent =
              "Share cancelled";
            return;
          }
        }
      }
    }

    /*
     * FALLBACK
     * Android/browser will show its normal save/download dialog.
     */
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");

    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    a.remove();

    setTimeout(() => URL.revokeObjectURL(url), 1000);

    document.getElementById("timelineStatus").textContent =
      "Exported — choose save location";
  } catch (error) {
    console.error("MMK export error:", error);
    document.getElementById("timelineStatus").textContent = "Export failed";
    alert("MMK Studio could not export this project.");
  }
}

function importProject() {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = ".mmkstudio,.json,application/octet-stream,application/json";

  input.onchange = async () => {
    const file = input.files[0];
    if (!file) return;

    try {
      const data = JSON.parse(await file.text());

      if (!data.project || !data.pattern) {
        throw new Error("Invalid MMK Studio project");
      }

      pushHistory();

      project = data.project;
      pattern = data.pattern;
      timeline = data.timeline || {
        beat:Array(16).fill(1),
        sample:Array(16).fill(0),
        voice:Array(16).fill(0)
      };

      if (typeof clips !== "undefined") {
        clips = Array.isArray(data.clips)
          ? data.clips.map(c => ({
              id: Date.now() + Math.random(),
              name: c.name || "Audio Clip",
              url: "",
              start: Number(c.start) || 0,
              duration: Number(c.duration) || 4,
              trimStart: Number(c.trimStart) || 0,
              trimEnd: Number(c.trimEnd) || Number(c.duration) || 4
            }))
          : [];
      }

      projectNameEl.textContent =
        project.name || "Untitled MMK Project";

      bpmEl.value = Number(project.bpm) || 90;

      renderPattern();
      renderTimeline();
      drawWaveform();

      if (typeof renderRealTimeline === "function") {
        renderRealTimeline();
      }

      saveProject(false);

      document.getElementById("timelineStatus").textContent =
        "Imported";

      alert("MMK project imported successfully.");
    } catch (_) {
      alert("That file is not a valid MMK Studio project.");
    }
  };

  input.click();
}

function renderLibrarySection(type) {
  const library = getProjectLibrary();
  const items = type === "draft" ? library.drafts : library.projects;
  const title = type === "draft" ? "📝 DRAFTS" : "📁 PROJECTS";

  if (!items.length) {
    return `
      <section class="library-section">
        <h3>${title}</h3>
        <p class="muted">
          ${type === "draft"
            ? "No drafts yet. Use SAVE DRAFT while you are working."
            : "No projects yet. Use SAVE PROJECT when your work is ready."}
        </p>
      </section>
    `;
  }

  return `
    <section class="library-section">
      <h3>${title} <span class="library-count">${items.length}</span></h3>

      <div class="library-list">
        ${items.map(item => {
          const savedProject = item.project || {};
          const name = savedProject.name || "Untitled MMK Project";
          const bpm = Number(savedProject.bpm) || 90;
          const savedAt = item.savedAt
            ? new Date(item.savedAt).toLocaleString()
            : "Unknown";

          return `
            <div class="project-item">
              <div>
                <strong>${escapeHtml(name)}</strong>
                <span>BPM ${bpm}</span>
                <small>${type === "draft" ? "Draft" : "Saved"} • ${escapeHtml(savedAt)}</small>
              </div>

              <button class="open-library-item" data-id="${escapeHtml(item.id)}" data-type="${type}">
                OPEN
              </button>
            </div>
          `;
        }).join("")}
      </div>
    </section>
  `;
}

function showProjects() {
  workspace.innerHTML = `
    <h3>🎚️ MMK PROJECT LIBRARY</h3>
    <p class="muted">Your Studio work is stored offline on this device.</p>

    <div class="library-actions">
      <button id="librarySaveDraft" class="secondary">SAVE DRAFT</button>
      <button id="librarySaveProject" class="primary">SAVE PROJECT</button>
    </div>

    ${renderLibrarySection("project")}
    ${renderLibrarySection("draft")}
  `;

  document.getElementById("librarySaveDraft").onclick = () => {
    saveDraft();
    showProjects();
  };

  document.getElementById("librarySaveProject").onclick = () => {
    saveProject();
    showProjects();
  };

  document.querySelectorAll(".open-library-item").forEach(button => {
    button.onclick = () => {
      const id = button.dataset.id;
      const type = button.dataset.type;

      if (loadLibraryItem(id, type)) {
        setTimelineStatus(
          type === "draft" ? "Draft opened" : "Project opened"
        );

        alert(
          type === "draft"
            ? "MMK draft opened successfully."
            : "MMK project opened successfully."
        );
      }
    };
  });
}

function loadLibraryItem(id, type) {
  const library = getProjectLibrary();
  const collection = type === "draft" ? library.drafts : library.projects;
  const item = collection.find(entry => entry.id === id);

  if (!item) return false;

  return applyProjectData(item);
}

function applyProjectData(data) {
  if (!data || !data.project || !data.pattern) return false;

  project = data.project;
  pattern = data.pattern;

  timeline = data.timeline || {
    beat: Array(16).fill(1),
    sample: Array(16).fill(0),
    voice: Array(16).fill(0)
  };

  if (typeof clips !== "undefined") {
    clips = Array.isArray(data.clips)
      ? data.clips.map(c => ({
          id: Date.now() + Math.random(),
          name: c.name || "Audio Clip",
          url: "",
          start: Number(c.start) || 0,
          duration: Number(c.duration) || 4,
          trimStart: Number(c.trimStart) || 0,
          trimEnd: Number(c.trimEnd) || Number(c.duration) || 4
        }))
      : [];
  }

  projectNameEl.textContent = project.name || "Untitled MMK Project";
  bpmEl.value = Number(project.bpm) || 90;

  renderPattern();
  renderTimeline();
  drawWaveform();

  if (typeof renderRealTimeline === "function") {
    renderRealTimeline();
  }

  return true;
}

function loadProject() {
  const saved = localStorage.getItem("mmkStudioProject");
  if (!saved) return false;

  try {
    const data = JSON.parse(saved);
    return applyProjectData(data);
  } catch (_) {
    return false;
  }
}

function newProject() {
  const name = prompt("Project name:", "My New Beat");
  if (!name) return;

  project = {
    name,
    bpm: 90,
    lyrics: "",
    samples: [],
    recordings: []
  };

  pattern = {
    kick:  [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
    snare: [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
    hat:   [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]
  };

  projectNameEl.textContent = name;
  bpmEl.value = 90;
  history = [];
  timeline = {
    beat:Array(16).fill(1),
    sample:Array(16).fill(0),
    voice:Array(16).fill(0)
  };
  renderPattern();
  renderTimeline();
  drawWaveform();
  workspace.innerHTML = "<h3>New project ready.</h3><p>Make your first beat.</p>";
}

function safeName(name) {
  return name.replace(/[^a-z0-9_-]+/gi, "-").replace(/^-|-$/g, "") || "mmk-project";
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
  }[c]));
}

document.addEventListener("click", e => {
  const action = e.target.dataset.action;
  if (!action) return;

  if (action === "play") startBeat();
  if (action === "stop") stopBeat();
  if (action === "new-beat") randomBeat();
  if (action === "samples") showSamples();
  if (action === "record") recordAudio();
  if (action === "lyrics") showLyrics();
  if (action === "projects") showProjects();
  if (action === "save") saveProject();
  if (action === "export") exportProject();
  if (action === "import") importProject();
  if (action === "undo") undo();
  if (action === "autosave") {
    autosaveEnabled = !autosaveEnabled;
    e.target.textContent = autosaveEnabled ? "⚡ AUTO-SAVE" : "⏸ AUTO-SAVE";
    e.target.classList.toggle("autosave-on", autosaveEnabled);
  }
  if (action === "new-project") newProject();
});

bpmEl.addEventListener("change", () => {
  project.bpm = Number(bpmEl.value) || 90;
});

renderPattern();
renderTimeline();
drawWaveform();
loadProject();

setInterval(() => {
  if (autosaveEnabled) autoSave();
}, 15000);


/* MMK STUDIO v0.4 REAL TIMELINE */
let clips = [];
let selectedClip = null;
let snapEnabled = true;
let loopEnabled = false;
let timelinePlaying = false;
let timelineStart = 0;

function setTimelineStatus(msg){
  const el = document.getElementById("timelineStatus");
  if(el) el.textContent = msg;
}

function makeClip(file){
  const url = URL.createObjectURL(file);
  return {
    id: Date.now() + Math.random(),
    name: file.name,
    url,
    start: 0,
    duration: 4,
    trimStart: 0,
    trimEnd: 4
  };
}

function renderRealTimeline(){
  const grid = document.getElementById("sampleTrack");
  if(!grid) return;

  grid.innerHTML = "";

  for(let i=0;i<16;i++){
    const cell = document.createElement("div");
    cell.className = "timeline-cell";
    cell.dataset.beat = i;
    grid.appendChild(cell);
  }

  clips.forEach(clip=>{
    const el = document.createElement("button");
    el.className = "audio-clip" + (selectedClip === clip.id ? " selected" : "");
    el.textContent = "♪ " + clip.name;
    el.title = "Tap to select • long press/drag supported";
    el.style.left = ((clip.start / 16) * 100) + "%";
    el.style.width = Math.max(6, (clip.duration / 16) * 100) + "%";

    el.onclick = ()=>{
      selectedClip = clip.id;
      renderRealTimeline();
      setTimelineStatus("Selected: " + clip.name);
    };

    grid.appendChild(el);
  });
}

function snapBeat(value){
  if(!snapEnabled) return value;
  return Math.round(value);
}

function addAudioClip(file){
  if(!file) return;
  const clip = makeClip(file);
  clip.start = snapBeat(clips.length);
  clips.push(clip);
  selectedClip = clip.id;
  renderRealTimeline();
  saveProject();
  setTimelineStatus("Added: " + file.name);
}

function toggleSnap(){
  snapEnabled = !snapEnabled;
  const b = document.getElementById("snapBtn");
  if(b) b.textContent = snapEnabled ? "🧲 SNAP ON" : "🧲 SNAP OFF";
  setTimelineStatus(snapEnabled ? "Snap enabled" : "Snap disabled");
}

function toggleLoop(){
  loopEnabled = !loopEnabled;
  const b = document.getElementById("loopBtn");
  if(b) b.textContent = loopEnabled ? "🔁 LOOP ON" : "🔁 LOOP OFF";
  setTimelineStatus(loopEnabled ? "Loop enabled" : "Loop disabled");
}

function removeSelectedClip(){
  if(selectedClip === null) return;
  clips = clips.filter(c=>c.id !== selectedClip);
  selectedClip = null;
  renderRealTimeline();
  saveProject();
  setTimelineStatus("Clip removed");
}

/* Timeline clip persistence is handled directly by saveProject(). */

document.addEventListener("DOMContentLoaded", ()=>{
  const add = document.getElementById("addClipBtn");
  const input = document.getElementById("clipFile");

  if(add && input){
    add.onclick = ()=>input.click();
    input.onchange = ()=>{
      addAudioClip(input.files[0]);
      input.value = "";
    };
  }

  const snap = document.getElementById("snapBtn");
  if(snap) snap.onclick = toggleSnap;

  const loop = document.getElementById("loopBtn");
  if(loop) loop.onclick = toggleLoop;

  const remove = document.getElementById("removeClipBtn");
  if(remove) remove.onclick = removeSelectedClip;

  const saved = localStorage.getItem("mmkStudioProject");
  if(saved){
    try{
      const data = JSON.parse(saved);
      clips = Array.isArray(data.clips)
        ? data.clips.map(c=>({
            id: Date.now() + Math.random(),
            name: c.name,
            url: "",
            start: Number(c.start) || 0,
            duration: Number(c.duration) || 4,
            trimStart: Number(c.trimStart) || 0,
            trimEnd: Number(c.trimEnd) || Number(c.duration) || 4
          }))
        : [];
    }catch(e){
      clips = [];
    }
  }

  renderRealTimeline();
});
