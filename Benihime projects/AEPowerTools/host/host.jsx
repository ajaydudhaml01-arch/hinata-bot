/* AE PowerTools — ExtendScript Host (host.jsx)
   All functions return JSON: {"success": bool, "message": "...", "data": ...} */

function jsonOk(msg, data) {
    var o = { success: true, message: msg };
    if (data !== undefined) o.data = data;
    return JSON.stringify(o);
}

function jsonErr(msg) {
    return JSON.stringify({ success: false, message: msg });
}

function getActiveComp() {
    var comp = app.project.activeItem;
    if (!comp || !(comp instanceof CompItem)) return null;
    return comp;
}

function requireComp() {
    var c = getActiveComp();
    if (!c) throw new Error("No active composition");
    return c;
}

function requireSelection() {
    var c = requireComp();
    if (!c.selectedLayers || c.selectedLayers.length === 0) throw new Error("No layers selected");
    return c;
}

/* ═══════════════════════════════════════
   TAB 1 — LAYER TOOLS
   ═══════════════════════════════════════ */

function selectLayersByType(type) {
    try {
        var comp = requireComp();
        var count = 0;
        for (var i = 1; i <= comp.numLayers; i++) {
            var layer = comp.layer(i);
            var match = false;
            if (type === "shape" && layer instanceof ShapeLayer) match = true;
            else if (type === "text" && layer instanceof TextLayer) match = true;
            else if (type === "null" && layer.nullLayer) match = true;
            else if (type === "solid" && layer.source && layer.source.mainSource instanceof SolidSource && !layer.nullLayer && !layer.adjustmentLayer) match = true;
            else if (type === "precomp" && layer.source && layer.source instanceof CompItem) match = true;
            layer.selected = match;
            if (match) count++;
        }
        return jsonOk("Selected " + count + " " + type + " layer(s)");
    } catch (e) { return jsonErr(e.message); }
}

function renameLayers(mode, prefix, suffix, find, replace) {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        app.beginUndoGroup("AE PowerTools: Rename Layers");
        var count = 0;
        for (var i = 0; i < sel.length; i++) {
            var layer = sel[i];
            if (mode === "prefix") {
                layer.name = prefix + layer.name;
            } else if (mode === "suffix") {
                layer.name = layer.name + suffix;
            } else if (mode === "findReplace") {
                var re = new RegExp(find.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "g");
                layer.name = layer.name.replace(re, replace);
            } else if (mode === "autoNumber") {
                var base = layer.name.replace(/\s*\d+$/, "");
                layer.name = base + " " + (i + 1);
            }
            count++;
        }
        app.endUndoGroup();
        return jsonOk("Renamed " + count + " layer(s)");
    } catch (e) { return jsonErr(e.message); }
}

function soloSelectedLayers() {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        app.beginUndoGroup("AE PowerTools: Solo Toggle");
        for (var i = 0; i < sel.length; i++) {
            sel[i].solo = !sel[i].solo;
        }
        app.endUndoGroup();
        return jsonOk("Toggled solo on " + sel.length + " layer(s)");
    } catch (e) { return jsonErr(e.message); }
}

function lockAllLayers(lock) {
    try {
        var comp = requireComp();
        app.beginUndoGroup("AE PowerTools: Lock/Unlock");
        for (var i = 1; i <= comp.numLayers; i++) {
            comp.layer(i).locked = lock;
        }
        app.endUndoGroup();
        return jsonOk((lock ? "Locked" : "Unlocked") + " all " + comp.numLayers + " layer(s)");
    } catch (e) { return jsonErr(e.message); }
}

function deleteDisabledLayers() {
    try {
        var comp = requireComp();
        app.beginUndoGroup("AE PowerTools: Delete Disabled");
        var count = 0;
        for (var i = comp.numLayers; i >= 1; i--) {
            var layer = comp.layer(i);
            if (!layer.enabled) {
                layer.locked = false;
                layer.remove();
                count++;
            }
        }
        app.endUndoGroup();
        return jsonOk("Deleted " + count + " disabled layer(s)");
    } catch (e) { return jsonErr(e.message); }
}

function centerAnchorPoint() {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        app.beginUndoGroup("AE PowerTools: Center Anchor");
        var count = 0;
        for (var i = 0; i < sel.length; i++) {
            var layer = sel[i];
            var rect = layer.sourceRectAtTime(comp.time, false);
            var cx = rect.left + rect.width / 2;
            var cy = rect.top + rect.height / 2;
            var curAnchor = layer.property("ADBE Transform Group").property("ADBE Anchor Point").value;
            var dx = cx - curAnchor[0];
            var dy = cy - curAnchor[1];
            layer.property("ADBE Transform Group").property("ADBE Anchor Point").setValue([cx, cy]);
            var pos = layer.property("ADBE Transform Group").property("ADBE Position").value;
            if (pos.length === 3) {
                layer.property("ADBE Transform Group").property("ADBE Position").setValue([pos[0] + dx, pos[1] + dy, pos[2]]);
            } else {
                layer.property("ADBE Transform Group").property("ADBE Position").setValue([pos[0] + dx, pos[1] + dy]);
            }
            count++;
        }
        app.endUndoGroup();
        return jsonOk("Centered anchor on " + count + " layer(s)");
    } catch (e) { return jsonErr(e.message); }
}

function setBlendMode(modeVal) {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        app.beginUndoGroup("AE PowerTools: Set Blend Mode");
        for (var i = 0; i < sel.length; i++) {
            sel[i].blendingMode = modeVal;
        }
        app.endUndoGroup();
        return jsonOk("Set blend mode on " + sel.length + " layer(s)");
    } catch (e) { return jsonErr(e.message); }
}

function duplicateWithOffset(offX, offY, offT, copies) {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        app.beginUndoGroup("AE PowerTools: Duplicate Offset");
        var totalCreated = 0;
        for (var s = 0; s < sel.length; s++) {
            var srcLayer = sel[s];
            for (var c = 1; c <= copies; c++) {
                var dup = srcLayer.duplicate();
                var pos = dup.property("ADBE Transform Group").property("ADBE Position").value;
                if (pos.length === 3) {
                    dup.property("ADBE Transform Group").property("ADBE Position").setValue([pos[0] + offX * c, pos[1] + offY * c, pos[2]]);
                } else {
                    dup.property("ADBE Transform Group").property("ADBE Position").setValue([pos[0] + offX * c, pos[1] + offY * c]);
                }
                dup.startTime = srcLayer.startTime + offT * c;
                totalCreated++;
            }
        }
        app.endUndoGroup();
        return jsonOk("Created " + totalCreated + " duplicate(s)");
    } catch (e) { return jsonErr(e.message); }
}

/* ═══════════════════════════════════════
   TAB 2 — KEYFRAME TOOLS
   ═══════════════════════════════════════ */

function iterateProperties(propGroup, callback) {
    for (var i = 1; i <= propGroup.numProperties; i++) {
        var prop = propGroup.property(i);
        if (prop.propertyType === PropertyType.PROPERTY) {
            if (prop.numKeys > 0) callback(prop);
        } else if (prop.propertyType === PropertyType.INDEXED_GROUP || prop.propertyType === PropertyType.NAMED_GROUP) {
            iterateProperties(prop, callback);
        }
    }
}

function copyKeyframeTiming() {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        if (sel.length < 2) return jsonErr("Select at least 2 layers (source + targets)");
        app.beginUndoGroup("AE PowerTools: Copy Timing");
        var srcLayer = sel[0];
        var srcTimes = [];
        iterateProperties(srcLayer, function (prop) {
            for (var k = 1; k <= prop.numKeys; k++) {
                srcTimes.push(prop.keyTime(k));
            }
        });
        if (srcTimes.length === 0) return jsonErr("Source layer has no keyframes");
        srcTimes.sort(function (a, b) { return a - b; });
        for (var t = 1; t < sel.length; t++) {
            iterateProperties(sel[t], function (prop) {
                if (prop.numKeys === 0) return;
                var vals = [];
                for (var k = 1; k <= prop.numKeys; k++) vals.push(prop.keyValue(k));
                var timesToUse = srcTimes.slice(0, vals.length);
                while (prop.numKeys > 0) prop.removeKey(1);
                for (var k = 0; k < vals.length; k++) {
                    var ti = k < timesToUse.length ? timesToUse[k] : srcTimes[srcTimes.length - 1];
                    prop.setValueAtTime(ti, vals[k]);
                }
            });
        }
        app.endUndoGroup();
        return jsonOk("Copied timing to " + (sel.length - 1) + " layer(s)");
    } catch (e) { return jsonErr(e.message); }
}

function reverseKeyframes() {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        app.beginUndoGroup("AE PowerTools: Reverse Keyframes");
        var count = 0;
        for (var s = 0; s < sel.length; s++) {
            iterateProperties(sel[s], function (prop) {
                if (prop.numKeys < 2) return;
                var times = [], vals = [], inEases = [], outEases = [], interps = [];
                for (var k = 1; k <= prop.numKeys; k++) {
                    times.push(prop.keyTime(k));
                    vals.push(prop.keyValue(k));
                    inEases.push(prop.keyInTemporalEase(k));
                    outEases.push(prop.keyOutTemporalEase(k));
                    interps.push(prop.keyInInterpolationType(k));
                }
                vals.reverse();
                while (prop.numKeys > 0) prop.removeKey(1);
                for (var k = 0; k < times.length; k++) {
                    prop.setValueAtTime(times[k], vals[k]);
                    try {
                        prop.setTemporalEaseAtKey(k + 1, inEases[k], outEases[k]);
                        prop.setInterpolationTypeAtKey(k + 1, interps[k]);
                    } catch (ignored) {}
                }
                count++;
            });
        }
        app.endUndoGroup();
        return jsonOk("Reversed keyframes on " + count + " propert(ies)");
    } catch (e) { return jsonErr(e.message); }
}

function easeKeyframes(type) {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        app.beginUndoGroup("AE PowerTools: Ease Keyframes");
        var count = 0;
        for (var s = 0; s < sel.length; s++) {
            iterateProperties(sel[s], function (prop) {
                for (var k = 1; k <= prop.numKeys; k++) {
                    if (!prop.keySelected(k)) continue;
                    try {
                        var dims = prop.keyInTemporalEase(k).length;
                        var easeVal = new KeyframeEase(0, 75);
                        var easeArr = [];
                        for (var d = 0; d < dims; d++) easeArr.push(easeVal);
                        if (type === "in") {
                            prop.setTemporalEaseAtKey(k, easeArr);
                        } else if (type === "out") {
                            prop.setTemporalEaseAtKey(k, undefined, easeArr);
                        } else {
                            prop.setTemporalEaseAtKey(k, easeArr, easeArr);
                        }
                        count++;
                    } catch (ignored) {}
                }
            });
        }
        app.endUndoGroup();
        return jsonOk("Eased " + count + " keyframe(s)");
    } catch (e) { return jsonErr(e.message); }
}

function snapKeyframesToFrame() {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        var frameDur = comp.frameDuration;
        app.beginUndoGroup("AE PowerTools: Snap to Frame");
        var count = 0;
        for (var s = 0; s < sel.length; s++) {
            iterateProperties(sel[s], function (prop) {
                for (var k = prop.numKeys; k >= 1; k--) {
                    var t = prop.keyTime(k);
                    var snapped = Math.round(t / frameDur) * frameDur;
                    if (Math.abs(t - snapped) > 0.0001) {
                        var val = prop.keyValue(k);
                        prop.removeKey(k);
                        prop.setValueAtTime(snapped, val);
                        count++;
                    }
                }
            });
        }
        app.endUndoGroup();
        return jsonOk("Snapped " + count + " keyframe(s) to nearest frame");
    } catch (e) { return jsonErr(e.message); }
}

function offsetKeyframes(frames) {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        var offset = frames * comp.frameDuration;
        app.beginUndoGroup("AE PowerTools: Offset Keyframes");
        var count = 0;
        for (var s = 0; s < sel.length; s++) {
            iterateProperties(sel[s], function (prop) {
                var keys = [];
                for (var k = 1; k <= prop.numKeys; k++) {
                    if (prop.keySelected(k)) {
                        keys.push({ time: prop.keyTime(k), value: prop.keyValue(k) });
                    }
                }
                for (var k = prop.numKeys; k >= 1; k--) {
                    if (prop.keySelected(k)) prop.removeKey(k);
                }
                for (var k = 0; k < keys.length; k++) {
                    prop.setValueAtTime(keys[k].time + offset, keys[k].value);
                    count++;
                }
            });
        }
        app.endUndoGroup();
        return jsonOk("Offset " + count + " keyframe(s) by " + frames + " frame(s)");
    } catch (e) { return jsonErr(e.message); }
}

function convertToHoldKeyframes() {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        app.beginUndoGroup("AE PowerTools: Hold Keyframes");
        var count = 0;
        for (var s = 0; s < sel.length; s++) {
            iterateProperties(sel[s], function (prop) {
                for (var k = 1; k <= prop.numKeys; k++) {
                    try {
                        prop.setInterpolationTypeAtKey(k, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.HOLD);
                        count++;
                    } catch (ignored) {}
                }
            });
        }
        app.endUndoGroup();
        return jsonOk("Converted " + count + " keyframe(s) to hold");
    } catch (e) { return jsonErr(e.message); }
}

function deleteAllKeyframes() {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        app.beginUndoGroup("AE PowerTools: Delete Keyframes");
        var count = 0;
        for (var s = 0; s < sel.length; s++) {
            var selProps = sel[s].selectedProperties;
            if (selProps.length > 0) {
                for (var p = 0; p < selProps.length; p++) {
                    var prop = selProps[p];
                    if (prop.propertyType === PropertyType.PROPERTY) {
                        while (prop.numKeys > 0) { prop.removeKey(1); count++; }
                    }
                }
            } else {
                iterateProperties(sel[s], function (prop) {
                    while (prop.numKeys > 0) { prop.removeKey(1); count++; }
                });
            }
        }
        app.endUndoGroup();
        return jsonOk("Deleted " + count + " keyframe(s)");
    } catch (e) { return jsonErr(e.message); }
}

/* ═══════════════════════════════════════
   TAB 3 — COMPOSITION TOOLS
   ═══════════════════════════════════════ */

function createNewComp(name, w, h, fps, dur, bgColor) {
    try {
        app.beginUndoGroup("AE PowerTools: New Comp");
        var comp = app.project.items.addComp(name, w, h, 1, dur, fps);
        comp.bgColor = bgColor;
        comp.openInViewer();
        app.endUndoGroup();
        return jsonOk("Created comp '" + name + "' (" + w + "x" + h + " @ " + fps + "fps)");
    } catch (e) { return jsonErr(e.message); }
}

function createCompPreset(preset) {
    try {
        var presets = {
            "1080p":  { w: 1920, h: 1080, fps: 30, name: "1080p Comp" },
            "4K":     { w: 3840, h: 2160, fps: 30, name: "4K Comp" },
            "reels":  { w: 1080, h: 1920, fps: 30, name: "Reels 9:16" },
            "square": { w: 1080, h: 1080, fps: 30, name: "Square 1:1" },
            "twitter":{ w: 1920, h: 1080, fps: 30, name: "Twitter 16:9" }
        };
        var p = presets[preset];
        if (!p) return jsonErr("Unknown preset: " + preset);
        app.beginUndoGroup("AE PowerTools: Comp Preset");
        var comp = app.project.items.addComp(p.name, p.w, p.h, 1, 10, p.fps);
        comp.bgColor = [0, 0, 0];
        comp.openInViewer();
        app.endUndoGroup();
        return jsonOk("Created '" + p.name + "' (" + p.w + "x" + p.h + ")");
    } catch (e) { return jsonErr(e.message); }
}

function trimCompToWorkArea() {
    try {
        var comp = requireComp();
        app.beginUndoGroup("AE PowerTools: Trim to Work Area");
        comp.duration = comp.workAreaStart + comp.workAreaDuration;
        app.endUndoGroup();
        return jsonOk("Trimmed comp to work area (" + comp.workAreaDuration.toFixed(2) + "s)");
    } catch (e) { return jsonErr(e.message); }
}

function duplicateComp() {
    try {
        var comp = requireComp();
        app.beginUndoGroup("AE PowerTools: Duplicate Comp");
        var dup = comp.duplicate();
        dup.name = comp.name + " Copy";
        dup.openInViewer();
        app.endUndoGroup();
        return jsonOk("Duplicated as '" + dup.name + "'");
    } catch (e) { return jsonErr(e.message); }
}

function precomposeSelected() {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        app.beginUndoGroup("AE PowerTools: Pre-compose");

        var infos = [];
        for (var i = 0; i < sel.length; i++) {
            var layer = sel[i];
            infos.push({
                id: layer.id,
                index: layer.index,
                name: layer.name,
                startTime: layer.startTime,
                inPoint: layer.inPoint,
                outPoint: layer.outPoint
            });
        }
        
        // Sort descending by index — process bottom layers first so
        // precomposing one layer doesn't shift the indices of layers above it
        infos.sort(function (a, b) { return b.index - a.index; });

        // Helper to find a layer by its ID
        function getLayerById(c, id) {
            for (var k = 1; k <= c.numLayers; k++) {
                if (c.layer(k).id === id) return c.layer(k);
            }
            return null;
        }

        var count = 0;
        var failed = 0;
        var firstError = "";

        for (var i = 0; i < infos.length; i++) {
            var info = infos[i];
            try {
                var layer = getLayerById(comp, info.id);
                if (!layer) continue;

                var visibleDuration = info.outPoint - info.inPoint;
                if (visibleDuration <= 0) visibleDuration = comp.frameDuration;

                var precompName = info.name + "_comp";

                // Precompose this single layer individually
                var precompLayer = comp.layers.precompose([layer.index], precompName, true);
                var precompItem = precompLayer.source;

                // Trim the precomp comp duration and set work area
                if (precompItem) {
                    precompItem.duration = visibleDuration;
                    precompItem.workAreaStart = 0;
                    precompItem.workAreaDuration = visibleDuration;
                }

                // Restore/correct outPoint fallback
                try {
                    precompLayer.outPoint = info.outPoint;
                } catch (outErr) {
                    if (precompItem) {
                        precompLayer.outPoint = precompLayer.startTime + precompItem.duration;
                    }
                }
                
                // Keep the new precomp layer selected
                precompLayer.selected = true;

                count++;
            } catch (layerErr) {
                failed++;
                if (!firstError) firstError = layerErr.message;
            }
        }

        app.endUndoGroup();

        if (count === 0 && failed > 0) {
            return jsonErr("Failed to precompose layer(s): " + firstError);
        }

        return jsonOk(count + " layers precomped");
    } catch (e) { return jsonErr(e.message); }
}

function precompSelectedLayers() {
    return precomposeSelected();
}

function setCompBgColor(rgb) {
    try {
        var comp = requireComp();
        app.beginUndoGroup("AE PowerTools: Set BG Color");
        comp.bgColor = rgb;
        app.endUndoGroup();
        return jsonOk("Background color updated");
    } catch (e) { return jsonErr(e.message); }
}

function scaleComp(pct) {
    try {
        var comp = requireComp();
        var factor = pct / 100;
        var newW = Math.round(comp.width * factor);
        var newH = Math.round(comp.height * factor);
        app.beginUndoGroup("AE PowerTools: Scale Comp");
        comp.width = newW;
        comp.height = newH;
        for (var i = 1; i <= comp.numLayers; i++) {
            var layer = comp.layer(i);
            var s = layer.property("ADBE Transform Group").property("ADBE Scale").value;
            layer.property("ADBE Transform Group").property("ADBE Scale").setValue([s[0] * factor, s[1] * factor, s.length > 2 ? s[2] : 100]);
            var p = layer.property("ADBE Transform Group").property("ADBE Position").value;
            if (p.length === 3) {
                layer.property("ADBE Transform Group").property("ADBE Position").setValue([p[0] * factor, p[1] * factor, p[2]]);
            } else {
                layer.property("ADBE Transform Group").property("ADBE Position").setValue([p[0] * factor, p[1] * factor]);
            }
        }
        app.endUndoGroup();
        return jsonOk("Scaled comp to " + newW + "x" + newH + " (" + pct + "%)");
    } catch (e) { return jsonErr(e.message); }
}

/* ═══════════════════════════════════════
   TAB 4 — TEXT TOOLS
   ═══════════════════════════════════════ */

function applyFontToSelected(fontName) {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        app.beginUndoGroup("AE PowerTools: Apply Font");
        var count = 0;
        for (var i = 0; i < sel.length; i++) {
            if (!(sel[i] instanceof TextLayer)) continue;
            var textDoc = sel[i].property("ADBE Text Properties").property("ADBE Text Document").value;
            textDoc.font = fontName;
            sel[i].property("ADBE Text Properties").property("ADBE Text Document").setValue(textDoc);
            count++;
        }
        app.endUndoGroup();
        if (count === 0) return jsonErr("No text layers selected");
        return jsonOk("Applied font '" + fontName + "' to " + count + " layer(s)");
    } catch (e) { return jsonErr(e.message); }
}

function setFontSize(size) {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        app.beginUndoGroup("AE PowerTools: Set Font Size");
        var count = 0;
        for (var i = 0; i < sel.length; i++) {
            if (!(sel[i] instanceof TextLayer)) continue;
            var textDoc = sel[i].property("ADBE Text Properties").property("ADBE Text Document").value;
            textDoc.fontSize = size;
            sel[i].property("ADBE Text Properties").property("ADBE Text Document").setValue(textDoc);
            count++;
        }
        app.endUndoGroup();
        if (count === 0) return jsonErr("No text layers selected");
        return jsonOk("Set font size " + size + " on " + count + " layer(s)");
    } catch (e) { return jsonErr(e.message); }
}

function setTextColor(rgb) {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        app.beginUndoGroup("AE PowerTools: Set Text Color");
        var count = 0;
        for (var i = 0; i < sel.length; i++) {
            if (!(sel[i] instanceof TextLayer)) continue;
            var textDoc = sel[i].property("ADBE Text Properties").property("ADBE Text Document").value;
            textDoc.fillColor = rgb;
            sel[i].property("ADBE Text Properties").property("ADBE Text Document").setValue(textDoc);
            count++;
        }
        app.endUndoGroup();
        if (count === 0) return jsonErr("No text layers selected");
        return jsonOk("Set text color on " + count + " layer(s)");
    } catch (e) { return jsonErr(e.message); }
}

function findReplaceText(find, replace) {
    try {
        var comp = requireComp();
        app.beginUndoGroup("AE PowerTools: Find & Replace Text");
        var count = 0;
        for (var i = 1; i <= comp.numLayers; i++) {
            var layer = comp.layer(i);
            if (!(layer instanceof TextLayer)) continue;
            var textDoc = layer.property("ADBE Text Properties").property("ADBE Text Document").value;
            var original = textDoc.text;
            var re = new RegExp(find.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "g");
            var updated = original.replace(re, replace);
            if (updated !== original) {
                textDoc.text = updated;
                layer.property("ADBE Text Properties").property("ADBE Text Document").setValue(textDoc);
                count++;
            }
        }
        app.endUndoGroup();
        return jsonOk("Replaced text in " + count + " layer(s)");
    } catch (e) { return jsonErr(e.message); }
}

function auditTextLayers() {
    try {
        var comp = requireComp();
        var results = [];
        for (var i = 1; i <= comp.numLayers; i++) {
            var layer = comp.layer(i);
            if (!(layer instanceof TextLayer)) continue;
            var textDoc = layer.property("ADBE Text Properties").property("ADBE Text Document").value;
            results.push({ name: layer.name, text: textDoc.text });
        }
        if (results.length === 0) return jsonErr("No text layers in comp");
        return jsonOk("Found " + results.length + " text layer(s)", results);
    } catch (e) { return jsonErr(e.message); }
}

/* ═══════════════════════════════════════
   TAB 5 — RENDER & EXPORT
   ═══════════════════════════════════════ */

function addToRenderQueue() {
    try {
        var comp = requireComp();
        app.project.renderQueue.items.add(comp);
        return jsonOk("Added '" + comp.name + "' to render queue");
    } catch (e) { return jsonErr(e.message); }
}

function addAllCompsToRQ() {
    try {
        var count = 0;
        for (var i = 1; i <= app.project.numItems; i++) {
            var item = app.project.item(i);
            if (item instanceof CompItem) {
                app.project.renderQueue.items.add(item);
                count++;
            }
        }
        if (count === 0) return jsonErr("No compositions in project");
        return jsonOk("Added " + count + " comp(s) to render queue");
    } catch (e) { return jsonErr(e.message); }
}

function startRenderQueue() {
    try {
        var rq = app.project.renderQueue;
        if (rq.numItems === 0) return jsonErr("Render queue is empty");
        var ready = 0;
        for (var i = 1; i <= rq.numItems; i++) {
            if (rq.item(i).status === RQItemStatus.QUEUED) ready++;
        }
        if (ready === 0) return jsonErr("No queued items in render queue");
        rq.render();
        return jsonOk("Render complete (" + ready + " item(s))");
    } catch (e) { return jsonErr(e.message); }
}

function pickOutputFolder() {
    try {
        var folder = Folder.selectDialog("Select output folder");
        if (!folder) return jsonErr("No folder selected");
        return jsonOk("Output path set", folder.fsName);
    } catch (e) { return jsonErr(e.message); }
}

function exportViaAME(preset, outputPath) {
    try {
        var comp = requireComp();

        if (preset === "PNG_Seq") {
            app.beginUndoGroup("AE PowerTools: PNG Sequence");
            var rqItem = app.project.renderQueue.items.add(comp);
            var om = rqItem.outputModule(1);
            om.applyTemplate("_HIDDEN X-Factor 8 Premul");
            try { om.applyTemplate("PNG Sequence"); } catch (ignored) {}
            if (outputPath && outputPath !== "") {
                var outFile = new File(outputPath + "/" + comp.name + "_[#####].png");
                om.file = outFile;
            }
            app.endUndoGroup();
            return jsonOk("Added PNG Sequence to render queue");
        }

        var formatMap = {
            "H264_1080": "H.264",
            "H264_4K":   "H.264",
            "ProRes422": "QuickTime",
            "ProRes4444": "QuickTime",
            "GIF":       "Animated GIF",
            "WebM":      "WebM"
        };
        var format = formatMap[preset] || "H.264";

        var projFile = app.project.file;
        if (!projFile) {
            app.project.renderQueue.items.add(comp);
            return jsonOk("Added to render queue (save project first for AME export)");
        }

        try {
            app.project.renderQueue.items.add(comp);
            var rqItem = app.project.renderQueue.item(app.project.renderQueue.numItems);
            var om = rqItem.outputModule(1);
            if (outputPath && outputPath !== "") {
                var ext = (preset === "GIF") ? ".gif" : (preset === "WebM") ? ".webm" : ".mp4";
                if (preset === "ProRes422" || preset === "ProRes4444") ext = ".mov";
                om.file = new File(outputPath + "/" + comp.name + "_" + preset + ext);
            }
            return jsonOk("Added '" + comp.name + "' (" + preset + ") to render queue. Configure output module for " + format + " settings.");
        } catch (ameErr) {
            return jsonOk("Added to render queue. Set output format to " + format + " manually.");
        }
    } catch (e) { return jsonErr(e.message); }
}

/* ═══════════════════════════════════════
   TAB 6 — EXPRESSION TOOLS
   ═══════════════════════════════════════ */

function applyExpressionPreset(preset, freq, amp, speedMult, seed, rmin, rmax, bAmp, bFreq, bDecay, pFps) {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        var expr = "";
        switch (preset) {
            case "wiggle":
                expr = "wiggle(" + freq + ", " + amp + ")";
                break;
            case "loopOut":
                expr = 'loopOut("cycle")';
                break;
            case "loopIn":
                expr = 'loopIn("cycle")';
                break;
            case "timeSpeed":
                expr = "value * time * " + speedMult;
                break;
            case "random":
                expr = "seedRandom(" + seed + ", true);\nrandom(" + rmin + ", " + rmax + ")";
                break;
            case "bounce":
                expr = "n = 0;\nif (numKeys > 0) {\n  n = nearestKey(time).index;\n  if (key(n).time > time) n--;\n}\nif (n == 0) {\n  t = 0;\n} else {\n  t = time - key(n).time;\n}\nif (n > 0 && t < 1) {\n  v = velocityAtTime(key(n).time - thisComp.frameDuration / 10);\n  amp = " + bAmp + ";\n  freq = " + bFreq + ";\n  decay = " + bDecay + ";\n  value + v * amp * Math.sin(freq * t * 2 * Math.PI) / Math.exp(decay * t);\n} else {\n  value;\n}";
                break;
            case "posterizeTime":
                expr = "posterizeTime(" + pFps + ");\nvalue";
                break;
        }
        if (expr === "") return jsonErr("Unknown preset");
        app.beginUndoGroup("AE PowerTools: Apply Expression");
        var count = 0;
        for (var s = 0; s < sel.length; s++) {
            var selProps = sel[s].selectedProperties;
            if (selProps.length > 0) {
                for (var p = 0; p < selProps.length; p++) {
                    if (selProps[p].propertyType === PropertyType.PROPERTY && selProps[p].canSetExpression) {
                        selProps[p].expression = expr;
                        count++;
                    }
                }
            } else {
                var tProp = sel[s].property("ADBE Transform Group").property("ADBE Position");
                if (tProp && tProp.canSetExpression) {
                    tProp.expression = expr;
                    count++;
                }
            }
        }
        app.endUndoGroup();
        if (count === 0) return jsonErr("No applicable properties found. Select properties in timeline.");
        return jsonOk("Applied '" + preset + "' to " + count + " propert(ies)");
    } catch (e) { return jsonErr(e.message); }
}

function removeAllExpressions() {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        app.beginUndoGroup("AE PowerTools: Remove Expressions");
        var count = 0;
        for (var s = 0; s < sel.length; s++) {
            iterateProperties(sel[s], function (prop) {
                if (prop.canSetExpression && prop.expression !== "") {
                    prop.expression = "";
                    count++;
                }
            });
            var iterExpr = function (pg) {
                for (var i = 1; i <= pg.numProperties; i++) {
                    var p = pg.property(i);
                    if (p.propertyType === PropertyType.PROPERTY) {
                        if (p.canSetExpression && p.expression !== "") {
                            p.expression = "";
                            count++;
                        }
                    } else {
                        iterExpr(p);
                    }
                }
            };
            iterExpr(sel[s]);
        }
        app.endUndoGroup();
        return jsonOk("Removed " + count + " expression(s)");
    } catch (e) { return jsonErr(e.message); }
}

function toggleExpressionsInComp(enable) {
    try {
        var comp = requireComp();
        app.beginUndoGroup("AE PowerTools: Toggle Expressions");
        var count = 0;
        for (var i = 1; i <= comp.numLayers; i++) {
            var toggleExprRecursive = function (pg) {
                for (var j = 1; j <= pg.numProperties; j++) {
                    var p = pg.property(j);
                    if (p.propertyType === PropertyType.PROPERTY) {
                        if (p.canSetExpression && p.expression !== "") {
                            p.expressionEnabled = enable;
                            count++;
                        }
                    } else {
                        toggleExprRecursive(p);
                    }
                }
            };
            toggleExprRecursive(comp.layer(i));
        }
        app.endUndoGroup();
        return jsonOk((enable ? "Enabled" : "Disabled") + " " + count + " expression(s)");
    } catch (e) { return jsonErr(e.message); }
}

function copyPasteExpression() {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        if (sel.length < 2) return jsonErr("Select source layer first, then target layers");
        var srcLayer = sel[0];
        var srcExpr = null;
        var srcPropName = null;
        var srcSelProps = srcLayer.selectedProperties;
        if (srcSelProps.length > 0) {
            for (var p = 0; p < srcSelProps.length; p++) {
                if (srcSelProps[p].propertyType === PropertyType.PROPERTY && srcSelProps[p].expression !== "") {
                    srcExpr = srcSelProps[p].expression;
                    srcPropName = srcSelProps[p].matchName;
                    break;
                }
            }
        }
        if (!srcExpr) {
            iterateProperties(srcLayer, function (prop) {
                if (!srcExpr && prop.canSetExpression && prop.expression !== "") {
                    srcExpr = prop.expression;
                    srcPropName = prop.matchName;
                }
            });
        }
        if (!srcExpr) return jsonErr("No expression found on source layer");
        app.beginUndoGroup("AE PowerTools: Copy/Paste Expression");
        var count = 0;
        for (var t = 1; t < sel.length; t++) {
            var findAndApply = function (pg) {
                for (var i = 1; i <= pg.numProperties; i++) {
                    var p = pg.property(i);
                    if (p.propertyType === PropertyType.PROPERTY) {
                        if (p.matchName === srcPropName && p.canSetExpression) {
                            p.expression = srcExpr;
                            count++;
                            return true;
                        }
                    } else {
                        if (findAndApply(p)) return true;
                    }
                }
                return false;
            };
            findAndApply(sel[t]);
        }
        app.endUndoGroup();
        return jsonOk("Pasted expression to " + count + " layer(s)");
    } catch (e) { return jsonErr(e.message); }
}

/* ═══════════════════════════════════════
   TAB 7 — COLOR & EFFECTS
   ═══════════════════════════════════════ */

function addAdjustmentLayer() {
    try {
        var comp = requireComp();
        app.beginUndoGroup("AE PowerTools: Adjustment Layer");
        var solid = comp.layers.addSolid([1, 1, 1], "Adjustment Layer", comp.width, comp.height, 1, comp.duration);
        solid.adjustmentLayer = true;
        solid.moveToBeginning();
        app.endUndoGroup();
        return jsonOk("Added adjustment layer");
    } catch (e) { return jsonErr(e.message); }
}

function applyQuickEffect(effect) {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        var effectMatchNames = {
            "Lumetri":        "ADBE Lumetri",
            "Curves":         "ADBE CurvesCustom",
            "HueSat":         "ADBE HUE SATURATION",
            "BrightContrast": "ADBE Brightness & Contrast 2"
        };
        var mn = effectMatchNames[effect];
        if (!mn) return jsonErr("Unknown effect: " + effect);
        app.beginUndoGroup("AE PowerTools: Quick Effect");
        var count = 0;
        for (var i = 0; i < sel.length; i++) {
            try {
                sel[i].property("ADBE Effect Parade").addProperty(mn);
                count++;
            } catch (effErr) {
                // Lumetri may not be available in all AE versions
                if (effect === "Lumetri") {
                    try {
                        sel[i].property("ADBE Effect Parade").addProperty("ADBE Color Balance (HLS)");
                        count++;
                    } catch (ignored) {}
                }
            }
        }
        app.endUndoGroup();
        if (count === 0) return jsonErr("Could not apply " + effect + ". Effect may not be installed.");
        return jsonOk("Applied " + effect + " to " + count + " layer(s)");
    } catch (e) { return jsonErr(e.message); }
}

function copyPasteEffects() {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        if (sel.length < 2) return jsonErr("Select source + target layers");
        var srcLayer = sel[0];
        var srcEffects = srcLayer.property("ADBE Effect Parade");
        if (!srcEffects || srcEffects.numProperties === 0) return jsonErr("Source layer has no effects");
        app.beginUndoGroup("AE PowerTools: Copy/Paste Effects");
        var count = 0;
        for (var t = 1; t < sel.length; t++) {
            for (var e = 1; e <= srcEffects.numProperties; e++) {
                try {
                    var effName = srcEffects.property(e).matchName;
                    sel[t].property("ADBE Effect Parade").addProperty(effName);
                    count++;
                } catch (ignored) {}
            }
        }
        app.endUndoGroup();
        return jsonOk("Copied " + srcEffects.numProperties + " effect(s) to " + (sel.length - 1) + " layer(s)");
    } catch (e) { return jsonErr(e.message); }
}

function removeAllEffects() {
    try {
        var comp = requireSelection();
        var sel = comp.selectedLayers;
        app.beginUndoGroup("AE PowerTools: Remove Effects");
        var count = 0;
        for (var i = 0; i < sel.length; i++) {
            var fx = sel[i].property("ADBE Effect Parade");
            if (fx) {
                while (fx.numProperties > 0) {
                    fx.property(1).remove();
                    count++;
                }
            }
        }
        app.endUndoGroup();
        return jsonOk("Removed " + count + " effect(s)");
    } catch (e) { return jsonErr(e.message); }
}

/* ═══════════════════════════════════════
   TAB 8 — PROJECT TOOLS
   ═══════════════════════════════════════ */

function showProjectInfo() {
    try {
        var compCount = 0, footageCount = 0, totalItems = app.project.numItems;
        for (var i = 1; i <= totalItems; i++) {
            var item = app.project.item(i);
            if (item instanceof CompItem) compCount++;
            else if (item instanceof FootageItem) footageCount++;
        }
        var filePath = app.project.file ? app.project.file.fsName : null;
        return jsonOk("Project info loaded", {
            comps: compCount,
            footage: footageCount,
            totalItems: totalItems,
            filePath: filePath
        });
    } catch (e) { return jsonErr(e.message); }
}

function consolidateFootage() {
    try {
        app.beginUndoGroup("AE PowerTools: Consolidate");
        var before = app.project.numItems;
        app.project.consolidateFootage();
        var after = app.project.numItems;
        app.endUndoGroup();
        return jsonOk("Consolidated footage. Removed " + (before - after) + " duplicate(s)");
    } catch (e) { return jsonErr(e.message); }
}

function removeUnusedItems() {
    try {
        app.beginUndoGroup("AE PowerTools: Remove Unused");
        var before = app.project.numItems;
        app.project.removeUnusedFootage();
        var after = app.project.numItems;
        app.endUndoGroup();
        return jsonOk("Removed " + (before - after) + " unused item(s)");
    } catch (e) { return jsonErr(e.message); }
}

function searchProjectItems(query) {
    try {
        var results = [];
        var q = query.toLowerCase();
        for (var i = 1; i <= app.project.numItems; i++) {
            var item = app.project.item(i);
            if (item.name.toLowerCase().indexOf(q) !== -1) {
                var itemType = "Other";
                if (item instanceof CompItem) itemType = "Comp";
                else if (item instanceof FootageItem) itemType = "Footage";
                else if (item instanceof FolderItem) itemType = "Folder";
                results.push({ name: item.name, type: itemType });
            }
        }
        return jsonOk("Found " + results.length + " item(s)", results);
    } catch (e) { return jsonErr(e.message); }
}

function createFolderStructure() {
    try {
        app.beginUndoGroup("AE PowerTools: Folder Structure");
        var folders = ["_COMPS", "_FOOTAGE", "_PRECOMPS", "_RENDERS"];
        var created = 0;
        for (var f = 0; f < folders.length; f++) {
            var exists = false;
            for (var i = 1; i <= app.project.numItems; i++) {
                if (app.project.item(i) instanceof FolderItem && app.project.item(i).name === folders[f]) {
                    exists = true;
                    break;
                }
            }
            if (!exists) {
                app.project.items.addFolder(folders[f]);
                created++;
            }
        }
        app.endUndoGroup();
        if (created === 0) return jsonOk("All folders already exist");
        return jsonOk("Created " + created + " folder(s)");
    } catch (e) { return jsonErr(e.message); }
}
