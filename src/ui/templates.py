"""
templates.py
------------
Contains the full HTML/CSS/JS for the browser dock UI.

The UI features a pitch black & white monotonous theme with vibrant,
color-coded squarish chips for state indication and clean SVG icons.
"""


def get_dock_html(http_port):
    """Return the complete HTML page for the browser dock."""
    return _DOCK_HTML.replace("{{HTTP_PORT}}", str(http_port))


_DOCK_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Per-Scene Audio</title>
<style>
/* ================================================================
   Pitch Black & White Monotonous Theme + Vibrant State Chips
   ================================================================ */
:root {
  --bg-root:       #000000;
  --bg-card:       #0a0a0a;
  --bg-elevated:   #141414;
  --bg-hover:      #222222;
  --border-dark:   #1a1a1a;
  --border-mid:    #2a2a2a;
  --border-light:  #404040;
  
  --text-main:     #ffffff;
  --text-muted:    #888888;
  --text-dim:      #555555;
  
  /* Vibrant squarish chips */
  --chip-active-bg:   #00e676;
  --chip-active-fg:   #000000;
  
  --chip-muted-bg:    #ff1744;
  --chip-muted-fg:    #ffffff;
  
  --chip-auto-bg:     #ff9100;
  --chip-auto-fg:     #000000;
  
  --chip-live-bg:     #10b981;
  
  --chip-vol-bg:      #29b6f6;
  --chip-vol-fg:      #000000;

  --radius-chip:      2px;
  --radius-btn:       3px;
  --font:             -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

html, body {
  background: var(--bg-root);
  color: var(--text-main);
  font-family: var(--font);
  font-size: 12px;
  line-height: 1.4;
  overflow-x: hidden;
  user-select: none;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg-root); }
::-webkit-scrollbar-thumb { background: var(--border-light); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ================================================================
   Layout
   ================================================================ */
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 6px;
  gap: 6px;
  background: var(--bg-root);
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 6px;
  border-radius: var(--radius-chip);
  font-size: 9.5px;
  font-weight: 800;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  white-space: nowrap;
}
.chip-active {
  background: var(--chip-active-bg);
  color: var(--chip-active-fg);
}
.chip-muted {
  background: var(--chip-muted-bg);
  color: var(--chip-muted-fg);
}
.chip-auto {
  background: var(--chip-auto-bg);
  color: var(--chip-auto-fg);
}
.chip-vol {
  background: var(--chip-vol-bg);
  color: var(--chip-vol-fg);
}

/* -- Scene Tabs -- */
.scene-tabs-wrapper {
  flex-shrink: 0;
  border-bottom: 1px solid var(--border-mid);
  padding-bottom: 4px;
}
.scene-tabs {
  display: flex;
  gap: 4px;
  overflow-x: auto;
  padding-bottom: 2px;
}
.scene-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-dark);
  border-radius: var(--radius-btn);
  color: var(--text-muted);
  cursor: pointer;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
  transition: all 0.15s ease;
}
.scene-tab:hover {
  background: var(--bg-hover);
  color: var(--text-main);
  border-color: var(--border-light);
}
.scene-tab.selected {
  background: #ffffff;
  color: #000000;
  border-color: #ffffff;
  font-weight: 700;
}
.tab-live-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--chip-live-bg);
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.8);
  flex-shrink: 0;
}

/* -- Track List -- */
.track-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-right: 2px;
}

.track-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  background: var(--bg-card);
  border: 1px solid var(--border-dark);
  border-radius: var(--radius-btn);
  transition: background 0.15s ease, border-color 0.15s ease;
}
.track-row:hover {
  background: var(--bg-elevated);
  border-color: var(--border-mid);
}

.track-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.track-name {
  font-size: 11.5px;
  font-weight: 600;
  color: var(--text-main);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Controls inside row */
.track-controls {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

/* Volume Slider */
.vol-wrap {
  display: flex;
  align-items: center;
  gap: 4px;
  background: var(--bg-elevated);
  padding: 0 6px;
  height: 26px;
  border: 1px solid var(--border-dark);
  border-radius: var(--radius-btn);
  box-sizing: border-box;
}
.vol-icon {
  display: flex;
  align-items: center;
  color: var(--text-muted);
}
.vol-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 65px;
  height: 3px;
  border-radius: 1px;
  background: var(--border-light);
  outline: none;
  cursor: pointer;
}
.vol-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 10px;
  height: 10px;
  border-radius: 1px;
  background: #ffffff;
  cursor: pointer;
  border: none;
  transition: transform 0.1s ease;
}
.vol-slider::-webkit-slider-thumb:hover {
  transform: scale(1.25);
}
.vol-value {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-main);
  width: 48px;
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
  overflow: hidden;
  line-height: 1;
}

/* Mute Toggle Button */
.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: var(--radius-btn);
  border: 1px solid var(--border-mid);
  background: var(--bg-elevated);
  color: var(--text-main);
  cursor: pointer;
  transition: all 0.15s ease;
}
.icon-btn:hover {
  background: var(--bg-hover);
  border-color: var(--border-light);
}
.icon-btn.btn-active-toggle {
  background: var(--chip-active-bg);
  color: var(--chip-active-fg);
  border-color: var(--chip-active-bg);
}
.icon-btn.btn-muted-toggle {
  background: var(--chip-muted-bg);
  color: var(--chip-muted-fg);
  border-color: var(--chip-muted-bg);
}

/* -- Footer Actions -- */
.actions-bar {
  display: flex;
  gap: 5px;
  flex-shrink: 0;
  padding-top: 4px;
  border-top: 1px solid var(--border-mid);
}

.action-btn {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 6px 8px;
  border-radius: var(--radius-btn);
  border: 1px solid var(--border-mid);
  background: var(--bg-elevated);
  color: var(--text-main);
  cursor: pointer;
  font-size: 11px;
  font-weight: 600;
  transition: all 0.15s ease;
}
.action-btn:hover {
  background: #ffffff;
  color: #000000;
  border-color: #ffffff;
}
.action-btn.danger-action:hover {
  background: var(--chip-muted-bg);
  color: #ffffff;
  border-color: var(--chip-muted-bg);
}

/* -- Empty State -- */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  gap: 8px;
  font-size: 11.5px;
}

/* -- Toast -- */
.toast {
  position: fixed;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%) translateY(50px);
  background: #ffffff;
  color: #000000;
  font-weight: 700;
  padding: 5px 12px;
  border-radius: var(--radius-chip);
  font-size: 10.5px;
  opacity: 0;
  transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  pointer-events: none;
  z-index: 100;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(0,0,0,0.5);
}
.toast.show {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}
</style>
</head>
<body>
<div class="app">
  <!-- Scene Navigation Tabs -->
  <div class="scene-tabs-wrapper">
    <div class="scene-tabs" id="sceneTabs"></div>
  </div>

  <!-- Audio Tracks List -->
  <div class="track-list" id="trackList">
    <div class="empty-state">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="opacity:0.4"><path d="M11 5L6 9H2V15H6L11 19V5Z"/><line x1="23" y1="9" x2="17" y2="15"/><line x1="17" y1="9" x2="23" y2="15"/></svg>
      <span>Select a scene to configure audio tracks</span>
    </div>
  </div>

  <!-- Footer Actions (Apply, Refresh, Clear) -->
  <div class="actions-bar">
    <button class="action-btn" onclick="applyNow()" title="Force re-apply audio rules for active scene">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
      Apply Now
    </button>
    <button class="action-btn" onclick="refreshData()" title="Refresh scenes & tracks from OBS">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/></svg>
      Refresh
    </button>
    <button class="action-btn danger-action" onclick="clearSceneRules()" title="Wipe rules for currently selected scene">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
      Clear Scene
    </button>
  </div>
</div>

<!-- Toast -->
<div class="toast" id="toast"></div>

<script>
/* ================================================================
   Application Logic
   ================================================================ */
const API = "http://127.0.0.1:{{HTTP_PORT}}/api";

let scenes = [];
let audioTracks = [];
let rules = {};
let selectedScene = null;
let currentScene = null;

// SVG Icons
const SVG_UNMUTED = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>`;
const SVG_MUTED = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="23" y1="9" x2="17" y2="15"></line><line x1="17" y1="9" x2="23" y2="15"></line></svg>`;

document.addEventListener("DOMContentLoaded", () => {
  refreshData();
  setInterval(pollCurrentScene, 1500);
});

async function refreshData() {
  try {
    const [stateRes, rulesRes] = await Promise.all([
      fetch(API + "/state"),
      fetch(API + "/rules"),
    ]);
    const state = await stateRes.json();
    const rulesData = await rulesRes.json();

    scenes = state.scenes || [];
    audioTracks = state.audio_tracks || [];
    currentScene = state.current_scene;
    rules = rulesData.rules || {};

    if (!selectedScene || !scenes.includes(selectedScene)) {
      selectedScene = currentScene;
    }

    renderSceneTabs();
    renderTrackList();
  } catch (e) {
    console.error("refreshData error:", e);
  }
}

async function pollCurrentScene() {
  try {
    const res = await fetch(API + "/state");
    const state = await res.json();
    if (state.current_scene !== currentScene) {
      currentScene = state.current_scene;
      renderSceneTabs();
    }
  } catch (_) {}
}

function renderSceneTabs() {
  const container = document.getElementById("sceneTabs");
  container.innerHTML = "";
  scenes.forEach(name => {
    const tab = document.createElement("div");
    const isSelected = name === selectedScene;
    const isLive = name === currentScene;

    tab.className = "scene-tab" + (isSelected ? " selected" : "");
    
    if (isLive) {
      const dot = document.createElement("span");
      dot.className = "tab-live-dot";
      dot.title = "Live in OBS";
      tab.appendChild(dot);
    }

    const titleSpan = document.createElement("span");
    titleSpan.textContent = name;
    tab.appendChild(titleSpan);

    tab.onclick = () => {
      selectedScene = name;
      renderSceneTabs();
      renderTrackList();
    };
    container.appendChild(tab);
  });
}

function renderTrackList() {
  const container = document.getElementById("trackList");
  if (!selectedScene || audioTracks.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="opacity:0.4"><path d="M11 5L6 9H2V15H6L11 19V5Z"/><line x1="23" y1="9" x2="17" y2="15"/><line x1="17" y1="9" x2="23" y2="15"/></svg>
        <span>No audio tracks or scene selected</span>
      </div>`;
    return;
  }

  const sceneRules = rules[selectedScene] || {};
  container.innerHTML = "";

  audioTracks.forEach(track => {
    const entry = sceneRules[track];
    const hasRule = !!entry;
    const isMuted = hasRule ? entry.mute : true;
    const volDb = (entry && entry.volume_db !== undefined) ? entry.volume_db : null;

    const row = document.createElement("div");
    row.className = "track-row";

    // Track info with vibrant status chip
    const info = document.createElement("div");
    info.className = "track-info";

    const nameEl = document.createElement("span");
    nameEl.className = "track-name";
    nameEl.textContent = track;
    info.appendChild(nameEl);

    // State chip
    const chip = document.createElement("span");
    if (!hasRule) {
      chip.className = "chip chip-auto";
      chip.textContent = "AUTO-MUTE";
    } else if (isMuted) {
      chip.className = "chip chip-muted";
      chip.textContent = "MUTED";
    } else {
      chip.className = "chip chip-active";
      chip.textContent = "ACTIVE";
    }
    info.appendChild(chip);

    row.appendChild(info);

    // Controls
    const controls = document.createElement("div");
    controls.className = "track-controls";

    // Volume Slider & Label
    const volWrap = document.createElement("div");
    volWrap.className = "vol-wrap";

    const volIcon = document.createElement("span");
    volIcon.className = "vol-icon";
    volIcon.innerHTML = `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon></svg>`;
    volWrap.appendChild(volIcon);

    const slider = document.createElement("input");
    slider.type = "range";
    slider.className = "vol-slider";
    slider.min = -60;
    slider.max = 0;
    slider.step = 0.5;
    slider.value = volDb !== null ? volDb : 0;

    const volVal = document.createElement("span");
    volVal.className = "vol-value";
    volVal.textContent = (volDb !== null ? volDb.toFixed(1) : "0.0") + " dB";

    slider.oninput = () => {
      volVal.textContent = parseFloat(slider.value).toFixed(1) + " dB";
    };
    slider.onchange = () => {
      setRule(selectedScene, track, !isMuted, parseFloat(slider.value));
    };

    volWrap.appendChild(slider);
    volWrap.appendChild(volVal);
    controls.appendChild(volWrap);

    // Mute/Unmute Toggle Button
    const muteBtn = document.createElement("button");
    muteBtn.className = "icon-btn " + (isMuted ? "btn-muted-toggle" : "btn-active-toggle");
    muteBtn.innerHTML = isMuted ? SVG_MUTED : SVG_UNMUTED;
    muteBtn.title = isMuted ? "Click to set ACTIVE" : "Click to set MUTED";
    muteBtn.onclick = () => {
      const newMuted = !isMuted;
      const vol = volDb !== null ? volDb : (parseFloat(slider.value) || null);
      setRule(selectedScene, track, !newMuted, vol);
    };
    controls.appendChild(muteBtn);

    row.appendChild(controls);
    container.appendChild(row);
  });
}

async function setRule(scene, track, active, volumeDb) {
  try {
    const body = { scene, track, active };
    if (volumeDb !== null && volumeDb !== undefined) {
      body.volume_db = volumeDb;
    }
    await fetch(API + "/rule", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const rulesRes = await fetch(API + "/rules");
    const rulesData = await rulesRes.json();
    rules = rulesData.rules || {};
    renderTrackList();
    toast(active ? track + " → ACTIVE" : track + " → MUTED");
  } catch (e) {
    toast("Error saving rule");
  }
}

async function applyNow() {
  try {
    await fetch(API + "/apply", { method: "POST" });
    toast("Applied rules for " + (currentScene || "scene"));
  } catch (e) {
    toast("Apply failed");
  }
}

async function clearSceneRules() {
  if (!selectedScene) return;
  if (!confirm("Clear all rules for scene '" + selectedScene + "'?")) return;
  try {
    await fetch(API + "/clear_scene", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scene: selectedScene }),
    });
    const rulesRes = await fetch(API + "/rules");
    const rulesData = await rulesRes.json();
    rules = rulesData.rules || {};
    renderTrackList();
    toast("Cleared rules for " + selectedScene);
  } catch (e) {
    toast("Clear failed");
  }
}

let toastTimer = null;
function toast(msg) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove("show"), 1800);
}
</script>
</body>
</html>"""
