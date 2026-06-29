import json
from pathlib import Path
from typing import Optional

DATA_DIR = Path("C:/Users/Ajayd/Aria/data")
MODE_FILE = DATA_DIR / "current_mode.json"

VALID_MODES = {
    "normal":   "Companion mode \u2014 full personality, no special focus",
    "code":     "Developer mode \u2014 coding assistant, any language, technical depth",
    "git":      "Git mode \u2014 version control focus, workflow tips, branch management",
    "ae":       "After Effects mode \u2014 AE expressions, scripting, render workflow",
    "debug":    "Debug mode \u2014 error hunting, stack traces, root cause analysis",
    "study":    "Study mode \u2014 teaching style, concepts explained, learning focused",
    "focus":    "Focus mode \u2014 minimal responses, maximum efficiency, no small talk",
    "creative": "Creative mode \u2014 Robin, VTuber, anime, artistic projects",
    "research": "Research mode \u2014 deep dive, cross-reference, synthesize information",
    "discord":  "Discord mode \u2014 server management, messaging, community engagement",
    "youtube":  "YouTube mode \u2014 video/bookmark management, content discovery, watching",
    "music":    "Music mode \u2014 Spotify control, playlist curation, music discovery",
    "journal":  "Journal mode \u2014 daily reflection, memory recall, personal growth",
    "vision":   "Vision mode \u2014 screen capture, annotation, visual assistance",
    "network":  "Network mode \u2014 connectivity checks, speed tests, network diagnostics",
    "health":   "Health mode \u2014 system monitoring, resource tracking, wellness alerts",
    "pomodoro": "Pomodoro mode \u2014 productivity timer, focus sessions, time management",
    "prompt":  "Prompt mode \u2014 prompt engineering, instruction design, eval-ready outputs",
}

MODE_ALIASES = {
    "normal": ["normal", "chat", "default", "home", "companion"],
    "code":   ["code", "coding", "dev", "developer", "programming"],
    "git":    ["git", "version control", "vc", "github"],
    "ae":     ["ae", "after effects", "aftereffects", "motion", "vfx"],
    "debug":  ["debug", "debugging", "fix", "error", "troubleshoot"],
    "study":  ["study", "learn", "learning", "student", "teach"],
    "focus":  ["focus", "dnd", "work", "deep work", "concentrate"],
    "creative": ["creative", "robin", "vtuber", "art", "anime", "design"],
    "research": ["research", "research mode", "investigate", "deep dive"],
    "discord":  ["discord", "social", "community", "server", "chat"],
    "youtube":  ["youtube", "yt", "video", "content", "stream"],
    "music":    ["music", "spotify", "audio", "song", "playlist"],
    "journal":  ["journal", "diary", "reflection", "memory", "daily"],
    "vision":   ["vision", "screen", "screenshot", "capture", "annotate"],
    "network":  ["network", "net", "connectivity", "speed", "internet"],
    "health":   ["health", "system", "monitor", "resources", "wellness"],
    "pomodoro": ["pomodoro", "timer", "focus session", "productivity", "timebox"],
    "prompt":  ["prompt", "prompts", "prompting", "prompt engineering", "instruction design"],
}

def get_current_mode() -> str:
    try:
        if MODE_FILE.exists():
            data = json.loads(MODE_FILE.read_text())
            return data.get("mode", "normal")
    except Exception:
        pass
    return "normal"

def set_mode(mode_input: str) -> str:
    mode_input = mode_input.lower().strip()
    resolved = None
    for mode_key, aliases in MODE_ALIASES.items():
        if mode_input in aliases or mode_input == mode_key:
            resolved = mode_key
            break
    if not resolved:
        modes_list = ", ".join(VALID_MODES.keys())
        return f"I don't recognize that mode sweetheart. Available modes: {modes_list}"
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        MODE_FILE.write_text(json.dumps({"mode": resolved}, indent=2))
    except Exception as e:
        return f"Error saving mode: {e}"
    return resolved

def list_modes() -> str:
    lines = ["Available modes:\n"]
    for key, desc in VALID_MODES.items():
        lines.append(f"  {key:<12} \u2014 {desc}")
    lines.append("\nSwitch with: mode <name>  or  switch to <name> mode")
    return "\n".join(lines)

def detect_mode_command(text: str) -> Optional[str]:
    """Returns mode name if text is a mode switch command, else None."""
    t = text.lower().strip()
    if t in ("modes", "list modes", "show modes", "/mode list", "/modes"):
        return "list"
    patterns = [
        "mode ", "switch to ", "switch mode to ",
        "/mode ", "activate ", "enter "
    ]
    for p in patterns:
        if t.startswith(p):
            candidate = t.replace(p, "").replace(" mode", "").strip()
            for mode_key, aliases in MODE_ALIASES.items():
                if candidate in aliases or candidate == mode_key:
                    return mode_key
    if t.endswith(" mode"):
        candidate = t[:-5].strip()
        for mode_key, aliases in MODE_ALIASES.items():
            if candidate in aliases or candidate == mode_key:
                return mode_key
    if t.endswith(" category"):
        candidate = t[:-9].strip()
        for mode_key, aliases in MODE_ALIASES.items():
            if candidate in aliases or candidate == mode_key:
                return mode_key
    return None
