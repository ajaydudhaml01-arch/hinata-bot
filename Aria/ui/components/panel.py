"""
Response panel — rich bordered panels with enhanced markdown rendering.

Wraps Aria's responses in a styled panel with mood-colored border,
tool call footer, model badge, and rich content parsing.
"""

import re
import datetime
from pathlib import Path
from typing import List, Tuple

from rich.console import Console, Group
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text
from rich.style import Style
from rich import box

from ui.theme import (
    SURFACE_BORDER, SURFACE_BORDER2, SURFACE_ALT,
    TEXT, TEXT_DIM, TEXT_MUTED, TEXT_FAINT, TIMESTAMP,
    ACCENT, ACCENT_BRIGHT, ACCENT_DIM,
    SUCCESS, INFO, WARNING, PURPLE, SEPARATOR,
    get_mood_config, get_mode_config,
)
from ui.layout import get_console, spacer, dim, content_width, pill_badge, duration_str


def render_response_panel(
    content: str,
    energy: int = 80,
    affection: int = 80,
    current_mode: str = "normal",
    tool_call_count: int = 0,
    response_time_ms: float = 0,
    model_name: str = "",
) -> None:
    """Render Aria's response in a styled bordered panel."""
    console = get_console()
    mood = get_mood_config(energy, affection)
    mode = get_mode_config(current_mode)

    segments = _parse_content_segments(content)
    if _looks_like_startup_greeting(content):
        inner = _render_startup_response(content, mode)
    else:
        inner = _render_response_segments(segments)

    # ── Title (header) ──────────────────────────────────────────────────
    title_text = Text()
    title_text.append(f" {mode['emoji']}  ", style="")
    title_text.append(f"{mode['label']}", style=f"bold {mode['color']}")

    # Mood dot on the right side of title
    title_text.append("  ", style="")
    title_text.append(f"{mood['dot']}", style=f"{mood['color']}")

    # ── Footer (subtitle) ───────────────────────────────────────────────
    footer_text = Text()

    if tool_call_count > 0:
        footer_text.append(f"⚡ {tool_call_count} tool{'s' if tool_call_count != 1 else ''}", style=f"dim {TEXT_MUTED}")
        footer_text.append(f"  {SEPARATOR}  ", style=f"dim {TEXT_FAINT}")

    if response_time_ms > 0:
        footer_text.append(f"{duration_str(response_time_ms)}", style=f"dim {TEXT_MUTED}")
        footer_text.append(f"  {SEPARATOR}  ", style=f"dim {TEXT_FAINT}")

    if model_name:
        footer_text.append(f"{model_name}", style=f"dim {TEXT_FAINT}")
        footer_text.append(f"  {SEPARATOR}  ", style=f"dim {TEXT_FAINT}")

    ts = datetime.datetime.now().strftime("%H:%M")
    footer_text.append(ts, style=f"dim {TIMESTAMP}")

    border_color = mood["color"] if mood else ACCENT_DIM
    panel = Panel(
        inner,
        box=box.ROUNDED,
        border_style=Style(color=border_color, dim=True),
        title=title_text,
        title_align="left",
        subtitle=footer_text,
        subtitle_align="right",
        padding=(1, 2),
        width=content_width(),
    )

    console.print()
    console.print(panel)
    console.print()


# ── Specialized Renderers ────────────────────────────────────────────────────


def _render_response_segments(segments: List[Tuple]) -> Group | Text:
    """Render parsed markdown/code/list segments for normal assistant replies."""
    inner_parts = []
    for seg_type, val in segments:
        if seg_type == "text":
            linked = _inject_links(val)
            inner_parts.append(Markdown(linked))
        elif seg_type == "code":
            code_text, lang = val
            lang = lang.strip() if lang.strip() else ""

            if lang:
                lang_badge = Text()
                lang_badge.append("  「", style=f"dim {PURPLE}")
                lang_badge.append(lang.upper(), style=f"bold {PURPLE}")
                lang_badge.append("」", style=f"dim {PURPLE}")
                inner_parts.append(lang_badge)

            syntax = Syntax(
                code_text,
                lang if lang else "python",
                theme="monokai",
                background_color="default",
                line_numbers=True,
                word_wrap=True,
            )
            inner_parts.append(syntax)
        elif seg_type == "list_table":
            table = Table(
                show_header=False, show_edge=False,
                box=None, padding=(0, 2),
                style="dim",
            )
            table.add_column("idx", style=f"bold {ACCENT}", width=4, justify="right")
            table.add_column("item", style=TEXT)
            for idx, item in val:
                table.add_row(f"{idx}.", item)
            inner_parts.append(table)

    return Group(*inner_parts) if inner_parts else Text("")


def _looks_like_startup_greeting(content: str) -> bool:
    """Detect the startup greeting so it can get a dashboard-style layout."""
    return "Here's your briefing:" in content or "pending reminder(s)" in content


def _render_startup_response(content: str, mode: dict) -> Group:
    """Render the startup greeting as compact cards instead of one wrapped paragraph."""
    greeting, briefing, notes = _split_startup_content(content)
    parts = []

    if greeting:
        hero = Text()
        hero.append("  ✨ ", style=f"bold {mode['color']}")
        hero.append(greeting.replace("\n", " ").strip(), style=TEXT)
        parts.append(Panel(
            hero,
            box=box.ROUNDED,
            border_style=Style(color=mode["color"], dim=True),
            padding=(0, 1),
        ))

    if briefing:
        table = Table.grid(padding=(0, 2))
        table.add_column(style=f"bold {ACCENT}", width=18)
        table.add_column(style=TEXT_DIM)
        for label, value in _briefing_rows(briefing):
            table.add_row(label, value)
        parts.append(Panel(
            table,
            box=box.ROUNDED,
            border_style=Style(color=ACCENT_DIM, dim=True),
            title=Text("  📋 Briefing  ", style=f"bold {ACCENT}"),
            title_align="left",
            padding=(0, 1),
        ))

    for note in notes:
        t = Text()
        t.append("  ◌ ", style=f"dim {WARNING}")
        t.append(note.strip(), style=f"dim {TEXT_DIM}")
        parts.append(t)

    return Group(*parts)


def _split_startup_content(content: str) -> tuple[str, str, list[str]]:
    greeting = content.strip()
    briefing = ""
    notes: list[str] = []

    marker = "📋 Here's your briefing:"
    if marker in greeting:
        greeting, rest = greeting.split(marker, 1)
        briefing = rest.strip()

    note_markers = ["Also...", "🔔"]
    for marker in note_markers:
        source = briefing if briefing else greeting
        if marker in source:
            before, after = source.split(marker, 1)
            notes.append(marker + after.strip())
            if briefing:
                briefing = before.strip()
            else:
                greeting = before.strip()

    return greeting.strip(), briefing.strip(), notes


def _briefing_rows(briefing: str) -> list[tuple[str, str]]:
    rows = []
    for line in briefing.splitlines():
        text = line.strip()
        if not text:
            continue
        lower = text.lower()
        if lower.startswith("this is session"):
            rows.append(("Session", text.replace("This is ", "")))
        elif lower.startswith("last session ended"):
            rows.append(("Last seen", text.replace("Last session ended ", "")))
        elif lower.startswith("average session"):
            rows.append(("Pattern", text))
        elif lower.startswith("today you've logged"):
            rows.append(("Logged", text.replace("Today you've logged: ", "")))
        elif lower.startswith("haven't logged"):
            rows.append(("Needs care", text.replace("Haven't logged today: ", "")))
        elif lower.startswith("you have") and "pending todo" in lower:
            rows.append(("Todos", text))
        elif lower.startswith("active project"):
            rows.append(("Project", text.replace("Active project: ", "")))
        else:
            rows.append(("Note", text))
    return rows


# ── Content Parsing ─────────────────────────────────────────────────────────

def _inject_links(text: str) -> str:
    """Convert local file paths to clickable links."""
    path_pattern = r'([A-Za-z]:\\[A-Za-z0-9_\\.\\\\\\-\\(\\) ]+|/[A-Za-z0-9_\\.\\/\\-]+)'
    def replacer(match):
        path_str = match.group(1)
        try:
            resolved = Path(path_str.strip("\"'"))
            if resolved.exists():
                return f"[link={resolved.absolute().as_uri()}]{resolved.name}[/link]"
        except Exception:
            pass
        return path_str
    return re.sub(path_pattern, replacer, text)


def _parse_content_segments(content: str) -> List[Tuple]:
    """Split response content into text, code, and list segments."""
    code_block_pattern = r'```(\w*)\n(.*?)```'
    parts = re.split(code_block_pattern, content, flags=re.DOTALL)
    segments = []
    i = 0
    while i < len(parts):
        if i % 3 == 0:
            text_seg = parts[i]
            if text_seg.strip():
                list_items = []
                current_text = []
                is_list = False
                for line in text_seg.splitlines():
                    lm = re.match(r'^\s*(\d+)\.\s+(.*)$', line)
                    if lm:
                        is_list = True
                        if current_text:
                            segments.append(("text", "\n".join(current_text)))
                            current_text = []
                        list_items.append((lm.group(1), lm.group(2)))
                    else:
                        if is_list:
                            if line.strip() == "":
                                segments.append(("list_table", list_items))
                                list_items = []
                                is_list = False
                            else:
                                if list_items:
                                    idx, last = list_items[-1]
                                    list_items[-1] = (idx, last + "\n" + line)
                                else:
                                    current_text.append(line)
                        else:
                            current_text.append(line)
                if list_items:
                    segments.append(("list_table", list_items))
                if current_text:
                    segments.append(("text", "\n".join(current_text)))
        else:
            lang = parts[i]
            code_text = parts[i + 1]
            segments.append(("code", (code_text, lang)))
            i += 1
        i += 1
    return segments
