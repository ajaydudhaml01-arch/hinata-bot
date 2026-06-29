"""
Dialogs — styled modal-like panels for mode switches and confirmations.
"""

from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from rich import box

from ui.layout import get_console, content_width
from ui.theme import SURFACE_BORDER, TEXT_DIM, TEXT_MUTED, TEXT_FAINT, SEPARATOR


MODE_SWITCH_HINTS = {
    "prompt": {
        "focus": "I’ll shape responses around prompt engineering: goal, model, inputs, constraints, examples, output format, and evaluation checks.",
        "try": "Try: “turn this into a reusable prompt template” or “critique this prompt before I use it”.",
    },
    "code": {
        "focus": "I’ll prioritize implementation details, architecture, correctness, tests, and practical next steps.",
        "try": "Try: “build this feature”, “review this file”, or “run the tests after changing it”.",
    },
    "debug": {
        "focus": "I’ll trace errors methodically, separate symptoms from root causes, and verify fixes when possible.",
        "try": "Try: paste the exact traceback, failing command, and what changed recently.",
    },
    "study": {
        "focus": "I’ll teach from first principles, use examples, and check understanding instead of only giving answers.",
        "try": "Try: “explain this like I’m new” or “quiz me after teaching it”.",
    },
    "focus": {
        "focus": "I’ll keep replies short, direct, and task-oriented with minimal chatter.",
        "try": "Try: tell me the exact task and I’ll keep us locked on it.",
    },
}


def render_mode_switch(mode_key: str, mode_cfg: dict) -> None:
    """Print a styled mode-switch dialog panel with description."""
    console = get_console()
    hint = MODE_SWITCH_HINTS.get(mode_key, {
        "focus": f"I’ll filter replies through {mode_cfg['desc'].lower()} context until you switch modes again.",
        "try": "Try asking for the next action you want in this mode.",
    })

    inner = Text()
    inner.append(f"\n  {mode_cfg['emoji']}  ", style="")
    inner.append(f"{mode_cfg['label']} MODE", style=f"bold {mode_cfg['color']}")
    inner.append(f"  {SEPARATOR}  ", style=f"dim {TEXT_FAINT}")
    inner.append(f"{mode_cfg['desc']}", style=f"dim {TEXT_DIM}")
    inner.append("\n\n", style="")
    inner.append("  Active lens   ", style=f"bold {mode_cfg['color']}")
    inner.append(hint["focus"], style=TEXT_DIM)
    inner.append("\n", style="")
    inner.append("  Best next ask ", style=f"bold {mode_cfg['color']}")
    inner.append(hint["try"], style=f"dim {TEXT_MUTED}")
    inner.append("\n", style="")

    panel = Panel(
        inner,
        box=box.ROUNDED,
        border_style=Style(color=mode_cfg["color"], dim=True),
        title=Text("  ✦ Mode updated  ", style=f"bold {mode_cfg['color']}"),
        title_align="left",
        padding=(0, 2),
        width=content_width(),
    )
    console.print()
    console.print(panel)
    console.print()


def render_confirm(prompt: str, default_yes: bool = False) -> None:
    """Print a styled confirmation prompt hint."""
    console = get_console()
    t = Text()
    t.append("  ⚠  ", style="bold #fbbf24")
    t.append(prompt, style="white")
    t.append("  ", style="")
    if default_yes:
        t.append("[Y", style="bold #34d399")
        t.append("/n]", style=f"dim {TEXT_MUTED}")
    else:
        t.append("[y/", style=f"dim {TEXT_MUTED}")
        t.append("N]", style="bold #f87171")
    console.print(t)
