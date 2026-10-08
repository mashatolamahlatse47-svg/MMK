const workspace = document.getElementById("workspace");
const patternEl = document.getElementById("pattern");
const projectNameEl = document.getElementById("projectName");
const bpmEl = document.getElementById("bpm");
const canvas = document.getElementById("waveform");

let audioContext = null;

/* =========================================================
   MMK STUDIO AUDIO VAULT
   Persistent offline audio storage using IndexedDB
   ========================================================= */

const MMK_AUDIO_DB = "mmkStudioAudioVault";
const MMK_AUDIO_STORE = "audio";

function openAudioVault() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(MMK_AUDIO_DB, 1);

    request.onupgradeneeded = () => {
      const db = request.result;

      if (!db.objectStoreNames.contains(MMK_AUDIO_STORE)) {
        db.createObjectStore(MMK_AUDIO_STORE, { keyPath: "id" });
      }
    };

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function saveAudioBlob(blob, name = "audio") {
  const id =
    "audio-" +
    Date.now() +
    "-" +
    Math.random().toString(36).slice(2, 8);

  const db = await openAudioVault();

  return new Promise((resolve, reject) => {
    const tx = db.transaction(MMK_AUDIO_STORE, "readwrite");
    const store = tx.objectStore(MMK_AUDIO_STORE);

    store.put({
      id,
      name,
      type: blob.type || "audio/*",
      blob,
      savedAt: new Date().toISOString()
    });

    tx.oncomplete = () => {
      db.close();
      resolve(id);
    };

    tx.onerror = () => {
      db.close();
      reject(tx.error);
    };
  });
}

async function loadAudioBlob(id) {
  if (!id) return null;

  const db = await openAudioVault();

  return new Promise((resolve, reject) => {
    const tx = db.transaction(MMK_AUDIO_STORE, "readonly");
    const request = tx.objectStore(MMK_AUDIO_STORE).get(id);

    request.onsuccess = () => {
      const record = request.result || null;
      db.close();
      resolve(record ? record.blob : null);
    };

    request.onerror = () => {
      db.close();
      reject(request.error);
    };
  });
}

async function deleteAudioBlob(id) {
  if (!id) return;

  const db = await openAudioVault();

  return new Promise((resolve, reject) => {
    const tx = db.transaction(MMK_AUDIO_STORE, "readwrite");
    tx.objectStore(MMK_AUDIO_STORE).delete(id);

    tx.oncomplete = () => {
      db.close();
      resolve();
    };

    tx.onerror = () => {
      db.close();
      reject(tx.error);
    };
  });
}


let beatTimer = null;
let beatSchedulerTimer = null;
let beatNextTime = 0;
let masterTransportState = "stopped";
let masterProjectPosition = 0;
let masterProjectLength = 300;
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
  hat:   [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
  clap:  [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
  perc:  [0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0]
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


function playPianoNote(freq, duration = 0.9, volume = 0.16) {
  const ctx = getAudioContext();
  const now = ctx.currentTime;

  const master = ctx.createGain();
  const filter = ctx.createBiquadFilter();

  master.gain.setValueAtTime(0.001, now);
  master.gain.exponentialRampToValueAtTime(volume, now + 0.008);
  master.gain.exponentialRampToValueAtTime(0.001, now + duration);

  filter.type = "lowpass";
  filter.frequency.setValueAtTime(Math.min(4200, freq * 8), now);
  filter.Q.value = 0.7;

  master.connect(filter);
  filter.connect(ctx.destination);

  const harmonics = [
    { multiple: 1, gain: 1.00 },
    { multiple: 2, gain: 0.42 },
    { multiple: 3, gain: 0.20 },
    { multiple: 4, gain: 0.10 }
  ];

  harmonics.forEach(({ multiple, gain: harmonicGain }) => {
    const osc = ctx.createOscillator();
    const partial = ctx.createGain();

    osc.type = "sine";
    osc.frequency.setValueAtTime(freq * multiple, now);

    partial.gain.setValueAtTime(harmonicGain, now);
    partial.gain.exponentialRampToValueAtTime(
      0.001,
      now + duration
    );

    osc.connect(partial);
    partial.connect(master);

    osc.start(now);
    osc.stop(now + duration + 0.02);
  });
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

function playSnare() {
  noise(0.18, 900, 0.18);
}

function playHat() {
  noise(0.055, 5000, 0.07);
}

function playClap() {
  noise(0.11, 1400, 0.13);
  setTimeout(() => noise(0.07, 1800, 0.08), 28);
}

function playPerc() {
  const ctx = getAudioContext();
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();

  osc.type = "triangle";
  osc.frequency.setValueAtTime(620, ctx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(180, ctx.currentTime + 0.09);

  gain.gain.setValueAtTime(0.16, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.1);

  osc.connect(gain);
  gain.connect(ctx.destination);

  osc.start();
  osc.stop(ctx.currentTime + 0.1);
}

function playStep(step) {
  currentStep = step;
  document.querySelectorAll(".step").forEach(b => b.classList.remove("current"));
  document.querySelectorAll(`.step[data-step="${step}"]`).forEach(b => b.classList.add("current"));

  if (pattern.kick[step]) playKick();
  if (pattern.snare[step]) playSnare();
  if (pattern.hat[step]) playHat();
  if (pattern.clap[step]) playClap();
  if (pattern.perc[step]) playPerc();
}

async function startBeat() {
  const ctx = getAudioContext();

  if (ctx.state === "suspended") {
    await ctx.resume();
  }

  if (ctx.state !== "running") {
    console.error("MMK AudioContext not running:", ctx.state);
    setTimelineStatus("Audio engine is not running");
    return;
  }

  const bpm = Math.max(40, Math.min(220, Number(bpmEl.value) || 90));
  project.bpm = bpm;

  stopBeat();

  masterTransportState = "playing";
  masterProjectPosition = 0;
  masterProjectLength = 300;

  const stepDuration = 60 / bpm / 4;
  const lookAhead = 0.1;
  const schedulerInterval = 25;

  beatNextTime = ctx.currentTime + 0.05;

  function scheduleBeat() {
    if (masterTransportState !== "playing") return;

    while (
      beatNextTime < ctx.currentTime + lookAhead &&
      masterProjectPosition < masterProjectLength
    ) {
      const step = Math.floor(masterProjectPosition / stepDuration) % 16;

      playStep(step);

      masterProjectPosition += stepDuration;
      beatNextTime += stepDuration;
    }

    if (masterProjectPosition >= masterProjectLength) {
      stopBeat();
      setTimelineStatus("5-minute project finished");
      return;
    }

    beatSchedulerTimer = setTimeout(scheduleBeat, schedulerInterval);
  }

  scheduleBeat();
  setTimelineStatus("Playing • 0:00 / 5:00");
}

function pauseBeat() {
  if (masterTransportState !== "playing") return;

  masterTransportState = "paused";

  if (beatSchedulerTimer) {
    clearTimeout(beatSchedulerTimer);
    beatSchedulerTimer = null;
  }

  setTimelineStatus(
    "Paused • " +
    formatTransportTime(masterProjectPosition) +
    " / 5:00"
  );
}

async function resumeBeat() {
  if (masterTransportState !== "paused") {
    return startBeat();
  }

  const ctx = getAudioContext();

  if (ctx.state === "suspended") {
    await ctx.resume();
  }

  if (ctx.state !== "running") {
    setTimelineStatus("Audio engine is not running");
    return;
  }

  const bpm = Math.max(40, Math.min(220, Number(bpmEl.value) || 90));
  project.bpm = bpm;

  const stepDuration = 60 / bpm / 4;
  const lookAhead = 0.1;
  const schedulerInterval = 25;

  masterTransportState = "playing";
  beatNextTime = ctx.currentTime + 0.05;

  function scheduleBeat() {
    if (masterTransportState !== "playing") return;

    while (
      beatNextTime < ctx.currentTime + lookAhead &&
      masterProjectPosition < masterProjectLength
    ) {
      const step = Math.floor(masterProjectPosition / stepDuration) % 16;

      playStep(step);

      masterProjectPosition += stepDuration;
      beatNextTime += stepDuration;
    }

    if (masterProjectPosition >= masterProjectLength) {
      stopBeat();
      setTimelineStatus("5-minute project finished");
      return;
    }

    beatSchedulerTimer = setTimeout(scheduleBeat, schedulerInterval);
  }

  scheduleBeat();

  setTimelineStatus(
    "Playing • " +
    formatTransportTime(masterProjectPosition) +
    " / 5:00"
  );
}

function formatTransportTime(seconds) {
  const safe = Math.max(0, Number(seconds) || 0);
  const minutes = Math.floor(safe / 60);
  const secs = Math.floor(safe % 60);

  return minutes + ":" + String(secs).padStart(2, "0");
}

function stopBeat() {
  if (beatTimer) {
    clearInterval(beatTimer);
    beatTimer = null;
  }

  if (beatSchedulerTimer) {
    clearTimeout(beatSchedulerTimer);
    beatSchedulerTimer = null;
  }

  masterTransportState = "stopped";
  masterProjectPosition = 0;
  beatNextTime = 0;
  currentStep = -1;

  document
    .querySelectorAll(".step")
    .forEach(b => b.classList.remove("current"));

  setTimelineStatus("Stopped • 0:00 / 5:00");
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
  // The workspace can be replaced by screens such as Projects.
  // Always find the current waveform canvas instead of using a stale reference.
  const currentCanvas = document.getElementById("waveform");

  if (!currentCanvas) {
    console.warn("MMK waveform canvas is not currently available.");
    return;
  }

  const ctx = currentCanvas.getContext("2d");
  const w = currentCanvas.width;
  const h = currentCanvas.height;
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
          audioId: c.audioId || null,
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
  const library = getProjectLibrary();

  // Give the project its permanent library ID BEFORE creating the snapshot.
  if (!project.libraryId) {
    project.libraryId =
      "mmk-" + Date.now() + "-" + Math.random().toString(36).slice(2, 8);
  }

  const snapshot = getStudioSnapshot();
  const collection = type === "draft" ? library.drafts : library.projects;
  const existingId = project.libraryId;

  const index = collection.findIndex(item => item.id === existingId);

  const entry = {
    ...snapshot,
    project: JSON.parse(JSON.stringify(snapshot.project)),
    id: existingId,
    type
  };

  if (index >= 0) {
    collection[index] = entry;
  } else {
    collection.unshift(entry);
  }

  localStorage.setItem("mmkStudioLibrary", JSON.stringify(library));

  // Keep the latest complete snapshot for fast startup recovery.
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
              audioId: c.audioId || null,
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

              <div class="library-item-actions">
                <button class="play-library-item" data-id="${escapeHtml(item.id)}" data-type="${type}">
                  ▶ PLAY
                </button>

                <button class="save-library-file" data-id="${escapeHtml(item.id)}" data-type="${type}">
                  💾 FILE
                </button>

                <button class="open-library-item" data-id="${escapeHtml(item.id)}" data-type="${type}">
                  OPEN
                </button>

                <button class="delete-library-item" data-id="${escapeHtml(item.id)}" data-type="${type}">
                  🗑 DELETE
                </button>
              </div>
            </div>
          `;
        }).join("")}
      </div>
    </section>
  `;
}

async function exportLibraryItem(id, type) {
  const library = getProjectLibrary();
  const collection = type === "draft" ? library.drafts : library.projects;
  const item = collection.find(entry => entry.id === id);

  if (!item || !item.project || !item.pattern) {
    alert("MMK Studio could not export this item.");
    return;
  }

  try {
    const projectData = JSON.stringify({
      ...item,
      mmkStudio: "MMK Studio",
      version: "0.4.1",
      exportedAt: new Date().toISOString()
    }, null, 2);

    const name = item.project.name || "Untitled MMK Project";
    const fileName =
      safeName(name) + "-MMK-Studio-project.mmkstudio";

    const blob = new Blob([projectData], {
      type: "application/octet-stream"
    });

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
        await navigator.share({
          title: "MMK Studio Project",
          text: name,
          files: [file]
        });

        setTimelineStatus("Project saved to Files/share");
        return;
      }
    }

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    link.remove();

    setTimeout(() => URL.revokeObjectURL(url), 1000);

    setTimelineStatus("Project file saved");
    alert("MMK project file saved.");
  } catch (error) {
    console.error("MMK library file export error:", error);
    alert("MMK Studio could not save this project to Files.");
  }
}

function deleteLibraryItem(id, type) {
  const library = getProjectLibrary();
  const collection = type === "draft" ? library.drafts : library.projects;
  const index = collection.findIndex(entry => entry.id === id);

  if (index < 0) {
    alert("MMK Studio could not find this saved item.");
    return;
  }

  const item = collection[index];
  const name = item.project?.name || "Untitled MMK Project";
  const kind = type === "draft" ? "draft" : "project";

  const confirmed = confirm(
    'Delete "' + name + '" from MMK Studio ' + kind + 's?\n\n' +
    "This removes the Library copy only. A file you already exported to your device will not be deleted."
  );

  if (!confirmed) return;

  collection.splice(index, 1);
  localStorage.setItem("mmkStudioLibrary", JSON.stringify(library));

  const currentId = project && project.libraryId;

  if (currentId === id) {
    localStorage.removeItem("mmkStudioProject");
  }

  showProjects();
  setTimelineStatus("Library item deleted");
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

  document.querySelectorAll(".play-library-item").forEach(button => {
    button.onclick = async () => {
      const id = button.dataset.id;
      const type = button.dataset.type;
      const library = getProjectLibrary();
      const collection = type === "draft" ? library.drafts : library.projects;
      const item = collection.find(entry => entry.id === id);

      if (!item || !item.project || !item.pattern) {
        alert("MMK Studio could not preview this project.");
        return;
      }

      stopBeat();

      const originalPattern = pattern;
      const originalBpm = bpmEl.value;

      try {
        pattern = JSON.parse(JSON.stringify(item.pattern));
        bpmEl.value = Number(item.project.bpm) || 90;

        await startBeat();

        setTimelineStatus(
          type === "draft"
            ? "Playing draft preview"
            : "Playing project preview"
        );

        button.textContent = "■ STOP";

        const previewDuration =
          Math.max(4, Math.min(30, 60000 / (Number(bpmEl.value) || 90) * 16 / 1000));

        setTimeout(() => {
          stopBeat();
          pattern = originalPattern;
          bpmEl.value = originalBpm;
          button.textContent = "▶ PLAY";
          setTimelineStatus("Preview stopped");
        }, previewDuration * 1000);

      } catch (error) {
        console.error("MMK library preview error:", error);
        stopBeat();
        pattern = originalPattern;
        bpmEl.value = originalBpm;
        button.textContent = "▶ PLAY";
        alert("MMK Studio could not preview this project.");
      }
    };
  });

  document.querySelectorAll(".save-library-file").forEach(button => {
    button.onclick = () => {
      exportLibraryItem(
        button.dataset.id,
        button.dataset.type
      );
    };
  });

  document.querySelectorAll(".delete-library-item").forEach(button => {
    button.onclick = () => {
      deleteLibraryItem(
        button.dataset.id,
        button.dataset.type
      );
    };
  });

  document.querySelectorAll(".open-library-item").forEach(button => {
    button.onclick = () => {
      const id = button.dataset.id;
      const type = button.dataset.type;

      loadLibraryItem(id, type).then(success => {
        if (!success) {
          alert("MMK Studio could not open this project.");
          return;
        }

        setTimelineStatus(
          type === "draft" ? "Draft opened" : "Project opened"
        );

        alert(
          type === "draft"
            ? "MMK draft opened successfully."
            : "MMK project opened successfully."
        );
      }).catch(error => {
        console.error("MMK library open error:", error);
        setTimelineStatus("Project open failed");
        alert("MMK Studio could not open this project.");
      });
    };
  });
}

async function loadLibraryItem(id, type) {
  const library = getProjectLibrary();
  const collection = type === "draft" ? library.drafts : library.projects;
  const item = collection.find(entry => entry.id === id);

  if (!item) {
    alert("MMK DEBUG: saved item was not found.");
    return false;
  }

  const normalized = {
    ...item,
    project: item.project || null,
    pattern: item.pattern || null,
    timeline: item.timeline || null,
    clips: Array.isArray(item.clips) ? item.clips : []
  };

  if (!normalized.project || !normalized.pattern) {
    alert(
      "MMK DEBUG: incomplete project\\n" +
      "project: " + !!normalized.project + "\\n" +
      "pattern: " + !!normalized.pattern + "\\n" +
      "timeline: " + !!normalized.timeline + "\\n" +
      "clips: " + normalized.clips.length
    );
    return false;
  }

  try {
    return await applyProjectData(normalized);
  } catch (error) {
    console.error("MMK project open error:", error);
    alert(
      "MMK DEBUG OPEN ERROR:\\n" +
      (error && error.message ? error.message : String(error))
    );
    return false;
  }
}

async function applyProjectData(data) {
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
          audioId: c.audioId || null,
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

  if (typeof clips !== "undefined" && clips.length) {
    for (const clip of clips) {
      if (!clip.audioId) continue;

      try {
        const blob = await loadAudioBlob(clip.audioId);

        if (blob) {
          clip.url = URL.createObjectURL(blob);
        }
      } catch (error) {
        console.error("MMK audio restore error:", error);
      }
    }

    renderRealTimeline();
  }

  return true;
}
async function loadProject() {
  // First try the latest complete project snapshot.
  try {
    const saved = localStorage.getItem("mmkStudioProject");

    if (saved) {
      const data = JSON.parse(saved);

      if (await applyProjectData(data)) {
        setTimelineStatus("Project restored");
        return true;
      }
    }
  } catch (error) {
    console.warn("MMK latest project recovery failed:", error);
  }

  // Recovery path: restore the newest saved project from the library.
  try {
    const library = getProjectLibrary();
    const allItems = [
      ...library.projects,
      ...library.drafts
    ].filter(item => item && item.project && item.pattern);

    allItems.sort((a, b) =>
      String(b.savedAt || "").localeCompare(String(a.savedAt || ""))
    );

    if (allItems.length) {
      const recovered = await applyProjectData(allItems[0]);

      if (recovered) {
        localStorage.setItem(
          "mmkStudioProject",
          JSON.stringify(allItems[0])
        );
        setTimelineStatus("Project recovered from library");
        return true;
      }
    }
  } catch (error) {
    console.warn("MMK library recovery failed:", error);
  }

  return false;
}

function newProject() {
  const name = prompt("Project name:", "My New Beat");
  if (!name) return;

  project = {
    name,
    bpm: 90,
    lyrics: "",
    samples: [],
    recordings: [],
    libraryId: null
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

  if (action === "play") {
    if (masterTransportState === "paused") {
      resumeBeat();
    } else {
      startBeat();
    }
  }

  if (action === "stop") stopBeat();
  if (action === "new-beat") randomBeat();
  if (action === "samples") showSamples();
  if (action === "record") recordAudio();
  if (action === "lyrics") showLyrics();
  if (action === "projects") showProjects();

  if (action === "save") {
    try {
      saveProject();
    } catch (error) {
      console.error("MMK SAVE ERROR:", error);
      const status = document.getElementById("timelineStatus");
      if (status) {
        status.textContent = "SAVE ERROR: " + (error.message || error);
      }
      alert("MMK SAVE ERROR: " + (error.message || error));
    }
  }

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

/* MMK STUDIO v0.4 REAL TIMELINE STATE */
let clips = [];
let selectedClip = null;
let snapEnabled = true;
let loopEnabled = false;
let timelinePlaying = false;
let timelineStart = 0;

renderPattern();
renderTimeline();
drawWaveform();

function autoSave() {
  try {
    saveDraft(false);
    setTimelineStatus("Auto-saved draft");
  } catch (error) {
    console.error("MMK auto-draft error:", error);
    setTimelineStatus("Auto-save failed");
  }
}

setInterval(() => {
  if (autosaveEnabled) autoSave();
}, 15000);


loadProject();

/* MMK STUDIO v0.4 REAL TIMELINE */

function setTimelineStatus(msg){
  const el = document.getElementById("timelineStatus");
  if(el) el.textContent = msg;
}

async function makeClip(file){
  if(!file) return null;

  const url = URL.createObjectURL(file);
  const audioId = await saveAudioBlob(file, file.name);

  const duration = await new Promise((resolve) => {
    const probe = new Audio();

    probe.onloadedmetadata = () => {
      const value = Number(probe.duration);
      URL.revokeObjectURL(probe.src);
      resolve(Number.isFinite(value) && value > 0 ? value : 4);
    };

    probe.onerror = () => {
      URL.revokeObjectURL(probe.src);
      resolve(4);
    };

    probe.src = url;
  });

  return {
    id: Date.now() + Math.random(),
    audioId,
    name: file.name,
    url,
    start: 0,
    duration,
    trimStart: 0,
    trimEnd: duration
  };
}


let activeTimelineAudio = null;

async function playSelectedTimelineClip(){
  if(typeof selectedClip === "undefined" || selectedClip === null){
    setTimelineStatus("Select an audio clip first");
    return;
  }

  const clip = clips.find(c => c.id === selectedClip);
  if(!clip){
    setTimelineStatus("Selected clip not found");
    return;
  }

  try{
    if(activeTimelineAudio){
      activeTimelineAudio.pause();
      activeTimelineAudio.removeAttribute("src");
      activeTimelineAudio.load();
      activeTimelineAudio = null;
    }

    setTimelineStatus("Loading: " + clip.name);

    let url = clip.url;

    if(!url && clip.audioId){
      const blob = await loadAudioBlob(clip.audioId);

      if(blob){
        url = URL.createObjectURL(blob);
        clip.url = url;
      }
    }

    if(!url){
      setTimelineStatus("Audio file not available");
      return;
    }

    const audio = new Audio();
    audio.preload = "auto";
    audio.src = url;
    audio.volume = 1;
    activeTimelineAudio = audio;

    audio.onplay = () => {
      timelinePlaying = true;
      setTimelineStatus("Playing: " + clip.name);
    };

    audio.onended = () => {
      timelinePlaying = false;

      if(activeTimelineAudio === audio){
        activeTimelineAudio = null;
      }

      if(loopEnabled){
        playSelectedTimelineClip();
      }else{
        setTimelineStatus("Finished: " + clip.name);
      }
    };

    audio.onerror = () => {
      timelinePlaying = false;

      if(activeTimelineAudio === audio){
        activeTimelineAudio = null;
      }

      console.error("MMK audio error:", audio.error);
      setTimelineStatus("Audio playback failed");
    };

    audio.load();

    await new Promise((resolve, reject) => {
      if(audio.readyState >= 2){
        resolve();
        return;
      }

      const ready = () => {
        cleanup();
        resolve();
      };

      const failed = () => {
        cleanup();
        reject(new Error("Audio could not load"));
      };

      const cleanup = () => {
        audio.removeEventListener("canplay", ready);
        audio.removeEventListener("error", failed);
      };

      audio.addEventListener("canplay", ready, {once:true});
      audio.addEventListener("error", failed, {once:true});
    });

    await audio.play();

  }catch(error){
    console.error("MMK timeline playback error:", error);
    timelinePlaying = false;

    if(activeTimelineAudio){
      activeTimelineAudio.pause();
      activeTimelineAudio = null;
    }

    setTimelineStatus("Playback could not start");
  }
}
function stopTimelinePlayback(){
  if(activeTimelineAudio){
    activeTimelineAudio.pause();
    activeTimelineAudio.currentTime = 0;
    activeTimelineAudio = null;
  }

  timelinePlaying = false;
  setTimelineStatus("Stopped");
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

    el.onclick = async ()=>{
      selectedClip = clip.id;
      renderRealTimeline();
      setTimelineStatus("Loading: " + clip.name);

      if(!clip.url && clip.audioId){
        try{
          const blob = await loadAudioBlob(clip.audioId);

          if(blob){
            clip.url = URL.createObjectURL(blob);
            setTimelineStatus("Selected: " + clip.name);
          }else{
            setTimelineStatus("Audio file not found");
          }
        }catch(error){
          console.error("MMK clip preload error:", error);
          setTimelineStatus("Audio could not be loaded");
        }
      }else{
        setTimelineStatus("Selected: " + clip.name);
      }
    };

    grid.appendChild(el);
  });
}

function snapBeat(value){
  if(!snapEnabled) return value;
  return Math.round(value);
}

async function addAudioClip(file){
  if(!file) return;

  try {
    setTimelineStatus("Saving audio: " + file.name);

    const clip = await makeClip(file);

    if(!clip){
      setTimelineStatus("Audio was not added");
      return;
    }

    clip.start = snapBeat(clips.length);
    clips.push(clip);
    selectedClip = clip.id;

    renderRealTimeline();
    saveProject();

    setTimelineStatus("Added and saved: " + file.name);
  } catch(error) {
    console.error("MMK audio vault error:", error);
    setTimelineStatus("Audio save failed");
    alert("MMK Studio could not save this audio file.");
  }
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
  const playTimelineBtn = document.getElementById("playTimelineBtn");
  const stopTimelineBtn = document.getElementById("stopTimelineBtn");

  if(playTimelineBtn){
    playTimelineBtn.addEventListener("click", playSelectedTimelineClip);
  }

  if(stopTimelineBtn){
    stopTimelineBtn.addEventListener("click", stopTimelinePlayback);
  }


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
            audioId: c.audioId || null,
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

/* =========================================================
   MMK INSTRUMENT / BEAT LAB — SELECTION LAYER
   Independent from the main Studio transport.
   ========================================================= */

const instrumentLabState = {
  category: "drums",
  instrument: "kick",
  playing: false,
  activeInstruments: new Set(["kick", "snare", "hat"])
};

const instrumentLabPatterns = {
  kick:  [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
  snare: [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
  hat:   [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
  clap:  [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
  perc:  [0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0],

  "bass-1":    [1,0,0,1,0,0,1,0,1,0,0,1,0,0,1,0],
  "bass-2":    [1,0,1,0,0,1,0,0,1,0,1,0,0,1,0,0],

  "guitar-1":  [1,0,0,0,0,1,0,0,1,0,0,0,0,1,0,0],
  "guitar-2":  [1,0,0,1,0,0,0,1,1,0,0,1,0,0,0,1],

  piano:       [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
  synth:       [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
  organ:       [1,0,0,0,0,0,1,0,1,0,0,0,0,0,1,0]
};

function updateInstrumentLabStatus(message) {
  const status = document.getElementById("instrumentLabStatus");
  if (status) status.textContent = message;
}

function selectInstrumentLabCategory(category) {
  instrumentLabState.category = category;

  document.querySelectorAll("[data-instrument-category]").forEach(button => {
    button.classList.toggle(
      "active",
      button.dataset.instrumentCategory === category
    );
  });

  document.querySelectorAll("[data-bank]").forEach(bank => {
    bank.hidden = bank.dataset.bank !== category;
  });

  updateInstrumentLabStatus(
    category.toUpperCase() + " — choose an instrument"
  );
}

function selectInstrumentLabInstrument(instrument) {
  if (!instrumentLabPatterns[instrument]) return;

  instrumentLabState.instrument = instrument;

  document.querySelectorAll(".instrument-pad").forEach(button => {
    button.classList.toggle(
      "active",
      button.dataset.instrument === instrument
    );
  });

  const patternDisplay = document.getElementById("instrumentPattern");

  if (patternDisplay) {
    const pattern = instrumentLabPatterns[instrument];

    patternDisplay.textContent =
      instrument.toUpperCase() +
      " • " +
      pattern.map(step => step ? "●" : "·").join(" ");
  }

  updateInstrumentLabStatus(
    instrument.toUpperCase() + " selected"
  );
}

document.querySelectorAll("[data-instrument-category]").forEach(button => {
  button.addEventListener("click", () => {
    selectInstrumentLabCategory(button.dataset.instrumentCategory);
  });
});

document.querySelectorAll(".instrument-pad").forEach(button => {
  button.addEventListener("click", () => {
    const instrument = button.dataset.instrument;

    if (instrumentLabState.activeInstruments.has(instrument)) {
      instrumentLabState.activeInstruments.delete(instrument);
      button.classList.remove("active");
    } else {
      instrumentLabState.activeInstruments.add(instrument);
      button.classList.add("active");
    }

    instrumentLabState.instrument = instrument;

    updateInstrumentLabStatus(
      instrument.toUpperCase() +
      (instrumentLabState.activeInstruments.has(instrument) ? " ON" : " OFF")
    );
  });
});

const firstInstrumentPad = document.querySelector(
  '.instrument-pad[data-instrument="kick"]'
);

if (firstInstrumentPad) {
  document.querySelectorAll(".instrument-pad").forEach(button => {
    button.classList.toggle(
      "active",
      instrumentLabState.activeInstruments.has(button.dataset.instrument)
    );
  });

  updateInstrumentLabStatus("DRUMS READY • KICK / SNARE / HI-HAT ON");
}

console.log("MMK INSTRUMENT LAB: selection layer ready");

function playInstrumentLabSound(instrument) {
  switch (instrument) {
    case "kick":
      playKick();
      break;
    case "snare":
      playSnare();
      break;
    case "hat":
      playHat();
      break;
    case "clap":
      playClap();
      break;
    case "perc":
      playPerc();
      break;
    case "bass-1":
      playTone(82.41, 0.35, "sawtooth", 0.12);
      break;
    case "bass-2":
      playTone(110.00, 0.35, "square", 0.10);
      break;
    case "guitar-1":
      playTone(196.00, 0.45, "triangle", 0.10);
      break;
    case "guitar-2":
      playTone(246.94, 0.45, "triangle", 0.10);
      break;
    case "piano":
      playPianoNote(261.63, 0.9, 0.14);
      break;
    case "synth":
      playTone(329.63, 0.5, "sawtooth", 0.08);
      break;
    case "organ":
      playTone(392.00, 0.7, "sine", 0.10);
      break;
  }
}

function playInstrumentLabStep(step) {
  instrumentLabState.activeInstruments.forEach(instrument => {
    const instrumentPattern = instrumentLabPatterns[instrument];

    if (instrumentPattern && instrumentPattern[step]) {
      playInstrumentLabSound(instrument);
    }
  });
}

let instrumentLabTimer = null;
let instrumentLabStep = 0;
let instrumentLabNextTime = 0;
let instrumentLabPlaying = false;

function instrumentLabStepDuration() {
  const bpm = Number(project.bpm) || 90;
  return 60 / bpm / 4;
}

function scheduleInstrumentLab() {
  if (!instrumentLabPlaying) return;

  const ctx = getAudioContext();
  const lookAhead = 0.1;

  while (instrumentLabNextTime < ctx.currentTime + lookAhead) {
    const step = instrumentLabStep;

    window.setTimeout(() => {
      if (instrumentLabPlaying) {
        playInstrumentLabStep(step);
      }
    }, Math.max(0, (instrumentLabNextTime - ctx.currentTime) * 1000));

    instrumentLabStep = (instrumentLabStep + 1) % 16;
    instrumentLabNextTime += instrumentLabStepDuration();
  }
}

function startInstrumentLab() {
  if (instrumentLabPlaying) return;

  const ctx = getAudioContext();

  instrumentLabPlaying = true;
  instrumentLabStep = 0;
  instrumentLabNextTime = ctx.currentTime;

  instrumentLabTimer = window.setInterval(
    scheduleInstrumentLab,
    25
  );

  scheduleInstrumentLab();

  updateInstrumentLabStatus("PLAYING • 16-STEP PATTERN");
}

function stopInstrumentLab() {
  instrumentLabPlaying = false;

  if (instrumentLabTimer) {
    window.clearInterval(instrumentLabTimer);
    instrumentLabTimer = null;
  }

  instrumentLabStep = 0;
  updateInstrumentLabStatus("STOPPED");
}

const instrumentPlayButton = document.getElementById("instrumentPlayBtn");
const instrumentStopButton = document.getElementById("instrumentStopBtn");

if (instrumentPlayButton) {
  instrumentPlayButton.addEventListener("click", startInstrumentLab);
}

if (instrumentStopButton) {
  instrumentStopButton.addEventListener("click", stopInstrumentLab);
}

console.log("MMK INSTRUMENT LAB: automatic sequencer ready");



const pianoKeyboardState = {
  activeNotes: new Map(),
  playing: false,
  timer: null,
  step: 0
};

function togglePianoNote(button) {
  if (!button) return;

  const note = button.dataset.note;
  const freq = Number(button.dataset.freq);

  if (!note || !Number.isFinite(freq)) return;

  if (pianoKeyboardState.activeNotes.has(note)) {
    pianoKeyboardState.activeNotes.delete(note);
    button.classList.remove("active");
    updateInstrumentLabStatus(note + " OFF");
    return;
  }

  pianoKeyboardState.activeNotes.set(note, freq);
  button.classList.add("active");
  updateInstrumentLabStatus(note + " ON");
}

function playSelectedPianoNotes() {
  pianoKeyboardState.activeNotes.forEach(freq => {
    playPianoNote(freq, 0.7, 0.12);
  });
}

function startPianoAutomation() {
  if (pianoKeyboardState.playing) return;

  if (pianoKeyboardState.activeNotes.size === 0) {
    updateInstrumentLabStatus("PIANO • choose notes first");
    return;
  }

  pianoKeyboardState.playing = true;
  pianoKeyboardState.step = 0;

  playSelectedPianoNotes();

  const intervalMs =
    ((60 / (Number(project.bpm) || 90)) / 2) * 1000;

  pianoKeyboardState.timer = window.setInterval(() => {
    if (!pianoKeyboardState.playing) return;

    playSelectedPianoNotes();
    pianoKeyboardState.step += 1;
  }, intervalMs);

  updateInstrumentLabStatus("PIANO • AUTOMATION PLAYING");
}

function stopPianoAutomation() {
  pianoKeyboardState.playing = false;

  if (pianoKeyboardState.timer) {
    window.clearInterval(pianoKeyboardState.timer);
    pianoKeyboardState.timer = null;
  }

  pianoKeyboardState.step = 0;
  updateInstrumentLabStatus("PIANO • READY");
}

document.querySelectorAll(".piano-key").forEach(button => {
  button.addEventListener("pointerdown", event => {
    event.preventDefault();
    togglePianoNote(button);
  });
});


const pianoPlayButton = document.getElementById("pianoPlayBtn");
const pianoStopButton = document.getElementById("pianoStopBtn");
const pianoAutomationStatus =
  document.getElementById("pianoAutomationStatus");

function updatePianoAutomationStatus(message) {
  if (pianoAutomationStatus) {
    pianoAutomationStatus.textContent = message;
  }
}

if (pianoPlayButton) {
  pianoPlayButton.addEventListener("click", () => {
    startPianoAutomation();

    if (pianoKeyboardState.playing) {
      updatePianoAutomationStatus("PLAYING");
    }
  });
}

if (pianoStopButton) {
  pianoStopButton.addEventListener("click", () => {
    stopPianoAutomation();
    updatePianoAutomationStatus("STOPPED");
  });
}

console.log("MMK PIANO KEYBOARD: persistent note automation ready");

/* =========================================================
   MMK PIANO → STUDIO TIMELINE
   Renders selected piano notes into a WAV Blob, then sends
   the result through the existing Audio Vault + clip system.
   ========================================================= */

function writeWav16(buffer) {
  const channels = buffer.numberOfChannels;
  const sampleRate = buffer.sampleRate;
  const frameCount = buffer.length;
  const bytesPerSample = 2;
  const blockAlign = channels * bytesPerSample;
  const dataSize = frameCount * blockAlign;
  const arrayBuffer = new ArrayBuffer(44 + dataSize);
  const view = new DataView(arrayBuffer);

  function writeString(offset, value) {
    for (let i = 0; i < value.length; i++) {
      view.setUint8(offset + i, value.charCodeAt(i));
    }
  }

  writeString(0, "RIFF");
  view.setUint32(4, 36 + dataSize, true);
  writeString(8, "WAVE");
  writeString(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, channels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * blockAlign, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, 16, true);
  writeString(36, "data");
  view.setUint32(40, dataSize, true);

  let offset = 44;

  for (let i = 0; i < frameCount; i++) {
    for (let channel = 0; channel < channels; channel++) {
      const sample = buffer.getChannelData(channel)[i];
      const clamped = Math.max(-1, Math.min(1, sample));
      const value = clamped < 0
        ? clamped * 0x8000
        : clamped * 0x7fff;

      view.setInt16(offset, value, true);
      offset += 2;
    }
  }

  return new Blob([arrayBuffer], { type: "audio/wav" });
}

async function renderPianoComposition() {
  const selectedNotes = [...pianoKeyboardState.activeNotes.values()];

  if (!selectedNotes.length) {
    throw new Error("Choose at least one piano note first.");
  }

  const bpm = Number(project.bpm) || 90;
  const stepDuration = 60 / bpm / 2;
  const steps = 16;
  const tail = 0.5;
  const duration = (steps * stepDuration) + tail;
  const sampleRate = 44100;

  const offline = new OfflineAudioContext(
    2,
    Math.ceil(duration * sampleRate),
    sampleRate
  );

  selectedNotes.forEach((freq, noteIndex) => {
    for (let step = 0; step < steps; step++) {
      const start = step * stepDuration;

      const master = offline.createGain();
      const filter = offline.createBiquadFilter();

      const noteVolume =
        0.055 / Math.max(1, Math.sqrt(selectedNotes.length));

      master.gain.setValueAtTime(0.001, start);
      master.gain.exponentialRampToValueAtTime(
        noteVolume,
        start + 0.008
      );
      master.gain.exponentialRampToValueAtTime(
        0.001,
        start + Math.min(0.65, stepDuration * 0.9)
      );

      filter.type = "lowpass";
      filter.frequency.setValueAtTime(
        Math.min(4200, freq * 8),
        start
      );
      filter.Q.value = 0.7;

      master.connect(filter);
      filter.connect(offline.destination);

      const harmonics = [
        [1, 1.00],
        [2, 0.42],
        [3, 0.20],
        [4, 0.10]
      ];

      harmonics.forEach(([multiple, harmonicGain]) => {
        const osc = offline.createOscillator();
        const partial = offline.createGain();

        osc.type = "sine";
        osc.frequency.setValueAtTime(
          freq * multiple,
          start
        );

        partial.gain.setValueAtTime(
          harmonicGain,
          start
        );
        partial.gain.exponentialRampToValueAtTime(
          0.001,
          start + Math.min(0.7, stepDuration)
        );

        osc.connect(partial);
        partial.connect(master);

        osc.start(start);
        osc.stop(
          start + Math.min(0.75, stepDuration + 0.05)
        );
      });
    }
  });

  return offline.startRendering();
}

async function addPianoCompositionToStudio() {
  try {
    if (!pianoKeyboardState.activeNotes.size) {
      updatePianoAutomationStatus("CHOOSE NOTES FIRST");
      setTimelineStatus("Choose piano notes before adding to Studio.");
      return;
    }

    updatePianoAutomationStatus("RENDERING...");
    setTimelineStatus("Rendering piano composition...");

    const buffer = await renderPianoComposition();
    const wavBlob = writeWav16(buffer);

    const bpm = Number(project.bpm) || 90;
    const name =
      safeName(project.name || "MMK-Project") +
      "-piano-" +
      bpm +
      "bpm.wav";

    const file = new File(
      [wavBlob],
      name,
      { type: "audio/wav" }
    );

    await addAudioClip(file);

    updatePianoAutomationStatus("ADDED TO STUDIO");
    setTimelineStatus("Piano composition added to Studio.");
  } catch (error) {
    console.error("MMK piano-to-studio error:", error);
    updatePianoAutomationStatus("FAILED");
    setTimelineStatus("Piano composition could not be added.");
    alert("MMK Studio could not create the piano composition.");
  }
}

const addPianoToStudioButton =
  document.getElementById("addInstrumentToStudioBtn");

if (addPianoToStudioButton) {
  addPianoToStudioButton.addEventListener(
    "click",
    addPianoCompositionToStudio
  );
}

console.log("MMK PIANO → STUDIO: timeline rendering ready");


/* =========================================================
   MMK LIVE PROJECT DASHBOARD
   Reads existing Studio state. Does not control audio.
   ========================================================= */

function updateLiveProjectDashboard(action) {
  const name = document.getElementById("liveProjectName");
  const bpm = document.getElementById("liveProjectBpm");
  const instrument = document.getElementById("liveInstrument");
  const category = document.getElementById("liveCategory");
  const timelineState = document.getElementById("liveTimelineState");
  const autosave = document.getElementById("liveAutosaveState");
  const lastAction = document.getElementById("liveLastAction");

  if (name) {
    name.textContent = project.name || "Untitled MMK Project";
  }

  if (bpm) {
    bpm.textContent = Number(project.bpm) || 90;
  }

  if (instrument) {
    instrument.textContent =
      typeof instrumentLabState !== "undefined"
        ? String(instrumentLabState.instrument || "NONE").toUpperCase()
        : "NONE";
  }

  if (category) {
    category.textContent =
      typeof instrumentLabState !== "undefined"
        ? String(instrumentLabState.category || "NONE").toUpperCase()
        : "NONE";
  }

  if (timelineState) {
    timelineState.textContent =
      typeof timelinePlaying !== "undefined" && timelinePlaying
        ? "PLAYING"
        : "READY";
  }

  if (autosave) {
    autosave.textContent = autosaveEnabled ? "ON" : "OFF";
  }

  if (action && lastAction) {
    lastAction.textContent = action;
  }
}

setInterval(() => {
  updateLiveProjectDashboard();
}, 500);

updateLiveProjectDashboard("Studio ready");

console.log("MMK LIVE PROJECT DASHBOARD: LIVE");

/* =========================================================
   MMK LIVE PROJECT FLOW — STATE DISPLAY
   Display layer only. Does not control audio transport.
   ========================================================= */

function updateLiveProjectFlow(action) {
  const nodes = document.querySelectorAll(".flow-node");

  let activeStage = "project";

  if (
    typeof timelinePlaying !== "undefined" &&
    timelinePlaying
  ) {
    activeStage = "timeline";
  } else if (
    typeof instrumentLabState !== "undefined" &&
    instrumentLabState.instrument
  ) {
    activeStage = "instrument";
  }

  nodes.forEach(node => {
    node.classList.toggle(
      "active",
      node.dataset.flow === activeStage
    );
  });

  const projectName = document.getElementById("liveProjectName");
  const bpm = document.getElementById("liveProjectBpm");
  const instrument = document.getElementById("liveInstrument");
  const timelineState = document.getElementById("liveTimelineState");
  const autosave = document.getElementById("liveAutosaveState");
  const currentWork = document.getElementById("liveCurrentWork");
  const lastAction = document.getElementById("liveLastAction");

  if (projectName) {
    projectName.textContent =
      project.name || "Untitled MMK Project";
  }

  if (bpm) {
    bpm.textContent =
      (Number(project.bpm) || 90) + " BPM";
  }

  if (instrument) {
    instrument.textContent =
      typeof instrumentLabState !== "undefined"
        ? String(
            instrumentLabState.instrument || "NONE"
          ).toUpperCase()
        : "NONE";
  }

  if (timelineState) {
    timelineState.textContent =
      typeof timelinePlaying !== "undefined" &&
      timelinePlaying
        ? "PLAYING"
        : "READY";
  }

  if (autosave) {
    autosave.textContent =
      autosaveEnabled ? "AUTO-SAVE ON" : "AUTO-SAVE OFF";
  }

  if (currentWork) {
    const currentInstrument =
      typeof instrumentLabState !== "undefined"
        ? String(
            instrumentLabState.instrument || "NONE"
          ).toUpperCase()
        : "NONE";

    const currentCategory =
      typeof instrumentLabState !== "undefined"
        ? String(
            instrumentLabState.category || "NONE"
          ).toUpperCase()
        : "NONE";

    currentWork.textContent =
      currentInstrument + " • " + currentCategory;
  }

  if (action && lastAction) {
    lastAction.textContent = action;
  }
}

setInterval(() => {
  updateLiveProjectFlow();
}, 500);

updateLiveProjectFlow("Studio ready");

console.log("MMK LIVE PROJECT FLOW: CONNECTED");


/* =========================================================
   MMK AI MUSIC LAB — CONTROL LAYER
   UI interaction only. No external AI/API yet.
   ========================================================= */

const aiMusicLabState = {
  tool: null
};

const aiToolPrompts = {
  hook: "What is the song about? Give me a strong hip-hop hook idea.",
  verse: "What is the story? Give me a verse concept with strong imagery and rhyme ideas.",
  chorus: "What emotion should the chorus create? Build a memorable chorus concept.",
  structure: "Help me structure this song from intro to outro.",
  style: "Describe the sound, mood, tempo and production style for this song.",
  beat: "Describe a hip-hop beat idea that fits this project.",
  automation: "What Studio tasks should be automated for this project?",
  brain: "Analyze the current project and suggest the next best creative step."
};

function selectAITool(tool) {
  if (!aiToolPrompts[tool]) return;

  aiMusicLabState.tool = tool;

  document.querySelectorAll(".ai-tool").forEach(button => {
    button.classList.toggle(
      "active",
      button.dataset.aiTool === tool
    );
  });

  const title = document.getElementById("aiWorkspaceTitle");
  const prompt = document.getElementById("aiPrompt");
  const status = document.getElementById("aiMusicLabStatus");

  const names = {
    hook: "AI Hook Generator",
    verse: "AI Verse Assistant",
    chorus: "AI Chorus Builder",
    structure: "AI Song Structure",
    style: "AI Style Director",
    beat: "AI Beat Ideas",
    automation: "Studio Automation",
    brain: "MMK Project Brain"
  };

  if (title) {
    title.textContent = names[tool] || "AI Workspace";
  }

  if (prompt) {
    prompt.value = aiToolPrompts[tool];
  }

  if (status) {
    status.textContent = tool.toUpperCase() + " READY";
  }

  if (typeof updateLiveProjectDashboard === "function") {
    updateLiveProjectDashboard("AI " + tool.toUpperCase() + " selected");
  }

  if (typeof updateLiveProjectFlow === "function") {
    updateLiveProjectFlow("AI " + tool.toUpperCase() + " selected");
  }
}

document.querySelectorAll(".ai-tool").forEach(button => {
  button.addEventListener("click", () => {
    selectAITool(button.dataset.aiTool);
  });
});

const aiGenerateBtn = document.getElementById("aiGenerateBtn");
const aiClearBtn = document.getElementById("aiClearBtn");

if (aiGenerateBtn) {
  aiGenerateBtn.addEventListener("click", () => {
    const output = document.getElementById("aiOutput");
    const prompt = document.getElementById("aiPrompt");

    if (!output) return;

    const request = prompt
      ? prompt.value.trim()
      : "";

    if (!request) {
      output.innerHTML =
        "<span>Enter an idea before generating.</span>";
      return;
    }

    output.innerHTML =
      "<strong>AI WORKSPACE READY</strong><br>" +
      "Your request has been captured for the AI engine.<br><br>" +
      "<small>External AI generation will be connected in the next layer.</small>";

    if (typeof updateLiveProjectFlow === "function") {
      updateLiveProjectFlow("AI request prepared");
    }
  });
}

if (aiClearBtn) {
  aiClearBtn.addEventListener("click", () => {
    const prompt = document.getElementById("aiPrompt");
    const output = document.getElementById("aiOutput");

    if (prompt) prompt.value = "";
    if (output) {
      output.innerHTML =
        "<span>AI results will appear here.</span>";
    }
  });
}

console.log("MMK AI MUSIC LAB: CONTROL LAYER READY");


/* =========================================================
   MMK AI MUSIC LAB — SAMPLE VAULT CONNECTION
   Uses the existing MMK Audio Vault.
   ========================================================= */

const aiSamples = [];

function renderAISamples() {
  const list = document.getElementById("aiSamplesList");
  const status = document.getElementById("aiSamplesStatus");

  if (status) {
    status.textContent =
      aiSamples.length + " SAMPLE" +
      (aiSamples.length === 1 ? "" : "S");
  }

  if (!list) return;

  if (!aiSamples.length) {
    list.innerHTML =
      "<span>No samples added yet.</span>";
    return;
  }

  list.innerHTML = "";

  aiSamples.forEach((sample, index) => {
    const row = document.createElement("div");
    row.className = "ai-sample-row";

    row.innerHTML = `
      <div>
        <strong>${sample.name}</strong>
        <small>Audio Sample ${index + 1}</small>
      </div>
      <button type="button" data-sample-index="${index}">
        REMOVE
      </button>
    `;

    row.querySelector("button").addEventListener(
      "click",
      () => {
        aiSamples.splice(index, 1);
        renderAISamples();
      }
    );

    list.appendChild(row);
  });
}

async function addAISamples(files) {
  if (!files || !files.length) return;

  const status = document.getElementById("aiSamplesStatus");

  if (status) {
    status.textContent = "ADDING...";
  }

  for (const file of files) {
    try {
      const audioId = await saveAudioBlob(
        file,
        file.name
      );

      aiSamples.push({
        id: audioId,
        name: file.name,
        type: file.type || "audio/*"
      });
    } catch (error) {
      console.error(
        "MMK AI SAMPLE SAVE ERROR:",
        error
      );
    }
  }

  renderAISamples();

  if (typeof updateLiveProjectFlow === "function") {
    updateLiveProjectFlow(
      aiSamples.length + " sample(s) added"
    );
  }
}

const aiAddSamplesBtn =
  document.getElementById("aiAddSamplesBtn");

const aiSampleInput =
  document.getElementById("aiSampleInput");

if (aiAddSamplesBtn && aiSampleInput) {
  aiAddSamplesBtn.addEventListener(
    "click",
    () => aiSampleInput.click()
  );

  aiSampleInput.addEventListener(
    "change",
    async () => {
      await addAISamples(
        Array.from(aiSampleInput.files || [])
      );

      aiSampleInput.value = "";
    }
  );
}

renderAISamples();

console.log(
  "MMK AI MUSIC LAB: SAMPLE VAULT CONNECTED"
);


/* =========================================================
   MMK AI HOOK — BACKEND CONNECTION
   ========================================================= */

async function requestAIHook() {
  const prompt = document.getElementById("aiPrompt");
  const output = document.getElementById("aiOutput");
  const status = document.getElementById("aiMusicLabStatus");

  if (!prompt || !output) return;

  const idea = prompt.value.trim();

  if (!idea) {
    output.innerHTML =
      "<span>Write your song idea first.</span>";
    return;
  }

  if (status) status.textContent = "GENERATING...";

  output.innerHTML =
    "<span>Connecting to MMK AI Hook Engine...</span>";

  try {
    const response = await fetch(
      "http://127.0.0.1:8091/api/ai/hook",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ idea })
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.error || "AI Hook request failed."
      );
    }

    output.innerHTML = `
      <strong>🎤 AI HOOK REQUEST</strong>
      <p>${data.idea}</p>
      <small>MMK AI Hook Engine connected.</small>
    `;

    if (status) status.textContent = "CONNECTED";

    if (typeof updateLiveProjectFlow === "function") {
      updateLiveProjectFlow("AI Hook generated");
    }

  } catch (error) {
    console.error("MMK AI HOOK ERROR:", error);

    output.innerHTML =
      "<span>AI connection failed. Check the MMK AI backend.</span>";

    if (status) status.textContent = "ERROR";
  }
}

const originalAIGenerateButton =
  document.getElementById("aiGenerateBtn");

if (originalAIGenerateButton) {
  originalAIGenerateButton.addEventListener(
    "click",
    requestAIHook
  );
}

console.log("MMK AI HOOK: BACKEND CONNECTED");

