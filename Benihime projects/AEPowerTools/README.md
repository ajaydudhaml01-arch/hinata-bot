# AE PowerTools — After Effects CEP Extension

An all-in-one panel that speeds up motion design workflow in Adobe After Effects.  
**CEP 11** compatible with **AE 2022–2025** (v22.0+).

---

## Installation

### 1. Copy the Extension

Copy the entire `AEPowerTools` folder to your CEP extensions directory:

| OS | Path |
|---|---|
| **Windows** | `C:\Program Files (x86)\Common Files\Adobe\CEP\extensions\` |
| **macOS** | `/Library/Application Support/Adobe/CEP/extensions/` |

You can also use the per-user path:

| OS | Path |
|---|---|
| **Windows** | `%APPDATA%\Adobe\CEP\extensions\` |
| **macOS** | `~/Library/Application Support/Adobe/CEP/extensions/` |

### 2. Enable Unsigned Extensions (Debug Mode)

Adobe CEP requires extensions to be signed for production. During development, enable debug mode:

#### Windows
Open **Command Prompt as Administrator** and run:
```cmd
reg add "HKCU\SOFTWARE\Adobe\CSXS.11" /v PlayerDebugMode /t REG_SZ /d 1 /f
```

#### macOS
Open **Terminal** and run:
```bash
defaults write com.adobe.CSXS.11 PlayerDebugMode 1
```

> **Note**: Replace `CSXS.11` with your CEP version if different. After Effects 2022+ uses CEP 11.

### 3. Restart After Effects

Close and reopen After Effects completely after copying the extension and enabling debug mode.

### 4. Open the Panel

Go to: **Window → Extensions → AE PowerTools**

The panel will appear as a dockable panel in After Effects.

---

## Features & Usage Guide

### Tab 1 — Layer Tools

| Feature | Description |
|---|---|
| **Select by Type** | Click Shape, Text, Null, Solid, or Precomp to select all layers of that type |
| **Rename (Prefix/Suffix)** | Type prefix or suffix text, then click the button to rename selected layers |
| **Find & Replace** | Enter find/replace strings to batch-rename layer names |
| **Auto-Number** | Sequentially numbers selected layers (e.g., "Layer 1", "Layer 2") |
| **Solo Toggle** | Toggles solo state on all selected layers |
| **Lock/Unlock All** | Lock or unlock every layer in the comp |
| **Delete Disabled** | Removes all layers that have visibility (eyeball) turned off |
| **Center Anchor** | Moves anchor point to visual center while preserving layer position |
| **Blend Mode** | Select a blend mode from the dropdown and apply to all selected layers |
| **Duplicate with Offset** | Duplicate selected layers with X, Y pixel offset and time offset in seconds |

### Tab 2 — Keyframe Tools

| Feature | Description |
|---|---|
| **Copy Timing** | Copies keyframe times from the first selected layer and applies to other selected layers |
| **Reverse Keys** | Reverses keyframe values on selected layers (timing stays, values swap) |
| **Snap to Frame** | Snaps all keyframes to the nearest whole frame boundary |
| **Ease In/Out/InOut** | Applies easing to all **selected** keyframes (select keyframes in the timeline first) |
| **Offset** | Shifts selected keyframes forward/backward by N frames |
| **To Hold** | Converts all keyframes to hold interpolation |
| **Delete All Keys** | Deletes all keyframes on selected properties (or entire layers if no properties selected) |

### Tab 3 — Composition Tools

| Feature | Description |
|---|---|
| **New Composition** | Create a comp with custom name, dimensions, FPS, duration, and background color |
| **Quick Presets** | One-click creation: 1080p, 4K, Reels 9:16, Square 1:1, Twitter 16:9 |
| **Trim to Work Area** | Trims composition duration to match the work area |
| **Duplicate Comp** | Duplicates the active comp with " Copy" suffix |
| **Pre-compose** | Pre-composes selected layers with auto-generated name |
| **Set BG Color** | Changes the composition background color |
| **Scale Comp** | Resizes the comp and proportionally scales all layers |

### Tab 4 — Text Tools

| Feature | Description |
|---|---|
| **Apply Font** | Enter a font name (e.g., "Arial", "Futura-Bold") and apply to selected text layers |
| **Set Font Size** | Set a pixel size on all selected text layers |
| **Set Text Color** | Pick a color and apply to all selected text layers |
| **Find & Replace** | Search and replace text content across ALL text layers in the comp |
| **Audit Text Layers** | Lists every text layer with its text content for quick review |

### Tab 5 — Render & Export

| Feature | Description |
|---|---|
| **Add Active Comp** | Adds the active composition to the render queue |
| **Add All Comps** | Adds every composition in the project to the render queue |
| **Start Render** | Begins rendering all queued items |
| **Browse Output** | Pick an output folder via system dialog |
| **AME Presets** | Adds to render queue configured for: H.264 1080p, H.264 4K, ProRes 422, ProRes 4444, GIF, WebM, PNG Sequence |

> **Note**: Media Encoder integration uses the render queue. For native AME queue, use AE's built-in "Add to Adobe Media Encoder Queue" after adding items.

### Tab 6 — Expression Tools

| Feature | Description |
|---|---|
| **wiggle** | `wiggle(freq, amp)` — Frequency and amplitude inputs |
| **loopOut / loopIn** | Cycle-based loop expressions |
| **time × N** | Speed multiplier expression |
| **random (seeded)** | Seeded random value between min and max |
| **bounce** | Overshoot/bounce easing with configurable amp, freq, decay |
| **posterizeTime** | Frame rate reduction expression |
| **Remove from Selected** | Strips all expressions from selected layers |
| **Enable/Disable All** | Toggle all expressions in the entire comp |
| **Copy & Paste Expr** | Copy expression from first selected layer's property, paste to same property on other layers |

> **Tip**: Select the specific property in the timeline before applying an expression. If no property is selected, it defaults to Position.

### Tab 7 — Color & Effects

| Feature | Description |
|---|---|
| **Add Adjustment** | Creates a white solid adjustment layer at the top of the layer stack |
| **Quick Effects** | One-click apply: Lumetri Color, Curves, Hue/Saturation, Brightness & Contrast |
| **Color Palette** | Save up to 10 swatches (stored in browser localStorage). Click a swatch to copy its hex value. |
| **Copy & Paste FX** | Copy all effects from first selected layer to remaining selected layers |
| **Remove All FX** | Strip all effects from selected layers |

### Tab 8 — Project Tools

| Feature | Description |
|---|---|
| **Show Project Info** | Displays comp count, footage count, total items, and project file path |
| **Consolidate Footage** | Merges duplicate footage references |
| **Remove Unused** | Deletes all unused footage and items from the project |
| **Search Project** | Filter project items by name |
| **Create Folders** | Creates `_COMPS`, `_FOOTAGE`, `_PRECOMPS`, `_RENDERS` folders if they don't exist |

---

## Troubleshooting

### Panel Not Showing

1. **Verify installation path**: Make sure the `AEPowerTools` folder (containing `CSXS/manifest.xml`) is in the correct CEP extensions directory
2. **Check debug mode**: Ensure `PlayerDebugMode` is set to `1` for `CSXS.11`
3. **Restart AE completely**: Not just close/reopen the panel — quit and relaunch After Effects
4. **Check AE version**: This extension requires AE 2022 (v22.0) or later

### Script Errors

1. **"No active composition"**: Make sure a comp is open and active before running any tool
2. **"No layers selected"**: Select layers in the timeline first
3. **Expression errors**: Select the specific property in the timeline before applying expressions
4. **Font not found**: Use the exact PostScript name of the font (e.g., "HelveticaNeue-Bold" not "Helvetica Neue Bold")

### Render Issues

1. **"No queued items"**: Items must have status "Queued" — check that output modules are properly configured
2. **Output path errors**: Use the Browse button to select a valid output folder before exporting
3. **AME export**: If Media Encoder doesn't open, items are added to AE's render queue instead — configure output module manually

### CEP Debugging

Open Chrome DevTools for the panel by navigating to:
```
http://localhost:8091/
```
(Default CEP debug port — may vary. Check `.debug` file if you add one.)

---

## Folder Structure

```
AEPowerTools/
├── CSXS/
│   └── manifest.xml        ← Extension manifest (CEP 11)
├── index.html               ← Main panel UI
├── style.css                ← Dark AE-matching theme
├── main.js                  ← JS logic + CSInterface calls
├── host/
│   └── host.jsx             ← ExtendScript functions (AE API)
├── lib/
│   └── CSInterface.js       ← Adobe CSInterface library
└── README.md                ← This file
```

---

## License

This extension is provided as-is for personal and commercial use.
