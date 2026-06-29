"""
Aria Theme System — premium color palette, gradients, glow effects, and constants.

Designed for a modern, premium terminal aesthetic inspired by Warp, modern Neovim,
and cyberpunk-sleek design. Aria's signature pink (#ff6b9d) remains the anchor.
"""

# ── Base Surface Palette ─────────────────────────────────────────────────────
# Layered depth: deeper = further back, lighter = closer to foreground
SURFACE_BASE    = "#070708"   # deepest background
SURFACE_DEEP    = "#0a0a0b"   # main background
SURFACE         = "#0d0d10"   # standard surface
SURFACE_ALT     = "#121216"   # secondary surface (panels)
SURFACE_LIFT    = "#18181d"   # elevated surface (hover, active)
SURFACE_BORDER  = "#1e1e2a"   # subtle borders
SURFACE_BORDER2 = "#2a2a3e"   # emphasized borders
SURFACE_GLOW    = "#1a1025"   # subtle purple-tinted glow for active elements

# ── Text ─────────────────────────────────────────────────────────────────────
TEXT          = "#e8e8f0"   # primary — high contrast
TEXT_DIM      = "#a0a0b8"   # secondary
TEXT_MUTED    = "#6b6b82"   # tertiary, hints, labels
TEXT_FAINT    = "#49495c"   # ultra-subtle (decorative)
TIMESTAMP     = "#3d3d50"   # ultra-dim for timestamps

# ── Accent Palette (Aria signature) ──────────────────────────────────────────
ACCENT        = "#ff6b9d"   # Aria pink — primary accent
ACCENT_BRIGHT = "#ff8ab3"   # bright pink — highlights, glows
ACCENT_DIM    = "#d44a7a"   # dimmed
ACCENT_DEEP   = "#9e2f5a"   # deep pink — background glows

# ── Semantic Colors ──────────────────────────────────────────────────────────
SUCCESS       = "#34d399"   # green — success, active
SUCCESS_DIM   = "#1a8a5c"   # dimmed green
WARNING       = "#fbbf24"   # yellow — warnings, duration
WARNING_DIM   = "#b8860b"   # dimmed yellow
ERROR         = "#f87171"   # red — errors, failures
ERROR_DIM     = "#b91c1c"   # dimmed red
INFO          = "#22d3ee"   # cyan — informational
INFO_DIM      = "#0e7c94"   # dimmed cyan

# ── Extended Accents ─────────────────────────────────────────────────────────
PURPLE        = "#c084fc"   # creative/code mode
PURPLE_DIM    = "#7c3aed"
BLUE          = "#38bdf8"   # AE / network mode
BLUE_DIM      = "#0369a1"
ORANGE        = "#fb923c"   # pomodoro / worried mood
TEAL          = "#2dd4bf"   # vision mode
INDIGO        = "#818cf8"   # research / lonely mood
GRAY          = "#94a3b8"   # focus / hurt mood

# ── Gradient Definitions ─────────────────────────────────────────────────────
# For use with rich.text.Text gradient or styled segments
GRADIENT_PINK  = [ACCENT_DEEP, ACCENT_DIM, ACCENT, ACCENT_BRIGHT]
GRADIENT_SUNSET = [ERROR, WARNING, ACCENT]
GRADIENT_OCEAN  = [BLUE_DIM, BLUE, INFO]
GRADIENT_FOREST = [SUCCESS_DIM, SUCCESS, TEAL]
GRADIENT_PURPLE = [PURPLE_DIM, PURPLE, INDIGO]

# Banner gradient (pink → purple → indigo for the ASCII art)
GRADIENT_BANNER = ["#ff6b9d", "#e96baf", "#d46bc2", "#bf6bd5", "#a96be8", "#946bfb", "#818cf8"]

# ── Mood Colors ──────────────────────────────────────────────────────────────
MOOD_COLORS = {
    "happy":   ACCENT,
    "content": PURPLE,
    "lonely":  INDIGO,
    "worried": ORANGE,
    "hurt":    GRAY,
}

MOOD_CONFIGS = {
    "happy":   {"color": MOOD_COLORS["happy"],   "emoji": "✨", "title": "Happy",  "dot": "●"},
    "content": {"color": MOOD_COLORS["content"], "emoji": "🌸", "title": "Content", "dot": "●"},
    "lonely":  {"color": MOOD_COLORS["lonely"],  "emoji": "🌙", "title": "Lonely",  "dot": "●"},
    "worried": {"color": MOOD_COLORS["worried"], "emoji": "🌤", "title": "Worried", "dot": "●"},
    "hurt":    {"color": MOOD_COLORS["hurt"],    "emoji": "🕊", "title": "Hurt",    "dot": "●"},
}

# ── Mode Colors ──────────────────────────────────────────────────────────────
MODE_CONFIGS = {
    "normal":   {"color": ACCENT,          "emoji": "💬", "label": "NORMAL",   "desc": "Companion"},
    "code":     {"color": PURPLE,          "emoji": "💻", "label": "CODE",     "desc": "Developer"},
    "git":      {"color": WARNING,         "emoji": "🌿", "label": "GIT",      "desc": "Version Control"},
    "ae":       {"color": BLUE,            "emoji": "🎬", "label": "AE",       "desc": "After Effects"},
    "debug":    {"color": ERROR,           "emoji": "🔍", "label": "DEBUG",    "desc": "Error Hunter"},
    "study":    {"color": SUCCESS,         "emoji": "📚", "label": "STUDY",    "desc": "Learning"},
    "focus":    {"color": GRAY,            "emoji": "🎯", "label": "FOCUS",    "desc": "Deep Work"},
    "creative": {"color": INFO,            "emoji": "🎨", "label": "CREATIVE", "desc": "Robin & Art"},
    "research": {"color": INDIGO,          "emoji": "🔬", "label": "RESEARCH", "desc": "Deep Dive"},
    "discord":  {"color": "#5865F2",       "emoji": "💬", "label": "DISCORD",  "desc": "Community"},
    "youtube":  {"color": "#ff4444",       "emoji": "📺", "label": "YOUTUBE",  "desc": "Content"},
    "music":    {"color": "#1DB954",       "emoji": "🎵", "label": "MUSIC",    "desc": "Spotify & Audio"},
    "journal":  {"color": WARNING,         "emoji": "📓", "label": "JOURNAL",  "desc": "Reflection"},
    "vision":   {"color": TEAL,            "emoji": "📷", "label": "VISION",   "desc": "Screen Capture"},
    "network":  {"color": BLUE,            "emoji": "🌐", "label": "NETWORK",  "desc": "Connectivity"},
    "health":   {"color": ERROR,           "emoji": "❤️",  "label": "HEALTH",  "desc": "System Wellness"},
    "pomodoro": {"color": ORANGE,          "emoji": "⏱️",  "label": "TIMER",   "desc": "Productivity"},
    "prompt":  {"color": PURPLE,          "emoji": "✍️",  "label": "PROMPT",  "desc": "Prompt Engineering"},
}

# ── Tool Category Colors ────────────────────────────────────────────────────
# For colored badges next to tool completion lines
CATEGORY_COLORS = {
    "file":     "#38bdf8",   # blue — filesystem operations
    "code":     PURPLE,      # purple — code execution
    "git":      WARNING,     # yellow — version control
    "system":   SUCCESS,     # green — system info/control
    "memory":   ACCENT,      # pink — remember/recall
    "task":     ORANGE,      # orange — todos/reminders/pomodoro
    "project":  TEAL,        # teal — projects/bookmarks
    "discord":  "#5865F2",   # discord blue
    "spotify":  "#1DB954",   # spotify green
    "youtube":  "#ff4444",   # youtube red
    "web":      INFO,        # cyan — browser/web
    "desktop":  GRAY,        # gray — desktop automation
    "vault":    PURPLE,      # purple — password vault
    "monitor":  INDIGO,      # indigo — monitoring
}

TOOL_CATEGORIES = {
    # File operations
    "create_file": "file", "create_folder": "file", "move_item": "file",
    "rename_item": "file", "delete_item": "file", "list_directory": "file",
    "read_file": "file", "write_file": "file", "copy_file": "file",
    "append_file": "file", "read_lines": "file", "replace_lines": "file",
    "find_in_file": "file", "insert_at_line": "file", "delete_lines": "file",
    # Code
    "code_run_python": "code", "code_run_powershell": "code",
    "code_run_node": "code", "code_test_file": "code",
    # Git
    "git_status": "git", "git_commit": "git", "git_push": "git",
    "git_pull": "git", "git_branch_list": "git", "git_branch_create": "git",
    "git_log": "git", "git_diff": "git", "git_stash": "git", "git_stash_pop": "git",
    # System
    "open_application": "system", "close_application": "system",
    "get_battery_status": "system", "get_system_info": "system",
    "get_disk_space": "system", "get_running_processes": "system",
    "set_volume": "system", "set_brightness": "system",
    "run_shell_command": "system", "take_screenshot": "system",
    # Memory
    "remember": "memory", "recall": "memory", "forget": "memory",
    "save_session_summary": "memory",
    # Tasks
    "add_reminder": "task", "list_reminders": "task", "complete_reminder": "task",
    "log_habit": "task", "get_habit_report": "task",
    "add_todo": "task", "list_todos": "task", "complete_todo": "task", "delete_todo": "task",
    "start_pomodoro": "task", "stop_pomodoro": "task", "pomodoro_status": "task",
    # Projects
    "add_project": "project", "switch_project": "project", "list_projects": "project",
    "add_project_note": "project", "get_project_notes": "project",
    "bookmark_tutorial": "project", "list_bookmarks": "project", "resume_bookmark": "project",
    "save_concept": "project", "search_concepts": "project", "list_concepts": "project",
    # Discord
    "discord_unread_summary": "discord", "discord_read_channel": "discord",
    "discord_send_message": "discord", "discord_check_mentions": "discord",
    "discord_dm_read": "discord", "discord_dm_send": "discord",
    "discord_list_servers": "discord", "discord_list_channels": "discord",
    "discord_server_info": "discord", "discord_online_members": "discord",
    "discord_member_info": "discord",
    # Spotify
    "spotify_play": "spotify", "spotify_pause": "spotify",
    "spotify_resume": "spotify", "spotify_skip": "spotify",
    "spotify_previous": "spotify", "spotify_volume": "spotify",
    "spotify_current_track": "spotify", "spotify_queue_add": "spotify",
    "spotify_create_playlist": "spotify", "spotify_liked_songs": "spotify",
    # YouTube
    "youtube_bookmark_current": "youtube", "youtube_bookmarks_list": "youtube",
    "youtube_bookmark_open": "youtube", "youtube_bookmark_delete": "youtube",
    # Web
    "open_url": "web", "search_youtube": "web", "google_search": "web",
    "web_navigate": "web", "web_click": "web", "web_type": "web",
    "web_get_text": "web", "web_get_html": "web", "web_get_url": "web",
    "web_screenshot": "web",
    # Desktop automation
    "get_mouse_position": "desktop", "get_screen_size": "desktop",
    "mouse_move": "desktop", "scroll": "desktop", "keyboard_hotkey": "desktop",
    "mouse_click": "desktop", "mouse_double_click": "desktop",
    "mouse_right_click": "desktop", "mouse_drag": "desktop",
    "type_text": "desktop", "keyboard_press": "desktop",
    # Vault
    "vault_save": "vault", "vault_get": "vault", "vault_get_password": "vault",
    "vault_list": "vault", "vault_delete": "vault", "vault_lock": "vault",
    # Monitoring
    "screenshot_annotate": "monitor", "screenshot_compare": "monitor",
    "screenshot_annotate_file": "monitor", "check_screen_context": "monitor",
    "network_status": "monitor", "network_speedtest": "monitor",
    "log_health_nudge": "monitor", "sense_stuck": "monitor",
    "watch_process": "monitor", "get_active_renders": "monitor",
    # Journal/misc
    "journal_read": "task", "journal_search": "task",
    "journal_summary": "task", "journal_write_quick": "task",
    "self_update_prompt": "system", "set_dnd_mode": "system",
    "schedule_task": "task", "cancel_scheduled_task": "task",
    # Robin
    "robin_status": "monitor", "robin_start": "monitor", "robin_stop": "monitor",
    "robin_logs": "monitor", "robin_test": "monitor", "robin_compare": "monitor",
    # Anime/Budget
    "anime_add": "task", "anime_log_episode": "task",
    "anime_status": "task", "anime_list": "task", "anime_update_status": "task",
    "budget_set": "task", "budget_expense": "task",
    "budget_income": "task", "budget_summary": "task", "budget_recent": "task",
}

# ── Box Styles ───────────────────────────────────────────────────────────
# For use with rich.table.Table / rich.panel.Panel box parameter
from rich import box as _box

BOX_THIN    = _box.ROUNDED       # rounded corners, thin lines
BOX_SQUARE  = _box.SQUARE        # straight corners
BOX_MINIMAL = _box.MINIMAL       # no border lines
BOX_HEAVY   = _box.HEAVY         # thick lines
BOX_NONE    = _box.SIMPLE        # only horizontal rules

# ── Spacing & Layout ─────────────────────────────────────────────────────
PADDING      = 1       # internal panel padding
MARGIN       = 1       # space between elements
MAX_WIDTH    = 92      # max content width (centered in wider terminals)
STATUS_WIDTH = 140     # status bar width
DIVIDER_CHAR = "─"     # light horizontal line
DIVIDER_BOLD = "━"     # heavy horizontal line
BULLET       = "•"     # list bullet
ARROW        = "▸"     # arrow indicator
SEPARATOR    = "│"     # vertical separator (thin)
SEP_BOLD     = "┃"     # vertical separator (bold)
PROMPT_CHAR  = "❯"     # input prompt character

# ── Spinner / Animation ─────────────────────────────────────────────────
SPINNER_STYLE   = "arc"        # spinner for tool execution
THINKING_STYLE  = "dots"       # spinner for LLM thinking

# ── Glow / Shadow Styles ─────────────────────────────────────────────────
# Rich doesn't natively support glow, but we emulate it with layered colors
GLOW_ACCENT  = f"bold {ACCENT_BRIGHT} on {ACCENT_DEEP}"
GLOW_SUCCESS = f"bold {SUCCESS} on {SUCCESS_DIM}"
GLOW_ERROR   = f"bold {ERROR} on {ERROR_DIM}"
GLOW_INFO    = f"bold {INFO} on {INFO_DIM}"

# ── Quick Tips (rotating startup footer) ─────────────────────────────────
QUICK_TIPS = [
    "Try `/mode code` for developer mode with enhanced code features",
    "Say `clear` to reset the screen, `reset` to clear conversation history",
    "Drag & drop an image into the terminal for visual analysis",
    "Use `/model <name>` to switch LLM models on the fly",
    "Say `notifications` to see your alert history",
    "Try `$discord servers` for quick Discord commands",
    "Aria remembers! Ask her to `remember` anything important",
    "Say `unlock vault` to access your encrypted password manager",
    "Type `/help` to see all available commands and features",
    "Aria can run Python, PowerShell, and Node.js code directly",
]


# ── Utility Functions ────────────────────────────────────────────────────

def get_mood_config(energy: int, affection: int) -> dict:
    """Derive mood from energy/affection axes."""
    if affection < 35:
        key = "hurt"
    elif affection < 70:
        key = "lonely" if energy < 45 else "content"
    else:
        key = "worried" if energy < 45 else "happy"
    return MOOD_CONFIGS[key]


def get_mode_config(mode: str) -> dict:
    """Look up a mode config, falling back to normal."""
    return MODE_CONFIGS.get(mode.lower(), MODE_CONFIGS["normal"])


def get_tool_category(tool_name: str) -> tuple:
    """Get the category and color for a tool. Returns (category, color)."""
    cat = TOOL_CATEGORIES.get(tool_name, "system")
    color = CATEGORY_COLORS.get(cat, TEXT_MUTED)
    return cat, color
