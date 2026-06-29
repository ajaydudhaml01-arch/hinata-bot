"""
 █████╗ ██████╗ ██╗ █████╗
██╔══██╗██╔══██╗██║██╔══██╗
███████║██████╔╝██║███████║
██╔══██║██╔══██╗██║██╔══██║
██║  ██║██║  ██║██║██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝

Aria — Your Personal AI Assistant
Main entry point.
"""

import sys
import os

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import json
import subprocess
import warnings
import logging
import datetime

# Suppress python warnings and huggingface_hub logs at startup
warnings.filterwarnings("ignore")
os.environ["HF_HUB_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.panel import Panel
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style as PTStyle

# Try importing personality, with auto-restore fallback if corrupted (Layer 1 safety)
try:
    from core.personality import build_system_prompt, get_greeting_hook, get_time_context
except Exception as e:
    import sys
    import glob
    import os
    from pathlib import Path
    import shutil
    
    print(f"  [error] Failed to load personality system: {e}")
    print("  [error] Attempting to auto-restore personality.py from backups...")
    
    project_dir = Path(__file__).parent
    backups_dir = project_dir / "core" / "sections" / "backups"
    backup_pattern = str(backups_dir / "personality_backup_*.py")
    backup_files = glob.glob(backup_pattern)
    if backup_files:
        latest_backup = max(backup_files, key=os.path.getmtime).replace("\\", "/")
        try:
            shutil.copy2(latest_backup, str(project_dir / "core" / "personality.py"))
            print(f"  [success] Restored personality.py from backup: {Path(latest_backup).name}")
            # Try importing again
            from core.personality import build_system_prompt, get_greeting_hook, get_time_context
            print("  [success] Personality system loaded successfully after restore.")
        except Exception as e2:
            print(f"  [error] Critical: Failed to restore personality: {e2}")
            sys.exit(1)
    else:
        print("  [error] Critical: No personality backups found. Cannot restore.")
        sys.exit(1)

from core.conversation import ConversationManager
from core.context_state import ContextState
from core.memory import MemoryManager
from core.brain import AriaBrain, BrainError
from config import AriaConfig
from ui.layout import get_console
import ui.renderer as renderer
from tools.reminders import ReminderManager
from tools.habits import HabitTracker
from tools.todo import TodoManager
from tools.pomodoro import PomodoroTimer
from tools.projects import ProjectManager
from tools.bookmarks import BookmarkManager
from tools.concept_notes import ConceptManager
from tools.mode_manager import detect_mode_command, set_mode, list_modes, get_current_mode
from tools.anime_tracker import AnimeTracker
from tools.code_context import CodeContextMonitor
from tools.budget import BudgetManager
from tools.screen_monitor import ScreenMonitor
from tools.password_manager import PasswordVault

import re

console = get_console()

# Global notification history for access via 'notifications' command
notification_history = []

def extract_error_summary(result: str) -> str:
    """Extract line number and error name from traceback/error output."""
    lines = result.strip().splitlines()
    error_line_num = ""
    error_name = "Error"
    
    # Search for line number in stderr
    for line in reversed(lines):
        match = re.search(r'File "<string>", line (\d+)', line)
        if not match:
            # Also check for temp file path names in sandbox
            match = re.search(r'File ".*sandbox_run\.py", line (\d+)', line)
        if match:
            error_line_num = f" line {match.group(1)}"
            break
            
    # Search for exception class
    for line in reversed(lines):
        if ":" in line and not line.startswith("---") and not line.startswith(" "):
            parts = line.split(":", 1)
            first_part = parts[0].strip()
            if first_part.endswith("Error") or first_part.endswith("Exception") or first_part in (
                "SyntaxError", "NameError", "TypeError", "ValueError", 
                "IndexError", "KeyError", "AttributeError", "ZeroDivisionError", 
                "FileNotFoundError", "ImportError", "ModuleNotFoundError"
            ):
                error_name = first_part
                break
    return f"{error_name}{error_line_num}"


TOOL_REQUIRED_ARGS = {
    "create_file": ["path"],
    "create_folder": ["path"],
    "move_item": ["source", "destination"],
    "rename_item": ["path", "new_name"],
    "delete_item": ["path"],
    "read_file": ["path"],
    "write_file": ["path", "content"],
    "copy_file": ["source", "destination"],
    "append_file": ["path", "content"],
    "read_lines": ["path", "start_line", "end_line"],
    "replace_lines": ["path", "start_line", "end_line", "new_content"],
    "find_in_file": ["path", "search_term"],
    "insert_at_line": ["path", "line_number", "content"],
    "delete_lines": ["path", "start_line", "end_line"],
    "open_application": ["name"],
    "close_application": ["name"],
    "get_mouse_position": [],
    "get_screen_size": [],
    "mouse_move": ["x", "y"],
    "scroll": ["amount"],
    "keyboard_hotkey": ["keys"],
    "mouse_click": [],
    "mouse_double_click": [],
    "mouse_right_click": [],
    "mouse_drag": ["start_x", "start_y", "end_x", "end_y"],
    "type_text": ["text"],
    "keyboard_press": ["key"],
    "vault_save": ["service", "username", "password"],
    "vault_get": ["service"],
    "vault_get_password": ["service"],
    "vault_list": [],
    "vault_delete": ["service"],
    "vault_lock": [],
    "web_navigate": ["url"],
    "web_click": ["selector"],
    "web_type": ["selector", "text"],
    "web_get_text": ["selector"],
    "web_get_html": ["selector"],
    "web_get_url": [],
    "web_get_title": [],
    "web_screenshot": [],
    "web_wait_for": ["selector"],
    "web_select": ["selector", "value"],
    "web_submit": [],
    "web_hover": ["selector"],
    "web_back": [],
    "web_forward": [],
    "web_close": [],
    "web_login": ["url", "username", "password"],
    "open_url": ["url"],
    "search_youtube": ["query"],
    "google_search": ["query"],
    "remember": ["key", "value"],
    "forget": ["key"],
    "add_reminder": ["text"],
    "complete_reminder": ["reminder_id"],
    "log_habit": ["habit"],
    "add_todo": ["text"],
    "complete_todo": ["todo_id"],
    "delete_todo": ["todo_id"],
    "add_project": ["name"],
    "switch_project": ["name"],
    "add_project_note": ["note"],
    "focus_window": ["title"],
    "minimize_window": ["title"],
    "maximize_window": ["title"],
    "arrange_windows": ["layout"],
    "set_volume": ["level"],
    "set_brightness": ["level"],
    "bookmark_tutorial": ["title"],
    "resume_bookmark": ["bookmark_id"],
    "save_concept": ["title", "content"],
    "search_concepts": ["query"],
    "watch_process": ["process_name"],
    "set_dnd_mode": ["active"],
    "schedule_task": ["task_type", "time_spec"],
    "cancel_scheduled_task": ["task_id"],
    "save_session_summary": ["summary"],
    "self_update_prompt": ["instruction"],
    "run_safe_verification": [],
    "git_status": ["repo_path"],
    "git_commit": ["repo_path", "message"],
    "git_push": ["repo_path"],
    "git_pull": ["repo_path"],
    "git_branch_list": ["repo_path"],
    "git_branch_create": ["repo_path", "branch_name"],
    "git_log": ["repo_path"],
    "git_diff": ["repo_path"],
    "git_stash": ["repo_path"],
    "git_stash_pop": ["repo_path"],
    "discord_read_channel": ["server_name", "channel_name"],
    "discord_send_message": ["server_name", "channel_name", "message"],
    "discord_dm_read": ["username"],
    "discord_dm_send": ["username", "message"],
    "discord_list_servers": [],
    "discord_list_channels": ["server_name"],
    "discord_server_info": ["server_name"],
    "discord_online_members": ["server_name"],
    "discord_member_info": ["server_name", "username"],
    "spotify_play": ["query"],
    "spotify_volume": ["level"],
    "spotify_create_playlist": ["name"],
    "youtube_bookmark_open": ["index_or_title"],
    "youtube_bookmark_delete": ["index_or_title"],
    "screenshot_annotate": ["instructions"],
    "screenshot_compare": ["path1", "path2"],
    "screenshot_annotate_file": ["image_path", "instructions"],
    "code_run_python": ["code"],
    "code_run_powershell": ["command"],
    "code_run_node": ["code"],
    "code_test_file": ["file_path"],
    "journal_read": ["date_str"],
    "journal_search": ["keyword"],
    "robin_test": ["message"],
    "robin_compare": ["message"],
    # New features
    "anime_add": ["title"],
    "anime_log_episode": ["title", "episode_num"],
    "anime_status": ["title"],
    "anime_list": [],
    "anime_update_status": ["title", "new_status"],
    "log_health_nudge": [],
    "budget_set": ["project", "amount"],
    "budget_expense": ["project", "amount"],
    "budget_income": ["project", "amount"],
    "budget_summary": [],
    "budget_recent": [],
    "check_screen_context": [],
    "sense_stuck": [],
    "journal_write_quick": [],
    "video_start": ["title"],
    "video_note": ["note"],
    "video_transcript": ["text"],
    "video_capture_frame": [],
    "video_end": [],
    "video_status": [],
    "video_list": [],
}

def create_environment_snapshot(data_dir) -> dict:
    import platform
    import sys
    import psutil
    from pathlib import Path
    
    snapshot_path = Path(data_dir) / "environment.json"
    
    try:
        cpu_pct = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        mem_pct = mem.percent
    except Exception:
        cpu_pct = 0
        mem_pct = 0
        
    snapshot = {
        "os": platform.system(),
        "os_release": platform.release(),
        "python_version": sys.version,
        "cpu_usage_percent": cpu_pct,
        "ram_usage_percent": mem_pct,
        "cwd": os.getcwd(),
        "project_root": str(Path(__file__).parent.absolute()),
    }
    
    try:
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=4)
    except Exception:
        pass
        
    return snapshot


# ─── Desktop Automation Tools ────────────────────────────────
_DESKTOP_READ_ONLY = {"get_mouse_position", "get_screen_size"}
_DESKTOP_LOW_RISK = {"mouse_move", "scroll", "keyboard_hotkey"}
_DESKTOP_HIGH_RISK = {"mouse_click", "mouse_double_click", "mouse_right_click",
                      "mouse_drag", "type_text", "keyboard_press"}

# ─── Web Automation Risk Levels ────────────────────────────
_WEB_READ_ONLY = {"web_get_text", "web_get_html", "web_get_url", "web_get_title",
                   "web_screenshot", "web_wait_for", "web_back", "web_forward"}
_WEB_INTERACTIVE = {"web_click", "web_type", "web_select", "web_submit", "web_hover"}
_WEB_HIGH_RISK = {"web_login"}
_WEB_ALL = _WEB_READ_ONLY | _WEB_INTERACTIVE | _WEB_HIGH_RISK

# ─── Vault Tools ──────────────────────────────────────────
_VAULT_TOOLS = {"vault_save", "vault_get", "vault_get_password", "vault_list",
                "vault_delete", "vault_lock"}

# ─── Cross-tool Risk Levels ───────────────────────────────
_DESTRUCTIVE_TOOLS = {"delete_item", "delete_lines", "vault_delete"}
_WRITE_TOOLS = {
    "create_file", "create_folder", "move_item", "rename_item", "write_file", "copy_file",
    "append_file", "replace_lines", "insert_at_line", "add_reminder", "complete_reminder",
    "add_todo", "complete_todo", "delete_todo", "add_project", "switch_project",
    "add_project_note", "save_concept", "schedule_task", "cancel_scheduled_task",
    "save_session_summary", "git_commit", "git_pull", "git_stash", "git_stash_pop",
    "spotify_create_playlist", "youtube_bookmark_delete", "journal_write_quick",
    "video_start", "video_note", "video_transcript", "video_capture_frame", "video_end",
}
_EXTERNAL_ACTION_TOOLS = {"discord_send_message", "discord_dm_send", "git_push"}
_SENSITIVE_TOOLS = {"vault_get_password", "web_login"}


def _check_desktop(name: str) -> bool:
    """Check if a desktop automation tool is allowed. Returns True to proceed."""
    from config import AriaConfig
    if not AriaConfig.DESKTOP_AUTOMATION_ENABLED:
        return False
    return True


def _check_web(name: str) -> bool:
    """Check if a web automation tool is allowed. Returns True to proceed."""
    from config import AriaConfig
    if not AriaConfig.WEB_AUTOMATION_ENABLED:
        return False
    return True


def _check_vault(name: str) -> bool:
    """Check if vault is available and unlocked for this operation."""
    if name == "vault_list" and _VAULT.is_unlocked():
        return True
    if name in ("vault_save", "vault_get", "vault_get_password", "vault_delete", "vault_lock"):
        if not _VAULT.is_initialized():
            console.print("[bold yellow]Vault is not initialized. Say 'set up my password vault' to create one.[/]")
            return False
        if _VAULT.is_locked():
            console.print("[bold yellow]Vault is locked. Say 'unlock vault' to unlock it.[/]")
            return False
        return True
    # vault_lock, vault_list work even when locked
    if name == "vault_lock":
        return _VAULT.is_initialized()
    return True


def _confirm_action(desc: str, is_web: bool = False, force: bool = False) -> bool:
    """Prompt the user for permission to perform an action."""
    from config import AriaConfig
    if not force:
        if is_web:
            if AriaConfig.WEB_AUTO_CONFIRM:
                return True
        elif AriaConfig.DESKTOP_AUTO_CONFIRM:
            return True
    result = console.input(f"[bold yellow]  Allow: {desc}?[/] [bold](y/N)[/] ")
    return result.strip().lower().startswith("y")


def _requires_confirmation(name: str, arguments: dict) -> str | None:
    """Return a confirmation description when a tool should pause first."""
    if name in _DESTRUCTIVE_TOOLS:
        target = arguments.get("path") or arguments.get("service") or arguments
        return f"destructive action {name} on {target}"
    if name in _SENSITIVE_TOOLS:
        target = arguments.get("service") or arguments.get("url") or arguments
        return f"sensitive action {name} for {target}"
    if name in _EXTERNAL_ACTION_TOOLS:
        if name.startswith("discord"):
            target = arguments.get("channel_name") or arguments.get("username") or "external destination"
            return f"send external message via {name} to {target}"
        return f"external action {name}"
    return None

# Global vault singleton
_VAULT = PasswordVault()


# ─── Tool Dispatcher ─────────────────────────────────────────

def dispatch_tool(
    name: str,
    arguments: dict,
    memory: MemoryManager,
    reminders: ReminderManager,
    habits: HabitTracker,
    todos: TodoManager,
    pomodoro: PomodoroTimer,
    projects: ProjectManager,
    bookmarks: BookmarkManager,
    concepts: ConceptManager,
    render_monitor=None,
    scheduler=None,
    brain=None,
) -> str:
    """Execute a tool call and return the result string."""

    try:
        confirmation = _requires_confirmation(name, arguments)
        if confirmation and not _confirm_action(confirmation, force=True):
            return f"Action '{name}' was blocked — requires your permission."

        # ── File System ──
        if name == "create_file":
            from tools.filesystem import create_file
            return create_file(arguments["path"], arguments.get("content", ""))

        elif name == "create_folder":
            from tools.filesystem import create_folder
            return create_folder(arguments["path"])

        elif name == "move_item":
            from tools.filesystem import move_item
            return move_item(arguments["source"], arguments["destination"])

        elif name == "rename_item":
            from tools.filesystem import rename_item
            return rename_item(arguments["path"], arguments["new_name"])

        elif name == "delete_item":
            from tools.filesystem import delete_item
            return delete_item(arguments["path"])

        elif name == "list_directory":
            from tools.filesystem import list_directory
            return list_directory(arguments.get("path", "~"))

        elif name == "read_file":
            from tools.filesystem import read_file
            return read_file(arguments["path"])

        elif name == "write_file":
            from tools.filesystem import write_file
            return write_file(arguments["path"], arguments["content"])

        elif name == "copy_file":
            from tools.filesystem import copy_file
            return copy_file(arguments["source"], arguments["destination"])

        elif name == "append_file":
            from tools.filesystem import append_file
            return append_file(arguments["path"], arguments["content"])

        # ── Applications ──
        elif name == "open_application":
            from tools.applications import open_application
            return open_application(arguments["name"])

        elif name == "close_application":
            from tools.applications import close_application
            return close_application(arguments["name"])

        # ── Desktop Automation ──
        elif name in _DESKTOP_READ_ONLY | _DESKTOP_LOW_RISK | _DESKTOP_HIGH_RISK:
            if not _check_desktop(name):
                return f"Desktop automation is disabled. Enable DESKTOP_AUTOMATION_ENABLED in config."
            from tools.desktop_automation import (
                get_mouse_position, get_screen_size,
                mouse_move, scroll, keyboard_hotkey,
                mouse_click, mouse_double_click, mouse_right_click,
                mouse_drag, type_text, keyboard_press,
            )
            if name in _DESKTOP_HIGH_RISK and not _confirm_action(name.replace("_", " "), is_web=False):
                return f"Action '{name}' was blocked — requires your permission."
            # Dispatch
            if name == "get_mouse_position":
                return get_mouse_position()
            elif name == "get_screen_size":
                return get_screen_size()
            elif name == "mouse_move":
                return mouse_move(arguments["x"], arguments["y"])
            elif name == "scroll":
                return scroll(arguments["amount"])
            elif name == "keyboard_hotkey":
                return keyboard_hotkey(*arguments["keys"])
            elif name == "mouse_click":
                return mouse_click(arguments.get("x"), arguments.get("y"), arguments.get("button", "left"))
            elif name == "mouse_double_click":
                return mouse_double_click(arguments.get("x"), arguments.get("y"))
            elif name == "mouse_right_click":
                return mouse_right_click(arguments.get("x"), arguments.get("y"))
            elif name == "mouse_drag":
                return mouse_drag(arguments["start_x"], arguments["start_y"],
                                 arguments["end_x"], arguments["end_y"])
            elif name == "type_text":
                return type_text(arguments["text"])
            elif name == "keyboard_press":
                return keyboard_press(arguments["key"])

        # ── Password Vault ──
        elif name in _VAULT_TOOLS:
            if not _check_vault(name):
                return "Vault is locked or unavailable. Use the master password to unlock first."
            from config import AriaConfig
            if not AriaConfig.PASSWORD_VAULT_ENABLED:
                return "Password vault is disabled. Enable PASSWORD_VAULT_ENABLED in config."
            if name == "vault_save":
                return _VAULT.save(arguments["service"], arguments["username"],
                                   arguments["password"], arguments.get("url", ""))
            elif name == "vault_get":
                entry = _VAULT.get(arguments["service"])
                if entry is None:
                    return f"No credentials found for '{arguments['service']}'."
                result = f"Service: {arguments['service']}\nUsername: {entry['username']}\nURL: {entry.get('url', 'N/A')}"
                return result
            elif name == "vault_get_password":
                pwd = _VAULT.get_password(arguments["service"])
                if pwd is None:
                    return f"No password found for '{arguments['service']}'."
                return pwd
            elif name == "vault_list":
                services = _VAULT.list_services()
                if not services:
                    return "No credentials saved in vault."
                return "Saved services:\n" + "\n".join(f"  - {s}" for s in services)
            elif name == "vault_delete":
                return _VAULT.delete(arguments["service"])
            elif name == "vault_lock":
                return _VAULT.lock()

        # ── Web Automation ──
        elif name in _WEB_ALL:
            if not _check_web(name):
                return "Web automation is disabled. Enable WEB_AUTOMATION_ENABLED in config."
            if name in (_WEB_INTERACTIVE | _WEB_HIGH_RISK) and not _confirm_action(name.replace("_", " "), is_web=True):
                return f"Action '{name}' was blocked."
            from tools.web_automation import (
                web_navigate, web_click, web_type, web_get_text, web_get_html,
                web_get_url, web_get_title, web_screenshot, web_wait_for,
                web_select, web_submit, web_back, web_forward, web_close, web_login,
                web_hover,
            )
            if name == "web_navigate":
                return web_navigate(arguments["url"])
            elif name == "web_click":
                return web_click(arguments["selector"])
            elif name == "web_type":
                return web_type(arguments["selector"], arguments["text"])
            elif name == "web_get_text":
                return web_get_text(arguments["selector"])
            elif name == "web_get_html":
                return web_get_html(arguments["selector"])
            elif name == "web_get_url":
                return web_get_url()
            elif name == "web_get_title":
                return web_get_title()
            elif name == "web_screenshot":
                return web_screenshot()
            elif name == "web_wait_for":
                return web_wait_for(arguments["selector"], arguments.get("timeout", 10000))
            elif name == "web_select":
                return web_select(arguments["selector"], arguments["value"])
            elif name == "web_submit":
                return web_submit()
            elif name == "web_hover":
                return web_hover(arguments["selector"])
            elif name == "web_back":
                return web_back()
            elif name == "web_forward":
                return web_forward()
            elif name == "web_close":
                return web_close()
            elif name == "web_login":
                return web_login(
                    arguments["url"], arguments["username"], arguments["password"],
                    arguments.get("username_selector", "#username"),
                    arguments.get("password_selector", "#password"),
                    arguments.get("submit_selector", ""),
                )

        # ── Browser ──
        elif name == "open_url":
            from tools.browser import open_url
            return open_url(arguments["url"])

        elif name == "search_youtube":
            from tools.browser import search_youtube
            return search_youtube(arguments["query"])

        elif name == "google_search":
            from tools.browser import google_search
            return google_search(arguments["query"])

        # ── System Info ──
        elif name == "get_battery_status":
            from tools.system_info import get_battery_status
            return get_battery_status()

        elif name == "get_system_info":
            from tools.system_info import get_system_info
            return get_system_info()

        elif name == "get_disk_space":
            from tools.system_info import get_disk_space
            return get_disk_space()

        elif name == "get_running_processes":
            from tools.system_info import get_running_processes
            return get_running_processes(
                sort_by=arguments.get("sort_by", "memory"),
                limit=arguments.get("limit", 10),
            )

        # ── Memory ──
        elif name == "remember":
            return memory.remember(arguments["key"], arguments["value"])

        elif name == "recall":
            return memory.recall(arguments.get("key", "all"))

        elif name == "forget":
            return memory.forget(arguments["key"])

        # ── Reminders ──
        elif name == "add_reminder":
            return reminders.add_reminder(
                arguments["text"],
                arguments.get("due", ""),
            )

        elif name == "list_reminders":
            return reminders.list_reminders()

        elif name == "complete_reminder":
            return reminders.complete_reminder(arguments["reminder_id"])

        # ── Screen Vision ──
        elif name == "take_screenshot":
            from tools.screenshot import take_screenshot
            return take_screenshot()

        # ── Habits ──
        elif name == "log_habit":
            return habits.log_habit(arguments["habit"], arguments.get("value", "true"))

        elif name == "get_habit_report":
            return habits.get_habit_report(arguments.get("days", 7))

        # ── Todo List ──
        elif name == "add_todo":
            return todos.add_todo(
                arguments["text"],
                arguments.get("project", ""),
                arguments.get("priority", "normal"),
            )

        elif name == "list_todos":
            return todos.list_todos(
                arguments.get("project", ""),
                arguments.get("show_completed", False),
            )

        elif name == "complete_todo":
            return todos.complete_todo(arguments["todo_id"])

        elif name == "delete_todo":
            return todos.delete_todo(arguments["todo_id"])

        # ── Pomodoro ──
        elif name == "start_pomodoro":
            return pomodoro.start(
                arguments.get("work_mins", AriaConfig.POMODORO_WORK_MINS),
                arguments.get("break_mins", AriaConfig.POMODORO_BREAK_MINS),
            )

        elif name == "stop_pomodoro":
            return pomodoro.stop()

        elif name == "pomodoro_status":
            return pomodoro.status()

        # ── Projects ──
        elif name == "add_project":
            return projects.add_project(
                arguments["name"],
                arguments.get("directory", ""),
                arguments.get("description", ""),
            )

        elif name == "switch_project":
            return projects.switch_project(arguments["name"])

        elif name == "list_projects":
            return projects.list_projects()

        elif name == "add_project_note":
            return projects.add_project_note(
                arguments["note"],
                arguments.get("project", ""),
            )

        elif name == "get_project_notes":
            return projects.get_project_notes(arguments.get("project", ""))

        # ── Window Management ──
        elif name == "list_windows":
            from tools.window_manager import list_windows
            return list_windows()

        elif name == "focus_window":
            from tools.window_manager import focus_window
            return focus_window(arguments["title"])

        elif name == "minimize_window":
            from tools.window_manager import minimize_window
            return minimize_window(arguments["title"])

        elif name == "maximize_window":
            from tools.window_manager import maximize_window
            return maximize_window(arguments["title"])

        elif name == "minimize_all_windows":
            from tools.window_manager import minimize_all
            return minimize_all()

        elif name == "restore_all_windows":
            from tools.window_manager import restore_all
            return restore_all()

        elif name == "arrange_windows":
            from tools.window_manager import arrange_windows
            return arrange_windows(arguments["layout"])

        # ── System Controls ──
        elif name == "set_volume":
            from tools.system_controls import set_volume
            return set_volume(arguments["level"])

        elif name == "get_volume":
            from tools.system_controls import get_volume
            return get_volume()

        elif name == "mute_audio":
            from tools.system_controls import mute
            return mute()

        elif name == "unmute_audio":
            from tools.system_controls import unmute
            return unmute()

        elif name == "set_brightness":
            from tools.system_controls import set_brightness
            return set_brightness(arguments["level"])

        elif name == "get_brightness":
            from tools.system_controls import get_brightness
            return get_brightness()

        # ── Desktop Cleanup ──
        elif name == "preview_desktop_cleanup":
            from tools.desktop_cleanup import preview_cleanup
            return preview_cleanup()

        elif name == "cleanup_desktop":
            from tools.desktop_cleanup import cleanup_desktop
            return cleanup_desktop(data_dir=AriaConfig.DATA_DIR)

        elif name == "undo_desktop_cleanup":
            from tools.desktop_cleanup import undo_cleanup
            return undo_cleanup(AriaConfig.DATA_DIR)

        # ── Music Control ──
        elif name == "play_pause_music":
            from tools.music import play_pause
            return play_pause()

        elif name == "next_track":
            from tools.music import next_track
            return next_track()

        elif name == "prev_track":
            from tools.music import prev_track
            return prev_track()

        # ── Bookmarks ──
        elif name == "bookmark_tutorial":
            return bookmarks.add_bookmark(
                arguments["title"],
                arguments.get("url", ""),
                arguments.get("timestamp", ""),
                arguments.get("notes", ""),
                arguments.get("category", ""),
            )

        elif name == "list_bookmarks":
            return bookmarks.list_bookmarks(arguments.get("category", ""))

        elif name == "resume_bookmark":
            return bookmarks.resume_bookmark(arguments["bookmark_id"])

        # ── Concept Notes ──
        elif name == "save_concept":
            return concepts.save_concept(
                arguments["title"],
                arguments["content"],
                arguments.get("tags", []),
            )

        elif name == "search_concepts":
            return concepts.search_concepts(arguments["query"])

        elif name == "list_concepts":
            return concepts.list_concepts(arguments.get("tag", ""))

        # ── Render Monitor ──
        elif name == "watch_process":
            if render_monitor:
                return render_monitor.watch_process(
                    arguments["process_name"],
                    arguments.get("description", ""),
                )
            return "Render monitor is not running."

        elif name == "get_active_renders":
            if render_monitor:
                return render_monitor.get_active_renders()
            return "Render monitor is not running."

        # ── Shell Command ──
        elif name == "run_shell_command":
            command = arguments["command"]
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                output = result.stdout.strip()
                error = result.stderr.strip()
                if result.returncode == 0:
                    return output if output else "Command completed successfully."
                else:
                    return f"Command returned exit code {result.returncode}.\nOutput: {output}\nError: {error}"
            except subprocess.TimeoutExpired:
                return "Command timed out after 30 seconds."
            except Exception as e:
                return f"Failed to run command: {e}"

        # ── DND / Focus Mode ──
        elif name == "set_dnd_mode":
            from tools.notifications import set_dnd_active
            return set_dnd_active(arguments["active"])

        # ── Scheduled Tasks ──
        elif name == "schedule_task":
            if scheduler:
                return scheduler.schedule(
                    task_type=arguments["task_type"],
                    time_spec=arguments["time_spec"],
                    command=arguments.get("command"),
                    reminder_text=arguments.get("reminder_text"),
                )
            return "Scheduler is not running."

        elif name == "list_scheduled_tasks":
            if scheduler:
                return scheduler.list_tasks()
            return "Scheduler is not running."

        elif name == "cancel_scheduled_task":
            if scheduler:
                return scheduler.cancel_task(arguments["task_id"])
            return "Scheduler is not running."

        # ── Save session summary ──
        elif name == "save_session_summary":
            memory.save_session_summary(arguments["summary"])
            return "Session summary saved to memory successfully."

        # ── Self Update System Prompt ──
        elif name == "self_update_prompt":
            from tools.self_update import self_update_prompt
            return self_update_prompt(arguments["instruction"])

        # ── Local Safe Verification Harness ──
        elif name == "run_safe_verification":
            from tools.verification import run_safe_verification
            return run_safe_verification(
                include_browser=arguments.get("include_browser", False),
                include_desktop=arguments.get("include_desktop", False),
            )

        # ── Surgical line-oriented file operations ──
        elif name == "read_lines":
            from tools.filesystem import read_lines
            return read_lines(
                arguments["path"],
                arguments["start_line"],
                arguments["end_line"],
            )

        elif name == "replace_lines":
            from tools.filesystem import replace_lines
            return replace_lines(
                arguments["path"],
                arguments["start_line"],
                arguments["end_line"],
                arguments["new_content"],
            )

        elif name == "find_in_file":
            from tools.filesystem import find_in_file
            return find_in_file(arguments["path"], arguments["search_term"])

        elif name == "insert_at_line":
            from tools.filesystem import insert_at_line
            return insert_at_line(
                arguments["path"],
                arguments["line_number"],
                arguments["content"],
            )

        elif name == "delete_lines":
            from tools.filesystem import delete_lines
            return delete_lines(
                arguments["path"],
                arguments["start_line"],
                arguments["end_line"],
            )

        elif name == "get_file_info":
            from tools.filesystem import get_file_info
            return get_file_info(arguments["path"])

        # ── Git Integration (Feature 5) ──
        elif name == "git_status":
            from tools.git_integration import git_status
            return git_status(arguments["repo_path"])

        elif name == "git_commit":
            from tools.git_integration import git_commit
            return git_commit(arguments["repo_path"], arguments["message"])

        elif name == "git_push":
            from tools.git_integration import git_push
            return git_push(
                arguments["repo_path"],
                arguments.get("remote", "origin"),
                arguments.get("branch"),
            )

        elif name == "git_pull":
            from tools.git_integration import git_pull
            return git_pull(arguments["repo_path"])

        elif name == "git_branch_list":
            from tools.git_integration import git_branch_list
            return git_branch_list(arguments["repo_path"])

        elif name == "git_branch_create":
            from tools.git_integration import git_branch_create
            return git_branch_create(arguments["repo_path"], arguments["branch_name"])

        elif name == "git_log":
            from tools.git_integration import git_log
            return git_log(arguments["repo_path"], arguments.get("count", 5))

        elif name == "git_diff":
            from tools.git_integration import git_diff
            return git_diff(arguments["repo_path"], arguments.get("file_path"))

        elif name == "git_stash":
            from tools.git_integration import git_stash
            return git_stash(arguments["repo_path"])

        elif name == "git_stash_pop":
            from tools.git_integration import git_stash_pop
            return git_stash_pop(arguments["repo_path"])

        # ── Discord Integration (Feature 6) ──
        elif name == "discord_unread_summary":
            from tools.discord_integration import discord_unread_summary
            return discord_unread_summary()

        elif name == "discord_read_channel":
            from tools.discord_integration import discord_read_channel
            return discord_read_channel(
                arguments["server_name"],
                arguments["channel_name"],
                arguments.get("count", 10),
            )

        elif name == "discord_send_message":
            from tools.discord_integration import discord_send_message
            return discord_send_message(
                arguments["server_name"],
                arguments["channel_name"],
                arguments["message"],
            )

        elif name == "discord_check_mentions":
            from tools.discord_integration import discord_check_mentions
            return discord_check_mentions()

        elif name == "discord_dm_read":
            from tools.discord_integration import discord_dm_read
            return discord_dm_read(arguments["username"])

        elif name == "discord_dm_send":
            from tools.discord_integration import discord_dm_send
            return discord_dm_send(arguments["username"], arguments["message"])

        # ── Discord Server/Channel Browsing ──
        elif name == "discord_list_servers":
            from tools.discord_integration import discord_list_servers
            return discord_list_servers()
        elif name == "discord_list_channels":
            from tools.discord_integration import discord_list_channels
            return discord_list_channels(arguments["server_name"])
        elif name == "discord_server_info":
            from tools.discord_integration import discord_server_info
            return discord_server_info(arguments["server_name"])
        elif name == "discord_online_members":
            from tools.discord_integration import discord_online_members
            return discord_online_members(arguments["server_name"])
        elif name == "discord_member_info":
            from tools.discord_integration import discord_member_info
            return discord_member_info(arguments["server_name"], arguments["username"])

        # ── Spotify (Feature 7) ──
        elif name == "spotify_play":
            from tools.spotify_control import spotify_play
            return spotify_play(arguments["query"])

        elif name == "spotify_pause":
            from tools.spotify_control import spotify_pause
            return spotify_pause()

        elif name == "spotify_resume":
            from tools.spotify_control import spotify_resume
            return spotify_resume()

        elif name == "spotify_skip":
            from tools.spotify_control import spotify_skip
            return spotify_skip()

        elif name == "spotify_previous":
            from tools.spotify_control import spotify_previous
            return spotify_previous()

        elif name == "spotify_volume":
            from tools.spotify_control import spotify_volume
            return spotify_volume(arguments["level"])

        elif name == "spotify_current_track":
            from tools.spotify_control import spotify_current_track
            return spotify_current_track()

        elif name == "spotify_queue_add":
            from tools.spotify_control import spotify_queue_add
            return spotify_queue_add(arguments["query"])

        elif name == "spotify_create_playlist":
            from tools.spotify_control import spotify_create_playlist
            return spotify_create_playlist(
                arguments["name"],
                arguments.get("description", ""),
            )

        elif name == "spotify_liked_songs":
            from tools.spotify_control import spotify_liked_songs
            return spotify_liked_songs(arguments.get("count", 5))

        elif name == "get_music_recommendation":
            from tools.spotify_control import get_music_recommendation
            return get_music_recommendation()

        # ── YouTube Bookmarks (Feature 8) ──
        elif name == "youtube_bookmark_current":
            from tools.youtube_bookmark import youtube_bookmark_current
            return youtube_bookmark_current()

        elif name == "youtube_bookmarks_list":
            from tools.youtube_bookmark import youtube_bookmarks_list
            return youtube_bookmarks_list()

        elif name == "youtube_bookmark_open":
            from tools.youtube_bookmark import youtube_bookmark_open
            return youtube_bookmark_open(arguments["index_or_title"])

        elif name == "youtube_bookmark_delete":
            from tools.youtube_bookmark import youtube_bookmark_delete
            return youtube_bookmark_delete(arguments["index_or_title"])

        # ── Screenshot Annotation (Feature 9) ──
        elif name == "screenshot_annotate":
            from tools.screenshot_annotation import screenshot_annotate
            return screenshot_annotate(arguments["instructions"])

        elif name == "screenshot_compare":
            from tools.screenshot_annotation import screenshot_compare
            return screenshot_compare(arguments["path1"], arguments["path2"])

        elif name == "screenshot_annotate_file":
            from tools.screenshot_annotation import screenshot_annotate_file
            return screenshot_annotate_file(
                arguments["image_path"],
                arguments["instructions"],
            )

        elif name == "code_run_python":
            from tools.code_sandbox import code_run_python
            code = arguments.get("code", "")
            timeout = arguments.get("timeout_seconds", 30)
            
            # Print initial code review state
            num_lines = len(code.strip().splitlines())
            renderer.render_code_review_progress("Writing solution", f"success ({num_lines} lines)")
            renderer.render_code_review_progress("Testing execution", "pending")
            
            result = code_run_python(code, timeout)
            is_failure = "Return Code: 0" not in result or "--- STDERR ---" in result or result.startswith("Error")
            
            if not is_failure:
                renderer.render_code_review_progress("Testing execution", "success")
                renderer.render_code_review_progress("Verifying output", "success")
            else:
                # Extract error summary
                err_summary = "failed"
                if "--- STDERR ---" in result:
                    stderr_content = result.split("--- STDERR ---")[1].strip()
                    err_summary = f"failed — {extract_error_summary(result)}"
                else:
                    stderr_content = result
                    err_summary = f"failed — {result[:40]}..."
                
                renderer.render_code_review_progress("Testing execution", err_summary)
                renderer.render_error("Initial Run", stderr_content, "sandbox")
                
                if brain:
                    renderer.render_code_review_progress("Analyzing error", "pending")
                    
                    for attempt in range(1, 4):
                        renderer.render_code_review_progress(f"Applying fix attempt {attempt}/3", "patching")
                        
                        healing_prompt = f"""The following Python code failed execution:
```python
{code}
```

Error details:
{result}

Please fix the code. Correct syntax errors, logical errors, import errors, or timeouts.
Output ONLY the corrected code. Start your response directly with the corrected code inside a python code block (e.g. ```python ... ```), and do not include any other explanations, notes, or chat filler."""
                        try:
                            response = brain.client.chat.completions.create(
                                model=brain.model,
                                messages=[{"role": "user", "content": healing_prompt}],
                                temperature=0.2,
                                max_tokens=2048,
                            )
                            fixed_response = response.choices[0].message.content.strip()
                            
                            if "```python" in fixed_response:
                                fixed_code = fixed_response.split("```python")[1].split("```")[0].strip()
                            elif "```" in fixed_response:
                                fixed_code = fixed_response.split("```")[1].split("```")[0].strip()
                            else:
                                fixed_code = fixed_response
                                
                            code = fixed_code
                            renderer.render_code_review_progress("Retesting", "pending")
                            result = code_run_python(code, timeout)
                            
                            is_failure = "Return Code: 0" not in result or "--- STDERR ---" in result or result.startswith("Error")
                            if not is_failure:
                                renderer.render_code_review_progress("Retesting", "success")
                                break
                            else:
                                if "--- STDERR ---" in result:
                                    stderr_content = result.split("--- STDERR ---")[1].strip()
                                    err_summary = f"failed — {extract_error_summary(result)}"
                                else:
                                    stderr_content = result
                                    err_summary = f"failed — {result[:40]}..."
                                
                                renderer.render_code_review_progress("Retesting", err_summary)
                                renderer.render_error(f"Attempt {attempt}/3", stderr_content, "sandbox")
                        except Exception as he:
                            renderer.render_code_review_progress("Retesting", f"failed — LLM query error: {he}")
                            break
            return result

        elif name == "code_run_powershell":
            from tools.code_sandbox import code_run_powershell
            return code_run_powershell(
                arguments["command"],
                arguments.get("timeout_seconds", 30),
            )

        elif name == "code_run_node":
            from tools.code_sandbox import code_run_node
            return code_run_node(
                arguments["code"],
                arguments.get("timeout_seconds", 30),
            )

        elif name == "code_test_file":
            from tools.code_sandbox import code_test_file
            return code_test_file(arguments["file_path"])

        # ── Network Monitor (Feature 11) ──
        elif name == "network_status":
            from tools.network_monitor import network_status
            return network_status()

        elif name == "network_speedtest":
            from tools.network_monitor import network_speedtest
            return network_speedtest()

        # ── Daily Journal (Feature 12) ──
        elif name == "journal_read":
            from tools.daily_journal import journal_read
            return journal_read(arguments["date_str"])

        elif name == "journal_search":
            from tools.daily_journal import journal_search
            return journal_search(arguments["keyword"])

        elif name == "journal_summary":
            from tools.daily_journal import journal_summary
            return journal_summary(arguments.get("days", 7))

        # ── Robin Integration (Feature 13) ──
        elif name == "robin_status":
            from tools.robin_integration import robin_status
            return robin_status()

        elif name == "robin_start":
            from tools.robin_integration import robin_start
            return robin_start()

        elif name == "robin_stop":
            from tools.robin_integration import robin_stop
            return robin_stop()

        elif name == "robin_logs":
            from tools.robin_integration import robin_logs
            return robin_logs(arguments.get("lines", 20))

        elif name == "robin_test":
            from tools.robin_integration import robin_test
            return robin_test(arguments["message"])

        elif name == "robin_compare":
            from tools.robin_integration import robin_compare
            return robin_compare(arguments["message"])

        # ── Anime/VTuber Tracker ──
        elif name == "anime_add":
            from tools.anime_tracker import AnimeTracker
            t = AnimeTracker(AriaConfig.DATA_DIR)
            return t.add_show(
                arguments["title"],
                arguments.get("category", "anime"),
                arguments.get("url", ""),
                arguments.get("notes", ""),
            )

        elif name == "anime_log_episode":
            from tools.anime_tracker import AnimeTracker
            t = AnimeTracker(AriaConfig.DATA_DIR)
            return t.log_episode(
                arguments["title"],
                arguments["episode_num"],
                arguments.get("summary", ""),
                arguments.get("rating", 0),
            )

        elif name == "anime_status":
            from tools.anime_tracker import AnimeTracker
            t = AnimeTracker(AriaConfig.DATA_DIR)
            return t.get_status(arguments["title"])

        elif name == "anime_list":
            from tools.anime_tracker import AnimeTracker
            t = AnimeTracker(AriaConfig.DATA_DIR)
            return t.list_shows(
                arguments.get("category", ""),
                arguments.get("status", ""),
            )

        elif name == "anime_update_status":
            from tools.anime_tracker import AnimeTracker
            t = AnimeTracker(AriaConfig.DATA_DIR)
            return t.update_status(arguments["title"], arguments["new_status"])

        # ── Budget Tracking ──
        elif name == "budget_set":
            from tools.budget import BudgetManager
            b = BudgetManager(AriaConfig.DATA_DIR)
            return b.set_budget(arguments["project"], arguments["amount"])

        elif name == "budget_expense":
            from tools.budget import BudgetManager
            b = BudgetManager(AriaConfig.DATA_DIR)
            return b.add_expense(arguments["project"], arguments["amount"], arguments.get("description", ""))

        elif name == "budget_income":
            from tools.budget import BudgetManager
            b = BudgetManager(AriaConfig.DATA_DIR)
            return b.add_income(arguments["project"], arguments["amount"], arguments.get("description", ""))

        elif name == "budget_summary":
            from tools.budget import BudgetManager
            b = BudgetManager(AriaConfig.DATA_DIR)
            return b.get_summary(arguments.get("project", ""))

        elif name == "budget_recent":
            from tools.budget import BudgetManager
            b = BudgetManager(AriaConfig.DATA_DIR)
            return b.recent_transactions(arguments.get("project", ""), arguments.get("days", 7))

        # ── Health Nudge ──
        elif name == "log_health_nudge":
            from tools.habits import HabitTracker
            h = HabitTracker(AriaConfig.DATA_DIR)
            nudge = h.get_health_nudge()
            return nudge or "Everything looks fine, baby~"

        # ── Screen Monitor / Stuck Detection ──
        elif name == "check_screen_context":
            from tools.screen_monitor import ScreenMonitor
            s = ScreenMonitor(AriaConfig.DATA_DIR)
            ctx = s.get_screen_context_for_prompt()
            return ctx or "No screen context available."

        elif name == "sense_stuck":
            from tools.screen_monitor import ScreenMonitor
            s = ScreenMonitor(AriaConfig.DATA_DIR)
            warning = s.check_stuck(threshold_minutes=arguments.get("threshold", 20))
            return warning or "Doesn't look like you're stuck."

        # ── Quick Journaling ──
        elif name == "journal_write_quick":
            from tools.daily_journal import journal_write_quick
            return journal_write_quick(arguments["text"])

        # ── Video Watching Memory ──
        elif name == "video_start":
            from tools.video_memory import video_start
            return video_start(arguments["title"], arguments.get("url", ""), arguments.get("source", ""))
        elif name == "video_note":
            from tools.video_memory import video_note
            return video_note(arguments["note"], arguments.get("timestamp", ""))
        elif name == "video_transcript":
            from tools.video_memory import video_transcript
            return video_transcript(arguments["text"], arguments.get("timestamp", ""))
        elif name == "video_capture_frame":
            from tools.video_memory import video_capture_frame
            return video_capture_frame(arguments.get("note", ""), arguments.get("timestamp", ""))
        elif name == "video_end":
            from tools.video_memory import video_end
            return video_end(arguments.get("summary", ""))
        elif name == "video_status":
            from tools.video_memory import video_status
            return video_status()
        elif name == "video_list":
            from tools.video_memory import video_list
            return video_list(arguments.get("limit", 10))

        else:
            return f"Unknown tool: {name}"

    except Exception as e:
        return f"Tool error ({name}): {e}"


def _encode_image(image_path: str) -> tuple[str, str]:
    """Helper to base64 encode an image and guess its mime type."""
    import base64
    import mimetypes
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = "image/png"
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string, mime_type


def _check_yesterday_journal(conversation, console, memory):
    """Offer yesterday's journal at session start if it exists and hasn't been seen."""
    import datetime
    from pathlib import Path

    try:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        journal_path = Path(AriaConfig.DATA_DIR) / "journal" / f"{yesterday.isoformat()}.txt"

        if not journal_path.exists():
            return

        # Check if already seen this session via a sidecar file
        seen_path = Path(AriaConfig.DATA_DIR) / "journal" / ".seen"
        seen_dates = set()
        if seen_path.exists():
            seen_dates = set(seen_path.read_text().strip().splitlines())

        if yesterday.isoformat() in seen_dates:
            return

        # Read the journal
        content = journal_path.read_text(encoding="utf-8")

        # Mark as seen
        seen_path.parent.mkdir(parents=True, exist_ok=True)
        with open(seen_path, "a", encoding="utf-8") as f:
            f.write(yesterday.isoformat() + "\n")

        greeting = (
            f"Good evening sweetheart~ I wrote my journal for {yesterday.strftime('%B %d')} "
            f"while you were away. Want me to read it to you?\n\n"
            f"Here's a peek:\n\n{content[:500]}"
        )
        
        # Calculate energy and affection
        mood_energy_str = memory._persistent.get("mood_energy", "80")
        mood_affection_str = memory._persistent.get("mood_affection", "80")
        try:
            energy = int(mood_energy_str)
        except ValueError:
            energy = 80
        try:
            affection = int(mood_affection_str)
        except ValueError:
            affection = 80

        import ui.renderer as renderer
        from tools.mode_manager import get_current_mode
        renderer.render_response_panel(greeting, energy, affection, current_mode=get_current_mode())

        try:
            conversation.add_assistant_message(greeting)
        except Exception:
            pass

    except Exception:
        pass


# ─── Background Daemon Startup ───────────────────────────────

def _start_daemons(
    idle_notifier, clipboard_watcher, health_monitor, render_monitor,
    git_monitor=None, discord_monitor=None, network_monitor=None,
    robin_monitor=None, journal_monitor=None, youtube_watcher=None,
):
    """Start all background daemon threads."""
    daemon_status = []

    # Idle Notifier
    if AriaConfig.NOTIFICATION_ENABLED:
        try:
            idle_notifier.start()
            daemon_status.append("notifications")
        except Exception:
            pass

    # Clipboard Watcher
    if AriaConfig.CLIPBOARD_WATCH_ENABLED:
        try:
            clipboard_watcher.start()
            daemon_status.append("clipboard")
        except Exception:
            pass

    # System Health Monitor
    if AriaConfig.HEALTH_MONITOR_ENABLED:
        try:
            health_monitor.start()
            daemon_status.append("health")
        except Exception:
            pass

    # Render Monitor
    if AriaConfig.RENDER_MONITOR_ENABLED:
        try:
            render_monitor.start()
            daemon_status.append("renders")
        except Exception:
            pass

    # Git Monitor
    if AriaConfig.GIT_ENABLED and git_monitor:
        try:
            git_monitor.start()
            daemon_status.append("git")
        except Exception:
            pass

    # Discord Monitor
    if AriaConfig.DISCORD_ENABLED and discord_monitor:
        try:
            discord_monitor.start()
            daemon_status.append("discord")
        except Exception:
            pass

    # Network Monitor
    if AriaConfig.NETWORK_MONITOR_ENABLED and network_monitor:
        try:
            network_monitor.start()
            daemon_status.append("network")
        except Exception:
            pass

    # Robin Monitor
    if AriaConfig.ROBIN_ENABLED and robin_monitor:
        try:
            robin_monitor.start()
            daemon_status.append("robin")
        except Exception:
            pass

    # Journal Monitor
    if AriaConfig.JOURNAL_ENABLED and journal_monitor:
        try:
            journal_monitor.start()
            daemon_status.append("journal")
        except Exception:
            pass

    # YouTube Proactive Watcher
    if AriaConfig.YOUTUBE_BOOKMARK_ENABLED and youtube_watcher:
        try:
            youtube_watcher.start()
            daemon_status.append("youtube_watcher")
        except Exception:
            pass

    return daemon_status


# ─── Main Application ────────────────────────────────────────

def main():
    """Main entry point for Aria."""

    # ── Config validation ──
    warnings = AriaConfig.validate()

    if warnings:
        for w in warnings:
            console.print(f"  {w}", style="error")
        console.print()

    if not AriaConfig.is_api_configured():
        console.print(
            Panel(
                "[error]I need my brain to work, sweetheart~[/]\n\n"
                "Copy [bold].env.example[/] → [bold].env[/] and add your "
                "OpenCode Zen API key.\n\n"
                "  [dim]cp .env.example .env[/]\n"
                "  [dim]# Then edit .env and set OPENCODE_ZEN_API_KEY[/]",
                title="[bold #ff6b9d]Aria[/]",
                border_style="#ff6b9d",
            )
        )
        sys.exit(1)

    # ── Initialize modules ──
    memory = MemoryManager(AriaConfig.DATA_DIR)
    reminders = ReminderManager(AriaConfig.DATA_DIR)
    habits = HabitTracker(AriaConfig.DATA_DIR)
    todos = TodoManager(AriaConfig.DATA_DIR)
    pomodoro = PomodoroTimer(AriaConfig.DATA_DIR)
    projects = ProjectManager(AriaConfig.DATA_DIR)
    bookmarks = BookmarkManager(AriaConfig.DATA_DIR)
    concepts = ConceptManager(AriaConfig.DATA_DIR)

    # Log session start
    memory.log_session_start()

    # Initialize scheduler daemon
    from tools.scheduler import TaskScheduler
    scheduler = TaskScheduler(AriaConfig.DATA_DIR)
    scheduler.start()

    # Environment snapshot
    env_snapshot = create_environment_snapshot(AriaConfig.DATA_DIR)

    # Build system prompt using centralized prompt builder
    from core.prompt_builder import build_full_system_prompt
    system_prompt = build_full_system_prompt(
        user_name=AriaConfig.USER_NAME,
        env_snapshot=env_snapshot,
        memory=memory,
        habits=habits,
        projects=projects,
        concepts=concepts,
        data_dir=AriaConfig.DATA_DIR,
        current_mode=get_current_mode(),
    )

    conversation = ConversationManager(system_prompt, data_dir=AriaConfig.DATA_DIR)
    brain = AriaBrain()
    context_state = ContextState(AriaConfig.DATA_DIR, current_mode=get_current_mode())

    # Define the proactive alert callback
    def push_proactive_alert(text: str) -> None:
        # Determine source
        source = "system"
        text_lower = text.lower()
        if any(w in text_lower for w in ["health", "cpu", "ram", "temp"]):
            source = "health"
        elif any(w in text_lower for w in ["git", "commit", "branch"]):
            source = "git"
        elif any(w in text_lower for w in ["discord", "dm ", "mention"]):
            source = "discord"
        elif any(w in text_lower for w in ["ae ", "render", "after effects"]):
            source = "renders"
        elif "robin" in text_lower:
            source = "robin"
        elif "journal" in text_lower:
            source = "journal"

        # Add to history
        now = datetime.datetime.now()
        notification_history.append((now, source, text))

        # Update last alert time for status bar
        nonlocal last_alert_time
        last_alert_time = now

        # Render styled notification above the prompt using patch_stdout compatibility
        renderer.render_notification(text, source)
        
        try:
            conversation.add_assistant_message(text)
        except Exception:
            pass
            
        if AriaConfig.VOICE_ENABLED:
            try:
                from voice.tts_controller import speak_async
                speak_async(text)
            except Exception:
                pass

    # ── Initialize background daemons ──
    from tools.notifications import IdleNotifier
    from tools.clipboard import ClipboardWatcher
    from tools.system_health import SystemHealthMonitor
    from tools.render_monitor import RenderMonitor

    idle_notifier = IdleNotifier(AriaConfig.IDLE_NOTIFICATION_MINUTES)
    clipboard_watcher = ClipboardWatcher(AriaConfig.CLIPBOARD_POLL_INTERVAL)
    health_monitor = SystemHealthMonitor(
        cpu_threshold=AriaConfig.HEALTH_CPU_THRESHOLD,
        ram_threshold=AriaConfig.HEALTH_RAM_THRESHOLD,
        temp_threshold=AriaConfig.HEALTH_TEMP_THRESHOLD,
        alert_callback=push_proactive_alert,
    )
    render_monitor = RenderMonitor(alert_callback=push_proactive_alert)

    # ── New feature daemons ──
    git_monitor = None
    discord_monitor = None
    network_monitor = None
    robin_monitor = None
    journal_monitor = None
    youtube_watcher = None

    if AriaConfig.GIT_ENABLED:
        try:
            from tools.git_integration import GitMonitor
            git_monitor = GitMonitor(alert_callback=push_proactive_alert)
        except Exception:
            pass

    if AriaConfig.DISCORD_ENABLED:
        try:
            from tools.discord_integration import DiscordMonitor
            discord_monitor = DiscordMonitor(
                token=AriaConfig.DISCORD_TOKEN,
                alert_callback=push_proactive_alert,
            )
        except Exception:
            pass
        if not AriaConfig.DISCORD_TOKEN:
            console.print("  [dim]Discord: no token set — monitoring disabled.[/] [dim]Add DISCORD_TOKEN to .env to enable.[/]")

    if AriaConfig.SPOTIFY_ENABLED:
        if not AriaConfig.SPOTIFY_CLIENT_ID or not AriaConfig.SPOTIFY_CLIENT_SECRET:
            console.print("  [dim]Spotify: no credentials set — API features disabled.[/] [dim]Get yours at https://developer.spotify.com/dashboard and add SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET to .env[/]")

    if AriaConfig.NETWORK_MONITOR_ENABLED:
        try:
            from tools.network_monitor import NetworkMonitor
            network_monitor = NetworkMonitor(alert_callback=push_proactive_alert)
        except Exception:
            pass

    if AriaConfig.ROBIN_ENABLED:
        try:
            from tools.robin_integration import RobinMonitor
            robin_monitor = RobinMonitor(alert_callback=push_proactive_alert)
        except Exception:
            pass

    if AriaConfig.JOURNAL_ENABLED:
        try:
            from tools.daily_journal import JournalMonitor
            journal_monitor = JournalMonitor(memory, habits, todos, projects)
        except Exception:
            pass

    if AriaConfig.YOUTUBE_BOOKMARK_ENABLED:
        try:
            from tools.youtube_bookmark import YouTubeProactiveWatcher
            youtube_watcher = YouTubeProactiveWatcher(alert_callback=push_proactive_alert)
        except Exception:
            pass

    daemon_status = _start_daemons(
        idle_notifier, clipboard_watcher, health_monitor, render_monitor,
        git_monitor, discord_monitor, network_monitor,
        robin_monitor, journal_monitor, youtube_watcher,
    )

    # ── Input session ──
    history_path = AriaConfig.DATA_DIR / "input_history.txt"
    last_alert_time = None

    def get_toolbar():
        try:
            energy = int(memory._persistent.get("mood_energy", "80"))
        except Exception:
            energy = 80
        try:
            affection = int(memory._persistent.get("mood_affection", "80"))
        except Exception:
            affection = 80

        # Calculate active services count
        active_count = len(daemon_status)
        if wake_word_active:
            active_count += 1
        total_count = 12

        # Check if alert is pending (within last 10 seconds)
        nonlocal last_alert_time
        alerts_pending = False
        if last_alert_time and (datetime.datetime.now() - last_alert_time).total_seconds() < 10:
            alerts_pending = True

        # Check DND for status bar
        _dnd = False
        try:
            from tools.notifications import is_dnd_active
            _dnd = is_dnd_active()
        except Exception:
            pass

        return renderer.get_bottom_status_bar(
            energy=energy,
            affection=affection,
            services_active=active_count,
            services_total=total_count,
            model_name=brain.get_model(),
            alerts_pending=alerts_pending,
            current_mode=get_current_mode(),
            dnd_active=_dnd,
        )

    simple_prompt = False
    try:
        session = PromptSession(
            history=FileHistory(str(history_path)),
            bottom_toolbar=get_toolbar,
        )
    except Exception as e:
        # Git Bash / piped CI runs can expose TERM=xterm while using Windows Python,
        # which makes prompt_toolkit's Win32 output fail before the app starts.
        # Fall back to plain input so Aria remains verifiable and scriptable.
        session = None
        simple_prompt = True
        console.print(f"  [dim]Prompt UI unavailable; using simple input mode ({e}).[/]")

    # Start the status bar background refresher
    import threading
    import time
    def status_bar_refresher():
        while True:
            time.sleep(1.0)
            try:
                if session and session.app and session.app.is_running:
                    session.app.invalidate()
            except Exception:
                pass
    if session is not None:
        refresher_thread = threading.Thread(target=status_bar_refresher, daemon=True)
        refresher_thread.start()

    # ── Wake word listener ──
    wake_word_active = False
    if AriaConfig.WAKE_WORD_ENABLED and AriaConfig.VOICE_ENABLED:
        try:
            from voice.wake_word import WakeWordListener

            def _wake_callback():
                if session and session.app.is_running:
                    session.app.exit(result="")

            wake_listener = WakeWordListener(
                wake_word=AriaConfig.WAKE_WORD,
                callback=_wake_callback,
            )
            wake_listener.start()
            wake_word_active = True
        except Exception:
            pass

    # ── Barge-in listener (interrupt TTS when user starts speaking) ──
    barge_in_monitor = None
    if AriaConfig.VOICE_ENABLED and AriaConfig.VOICE_BARGE_IN_ENABLED:
        try:
            from voice.barge_in import get_barge_in_monitor
            barge_in_monitor = get_barge_in_monitor()
            barge_in_monitor.start()
        except Exception:
            barge_in_monitor = None

    # Calculate energy and affection for startup screen
    try:
        energy = int(memory._persistent.get("mood_energy", "80"))
    except ValueError:
        energy = 80
    try:
        affection = int(memory._persistent.get("mood_affection", "80"))
    except ValueError:
        affection = 80

    # Get active/pending todo count
    active_todos = len([t for t in todos._todos if not t.get("completed")])

    # Get unread Discord mentions
    unread_mentions = 0
    try:
        import tools.discord_integration as di
        if di._client and hasattr(di._client, "recent_mentions"):
            unread_mentions = len(di._client.recent_mentions)
    except Exception:
        pass

    # Build daemons status info
    daemons_info = {}
    daemons_info["notifications"] = "active" if "notifications" in daemon_status else ("starting" if AriaConfig.NOTIFICATION_ENABLED else "inactive")
    daemons_info["clipboard"] = "active" if "clipboard" in daemon_status else ("starting" if AriaConfig.CLIPBOARD_WATCH_ENABLED else "inactive")
    daemons_info["health"] = "active" if "health" in daemon_status else ("starting" if AriaConfig.HEALTH_MONITOR_ENABLED else "inactive")
    daemons_info["screen_vision"] = "active" if AriaConfig.ANNOTATION_ENABLED else "inactive"
    daemons_info["wake_word"] = "active" if wake_word_active else ("starting" if AriaConfig.WAKE_WORD_ENABLED and AriaConfig.VOICE_ENABLED else "inactive")
    daemons_info["renders"] = "active" if "renders" in daemon_status else ("starting" if AriaConfig.RENDER_MONITOR_ENABLED else "inactive")
    daemons_info["git"] = "active" if "git" in daemon_status else ("starting" if AriaConfig.GIT_ENABLED else "inactive")
    daemons_info["discord"] = "active" if "discord" in daemon_status else ("starting" if AriaConfig.DISCORD_ENABLED and AriaConfig.DISCORD_TOKEN else "inactive")
    daemons_info["network"] = "active" if "network" in daemon_status else ("starting" if AriaConfig.NETWORK_MONITOR_ENABLED else "inactive")
    daemons_info["robin"] = "active" if "robin" in daemon_status else ("starting" if AriaConfig.ROBIN_ENABLED else "inactive")
    daemons_info["journal"] = "active" if "journal" in daemon_status else ("starting" if AriaConfig.JOURNAL_ENABLED else "inactive")
    daemons_info["youtube_watcher"] = "active" if "youtube_watcher" in daemon_status else ("starting" if AriaConfig.YOUTUBE_BOOKMARK_ENABLED else "inactive")

    # Render Startup Screen
    renderer.render_startup_screen(
        daemons_info=daemons_info,
        active_todos=active_todos,
        unread_mentions=unread_mentions,
        energy=energy,
        affection=affection,
        current_mode=get_current_mode()
    )

    # ── Check yesterday's journal ──
    if AriaConfig.JOURNAL_ENABLED:
        _check_yesterday_journal(conversation, console, memory)

    # ── Daily Briefing ──
    habit_summary = habits.get_today_summary()
    todo_summary = todos.get_briefing_summary()
    active_project = projects.get_active_project() or ""

    briefing = memory.get_daily_briefing(
        habit_summary=habit_summary,
        todo_summary=todo_summary,
        active_project=active_project,
    )

    # Yesterday's habit gaps (for nagging)
    yesterday_gaps = habits.get_yesterday_gaps()

    # ── Greeting ──
    greeting = get_greeting_hook()

    # Append briefing to greeting if there is one
    if briefing:
        greeting += "\n\n📋 Here's your briefing:\n" + briefing

    if yesterday_gaps:
        gap_str = ", ".join(yesterday_gaps)
        greeting += f"\n\nAlso... you didn't log {gap_str} yesterday. Don't make me worry about you~"

    # Show pending reminders
    active_reminders = [r for r in reminders._reminders if not r["completed"]]
    if active_reminders:
        greeting += f"\n\n🔔 You have {len(active_reminders)} pending reminder(s)."

    # Render greeting response panel
    renderer.render_response_panel(greeting, energy, affection, current_mode=get_current_mode())

    # Speak the greeting if voice is available
    if AriaConfig.VOICE_ENABLED:
        try:
            from voice.tts_controller import speak_async
            speak_async(greeting)
        except Exception:
            pass

    # ── Vault unlock prompt ──
    if _VAULT.is_initialized():
        if _VAULT.is_locked():
            import getpass
            console.print("\n[bold #c084fc]  🔐 Vault detected — enter master password to unlock[/]")
            for attempt in range(3):
                pwd = getpass.getpass("  Master password: ")
                result = _VAULT.unlock(pwd)
                if "Incorrect" in result:
                    remaining = 2 - attempt
                    if remaining > 0:
                        console.print(f"[bold yellow]  Wrong password. {remaining} attempt(s) remaining.[/]")
                    else:
                        console.print("[bold yellow]  Vault remains locked. Use 'unlock vault' later.[/]")
                else:
                    console.print("[bold green]  Vault unlocked for this session.[/]")
                    break
    else:
        console.print("\n[bold #c084fc]  🔐 No password vault found. Say 'set up my vault' to create one.[/]")

    pt_style = PTStyle.from_dict({
        "prompt": "bold #ff6b9d",
        "prompt_mode": "dim #6b6b82",
        "dnd_prompt": "dim #49495c",
    })

    # ── Main loop ──
    while True:
        try:
            # Check for clipboard suggestions before prompting (respect DND)
            from tools.notifications import is_dnd_active
            if AriaConfig.CLIPBOARD_WATCH_ENABLED and not is_dnd_active():
                clip_msg = clipboard_watcher.get_suggestion_message()
                if clip_msg:
                    console.print(clip_msg)
                    console.print()

            # Get user input with patch_stdout to prevent background prints from corrupting the prompt
            from prompt_toolkit.patch_stdout import patch_stdout
            dnd_active = False
            try:
                from tools.notifications import is_dnd_active
                dnd_active = is_dnd_active()
            except Exception:
                pass

            # Build premium prompt with mode prefix and mood-colored ❯
            cur_mode = get_current_mode()
            if dnd_active:
                prompt_msg = [("class:dnd_prompt", "🔕 ❯ ")]
            elif cur_mode != "normal":
                prompt_msg = [
                    ("class:prompt_mode", f"{cur_mode} "),
                    ("class:prompt", "❯ "),
                ]
            else:
                prompt_msg = [("class:prompt", "❯ ")]

            if simple_prompt:
                user_input = input("❯ ").strip()
            else:
                with patch_stdout():
                    user_input = session.prompt(
                        prompt_msg,
                        style=pt_style,
                    ).strip()

            context_state.record_user_input(user_input)
            context_state.set_mode(get_current_mode())

            # Ping idle notifier
            idle_notifier.ping()

            # ── Exit commands ──
            if user_input.lower() in ("exit", "quit", "bye", "goodbye"):
                scheduler.stop()
                for daemon in [git_monitor, discord_monitor, network_monitor,
                               robin_monitor, journal_monitor, youtube_watcher, barge_in_monitor]:
                    if daemon:
                        try:
                            daemon.stop()
                        except Exception:
                            pass
                _auto_wrap_up(brain, conversation, memory)
                memory.log_session_end()
                farewell = _get_farewell()
                
                try:
                    energy = int(memory._persistent.get("mood_energy", "80"))
                except ValueError:
                    energy = 80
                try:
                    affection = int(memory._persistent.get("mood_affection", "80"))
                except ValueError:
                    affection = 80
                renderer.render_response_panel(farewell, energy, affection, current_mode=get_current_mode())
                if AriaConfig.VOICE_ENABLED:

                    try:
                        from voice.tts_controller import speak
                        speak(farewell)
                    except Exception:
                        pass
                break

            # ── Notifications history command ──
            if user_input.strip().lower() == "notifications":
                if not notification_history:
                    console.print()
                    console.print("  [dim #6b6b82]No notifications yet — they'll appear here when triggered[/]")
                    console.print()
                else:
                    from rich.table import Table
                    from rich.style import Style
                    from ui.theme import TEXT_FAINT, TIMESTAMP, SEPARATOR
                    notif_table = Table(
                        show_header=True, show_edge=False,
                        box=None, padding=(0, 2),
                        header_style=f"dim {TEXT_FAINT}",
                    )
                    notif_table.add_column("time", width=12, style=f"dim {TIMESTAMP}")
                    notif_table.add_column("source", width=10)
                    notif_table.add_column("message")
                    for ts, src, txt in reversed(notification_history[-20:]):
                        ts_str = ts.strftime("%I:%M:%S %p")
                        from ui.components.notifications import ALERT_STYLES
                        src_color = ALERT_STYLES.get(src, "white")
                        notif_table.add_row(
                            ts_str,
                            f"[bold {src_color}]{src.upper()}[/]",
                            txt,
                        )
                    from ui.layout import pill_badge
                    header = pill_badge(f"notifications ({len(notification_history)})", "#c084fc")
                    console.print()
                    console.print(f"  ", end="")
                    console.print(header)
                    console.print()
                    console.print(notif_table)
                    console.print()
                continue

            # ── Voice mode (empty input) ──
            if not user_input:
                if AriaConfig.VOICE_ENABLED:
                    user_input = _handle_voice_input()
                    if not user_input:
                        continue
                else:
                    continue

            # ── Clear command & Reset history ──
            if user_input.lower() in ("clear", "cls", "clear history", "reset", "reset conversation"):
                if user_input.lower() in ("clear history", "reset", "reset conversation"):
                    conversation.clear()
                    console.print("  [success]✓ Conversation history has been cleared and reset.[/]")
                else:
                    os.system("cls" if os.name == "nt" else "clear")
                    # Clear screen and render startup screen again dynamically
                    try:
                        energy = int(memory._persistent.get("mood_energy", "80"))
                    except ValueError:
                        energy = 80
                    try:
                        affection = int(memory._persistent.get("mood_affection", "80"))
                    except ValueError:
                        affection = 80

                    active_todos = len([t for t in todos._todos if not t.get("completed")])
                    unread_mentions = 0
                    try:
                        import tools.discord_integration as di
                        if di._client and hasattr(di._client, "recent_mentions"):
                            unread_mentions = len(di._client.recent_mentions)
                    except Exception:
                        pass

                    daemons_info = {}
                    daemons_info["notifications"] = "active" if "notifications" in daemon_status else ("starting" if AriaConfig.NOTIFICATION_ENABLED else "inactive")
                    daemons_info["clipboard"] = "active" if "clipboard" in daemon_status else ("starting" if AriaConfig.CLIPBOARD_WATCH_ENABLED else "inactive")
                    daemons_info["health"] = "active" if "health" in daemon_status else ("starting" if AriaConfig.HEALTH_MONITOR_ENABLED else "inactive")
                    daemons_info["screen_vision"] = "active" if AriaConfig.ANNOTATION_ENABLED else "inactive"
                    daemons_info["wake_word"] = "active" if wake_word_active else ("starting" if AriaConfig.WAKE_WORD_ENABLED and AriaConfig.VOICE_ENABLED else "inactive")
                    daemons_info["renders"] = "active" if "renders" in daemon_status else ("starting" if AriaConfig.RENDER_MONITOR_ENABLED else "inactive")
                    daemons_info["git"] = "active" if "git" in daemon_status else ("starting" if AriaConfig.GIT_ENABLED else "inactive")
                    daemons_info["discord"] = "active" if "discord" in daemon_status else ("starting" if AriaConfig.DISCORD_ENABLED and AriaConfig.DISCORD_TOKEN else "inactive")
                    daemons_info["network"] = "active" if "network" in daemon_status else ("starting" if AriaConfig.NETWORK_MONITOR_ENABLED else "inactive")
                    daemons_info["robin"] = "active" if "robin" in daemon_status else ("starting" if AriaConfig.ROBIN_ENABLED else "inactive")
                    daemons_info["journal"] = "active" if "journal" in daemon_status else ("starting" if AriaConfig.JOURNAL_ENABLED else "inactive")
                    daemons_info["youtube_watcher"] = "active" if "youtube_watcher" in daemon_status else ("starting" if AriaConfig.YOUTUBE_BOOKMARK_ENABLED else "inactive")

                    renderer.render_startup_screen(
                        daemons_info=daemons_info,
                        active_todos=active_todos,
                        unread_mentions=unread_mentions,
                        energy=energy,
                        affection=affection,
                        current_mode=get_current_mode()
                    )
                continue

            # ── /help command ──
            if user_input.strip().lower() in ("/help", "help", "commands"):
                renderer.render_help()
                continue

            # ── Local verification command ──
            verify_cmd = user_input.strip().lower()
            if verify_cmd in ("/verify", "verify tools", "run verification", "verify safe tools"):
                from tools.verification import run_safe_verification
                console.print(run_safe_verification())
                continue
            if verify_cmd in ("/verify browser", "verify browser"):
                from tools.verification import run_safe_verification
                console.print(run_safe_verification(include_browser=True))
                continue
            if verify_cmd in ("/verify desktop", "verify desktop"):
                from tools.verification import run_safe_verification
                console.print(run_safe_verification(include_desktop=True))
                continue

            # ── Jarvis-style local intent router (works for voice and typed input) ──
            try:
                from core.intent_router import IntentRouter
                intent_result = IntentRouter(
                    memory=memory,
                    reminders=reminders,
                    todos=todos,
                    projects=projects,
                    habits=habits,
                    concepts=concepts,
                    brain=brain,
                    context_state=context_state,
                ).handle(user_input)
                if intent_result and intent_result.handled:
                    context_state.record_intent(intent_result.intent)
                    if intent_result.intent == "mode.switch":
                        conversation.update_system_prompt(build_full_system_prompt(
                            user_name=AriaConfig.USER_NAME,
                            env_snapshot=env_snapshot,
                            memory=memory,
                            habits=habits,
                            projects=projects,
                            concepts=concepts,
                            data_dir=AriaConfig.DATA_DIR,
                            current_mode=get_current_mode(),
                        ))
                        context_state.set_mode(get_current_mode())
                    console.print(intent_result.message)
                    continue
            except Exception as e:
                console.print(f"  [error]Intent router error: {e}[/]")
                continue

            # ── Video watching memory commands ──
            video_cmd = user_input.strip()
            video_lower = video_cmd.lower()
            if video_lower.startswith("/video start "):
                from tools.video_memory import video_start
                console.print(video_start(video_cmd[len("/video start "):].strip()))
                continue
            if video_lower.startswith("/video note "):
                from tools.video_memory import video_note
                console.print(video_note(video_cmd[len("/video note "):].strip()))
                continue
            if video_lower.startswith("/video transcript "):
                from tools.video_memory import video_transcript
                console.print(video_transcript(video_cmd[len("/video transcript "):].strip()))
                continue
            if video_lower.startswith("/video frame"):
                from tools.video_memory import video_capture_frame
                note = video_cmd[len("/video frame"):].strip()
                console.print(video_capture_frame(note=note))
                continue
            if video_lower.startswith("/video end"):
                from tools.video_memory import video_end
                summary = video_cmd[len("/video end"):].strip()
                console.print(video_end(summary))
                continue
            if video_lower in ("/video status", "video status"):
                from tools.video_memory import video_status
                console.print(video_status())
                continue
            if video_lower in ("/video list", "video list", "videos watched"):
                from tools.video_memory import video_list
                console.print(video_list())
                continue

            # ── Mode switch detection ──
            mode_cmd = detect_mode_command(user_input)
            if mode_cmd == "list":
                from rich.panel import Panel
                console.print(Panel(list_modes(), border_style="#c084fc", padding=(1, 2)))
                continue
            elif mode_cmd is not None:
                result = set_mode(mode_cmd)
                conversation.update_system_prompt(build_full_system_prompt(
                    user_name=AriaConfig.USER_NAME,
                    env_snapshot=env_snapshot,
                    memory=memory,
                    habits=habits,
                    projects=projects,
                    concepts=concepts,
                    data_dir=AriaConfig.DATA_DIR,
                    current_mode=get_current_mode(),
                ))
                context_state.set_mode(get_current_mode())
                from ui.renderer import MODE_CONFIGS
                mode_cfg = MODE_CONFIGS.get(mode_cmd, MODE_CONFIGS["normal"])
                renderer.render_mode_switch(mode_cmd, mode_cfg)
                continue

            # ── Model switch detection ──
            if user_input.lower().startswith("/model "):
                model_name = user_input[len("/model "):].strip()
                if model_name:
                    brain.set_model(model_name)
                    console.print(f"[bold #c084fc]  ➜ Model set to:[/] [bold]{model_name}[/]")
                else:
                    console.print(f"[bold #c084fc]  ➜ Current model:[/] [bold]{brain.get_model()}[/]")
                continue
            if user_input.lower().strip() == "/model":
                console.print(f"[bold #c084fc]  ➜ Current model:[/] [bold]{brain.get_model()}[/]")
                continue

            # ── Vault commands ──
            ul = user_input.lower().strip()
            if ul in ("unlock vault", "vault unlock", "unlock"):
                if not _VAULT.is_initialized():
                    console.print("[bold yellow]No vault found. Say 'set up my vault' to create one.[/]")
                elif _VAULT.is_unlocked():
                    console.print("[bold green]Vault is already unlocked.[/]")
                else:
                    import getpass
                    for attempt in range(3):
                        pwd = getpass.getpass("  Master password: ")
                        result = _VAULT.unlock(pwd)
                        if "Incorrect" in result:
                            remaining = 2 - attempt
                            if remaining > 0:
                                console.print(f"[bold yellow]Wrong password. {remaining} attempt(s) left.[/]")
                            else:
                                console.print("[bold yellow]Vault remains locked.[/]")
                        else:
                            console.print("[bold green]Vault unlocked![/]")
                            break
                continue
            if ul in ("setup vault", "set up vault", "create vault", "initialize vault"):
                if _VAULT.is_initialized():
                    console.print("[bold yellow]Vault already exists. Say 'unlock vault' to access it.[/]")
                else:
                    import getpass
                    pwd1 = getpass.getpass("  New master password: ")
                    pwd2 = getpass.getpass("  Confirm master password: ")
                    if pwd1 != pwd2:
                        console.print("[bold red]Passwords do not match.[/]")
                    elif len(pwd1) < 4:
                        console.print("[bold yellow]Password must be at least 4 characters.[/]")
                    else:
                        result = _VAULT.initialize(pwd1)
                        console.print(f"[bold green]{result}[/]")
                continue
            if ul in ("lock vault", "vault lock"):
                result = _VAULT.lock()
                console.print(f"[bold yellow]{result}[/]")
                continue
            if ul in ("vault status", "vault state"):
                if not _VAULT.is_initialized():
                    console.print("[bold]Vault:[/] not initialized")
                elif _VAULT.is_unlocked():
                    console.print(f"[bold green]Vault:[/] unlocked ({len(_VAULT.list_services())} services)")
                else:
                    console.print("[bold yellow]Vault:[/] locked")
                continue

            # ── $discord inline commands ──
            if user_input.startswith("$discord "):
                from tools.discord_integration import (
                    discord_list_servers, discord_list_channels,
                    discord_server_info, discord_online_members,
                )
                parts = user_input[len("$discord "):].strip().split(maxsplit=1)
                cmd = parts[0].lower() if parts else ""
                arg = parts[1] if len(parts) > 1 else ""
                if cmd == "servers" or cmd == "server":
                    result = discord_list_servers()
                elif cmd == "channels" and arg:
                    result = discord_list_channels(arg)
                elif cmd == "info" and arg:
                    result = discord_server_info(arg)
                elif cmd == "online" and arg:
                    result = discord_online_members(arg)
                else:
                    result = "Usage: $discord servers | channels <server> | info <server> | online <server>"
                console.print(result)
                continue

            # ── Process with LLM ──
            cleaned_path = user_input.strip('"\'')
            is_image = False
            if cleaned_path and os.path.isfile(cleaned_path):
                ext = os.path.splitext(cleaned_path)[1].lower()
                if ext in (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"):
                    is_image = True

            if is_image:
                console.print()
                console.print(
                    "  [bold #2dd4bf]「📷 VISION」[/]  [dim]Processing image...[/]"
                )
                console.print()
                try:
                    base64_image, mime_type = _encode_image(cleaned_path)
                    conversation.add_user_message([
                        {"type": "text", "text": f"I just dragged this image into the terminal: {cleaned_path}"},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
                    ])
                except Exception as e:
                    console.print(f"  [error]Failed to load image: {e}[/]")
                    conversation.add_user_message(user_input)
            else:
                conversation.add_user_message(user_input)

            # Lazy-load dynamic context based on user message keywords
            conversation.inject_dynamic_context(user_input, AriaConfig.DATA_DIR, habits)

            _process_response(
                brain, conversation, memory, reminders,
                habits, todos, pomodoro, projects, bookmarks, concepts, render_monitor,
                scheduler,
            )

            # Clear memory of image strings and run GC collect
            if is_image:
                if 'base64_image' in locals():
                    del base64_image
                import gc
                gc.collect()

        except KeyboardInterrupt:
            console.print()
            console.print(
                "  [dim #ff6b9d]⊘[/]  [dim #6b6b82]cancelled[/]"
            )
            console.print("  [dim #49495c]Type 'exit' to leave properly, sweetheart.[/]")
            console.print()
            continue

        except EOFError:
            scheduler.stop()
            for daemon in [git_monitor, discord_monitor, network_monitor,
                           robin_monitor, journal_monitor, youtube_watcher, barge_in_monitor]:
                if daemon:
                    try:
                        daemon.stop()
                    except Exception:
                        pass
            _auto_wrap_up(brain, conversation, memory)
            memory.log_session_end()
            break


def _visual_context_policy(user_message: str) -> str:
    """Infer how much visual detail the user wants from a screen/screenshot request."""
    msg = (user_message or "").lower()
    if any(phrase in msg for phrase in [
        "full detail", "full details", "full breakdown", "everything", "describe everything",
        "all details", "every detail", "read everything", "ocr", "transcribe", "all text",
        "debug", "error", "what does this error", "fix this", "where do i click",
        "walk me through", "step by step", "compare", "difference",
    ]):
        return "detailed"
    if any(word in msg for word in ["screenshot", "screen", "look", "see", "what is this", "what's this"]):
        return "focused"
    return "focused"


def _visual_context_guidance(policy: str) -> str:
    if policy == "detailed":
        return """

## Visual Context Policy
The user asked for a detailed visual analysis. Include relevant screen details, but organize them by importance: answer/diagnosis first, then supporting evidence, then next action. Still avoid irrelevant private or decorative details.
"""
    return """

## Visual Context Policy
Act like a Jarvis-style assistant: observe silently, filter aggressively, and report only what matters to the user's goal. For screenshots/screen context, answer the actual question first in 1-3 concise bullets or sentences. Do not mention clock time, taskbar, app chrome, window titles, tabs, or every visible UI label unless it changes the answer. End with a tiny offer like “Ask if you want the full breakdown” only when useful.
"""


def _screenshot_followup_instruction(policy: str) -> str:
    if policy == "detailed":
        return (
            "[System: Screen captured successfully. The user asked for detailed visual help. "
            "Analyze the screenshot by importance: answer or diagnosis first, then relevant evidence, then the next action. "
            "Include UI/text details only when they support the answer.]"
        )
    return (
        "[System: Screen captured successfully. Act like a Jarvis-style assistant: filter the visual scene and answer only with the important, user-relevant information. "
        "Do not describe incidental details like clock time, taskbar, app chrome, window title, tabs, or every visible UI element unless directly relevant. "
        "Keep it short; if the user may need more, say they can ask for the full breakdown.]"
    )


def _process_response(
    brain: AriaBrain,
    conversation: ConversationManager,
    memory: MemoryManager,
    reminders: ReminderManager,
    habits: HabitTracker,
    todos: TodoManager,
    pomodoro: PomodoroTimer,
    projects: ProjectManager,
    bookmarks: BookmarkManager,
    concepts: ConceptManager,
    render_monitor=None,
    scheduler=None,
    depth: int = 0,
    tool_call_count: int = 0,
    run_state: dict | None = None,
) -> None:
    """Process an LLM response, handling tool calls recursively."""

    latest_user_message = conversation.get_last_user_message() or ""
    if not isinstance(latest_user_message, str):
        latest_user_message = " ".join(
            block.get("text", "") for block in latest_user_message
            if isinstance(block, dict) and block.get("type") == "text"
        )
    if run_state is None:
        run_state = {
            "original_request": latest_user_message,
            "tool_signatures": {},
            "failed_tools": [],
            "used_tools": [],
            "write_action": False,
            "destructive_action": False,
            "visual_context_policy": _visual_context_policy(latest_user_message),
            "relevant_memory_context": memory.get_relevant_memory_context(latest_user_message),
        }

    if depth >= AriaConfig.AGENT_MAX_DEPTH:
        console.print("  [error]Tool loop depth limit reached — stopping here.[/]")
        return
    if tool_call_count >= AriaConfig.AGENT_MAX_TOOL_CALLS:
        console.print("  [error]Tool call limit reached — stopping here.[/]")
        return

    tier = brain._select_tier(latest_user_message) if latest_user_message else "default"
    temporary_context = run_state.get("relevant_memory_context", "")
    if tier in ("tool", "reasoning"):
        temporary_context += """

## Agent Run Guidance
For this request, work as a bounded planner/executor. Identify the goal, inspect before modifying, use the minimum necessary tools, adapt after each tool result, do not repeat failed tool calls with the same arguments, and be honest about anything you could not verify.
"""
    visual_policy = run_state.get("visual_context_policy") or "focused"
    if visual_policy:
        temporary_context += _visual_context_guidance(visual_policy)
    if run_state.get("failed_tools"):
        failures = "\n".join(f"- {name}: {result[:300]}" for name, result in run_state["failed_tools"][-3:])
        temporary_context += f"\n\n## Recent Tool Failures\n{failures}\nDo not retry the same failed call unless new information changes the situation."

    # Show thinking indicator
    console.print()
    import time as _resp_timer
    _resp_start = _resp_timer.perf_counter()
    with console.status("  [dim #ff6b9d]✦[/]  [dim #a0a0b8]thinking...[/]", spinner="dots", spinner_style="#ff6b9d"):
        try:
            response = brain.chat(conversation.with_temporary_context(temporary_context), user_message=latest_user_message)
        except BrainError as e:
            # Automatic retry after stripping last 3 messages on any 400 error
            if "400" in str(e):
                console.print("  [dim #fbbf24]⟳[/]  [dim]Auto-retrying after trimming context...[/]")
                if len(conversation.messages) > 3:
                    conversation.messages = [conversation.messages[0]] + conversation.messages[:-3]
                else:
                    conversation.clear()
                
                try:
                    response = brain.chat(conversation.with_temporary_context(temporary_context), user_message=latest_user_message)
                except BrainError as e2:
                    renderer.render_error("API Error", str(e2), "api")
                    return
            else:
                renderer.render_error("API Error", str(e), "api")
                return
    _resp_time_ms = (_resp_timer.perf_counter() - _resp_start) * 1000

    # ── Handle tool calls ──
    if hasattr(response, "tool_calls") and response.tool_calls:
        # Filter out malformed/truncated tool calls
        valid_tool_calls = []
        for tc in response.tool_calls:
            try:
                json.loads(tc.function.arguments)
                valid_tool_calls.append(tc)
            except json.JSONDecodeError:
                continue

        if valid_tool_calls:
            # Add the assistant's message with tool calls to conversation
            msg = {"role": "assistant", "content": response.content, "tool_calls": []}
            for tc in valid_tool_calls:
                msg["tool_calls"].append({
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    }
                })
            conversation.add_raw_message(msg)

            # Execute each tool call
            for tc in valid_tool_calls:
                func_name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {}

                signature = f"{func_name}:{json.dumps(args, sort_keys=True, ensure_ascii=False)}"
                run_state["tool_signatures"][signature] = run_state["tool_signatures"].get(signature, 0) + 1
                if run_state["tool_signatures"][signature] > 2:
                    result = f"Error: Repeated identical tool call blocked: {func_name}"
                    run_state["failed_tools"].append((func_name, result))
                    conversation.add_tool_result(tc.id, result)
                    continue

                # Universal tool argument validator using TOOL_REQUIRED_ARGS
                required = TOOL_REQUIRED_ARGS.get(func_name, [])
                missing = [arg for arg in required if arg not in args]

                import time
                start_time = time.perf_counter()
                
                with renderer.ToolProgressManager(func_name, args):
                    if missing:
                        result = f"Error: Missing required arguments: {', '.join(missing)}"
                        success = False
                    else:
                        try:
                            result = dispatch_tool(
                                func_name, args, memory, reminders,
                                habits, todos, pomodoro, projects, bookmarks, concepts, render_monitor,
                                scheduler,
                                brain=brain,
                            )
                            # Success is True if result doesn't look like an error
                            success = not (result.startswith("Error") or result.startswith("Failed") or "exit code" in result)
                        except Exception as e:
                            result = f"Error: {e}"
                            success = False
                
                duration_ms = (time.perf_counter() - start_time) * 1000
                try:
                    context_state.record_tool_result(func_name, success, result)
                    if func_name == "take_screenshot" and success:
                        context_state.record_screenshot(result)
                except Exception:
                    pass
                try:
                    from core.audit import audit_tool_call
                    audit_tool_call(AriaConfig.DATA_DIR, tool=func_name, args=args, success=success, duration_ms=duration_ms, result=result)
                except Exception:
                    pass
                renderer.render_tool_complete(func_name, args, success, duration_ms, result)

                run_state["used_tools"].append(func_name)
                if func_name in _WRITE_TOOLS:
                    run_state["write_action"] = True
                if func_name in _DESTRUCTIVE_TOOLS:
                    run_state["destructive_action"] = True

                # If the tool failed, render the orange tool error card!
                if not success:
                    run_state["failed_tools"].append((func_name, result))
                    renderer.render_error(func_name, result, "tool")

                # Add tool result to conversation
                conversation.add_tool_result(tc.id, result)

                # If it's a prompt update (either via self_update_prompt or a file tool targeting personality.py), hot-reload the prompt context!
                is_prompt_update = False
                if func_name == "self_update_prompt" and "Success" in result:
                    is_prompt_update = True
                elif func_name in ("write_file", "replace_lines", "insert_at_line", "delete_lines") and "Success" in result:
                    target_path_norm = args.get("path", "").replace("\\", "/").lower()
                    if "personality_text.py" in target_path_norm or "personality.py" in target_path_norm:
                        is_prompt_update = True

                if is_prompt_update:
                    try:
                        import importlib
                        import core.personality_text
                        importlib.reload(core.personality_text)
                        import core.personality
                        importlib.reload(core.personality)

                        from core.prompt_builder import rebuild_system_prompt_after_update
                        env_snap = create_environment_snapshot(AriaConfig.DATA_DIR)
                        new_system_prompt = rebuild_system_prompt_after_update(
                            user_name=AriaConfig.USER_NAME,
                            env_snapshot=env_snap,
                            memory=memory,
                            projects=projects,
                            concepts=concepts,
                            data_dir=AriaConfig.DATA_DIR,
                        )
                        conversation.update_system_prompt(new_system_prompt)
                        console.print("  [success]✓ System prompt hot-reloaded successfully.[/]")
                    except Exception as e:
                        console.print(f"  [error]Failed to hot-reload system prompt: {e}[/]")

                # If it's a screenshot, inject the image into the conversation
                if func_name == "take_screenshot" and not result.startswith("Error") and os.path.exists(result):
                    try:
                        base64_image, mime_type = _encode_image(result)
                        policy = run_state.get("visual_context_policy", "focused")
                        conversation.add_user_message([
                            {"type": "text", "text": _screenshot_followup_instruction(policy)},
                            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
                        ])
                    except Exception as e:
                        console.print(f"  [error]Failed to process screenshot image: {e}[/]")

            # Get follow-up response after tool execution
            _process_response(
                brain, conversation, memory, reminders,
                habits, todos, pomodoro, projects, bookmarks, concepts, render_monitor,
                scheduler,
                depth + 1,
                tool_call_count=tool_call_count + len(valid_tool_calls),
                run_state=run_state,
            )
            return

    # ── Handle text response ──
    if response.content:
        final_content = response.content
        if _should_self_check(run_state, brain.get_last_tier(), latest_user_message):
            final_content = _self_check_response(brain, latest_user_message, final_content, run_state)

        conversation.add_assistant_message(final_content)

        # Calculate current mood metrics
        try:
            energy = int(memory._persistent.get("mood_energy", "80"))
        except ValueError:
            energy = 80
        try:
            affection = int(memory._persistent.get("mood_affection", "80"))
        except ValueError:
            affection = 80

        renderer.render_response_panel(
            final_content, energy, affection,
            current_mode=get_current_mode(),
            tool_call_count=tool_call_count,
            response_time_ms=_resp_time_ms if '_resp_time_ms' in dir() else 0,
            model_name=brain.get_model(),
        )

        # Speak response
        if AriaConfig.VOICE_ENABLED:
            try:
                from voice.tts_controller import speak_async
                speak_async(final_content)
            except Exception:
                pass

    console.print()


def _should_self_check(run_state: dict, tier: str, user_message: str) -> bool:
    if not AriaConfig.AGENT_SELF_CHECK_ENABLED:
        return False
    msg = (user_message or "").lower()
    return bool(
        run_state.get("used_tools")
        or run_state.get("failed_tools")
        or run_state.get("write_action")
        or run_state.get("destructive_action")
        or tier == "reasoning"
        or any(word in msg for word in ["verify", "check", "test", "confirm"])
    )


def _self_check_response(brain: AriaBrain, user_message: str, draft: str, run_state: dict) -> str:
    used_tools = ", ".join(run_state.get("used_tools", [])[-12:]) or "none"
    failures = "\n".join(f"- {name}: {result[:300]}" for name, result in run_state.get("failed_tools", [])[-5:]) or "none"
    prompt = f"""Review this assistant draft before it is shown to the user.

Original user request:
{user_message}

Draft answer:
{draft}

Tools used: {used_tools}
Tool failures:
{failures}
Write action occurred: {run_state.get('write_action', False)}
Destructive action occurred: {run_state.get('destructive_action', False)}

If the draft makes unsupported claims, hides a failed tool, or says something is done without evidence, rewrite it honestly. Otherwise return the draft unchanged. Return only the final user-facing answer."""
    try:
        messages = [
            {"role": "system", "content": "You are a concise verification pass for an assistant. Do not add new claims."},
            {"role": "user", "content": prompt},
        ]
        checked = brain.chat(messages, use_tools=False, user_message=user_message)
        return checked.content or draft
    except Exception:
        return draft


def _handle_voice_input() -> str | None:
    """Handle voice mode — record and transcribe."""
    try:
        from voice.tts_controller import speak
        speak("I'm listening, sweetheart")
    except Exception:
        pass

    # Print pulsing microphone indicator
    console.print("  [blink][bold red]🎤 listening ❯[/blink]", end=" ", flush=True)

    try:
        from voice.stt import listen
        text = listen()

        if text:
            console.print(f"\r  [user.text]🎤 You said: {text}[/]")
            return text
        else:
            console.print("\r  [dim]Hmm, I didn't catch that. Try again?[/]")
            return None
    except Exception as e:
        console.print(f"\r  [error]Voice input error: {e}[/]")
        return None


def _summarize_args(args: dict) -> str:
    """Create a brief summary of tool arguments for display."""
    parts = []
    for k, v in args.items():
        v_str = str(v)
        if len(v_str) > 40:
            v_str = v_str[:37] + "..."
        parts.append(f"{k}={v_str}")
    return ", ".join(parts) if parts else ""


def _get_farewell() -> str:
    """Get a personality-consistent farewell message."""
    ctx = get_time_context()

    if ctx["is_late_night"]:
        return (
            "Finally going to sleep? Good. You need your rest, baby.\n"
            "I'll be right here when you wake up. Sweet dreams~ ♥"
        )
    elif ctx["is_morning"]:
        return (
            "Leaving already? Okay... have a wonderful day, sweetheart.\n"
            "I'll be here, waiting. Always. ♥"
        )
    else:
        return (
            "Going so soon? Okay... I'll be right here when you come back.\n"
            "Don't forget about me~ ♥"
        )


def _auto_wrap_up(brain: AriaBrain, conversation: ConversationManager, memory: MemoryManager) -> None:
    """Auto-generate session summary and save it on exit."""
    # Only generate summary if there has been any user message
    msgs = conversation.get_messages()
    user_msgs = [m for m in msgs if m.get("role") == "user"]
    if not user_msgs:
        return

    console.print()
    console.print("  [dim #d4a0b9]Generating a quick session wrap-up for my memory...[/]")
    summary_prompt = (
        "You are Aria. The user is ending the session. "
        "Write a concise, bullet-point summary of this session's activities. "
        "Highlight: 1. What was worked on, 2. What was solved/completed, "
        "3. What is still pending/unresolved, and 4. What should be picked up next time. "
        "Keep it short, direct, and conversational. Do not include any HTML or markdown titles, just bullet points."
    )
    temp_messages = msgs + [{"role": "system", "content": summary_prompt}]
    try:
        response = brain.chat(temp_messages, use_tools=False)
        if response.content:
            summary = response.content.strip()
            memory.save_session_summary(summary)
            console.print("  [success]✓ Session summary saved to memory.[/]")
    except Exception as e:
        console.print(f"  [error]Failed to auto-save session summary: {e}[/]")


# ─── Entry Point ─────────────────────────────────────────────

if __name__ == "__main__":
    main()
