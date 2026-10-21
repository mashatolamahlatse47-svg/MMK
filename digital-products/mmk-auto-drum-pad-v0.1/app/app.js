"use strict";

const sounds = [
  {name:"KICK",desc:"Deep drum",type:"kick"},
  {name:"SNARE",desc:"Backbeat",type:"snare"},
  {name:"CLOSED HAT",desc:"Tight rhythm",type:"hat"},
  {name:"OPEN HAT",desc:"Airy cymbal",type:"openhat"},
  {name:"CLAP",desc:"Sharp accent",type:"clap"},
  {name:"DEEP BASS",desc:"Low end",type:"bass"},
  {name:"PIANO",desc:"Story melody",type:"piano"},
  {name:"STRINGS",desc:"Emotional tone",type:"strings"},
  {name:"FX",desc:"Atmosphere",type:"fx"}
];

const $ = id => document.getElementById(id);
let audio = null, master = null, playing = false, timer = null;
let recordingDestination = null, recorder = null, recordedChunks = [];
let step = 0, activeLoops = new Set();
let pattern = sounds.map(() => Array(16).fill(false));
const loopTimers = new Map();

function audioReady(){
  if(!audio){
    audio = new (window.AudioContext || window.webkitAudioContext)();
    master = audio.createGain();
    master.gain.value = Number($("volume").value)/100;
    master.connect(audio.destination);
    recordingDestination = audio.createMediaStreamDestination();
    master.connect(recordingDestination);
  }
  if(audio.state === "suspended") audio.resume();
}

function tone(freq, duration, wave="sine", gain=.2, endFreq=null, when=null){
  audioReady();
  const t = when ?? audio.currentTime;
  const osc = audio.createOscillator(), amp = audio.createGain();
  osc.type = wave;
  osc.frequency.setValueAtTime(freq,t);
  if(endFreq) osc.frequency.exponentialRampToValueAtTime(Math.max(1,endFreq),t+duration);
  amp.gain.setValueAtTime(.0001,t);
  amp.gain.exponentialRampToValueAtTime(Math.max(.0002,gain),t+.008);
  amp.gain.exponentialRampToValueAtTime(.0001,t+duration);
  osc.connect(amp); amp.connect(master);
  osc.start(t); osc.stop(t+duration+.02);
}

function noise(duration,gain,filterFreq){
  audioReady();
  const length=Math.max(1,Math.floor(audio.sampleRate*duration));
  const buffer=audio.createBuffer(1,length,audio.sampleRate);
  const data=buffer.getChannelData(0);
  for(let i=0;i<length;i++) data[i]=Math.random()*2-1;
  const source=audio.createBufferSource(), filter=audio.createBiquadFilter(), amp=audio.createGain();
  source.buffer=buffer; filter.type="highpass"; filter.frequency.value=filterFreq;
  const t=audio.currentTime;
  amp.gain.setValueAtTime(gain,t);
  amp.gain.exponentialRampToValueAtTime(.0001,t+duration);
  source.connect(filter); filter.connect(amp); amp.connect(master);
  source.start(t);
}

function hit(type){
  switch(type){
    case "kick": tone(150,.38,"sine",.9,42); break;
    case "snare": noise(.19,.48,900); tone(190,.12,"triangle",.22,100); break;
    case "hat": noise(.055,.20,6500); break;
    case "openhat": noise(.32,.20,5000); break;
    case "clap":
      noise(.08,.45,1200);
      setTimeout(()=>{if(audio) noise(.07,.24,1200)},45);
      break;
    case "bass": tone(75,.48,"sawtooth",.38,48); break;
    case "piano":
      tone(261.63,.65,"triangle",.22);
      tone(329.63,.55,"sine",.13);
      tone(392,.7,"triangle",.13);
      break;
    case "strings":
      tone(220,1.1,"sawtooth",.10);
      tone(261.63,1.1,"triangle",.09);
      tone(329.63,1.1,"sine",.08);
      break;
    case "fx":
      tone(520,.6,"sine",.2,180);
      noise(.24,.09,1800);
      break;
  }
}

function renderPads(){
  $("pads").innerHTML="";
  sounds.forEach((s,i)=>{
    const b=document.createElement("button");
    b.className="pad"; b.id="pad"+i;
    b.innerHTML=`<strong>${s.name}</strong><small>${s.desc}</small>`;
    b.addEventListener("click",()=>{
      audioReady();
      if(activeLoops.has(i)){stopLoop(i);return}
      activeLoops.add(i); b.classList.add("active");
      hit(s.type);
      const ms=60000/tempo();
      loopTimers.set(i,setInterval(()=>{if(activeLoops.has(i))hit(s.type)},ms));
    });
    $("pads").appendChild(b);
  });
}
function tempo(){
  const n=Number($("bpm").value);
  return Math.min(180,Math.max(50,Number.isFinite(n)?n:90));
}
function stopLoop(i){
  activeLoops.delete(i);
  clearInterval(loopTimers.get(i));
  loopTimers.delete(i);
  $("pad"+i)?.classList.remove("active");
}
function stopAll(){
  playing=false; clearInterval(timer); timer=null;
  [...activeLoops].forEach(stopLoop);
  $("start").textContent="▶ PLAY PATTERN";
  document.querySelectorAll(".step").forEach(b=>b.classList.remove("current"));
}
function renderGrid(){
  $("sequencer").innerHTML="";
  sounds.forEach((s,r)=>{
    const row=document.createElement("div");row.className="seqrow";
    const label=document.createElement("div");label.className="rowname";label.textContent=s.name;
    row.appendChild(label);
    for(let c=0;c<16;c++){
      const b=document.createElement("button");b.className="step";
      if(pattern[r][c])b.classList.add("on");
      if(c%4===0)b.classList.add("beat");
      b.setAttribute("aria-label",`${s.name}, step ${c+1}`);
      b.addEventListener("click",()=>{
        pattern[r][c]=!pattern[r][c];b.classList.toggle("on",pattern[r][c]);
      });
      row.appendChild(b);
    }
    $("sequencer").appendChild(row);
  });
}
function tick(){
  const buttons=document.querySelectorAll(".step");
  buttons.forEach(b=>b.classList.remove("current"));
  sounds.forEach((s,r)=>{
    if(pattern[r][step])hit(s.type);
    const b=$("sequencer").children[r]?.children[step+1];
    if(b)b.classList.add("current");
  });
  step=(step+1)%16;
}
function startPattern(){
  audioReady();
  if(playing)return;
  playing=true;step=0;
  $("start").textContent="▶ PLAYING";
  tick();
  timer=setInterval(tick,60000/tempo()/4);
}
$("start").addEventListener("click",startPattern);
$("stop").addEventListener("click",stopAll);
$("volume").addEventListener("input",()=>{
  if(master)master.gain.value=Number($("volume").value)/100;
});
$("bpm").addEventListener("change",()=>{
  $("bpm").value=tempo();
  if(playing){clearInterval(timer);timer=setInterval(tick,60000/tempo()/4)}
  // Refresh active loop rates when tempo changes.
  [...activeLoops].forEach(i=>{
    clearInterval(loopTimers.get(i));
    loopTimers.set(i,setInterval(()=>hit(sounds[i].type),60000/tempo()));
  });
});
$("clear").addEventListener("click",()=>{
  pattern=sounds.map(()=>Array(16).fill(false));renderGrid();
  $("status").textContent="Pattern cleared.";
});
$("save").addEventListener("click",()=>{
  try{
    localStorage.setItem("mmkAutoDrumPadPattern",JSON.stringify({bpm:tempo(),pattern}));
    $("status").textContent="Pattern saved on this device.";
  }catch(e){$("status").textContent="Save failed: browser storage is unavailable."}
});
$("load").addEventListener("click",()=>{
  try{
    const data=JSON.parse(localStorage.getItem("mmkAutoDrumPadPattern"));
    if(!data||!Array.isArray(data.pattern)||data.pattern.length!==sounds.length)throw Error();
    pattern=data.pattern.map(row=>Array.from({length:16},(_,i)=>Boolean(row[i])));
    $("bpm").value=Number(data.bpm)||90;renderGrid();
    $("status").textContent="Saved pattern loaded.";
  }catch(e){$("status").textContent="No valid saved pattern found yet."}
});

function pcmWav(buffer){
  const channels=buffer.numberOfChannels, frames=buffer.length;
  const bytes= new ArrayBuffer(44+frames*channels*2), view=new DataView(bytes);
  const write=(o,s)=>{for(let i=0;i<s.length;i++)view.setUint8(o+i,s.charCodeAt(i))};
  write(0,"RIFF");view.setUint32(4,36+frames*channels*2,true);
  write(8,"WAVE");write(12,"fmt ");view.setUint32(16,16,true);
  view.setUint16(20,1,true);view.setUint16(22,channels,true);
  view.setUint32(24,buffer.sampleRate,true);
  view.setUint32(28,buffer.sampleRate*channels*2,true);
  view.setUint16(32,channels*2,true);view.setUint16(34,16,true);
  write(36,"data");view.setUint32(40,frames*channels*2,true);
  let offset=44;
  for(let i=0;i<frames;i++)for(let c=0;c<channels;c++){
    const sample=Math.max(-1,Math.min(1,buffer.getChannelData(c)[i]));
    view.setInt16(offset,sample<0?sample*32768:sample*32767,true);offset+=2;
  }
  return new Blob([bytes],{type:"audio/wav"});
}
async function exportWav(){
  const btn=$("export");btn.disabled=true;
  $("status").textContent="Rendering your beat...";
  try{
    const bpm=tempo(), sr=44100, duration=16*60000/bpm/1000/4;
    const offline=new OfflineAudioContext(2,Math.ceil(sr*duration),sr);
    const out=offline.createGain();out.gain.value=Number($("volume").value)/100;out.connect(offline.destination);
    // Reuse the same sound recipes in a temporary live-style render by rendering
    // the pattern with oscillator and noise voices directly into the offline output.
    function osc(freq,dur,wave,gain,end,when){
      const o=offline.createOscillator(),g=offline.createGain();
      o.type=wave;o.frequency.setValueAtTime(freq,when);
      if(end)o.frequency.exponentialRampToValueAtTime(Math.max(1,end),when+dur);
      g.gain.setValueAtTime(.0001,when);g.gain.exponentialRampToValueAtTime(gain,when+.008);
      g.gain.exponentialRampToValueAtTime(.0001,when+dur);
      o.connect(g);g.connect(out);o.start(when);o.stop(when+dur+.02);
    }
    function hiss(dur,gain,freq,when){
      const n=Math.floor(sr*dur),b=offline.createBuffer(1,n,sr),d=b.getChannelData(0);
      for(let i=0;i<n;i++)d[i]=Math.random()*2-1;
      const src=offline.createBufferSource(),f=offline.createBiquadFilter(),g=offline.createGain();
      src.buffer=b;f.type="highpass";f.frequency.value=freq;g.gain.setValueAtTime(gain,when);
      g.gain.exponentialRampToValueAtTime(.0001,when+dur);
      src.connect(f);f.connect(g);g.connect(out);src.start(when);
    }
    function voice(type,t){
      switch(type){
        case "kick":osc(150,.38,"sine",.9,42,t);break;
        case "snare":hiss(.19,.48,900,t);osc(190,.12,"triangle",.22,100,t);break;
        case "hat":hiss(.055,.20,6500,t);break;
        case "openhat":hiss(.32,.20,5000,t);break;
        case "clap":hiss(.08,.45,1200,t);hiss(.07,.24,1200,t+.045);break;
        case "bass":osc(75,.48,"sawtooth",.38,48,t);break;
        case "piano":osc(261.63,.65,"triangle",.22,null,t);osc(329.63,.55,"sine",.13,null,t);osc(392,.7,"triangle",.13,null,t);break;
        case "strings":osc(220,1.1,"sawtooth",.10,null,t);osc(261.63,1.1,"triangle",.09,null,t);osc(329.63,1.1,"sine",.08,null,t);break;
        case "fx":osc(520,.6,"sine",.2,180,t);hiss(.24,.09,1800,t);break;
      }
    }
    const beat=60/bpm/4;
    pattern.forEach((row,r)=>row.forEach((on,c)=>{if(on)voice(sounds[r].type,c*beat)}));
    const rendered=await offline.startRendering();
    const blob=pcmWav(rendered),url=URL.createObjectURL(blob),a=document.createElement("a");
    a.href=url;a.download="MMK-beat-"+Date.now()+".wav";a.click();
    setTimeout(()=>URL.revokeObjectURL(url),5000);
    $("status").textContent="WAV exported. Check your Downloads.";
  }catch(e){$("status").textContent="Export failed. Try a shorter pattern or reload the page."}
  finally{btn.disabled=false}
}
$("export").addEventListener("click",exportWav);

function startRecording(){
  audioReady();

  if(!window.MediaRecorder || !recordingDestination){
    alert("Live recording is not supported by this browser.");
    return;
  }

  try {
    const preferred = "audio/webm;codecs=opus";
    const mimeType = MediaRecorder.isTypeSupported(preferred)
      ? preferred
      : (MediaRecorder.isTypeSupported("audio/webm") ? "audio/webm" : "");

    recorder = mimeType
      ? new MediaRecorder(recordingDestination.stream, {mimeType})
      : new MediaRecorder(recordingDestination.stream);

    recordedChunks = [];

    recorder.ondataavailable = event => {
      if(event.data && event.data.size > 0) recordedChunks.push(event.data);
    };

    recorder.onstop = () => {
      if(recordedChunks.length){
        const blob = new Blob(recordedChunks, {
          type: recorder.mimeType || "audio/webm"
        });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "MMK-live-recording-" +
          new Date().toISOString().replace(/[:.]/g, "-") + ".webm";
        document.body.appendChild(link);
        link.click();
        link.remove();
        setTimeout(() => URL.revokeObjectURL(url), 2000);
      } else {
        alert("No audio data was captured. Please try again.");
      }

      $("record").disabled = false;
      $("stopRecording").disabled = true;
      $("record").textContent = "● START RECORDING";
    };

    recorder.start();
    $("record").disabled = true;
    $("stopRecording").disabled = false;
    $("record").textContent = "● RECORDING...";
  } catch(error) {
    console.error(error);
    alert("Recording could not start. Please check browser support.");
    $("record").disabled = false;
    $("stopRecording").disabled = true;
  }
}

function stopRecording(){
  if(recorder && recorder.state !== "inactive"){
    recorder.stop();
  }
}

$("record").addEventListener("click", startRecording);
$("stopRecording").addEventListener("click", stopRecording);

renderPads();renderGrid();
