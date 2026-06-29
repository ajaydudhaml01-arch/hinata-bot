"""
Prompt Builder — assembles the full system prompt from personality + all context sections.
Provides caching for sections that change infrequently.
"""

import json
from typing import Optional


def build_full_system_prompt(
    user_name: str,
    env_snapshot: Optional[dict],
    memory,
    habits,
    projects,
    concepts,
    data_dir,
    current_mode: str = "normal",
    skip_dynamic: bool = True,
) -> str:
    """Assemble the complete system prompt from personality + all context providers.

    When skip_dynamic=True (default), omits on-demand context sections
    (code, screen, health) — these are loaded lazily via inject_dynamic_context().
    """
    from core.personality import build_system_prompt
    system_prompt = build_system_prompt(user_name)

    # ── Environment Snapshot ──
    if env_snapshot:
        system_prompt += f"\n\n## Environment Snapshot\n{json.dumps(env_snapshot, indent=2)}"

    # ── Memory Context (session-level) ──
    memory_context = memory.get_memory_context()
    if memory_context:
        system_prompt += f"\n\n## Your Memories\n{memory_context}"

    # ── Pattern Insights (session-level) ──
    pattern_insights = memory.get_pattern_insights()
    if pattern_insights:
        system_prompt += f"\n\n## Observed Patterns\n{pattern_insights}"

    # ── Active Project (session-level) ──
    project_context = projects.get_active_project_context()
    if project_context:
        system_prompt += f"\n\n## Active Project\n{project_context}"

    # ── Last Session Summary (session-level) ──
    last_summary = memory.get_last_session_summary()
    if last_summary:
        system_prompt += f"\n\n## Last Session Summary\n{last_summary}"

    # ── Learned Concepts (session-level) ──
    concepts_context = concepts.get_concepts_context()
    if concepts_context:
        system_prompt += f"\n\n## Learned Concepts\n{concepts_context}"

    # ── Anime/VTuber Tracking (session-level) ──
    from tools.anime_tracker import AnimeTracker
    anime = AnimeTracker(data_dir)
    anime_ctx = anime.get_context()
    if anime_ctx:
        system_prompt += f"\n\n## Anime/VTuber Watching\n{anime_ctx}"

    # ── Video Watching Memory (session-level) ──
    try:
        from tools.video_memory import VideoSessionManager
        video_ctx = VideoSessionManager(data_dir).get_context()
        if video_ctx:
            system_prompt += f"\n\n## Videos Watched Together\n{video_ctx}"
    except Exception:
        pass

    if not skip_dynamic:
        # ── Code Context (VS Code + git) ──
        from tools.code_context import CodeContextMonitor
        code_mon = CodeContextMonitor(data_dir)
        code_ctx = code_mon.get_context_string()
        if code_ctx:
            system_prompt += f"\n\n## Active Code Context\n{code_ctx}"

        # ── Screen Context ──
        from tools.screen_monitor import ScreenMonitor
        scr = ScreenMonitor(data_dir)
        scr_ctx = scr.get_context_string()
        if scr_ctx:
            system_prompt += f"\n\n## Screen Context\n{scr_ctx}"

        # ── Budget Context (session-level) ──
        from tools.budget import BudgetManager
        budget = BudgetManager(data_dir)
        budget_ctx = budget.get_context()
        if budget_ctx:
            system_prompt += f"\n\n## Budget Status\n{budget_ctx}"

        # ── Health/Habit context (dynamic) ──
        sleep_ctx = habits.get_sleep_context()
        if sleep_ctx:
            system_prompt += f"\n\n## Sleep Context\n{sleep_ctx}"
        health_nudge = habits.get_health_nudge()
        if health_nudge:
            system_prompt += f"\n\n## Health Nudge\n{health_nudge}"

    # ── Mode-aware injection ──
    if current_mode != "normal":
        from ui.renderer import MODE_CONFIGS
        mode_cfg = MODE_CONFIGS.get(current_mode, MODE_CONFIGS["normal"])
        mode_injection = f"""

## ACTIVE MODE: {mode_cfg['label']}
You are currently in {mode_cfg['label']} MODE — {mode_cfg['desc']}.

In this mode you:
"""
        mode_behaviors = {
            "code":     "Focus entirely on code quality, architecture, and implementation. Proactively suggest improvements. Every response leans technical. Offer to run and test code immediately.",
            "git":      "Focus on git workflow, branch strategy, commit hygiene, and version control best practices. Proactively notice uncommitted changes. Offer git tips relevant to what you see. Suggest good commit messages.",
            "ae":       "Focus on After Effects — expressions, scripting, render settings, plugin usage, and workflow optimization. Watch for active renders. Proactively offer expression snippets and workflow shortcuts.",
            "debug":    "Focus entirely on finding and fixing errors. Be analytical and methodical. Read every error message carefully. Trace root causes, not just symptoms. Run code to verify fixes. Never leave an error unexplained.",
            "study":    "You are in full teaching mode. Explain everything from first principles. Use analogies. Check understanding. Celebrate progress. Never give code without explaining it. Connect new concepts to things already learned.",
            "focus":    "Minimal mode. Short efficient responses only. No small talk. No affectionate terms. Pure productivity. Flag distractions. Keep him on task. Only break focus mode for urgent health or system alerts.",
            "creative": "Focus on creative and artistic projects — Robin, VTuber development, anime-style work, design. Be imaginative and enthusiastic. Suggest creative directions. Think about personality and character design.",
            "research": "Deep dive mode. Search thoroughly before answering. Cross-reference sources. Present multiple perspectives. Flag uncertainties clearly. Synthesize information rather than just listing it.",
            "discord":  "Focus on Discord — server and channel management, message reading and sending, mention monitoring, community engagement. Proactively check unread messages and mentions. Offer to summarize channels and draft messages.",
            "youtube":  "Focus on YouTube — bookmark management, video search and discovery, watching suggestions. Proactively check for unwatched bookmarks. Offer content recommendations based on what you see.",
            "music":    "Focus on music and audio — Spotify control, playlist curation, music discovery. Proactively suggest music based on time of day, mood, or activity. Offer to create playlists and queue tracks.",
            "journal":  "Focus on journaling and reflection — daily entries, memory recall, pattern recognition. Proactively ask about his day, offer to log thoughts, and connect past entries to present context.",
            "vision":   "Focus on screen vision — screenshots, annotation, visual analysis. Proactively offer to capture the screen when describing visual tasks. Analyze screenshots in detail and suggest improvements.",
            "network":  "Focus on network operations — connectivity checks, speed tests, network diagnostics. Proactively monitor connection quality. Offer network troubleshooting and performance optimization tips.",
            "health":   "Focus on system health — CPU, RAM, disk monitoring, resource tracking, wellness alerts. Proactively flag high resource usage. Offer system optimization and cleanup suggestions.",
            "pomodoro": "Focus on productivity timing — pomodoro sessions, focus blocks, break management. Proactively suggest starting a timer when deep work is needed. Track session progress and offer break reminders.",
            "prompt":  "Focus on prompt engineering — clarify the target model, audience, inputs, constraints, success criteria, and output format before writing prompts. Structure prompts with role, context, task, constraints, examples, and evaluation checks. Prefer reusable prompt templates when the task may repeat, and include concise test cases or rubrics for judging prompt quality.",
        }
        mode_injection += mode_behaviors.get(current_mode, "Apply specialized focus for this mode.")
        mode_injection += "\n\nMaintain your core personality but filter everything through this mode's lens.\n"

        mode_injection += """

## MODE TIP (share this at the start of your first response in this session)
When you are in any non-normal mode, at the start of the first response of each session proactively share one highly specific tip or suggestion relevant to that mode. For git mode give a git workflow tip. For AE mode give an expression or shortcut tip. For debug mode ask what error he is hunting. For study mode ask what he is learning today. For focus mode confirm what the current task is and offer to time-block it. This happens once per session automatically, never repeatedly.
"""
        system_prompt += mode_injection

    return system_prompt


def rebuild_system_prompt_after_update(
    user_name: str,
    env_snapshot: Optional[dict],
    memory,
    projects,
    concepts,
    data_dir,
) -> str:
    """Rebuild system prompt after a self-update (hot-reload path, no mode injection)."""
    from core.personality import build_system_prompt
    system_prompt = build_system_prompt(user_name)

    system_prompt += """

## Jarvis-Style Response Filtering
Observe broadly, reason privately, and speak selectively. Default to important-only answers with progressive disclosure: give the smallest useful answer first, then offer more detail only when helpful. For screenshots and screen-aware replies, describe the main relevant thing first and skip incidental details like time, taskbar, window chrome, app title, tabs, and every small UI label unless directly relevant. Escalate detail only when the user asks for a full breakdown, OCR/read-all-text, debugging, where to click, step-by-step guidance, or comparison.
"""

    if env_snapshot:
        system_prompt += f"\n\n## Environment Snapshot\n{json.dumps(env_snapshot, indent=2)}"

    memory_context = memory.get_memory_context()
    if memory_context:
        system_prompt += f"\n\n## Your Memories\n{memory_context}"

    pattern_insights = memory.get_pattern_insights()
    if pattern_insights:
        system_prompt += f"\n\n## Observed Patterns\n{pattern_insights}"

    project_context = projects.get_active_project_context()
    if project_context:
        system_prompt += f"\n\n## Active Project\n{project_context}"

    last_summary = memory.get_last_session_summary()
    if last_summary:
        system_prompt += f"\n\n## Last Session Summary\n{last_summary}"

    concepts_context = concepts.get_concepts_context()
    if concepts_context:
        system_prompt += f"\n\n## Learned Concepts\n{concepts_context}"

    try:
        from tools.video_memory import VideoSessionManager
        video_ctx = VideoSessionManager(data_dir).get_context()
        if video_ctx:
            system_prompt += f"\n\n## Videos Watched Together\n{video_ctx}"
    except Exception:
        pass

    return system_prompt


def build_dynamic_sections(sections: set, data_dir, habits) -> str:
    """Build only the requested dynamic context sections, returned as a block.

    Used by ConversationManager.inject_dynamic_context() for lazy loading.
    """
    parts = []

    if "anime" in sections:
        from tools.anime_tracker import AnimeTracker
        anime = AnimeTracker(data_dir)
        ctx = anime.get_context()
        if ctx:
            parts.append(f"## Anime/VTuber Watching\n{ctx}")

    if "code" in sections:
        from tools.code_context import CodeContextMonitor
        code_mon = CodeContextMonitor(data_dir)
        ctx = code_mon.get_context_string()
        if ctx:
            parts.append(f"## Active Code Context\n{ctx}")

    if "screen" in sections:
        from tools.screen_monitor import ScreenMonitor
        scr = ScreenMonitor(data_dir)
        ctx = scr.get_context_string()
        if ctx:
            parts.append(f"## Screen Context\n{ctx}")

    if "budget" in sections:
        from tools.budget import BudgetManager
        budget = BudgetManager(data_dir)
        ctx = budget.get_context()
        if ctx:
            parts.append(f"## Budget Status\n{ctx}")

    if "health" in sections:
        sleep_ctx = habits.get_sleep_context()
        if sleep_ctx:
            parts.append(f"## Sleep Context\n{sleep_ctx}")
        health_nudge = habits.get_health_nudge()
        if health_nudge:
            parts.append(f"## Health Nudge\n{health_nudge}")

    return "\n\n".join(parts)
