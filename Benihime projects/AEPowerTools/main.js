/* AE PowerTools — Main JS (CSInterface bridge + UI logic) */
var csInterface = new CSInterface();

/* ─── Status Bar ─────────────────────── */
function setStatus(msg, type) {
    var el = document.getElementById("status-text");
    el.textContent = msg;
    el.className = type || "";
}

function handleResult(raw) {
    try {
        var r = (typeof raw === "string") ? JSON.parse(raw) : raw;
        setStatus(r.message, r.success ? "success" : "error");
        return r;
    } catch (e) {
        setStatus("Script error: " + raw, "error");
        return null;
    }
}

/* ─── Tab Switching ──────────────────── */
document.querySelectorAll(".tab-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
        document.querySelectorAll(".tab-btn").forEach(function (b) { b.classList.remove("active"); });
        document.querySelectorAll(".tab-content").forEach(function (c) { c.classList.remove("active"); });
        btn.classList.add("active");
        document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
    });
});

/* ═══════════════════════════════════════
   TAB 1 — LAYER TOOLS
   ═══════════════════════════════════════ */

function selectLayersByType(type) {
    csInterface.evalScript('selectLayersByType("' + type + '")', handleResult);
}

function renameLayers(mode) {
    var prefix = document.getElementById("rename-prefix").value;
    var suffix = document.getElementById("rename-suffix").value;
    var find = document.getElementById("rename-find").value;
    var replace = document.getElementById("rename-replace").value;
    var args = 'renameLayers("' + mode + '","' + escStr(prefix) + '","' + escStr(suffix) + '","' + escStr(find) + '","' + escStr(replace) + '")';
    csInterface.evalScript(args, handleResult);
}

function soloSelectedLayers() {
    csInterface.evalScript("soloSelectedLayers()", handleResult);
}

function lockAllLayers(lock) {
    csInterface.evalScript("lockAllLayers(" + lock + ")", handleResult);
}

function deleteDisabledLayers() {
    csInterface.evalScript("deleteDisabledLayers()", handleResult);
}

function centerAnchorPoint() {
    csInterface.evalScript("centerAnchorPoint()", handleResult);
}

function setBlendMode() {
    var mode = document.getElementById("blend-mode-select").value;
    csInterface.evalScript('setBlendMode(' + mode + ')', handleResult);
}

function duplicateWithOffset() {
    var x = parseFloat(document.getElementById("dup-offset-x").value) || 0;
    var y = parseFloat(document.getElementById("dup-offset-y").value) || 0;
    var t = parseFloat(document.getElementById("dup-offset-t").value) || 0;
    var n = parseInt(document.getElementById("dup-count").value) || 1;
    csInterface.evalScript('duplicateWithOffset(' + x + ',' + y + ',' + t + ',' + n + ')', handleResult);
}

/* ═══════════════════════════════════════
   TAB 2 — KEYFRAME TOOLS
   ═══════════════════════════════════════ */

function copyKeyframeTiming() {
    csInterface.evalScript("copyKeyframeTiming()", handleResult);
}

function reverseKeyframes() {
    csInterface.evalScript("reverseKeyframes()", handleResult);
}

function easeKeyframes(type) {
    csInterface.evalScript('easeKeyframes("' + type + '")', handleResult);
}

function snapKeyframesToFrame() {
    csInterface.evalScript("snapKeyframesToFrame()", handleResult);
}

function offsetKeyframes() {
    var frames = parseInt(document.getElementById("key-offset-frames").value) || 0;
    csInterface.evalScript("offsetKeyframes(" + frames + ")", handleResult);
}

function convertToHoldKeyframes() {
    csInterface.evalScript("convertToHoldKeyframes()", handleResult);
}

function deleteAllKeyframes() {
    csInterface.evalScript("deleteAllKeyframes()", handleResult);
}

/* ═══════════════════════════════════════
   TAB 3 — COMPOSITION TOOLS
   ═══════════════════════════════════════ */

function createNewComp() {
    var name = document.getElementById("comp-name").value || "New Comp";
    var w = parseInt(document.getElementById("comp-width").value) || 1920;
    var h = parseInt(document.getElementById("comp-height").value) || 1080;
    var fps = parseFloat(document.getElementById("comp-fps").value) || 30;
    var dur = parseFloat(document.getElementById("comp-duration").value) || 10;
    var hex = document.getElementById("comp-bg-color").value;
    var rgb = hexToRgbArray(hex);
    csInterface.evalScript('createNewComp("' + escStr(name) + '",' + w + ',' + h + ',' + fps + ',' + dur + ',[' + rgb + '])', handleResult);
}

function createCompPreset(preset) {
    csInterface.evalScript('createCompPreset("' + preset + '")', handleResult);
}

function trimCompToWorkArea() {
    csInterface.evalScript("trimCompToWorkArea()", handleResult);
}

function duplicateComp() {
    csInterface.evalScript("duplicateComp()", handleResult);
}

function precomposeSelected() {
    csInterface.evalScript("precomposeSelected()", handleResult);
}

function setCompBgColor() {
    var hex = document.getElementById("comp-set-bg").value;
    var rgb = hexToRgbArray(hex);
    csInterface.evalScript("setCompBgColor([" + rgb + "])", handleResult);
}

function scaleComp() {
    var pct = parseFloat(document.getElementById("comp-scale-pct").value) || 100;
    csInterface.evalScript("scaleComp(" + pct + ")", handleResult);
}

/* ═══════════════════════════════════════
   TAB 4 — TEXT TOOLS
   ═══════════════════════════════════════ */

function applyFontToSelected() {
    var font = document.getElementById("text-font").value;
    csInterface.evalScript('applyFontToSelected("' + escStr(font) + '")', handleResult);
}

function setFontSize() {
    var size = parseFloat(document.getElementById("text-size").value) || 48;
    csInterface.evalScript("setFontSize(" + size + ")", handleResult);
}

function setTextColor() {
    var hex = document.getElementById("text-color").value;
    var rgb = hexToRgbArray(hex);
    csInterface.evalScript("setTextColor([" + rgb + "])", handleResult);
}

function findReplaceText() {
    var find = document.getElementById("text-find").value;
    var rep = document.getElementById("text-replace-val").value;
    csInterface.evalScript('findReplaceText("' + escStr(find) + '","' + escStr(rep) + '")', handleResult);
}

function auditTextLayers() {
    csInterface.evalScript("auditTextLayers()", function (raw) {
        var r = handleResult(raw);
        var el = document.getElementById("text-audit-list");
        if (r && r.success && r.data) {
            var html = "";
            for (var i = 0; i < r.data.length; i++) {
                html += '<div class="audit-item"><span class="layer-name">' + escHtml(r.data[i].name) + ':</span> ' + escHtml(r.data[i].text) + '</div>';
            }
            el.innerHTML = html;
            el.classList.add("visible");
        } else {
            el.classList.remove("visible");
        }
    });
}

/* ═══════════════════════════════════════
   TAB 5 — RENDER & EXPORT
   ═══════════════════════════════════════ */

function addToRenderQueue() {
    csInterface.evalScript("addToRenderQueue()", handleResult);
}

function addAllCompsToRQ() {
    csInterface.evalScript("addAllCompsToRQ()", handleResult);
}

function startRenderQueue() {
    csInterface.evalScript("startRenderQueue()", handleResult);
}

function pickOutputFolder() {
    csInterface.evalScript("pickOutputFolder()", function (raw) {
        var r = handleResult(raw);
        if (r && r.success && r.data) {
            document.getElementById("render-output-path").value = r.data;
        }
    });
}

function exportViaAME(preset) {
    var outPath = document.getElementById("render-output-path").value;
    csInterface.evalScript('exportViaAME("' + preset + '","' + escStr(outPath) + '")', handleResult);
}

/* ═══════════════════════════════════════
   TAB 6 — EXPRESSION TOOLS
   ═══════════════════════════════════════ */

function onExprPresetChange() {
    var val = document.getElementById("expr-preset").value;
    var paramIds = ["expr-wiggle-params", "expr-time-params", "expr-random-params", "expr-bounce-params", "expr-posterize-params"];
    paramIds.forEach(function (id) { document.getElementById(id).classList.add("hidden"); });
    var map = { wiggle: "expr-wiggle-params", timeSpeed: "expr-time-params", random: "expr-random-params", bounce: "expr-bounce-params", posterizeTime: "expr-posterize-params" };
    if (map[val]) document.getElementById(map[val]).classList.remove("hidden");
}

function applyExpression() {
    var preset = document.getElementById("expr-preset").value;
    var freq = document.getElementById("expr-freq").value;
    var amp = document.getElementById("expr-amp").value;
    var speedMult = document.getElementById("expr-speed-mult").value;
    var seed = document.getElementById("expr-seed").value;
    var rmin = document.getElementById("expr-min").value;
    var rmax = document.getElementById("expr-max").value;
    var bAmp = document.getElementById("expr-bounce-amp").value;
    var bFreq = document.getElementById("expr-bounce-freq").value;
    var bDecay = document.getElementById("expr-bounce-decay").value;
    var pFps = document.getElementById("expr-poster-fps").value;
    var args = 'applyExpressionPreset("' + preset + '",' + freq + ',' + amp + ',' + speedMult + ',' + seed + ',' + rmin + ',' + rmax + ',' + bAmp + ',' + bFreq + ',' + bDecay + ',' + pFps + ')';
    csInterface.evalScript(args, handleResult);
}

function removeAllExpressions() {
    csInterface.evalScript("removeAllExpressions()", handleResult);
}

function toggleExpressionsInComp(enable) {
    csInterface.evalScript("toggleExpressionsInComp(" + enable + ")", handleResult);
}

function copyPasteExpression() {
    csInterface.evalScript("copyPasteExpression()", handleResult);
}

/* ═══════════════════════════════════════
   TAB 7 — COLOR & EFFECTS
   ═══════════════════════════════════════ */

function addAdjustmentLayer() {
    csInterface.evalScript("addAdjustmentLayer()", handleResult);
}

function applyQuickEffect(effect) {
    csInterface.evalScript('applyQuickEffect("' + effect + '")', handleResult);
}

function copyPasteEffects() {
    csInterface.evalScript("copyPasteEffects()", handleResult);
}

function removeAllEffects() {
    csInterface.evalScript("removeAllEffects()", handleResult);
}

/* ─── Color Palette (localStorage) ──── */
function loadPalette() {
    var swatches = JSON.parse(localStorage.getItem("aept_palette") || "[]");
    renderSwatches(swatches);
}

function renderSwatches(swatches) {
    var el = document.getElementById("palette-swatches");
    el.innerHTML = "";
    swatches.forEach(function (color, i) {
        var s = document.createElement("div");
        s.className = "swatch";
        s.style.background = color;
        s.title = color + " — click to copy hex";
        s.addEventListener("click", function () {
            navigator.clipboard.writeText(color).then(function () {
                setStatus("Copied " + color, "success");
            });
        });
        el.appendChild(s);
    });
}

function saveSwatch() {
    var color = document.getElementById("palette-color-pick").value;
    var swatches = JSON.parse(localStorage.getItem("aept_palette") || "[]");
    if (swatches.length >= 10) {
        setStatus("Palette full (10 max). Clear to add more.", "error");
        return;
    }
    swatches.push(color);
    localStorage.setItem("aept_palette", JSON.stringify(swatches));
    renderSwatches(swatches);
    setStatus("Saved swatch " + color, "success");
}

function clearPalette() {
    localStorage.removeItem("aept_palette");
    renderSwatches([]);
    setStatus("Palette cleared", "success");
}

/* ═══════════════════════════════════════
   TAB 8 — PROJECT TOOLS
   ═══════════════════════════════════════ */

function showProjectInfo() {
    csInterface.evalScript("showProjectInfo()", function (raw) {
        var r = handleResult(raw);
        var el = document.getElementById("project-info-panel");
        if (r && r.success && r.data) {
            var d = r.data;
            el.innerHTML =
                '<div class="info-row"><span class="label">Compositions</span><span class="value">' + d.comps + '</span></div>' +
                '<div class="info-row"><span class="label">Footage Items</span><span class="value">' + d.footage + '</span></div>' +
                '<div class="info-row"><span class="label">Total Items</span><span class="value">' + d.totalItems + '</span></div>' +
                '<div class="info-row"><span class="label">Project File</span><span class="value">' + escHtml(d.filePath || "Unsaved") + '</span></div>';
            el.classList.add("visible");
        }
    });
}

function consolidateFootage() {
    csInterface.evalScript("consolidateFootage()", handleResult);
}

function removeUnusedItems() {
    csInterface.evalScript("removeUnusedItems()", handleResult);
}

function searchProjectItems() {
    var q = document.getElementById("project-search").value;
    csInterface.evalScript('searchProjectItems("' + escStr(q) + '")', function (raw) {
        var r = handleResult(raw);
        var el = document.getElementById("project-search-results");
        if (r && r.success && r.data && r.data.length > 0) {
            var html = "";
            for (var i = 0; i < r.data.length; i++) {
                html += '<div class="audit-item">' + escHtml(r.data[i].name) + ' <span style="color:#666">(' + r.data[i].type + ')</span></div>';
            }
            el.innerHTML = html;
            el.classList.add("visible");
        } else {
            el.innerHTML = '<div class="audit-item">No items found.</div>';
            el.classList.add("visible");
        }
    });
}

function createFolderStructure() {
    csInterface.evalScript("createFolderStructure()", handleResult);
}

/* ─── Utilities ──────────────────────── */
function escStr(s) {
    return s.replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/'/g, "\\'");
}

function escHtml(s) {
    var d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
}

function hexToRgbArray(hex) {
    hex = hex.replace("#", "");
    var r = parseInt(hex.substring(0, 2), 16) / 255;
    var g = parseInt(hex.substring(2, 4), 16) / 255;
    var b = parseInt(hex.substring(4, 6), 16) / 255;
    return [r.toFixed(4), g.toFixed(4), b.toFixed(4)];
}

/* ─── Init: force-reload host.jsx so AE always uses the latest version ─── */
function loadHostScript() {
    var extPath = csInterface.getSystemPath(SystemPath.EXTENSION);
    var jsxPath = extPath + "/host/host.jsx";
    // Normalize path separators for ExtendScript
    jsxPath = jsxPath.replace(/\\/g, "/");
    csInterface.evalScript('$.evalFile("' + jsxPath + '")', function (result) {
        if (result === "EvalScript error." || result === "undefined") {
            setStatus("Warning: host.jsx reload failed — using cached version", "error");
        } else {
            setStatus("AE PowerTools loaded (v1.1)", "success");
        }
    });
}

loadPalette();
loadHostScript();
