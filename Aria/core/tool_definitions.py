"""
Tool Definitions — all 142 OpenAI function-calling tool definitions.
Exported as TOOL_DEFINITIONS for use by brain.py and dispatch.
"""

TOOL_DEFINITIONS = [
    # ════════════════════════════════════════════════════════════
    # FILE SYSTEM
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Create a new file with optional content. Use for creating files on Desktop, Documents, or anywhere on the user's system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Full file path (e.g., C:\\Users\\Ajayd\\Desktop\\notes.txt)"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file. Empty string for blank file.",
                        "default": ""
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_folder",
            "description": "Create a new folder/directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Full path for the new folder"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "move_item",
            "description": "Move a file or folder to a new location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "Current path of the file/folder"},
                    "destination": {"type": "string", "description": "Destination path"}
                },
                "required": ["source", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rename_item",
            "description": "Rename a file or folder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Current full path of the item"},
                    "new_name": {"type": "string", "description": "New name (just the name, not full path)"}
                },
                "required": ["path", "new_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_item",
            "description": "Delete a file or folder. This is destructive; use only when the user clearly asks to remove a specific item and expect confirmation before execution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Full path of the item to delete"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List contents of a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to list. Defaults to user's home directory.",
                        "default": "~"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a text file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Full path to the file to read"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write a string to a file at the given path, completely replacing its current content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Full path to the file to write"},
                    "content": {"type": "string", "description": "Complete text content to write to the file"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "copy_file",
            "description": "Copy a file from one path to another without modifying either.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "Full path to the source file"},
                    "destination": {"type": "string", "description": "Full path to the destination file"}
                },
                "required": ["source", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "append_file",
            "description": "Append a string to the end of an existing file without replacing existing content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Full path to the file to append to"},
                    "content": {"type": "string", "description": "Text content to append to the file"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_lines",
            "description": "Read a specific range of lines from a file (1-indexed, inclusive). Use this to inspect specific functions or code blocks in large files without reading the entire file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Full path to the target file"},
                    "start_line": {"type": "integer", "description": "The starting line number (1-indexed)"},
                    "end_line": {"type": "integer", "description": "The ending line number (1-indexed, inclusive)"}
                },
                "required": ["path", "start_line", "end_line"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "replace_lines",
            "description": "Replace a specific range of lines (1-indexed, inclusive) in a file with new content. Rest of the file remains untouched. Bypasses file size limits.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Full path to the target file"},
                    "start_line": {"type": "integer", "description": "The starting line number (1-indexed)"},
                    "end_line": {"type": "integer", "description": "The ending line number (1-indexed, inclusive)"},
                    "new_content": {"type": "string", "description": "The replacement content"}
                },
                "required": ["path", "start_line", "end_line", "new_content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_in_file",
            "description": "Search a file for a specific query (like a function, class name, or header) and return matching line numbers and contents. Use this first to locate where to edit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Full path to the target file"},
                    "search_term": {"type": "string", "description": "The term, keyword, function name, class name, or string to search for"}
                },
                "required": ["path", "search_term"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "insert_at_line",
            "description": "Insert new content at a specific line number (1-indexed) in a file, shifting existing lines down. Rest of the file is untouched.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Full path to the target file"},
                    "line_number": {"type": "integer", "description": "The line number (1-indexed) to insert at"},
                    "content": {"type": "string", "description": "The text content to insert"}
                },
                "required": ["path", "line_number", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_lines",
            "description": "Remove a specific range of lines (1-indexed, inclusive) cleanly from a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Full path to the target file"},
                    "start_line": {"type": "integer", "description": "The starting line number (1-indexed)"},
                    "end_line": {"type": "integer", "description": "The ending line number (1-indexed, inclusive)"}
                },
                "required": ["path", "start_line", "end_line"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_file_info",
            "description": "Get file metadata (size in bytes, total line count, last modified time) without reading the file content. Use before deciding how to approach a large file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Full path to the target file"}
                },
                "required": ["path"]
            }
        }
    },

    # ════════════════════════════════════════════════════════════
    # APPLICATIONS
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Open an application by name (e.g., 'notepad', 'chrome', 'vscode', 'explorer', 'spotify', 'discord', etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Application name (common name, not exe path)"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "close_application",
            "description": "Close a running application by its process name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Application/process name to close"}
                },
                "required": ["name"]
            }
        }
    },

    # ════════════════════════════════════════════════════════════
    # DESKTOP AUTOMATION (mouse + keyboard)
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "get_mouse_position",
            "description": "Get the current mouse cursor position on screen. Returns X, Y coordinates. Does not move the mouse.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_screen_size",
            "description": "Get the current screen resolution (width x height).",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mouse_move",
            "description": "Move the mouse cursor to absolute screen coordinates (x, y). Smooth movement.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "Target X coordinate on screen"},
                    "y": {"type": "integer", "description": "Target Y coordinate on screen"}
                },
                "required": ["x", "y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scroll",
            "description": "Scroll the mouse wheel. Use positive numbers to scroll up, negative to scroll down.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "integer", "description": "Number of scroll clicks. Positive = up, negative = down."}
                },
                "required": ["amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "keyboard_hotkey",
            "description": "Press a keyboard shortcut combination. Pass each key as a separate argument, e.g., for Ctrl+C pass keys=['ctrl','c']. Supports: ctrl, alt, shift, win, tab, esc, enter, f1-f24, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keys": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of key names to press simultaneously, e.g. ['ctrl', 'c'], ['alt', 'tab']"
                    }
                },
                "required": ["keys"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mouse_click",
            "description": "Click the mouse at the specified position. If x and y are omitted, clicks at the current cursor position.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "Optional X coordinate to click at"},
                    "y": {"type": "integer", "description": "Optional Y coordinate to click at"},
                    "button": {"type": "string", "enum": ["left", "middle", "right"], "description": "Mouse button to click (default: left)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mouse_double_click",
            "description": "Double-click at the specified position. If x and y are omitted, double-clicks at the current cursor position.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "Optional X coordinate"},
                    "y": {"type": "integer", "description": "Optional Y coordinate"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mouse_right_click",
            "description": "Right-click at the specified position. If x and y are omitted, right-clicks at the current cursor position.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "Optional X coordinate"},
                    "y": {"type": "integer", "description": "Optional Y coordinate"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mouse_drag",
            "description": "Drag the mouse from one position to another (click and hold, move, release). Useful for selecting text or moving items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_x": {"type": "integer", "description": "Starting X coordinate"},
                    "start_y": {"type": "integer", "description": "Starting Y coordinate"},
                    "end_x": {"type": "integer", "description": "Ending X coordinate"},
                    "end_y": {"type": "integer", "description": "Ending Y coordinate"}
                },
                "required": ["start_x", "start_y", "end_x", "end_y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Type a string of text at the current cursor position. Use for filling forms, typing messages, or entering text. Maximum 1000 characters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to type"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "keyboard_press",
            "description": "Press and release a single keyboard key. For key combinations use keyboard_hotkey instead. Common keys: enter, esc, tab, backspace, delete, space, up, down, left, right, f1-f24.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Key name to press"}
                },
                "required": ["key"]
            }
        }
    },

    # ════════════════════════════════════════════════════════════
    # BROWSER
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "open_url",
            "description": "Open a URL in the default web browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to open"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_youtube",
            "description": "Search YouTube for videos and open the search results page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for YouTube"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "google_search",
            "description": "Open a Google search in the browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for Google"}
                },
                "required": ["query"]
            }
        }
    },

    # ════════════════════════════════════════════════════════════
    # SYSTEM INFO
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "get_battery_status",
            "description": "Get current battery level and charging status.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Get system information: CPU, RAM, OS, uptime.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_disk_space",
            "description": "Get disk space usage for all drives.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_running_processes",
            "description": "Get top running processes by CPU or memory usage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sort_by": {
                        "type": "string",
                        "enum": ["cpu", "memory"],
                        "description": "Sort processes by CPU or memory usage",
                        "default": "memory"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of processes to return",
                        "default": 10
                    }
                },
                "required": []
            }
        }
    },

    # ════════════════════════════════════════════════════════════
    # MEMORY
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "remember",
            "description": "Store something in Aria's memory to remember across sessions. Use this when the user tells you to remember something.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Short label for what to remember (e.g., 'favorite_color', 'project_deadline')"},
                    "value": {"type": "string", "description": "The information to remember"}
                },
                "required": ["key", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "recall",
            "description": "Retrieve something from Aria's memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The label to look up. Use 'all' to list everything remembered.",
                        "default": "all"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "forget",
            "description": "Remove something from Aria's memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "The label to forget"}
                },
                "required": ["key"]
            }
        }
    },

    # ════════════════════════════════════════════════════════════
    # REMINDERS
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "add_reminder",
            "description": "Add a reminder or note for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The reminder text"},
                    "due": {"type": "string", "description": "Optional due date/time (natural language like 'tomorrow', '5pm', 'next Monday')", "default": ""}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_reminders",
            "description": "List all active reminders.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_reminder",
            "description": "Mark a reminder as completed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reminder_id": {"type": "integer", "description": "The ID of the reminder to complete"}
                },
                "required": ["reminder_id"]
            }
        }
    },

    # ════════════════════════════════════════════════════════════
    # SCREEN VISION
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Capture the user's screen when visual context is needed. After using it, answer with filtered, important-only observations unless the user explicitly asks for full detail/OCR/debug/step-by-step guidance.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },

    # ════════════════════════════════════════════════════════════
    # SHELL
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "run_shell_command",
            "description": "Run a shell command on the user's system. Use for anything that isn't covered by other tools — installing software, running scripts, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The shell command to run (PowerShell on Windows)"}
                },
                "required": ["command"]
            }
        }
    },

    # ════════════════════════════════════════════════════════════
    # HABITS
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "log_habit",
            "description": "Log a daily habit. Use when user says they ate, drank water, slept, exercised, took a break, or stretched. Common habits: eat, water, sleep, exercise, break, stretch.",
            "parameters": {
                "type": "object",
                "properties": {
                    "habit": {
                        "type": "string",
                        "description": "The habit name (e.g., 'eat', 'water', 'sleep', 'exercise')"
                    },
                    "value": {
                        "type": "string",
                        "description": "Optional value (e.g., '7 hours' for sleep, 'lunch' for eat)",
                        "default": "true"
                    }
                },
                "required": ["habit"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_habit_report",
            "description": "Get a summary of tracked habits over the last N days with streaks and completion data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "Number of days to report on",
                        "default": 7
                    }
                },
                "required": []
            }
        }
    },

    # ════════════════════════════════════════════════════════════
    # TODO LIST
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "add_todo",
            "description": "Add a task to the persistent todo list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The task description"},
                    "project": {"type": "string", "description": "Optional project to associate with", "default": ""},
                    "priority": {
                        "type": "string",
                        "enum": ["high", "normal", "low"],
                        "description": "Task priority",
                        "default": "normal"
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_todos",
            "description": "List all active todo items, optionally filtered by project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project": {"type": "string", "description": "Filter by project name", "default": ""},
                    "show_completed": {"type": "boolean", "description": "Include completed todos", "default": False}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_todo",
            "description": "Mark a todo item as complete.",
            "parameters": {
                "type": "object",
                "properties": {
                    "todo_id": {"type": "integer", "description": "The ID of the todo to complete"}
                },
                "required": ["todo_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_todo",
            "description": "Delete a todo item.",
            "parameters": {
                "type": "object",
                "properties": {
                    "todo_id": {"type": "integer", "description": "The ID of the todo to delete"}
                },
                "required": ["todo_id"]
            }
        }
    },

    # ════════════════════════════════════════════════════════════
    # POMODORO TIMER
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "start_pomodoro",
            "description": "Start a Pomodoro work/break timer cycle. Notifies when work period ends and break period ends.",
            "parameters": {
                "type": "object",
                "properties": {
                    "work_mins": {"type": "integer", "description": "Minutes of focused work", "default": 25},
                    "break_mins": {"type": "integer", "description": "Minutes of break", "default": 5}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "stop_pomodoro",
            "description": "Cancel the current Pomodoro timer.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "pomodoro_status",
            "description": "Check the current Pomodoro timer status — time remaining and phase.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },

    # ════════════════════════════════════════════════════════════
    # PROJECTS
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "add_project",
            "description": "Register a new project with a name and optional directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Project name"},
                    "directory": {"type": "string", "description": "Project directory path", "default": ""},
                    "description": {"type": "string", "description": "Brief project description", "default": ""}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "switch_project",
            "description": "Switch active project context. Loads project notes and directory info.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Project name to switch to"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_projects",
            "description": "List all registered projects.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_project_note",
            "description": "Add a note to a project (defaults to active project).",
            "parameters": {
                "type": "object",
                "properties": {
                    "note": {"type": "string", "description": "The note to add"},
                    "project": {"type": "string", "description": "Project name (defaults to active project)", "default": ""}
                },
                "required": ["note"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_project_notes",
            "description": "Get all notes for a project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project": {"type": "string", "description": "Project name (defaults to active project)", "default": ""}
                },
                "required": []
            }
        }
    },

    # ════════════════════════════════════════════════════════════
    # WINDOW MANAGEMENT
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "list_windows",
            "description": "List all currently open/visible windows.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "focus_window",
            "description": "Bring a window to the foreground by its title (substring match).",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Window title or partial title to match"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "minimize_window",
            "description": "Minimize a specific window by title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Window title to minimize"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "maximize_window",
            "description": "Maximize a specific window by title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Window title to maximize"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "minimize_all_windows",
            "description": "Minimize all windows (show desktop).",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "arrange_windows",
            "description": "Arrange open windows in a layout: side_by_side, stacked, or cascade.",
            "parameters": {
                "type": "object",
                "properties": {
                    "layout": {
                        "type": "string",
                        "enum": ["side_by_side", "stacked", "cascade"],
                        "description": "Window arrangement layout"
                    }
                },
                "required": ["layout"]
            }
        }
    },

    # ════════════════════════════════════════════════════════════
    # SYSTEM CONTROLS
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "set_volume",
            "description": "Set the system volume to a percentage (0-100).",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {"type": "integer", "description": "Volume level (0-100)"}
                },
                "required": ["level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_volume",
            "description": "Get the current system volume level.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mute_audio",
            "description": "Mute system audio.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "unmute_audio",
            "description": "Unmute system audio.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_brightness",
            "description": "Set screen brightness to a percentage (0-100).",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {"type": "integer", "description": "Brightness level (0-100)"}
                },
                "required": ["level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_brightness",
            "description": "Get current screen brightness.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },

    # ════════════════════════════════════════════════════════════
    # DESKTOP CLEANUP
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "preview_desktop_cleanup",
            "description": "Preview what a desktop cleanup would do — shows which files would be sorted into which folders. Does not move anything.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cleanup_desktop",
            "description": "Organize Desktop files into categorized folders (Images, Videos, Documents, Code, etc.). Creates an undo log.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "undo_desktop_cleanup",
            "description": "Undo the last desktop cleanup — restore all moved files to their original locations.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },

    # ════════════════════════════════════════════════════════════
    # MUSIC CONTROL
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "play_pause_music",
            "description": "Toggle play/pause for the active media player (Spotify, browser, VLC, etc.).",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "next_track",
            "description": "Skip to the next track in the active media player.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "prev_track",
            "description": "Go to the previous track in the active media player.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },

    # ════════════════════════════════════════════════════════════
    # BOOKMARKS
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "bookmark_tutorial",
            "description": "Save a tutorial bookmark with title, URL, timestamp, and notes. Use when user says 'bookmark this' or wants to save where they are in a tutorial.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Tutorial/video title"},
                    "url": {"type": "string", "description": "URL of the tutorial", "default": ""},
                    "timestamp": {"type": "string", "description": "Timestamp in the video (e.g., '12:30' or '1:05:20')", "default": ""},
                    "notes": {"type": "string", "description": "Optional notes about what was being learned", "default": ""},
                    "category": {"type": "string", "description": "Category (e.g., 'python', 'after-effects', 'blender')", "default": ""}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_bookmarks",
            "description": "List all saved tutorial bookmarks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Filter by category", "default": ""}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "resume_bookmark",
            "description": "Resume a bookmarked tutorial — opens the URL at the saved timestamp.",
            "parameters": {
                "type": "object",
                "properties": {
                    "bookmark_id": {"type": "integer", "description": "The bookmark ID to resume"}
                },
                "required": ["bookmark_id"]
            }
        }
    },

    # ════════════════════════════════════════════════════════════
    # CONCEPT NOTES
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "save_concept",
            "description": "Save a concept or piece of knowledge the user learned. Use when user says 'remember this concept' or explains something they learned.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Short title for the concept"},
                    "content": {"type": "string", "description": "Full explanation or notes about the concept"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags for categorization (e.g., ['python', 'async'])",
                        "default": []
                    }
                },
                "required": ["title", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_concepts",
            "description": "Search through saved concepts by keyword.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_concepts",
            "description": "List all saved concept notes, optionally filtered by tag.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tag": {"type": "string", "description": "Filter by tag", "default": ""}
                },
                "required": []
            }
        }
    },

    # ════════════════════════════════════════════════════════════
    # RENDER MONITOR
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "watch_process",
            "description": "Watch a specific process and notify when it finishes. Useful for renders, builds, or long-running tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "process_name": {"type": "string", "description": "Process name to watch (e.g., 'afterfx', 'ffmpeg', 'blender')"},
                    "description": {"type": "string", "description": "Description for the notification", "default": ""}
                },
                "required": ["process_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_active_renders",
            "description": "Check if any render processes are currently running.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_dnd_mode",
            "description": "Set Do Not Disturb (DND) / Focus Mode. When ON, all proactive notifications and suggestions are suppressed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "active": {
                        "type": "boolean",
                        "description": "True to turn DND on (quiet focus), False to turn DND off (resume normal notifications)"
                    }
                },
                "required": ["active"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_task",
            "description": "Schedule a reminder notification or background shell command to execute at a specific time or interval.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_type": {
                        "type": "string",
                        "enum": ["reminder", "command"],
                        "description": "Type of task to schedule."
                    },
                    "time_spec": {
                        "type": "string",
                        "description": "Time specification (e.g., 'in 5 minutes', '9pm', '21:00', 'daily 08:00', 'every morning at 8')"
                    },
                    "reminder_text": {
                        "type": "string",
                        "description": "Text for the reminder (required if task_type is 'reminder').",
                        "default": ""
                    },
                    "command": {
                        "type": "string",
                        "description": "Shell command to run (required if task_type is 'command').",
                        "default": ""
                    }
                },
                "required": ["task_type", "time_spec"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_scheduled_tasks",
            "description": "List all active scheduled reminders and background commands.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_scheduled_task",
            "description": "Cancel a scheduled task using its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to cancel."
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_session_summary",
            "description": "Save a session summary (what was worked on, completed, pending, and next steps) to persistent memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "The session summary bullet points."
                    }
                },
                "required": ["summary"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "self_update_prompt",
            "description": "Permanently update Aria's own system prompt with new instructions, behaviors, capabilities, or rules.",
            "parameters": {
                "type": "object",
                "properties": {
                    "instruction": {
                        "type": "string",
                        "description": "The instruction or rule block to permanently integrate into the system prompt."
                    }
                },
                "required": ["instruction"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_safe_verification",
            "description": "Run Aria's local safe verification harness for non-destructive filesystem, persistence, and read-only system tools. Optionally include browser or desktop read-only checks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "include_browser": {
                        "type": "boolean",
                        "description": "Launch Chromium and verify safe browser read/navigation commands against example.com.",
                        "default": False
                    },
                    "include_desktop": {
                        "type": "boolean",
                        "description": "Verify read-only desktop state commands like mouse position and screen size.",
                        "default": False
                    }
                },
                "required": []
            }
        }
    },
    # Git Integration
    {
        "type": "function",
        "function": {
            "name": "git_status",
            "description": "Get status of a git repository (branch, modified, untracked, staged).",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string", "description": "Path to the local git repository"}
                },
                "required": ["repo_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_commit",
            "description": "Stage all changes and commit with the given message.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string", "description": "Path to the local git repository"},
                    "message": {"type": "string", "description": "Commit message"}
                },
                "required": ["repo_path", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_push",
            "description": "Push committed changes of the active branch to remote. This affects shared repository state; use only when the user explicitly asks to push and expect confirmation before execution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string", "description": "Path to the local git repository"},
                    "remote": {"type": "string", "description": "Remote name (e.g. 'origin')", "default": "origin"},
                    "branch": {"type": "string", "description": "Branch to push. Defaults to active branch.", "default": ""}
                },
                "required": ["repo_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_pull",
            "description": "Pull latest changes from remote.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string", "description": "Path to the local git repository"}
                },
                "required": ["repo_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_branch_list",
            "description": "List all branches in the repository, with the active one marked.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string", "description": "Path to the local git repository"}
                },
                "required": ["repo_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_branch_create",
            "description": "Create and check out a new branch.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string", "description": "Path to the local git repository"},
                    "branch_name": {"type": "string", "description": "Name of the new branch"}
                },
                "required": ["repo_path", "branch_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_log",
            "description": "Get last N commits with author, timestamp, and message.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string", "description": "Path to the local git repository"},
                    "count": {"type": "integer", "description": "Number of commits to retrieve", "default": 5}
                },
                "required": ["repo_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_diff",
            "description": "Show git diff for a specific file or all changes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string", "description": "Path to the local git repository"},
                    "file_path": {"type": "string", "description": "Optional file path to diff. Empty for all changes.", "default": ""}
                },
                "required": ["repo_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_stash",
            "description": "Stash current local changes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string", "description": "Path to the local git repository"}
                },
                "required": ["repo_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_stash_pop",
            "description": "Restore last stashed changes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string", "description": "Path to the local git repository"}
                },
                "required": ["repo_path"]
            }
        }
    },
    # Discord Integration
    {
        "type": "function",
        "function": {
            "name": "discord_unread_summary",
            "description": "Get a summary of unread messages grouped by server and channel.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "discord_read_channel",
            "description": "Read last N messages from a specific channel.",
            "parameters": {
                "type": "object",
                "properties": {
                    "server_name": {"type": "string", "description": "Discord server name"},
                    "channel_name": {"type": "string", "description": "Channel name"},
                    "count": {"type": "integer", "description": "Number of messages to read", "default": 10}
                },
                "required": ["server_name", "channel_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "discord_send_message",
            "description": "Send a message to a Discord channel. This is visible to other people; use only when the user clearly asks to send or draft a specific message and expect confirmation before execution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "server_name": {"type": "string", "description": "Discord server name"},
                    "channel_name": {"type": "string", "description": "Channel name"},
                    "message": {"type": "string", "description": "Message content to send"}
                },
                "required": ["server_name", "channel_name", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "discord_check_mentions",
            "description": "Get all recent messages where the user was mentioned or replied to.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "discord_dm_read",
            "description": "Read recent DMs from a specific user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "Username of the DM partner"}
                },
                "required": ["username"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "discord_dm_send",
            "description": "Send a DM to a specific user. Confirms before sending.",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "Username to send the DM to"},
                    "message": {"type": "string", "description": "Message content"}
                },
                "required": ["username", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "discord_list_servers",
            "description": "List all Discord servers the bot is connected to, with member counts.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "discord_list_channels",
            "description": "List all text and voice channels in a Discord server.",
            "parameters": {
                "type": "object",
                "properties": {
                    "server_name": {"type": "string", "description": "Discord server name"}
                },
                "required": ["server_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "discord_server_info",
            "description": "Get information about a Discord server: member count, online count, channels, roles, owner, creation date, boost level.",
            "parameters": {
                "type": "object",
                "properties": {
                    "server_name": {"type": "string", "description": "Discord server name"}
                },
                "required": ["server_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "discord_online_members",
            "description": "List members who are currently online in a Discord server.",
            "parameters": {
                "type": "object",
                "properties": {
                    "server_name": {"type": "string", "description": "Discord server name"}
                },
                "required": ["server_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "discord_member_info",
            "description": "Get details about a specific member in a Discord server: nickname, status, roles, join date, account creation date, bot status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "server_name": {"type": "string", "description": "Discord server name"},
                    "username": {"type": "string", "description": "Username of the member (with discriminator if needed)"}
                },
                "required": ["server_name", "username"]
            }
        }
    },
    # Spotify and Media Control
    {
        "type": "function",
        "function": {
            "name": "spotify_play",
            "description": "Play a track, artist, album, or playlist on Spotify.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "spotify_pause",
            "description": "Pause playback.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "spotify_resume",
            "description": "Resume playback.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "spotify_skip",
            "description": "Skip to the next track.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "spotify_previous",
            "description": "Go to the previous track.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "spotify_volume",
            "description": "Set Spotify volume level (0 to 100).",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {"type": "integer", "description": "Volume level (0-100)"}
                },
                "required": ["level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "spotify_current_track",
            "description": "Get information about the currently playing track.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "spotify_queue_add",
            "description": "Add a track to Spotify queue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for the track to queue"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "spotify_create_playlist",
            "description": "Create a new Spotify playlist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Playlist name"},
                    "description": {"type": "string", "description": "Optional playlist description", "default": ""}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "spotify_liked_songs",
            "description": "Get recent liked songs from Spotify.",
            "parameters": {
                "type": "object",
                "properties": {
                    "count": {"type": "integer", "description": "Number of songs to retrieve", "default": 5}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_music_recommendation",
            "description": "Get a personalized music recommendation based on your listening history. Requires at least 20 logged listens.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    # YouTube Timestamp Bookmarking
    {
        "type": "function",
        "function": {
            "name": "youtube_bookmark_current",
            "description": "Bookmark current YouTube video and timestamp using screen vision.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "youtube_bookmarks_list",
            "description": "List all saved YouTube bookmarks.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "youtube_bookmark_open",
            "description": "Open a bookmarked video in the browser and seek to the saved timestamp.",
            "parameters": {
                "type": "object",
                "properties": {
                    "index_or_title": {"type": "string", "description": "Bookmark index or partial title"}
                },
                "required": ["index_or_title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "youtube_bookmark_delete",
            "description": "Delete a bookmarked video.",
            "parameters": {
                "type": "object",
                "properties": {
                    "index_or_title": {"type": "string", "description": "Bookmark index or partial title"}
                },
                "required": ["index_or_title"]
            }
        }
    },
    # Screenshot Annotation
    {
        "type": "function",
        "function": {
            "name": "screenshot_annotate",
            "description": "Take a screenshot and annotate it based on natural language instructions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "instructions": {"type": "string", "description": "Instructions (e.g. 'circle the error message', 'arrow to submit')"}
                },
                "required": ["instructions"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "screenshot_compare",
            "description": "Compare two screenshots using vision model and describe differences.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path1": {"type": "string", "description": "Path to first screenshot"},
                    "path2": {"type": "string", "description": "Path to second screenshot"}
                },
                "required": ["path1", "path2"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "screenshot_annotate_file",
            "description": "Annotate an existing image file based on instructions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Path to the target image file"},
                    "instructions": {"type": "string", "description": "Instructions (e.g. 'circle the error message')"}
                },
                "required": ["image_path", "instructions"]
            }
        }
    },
    # Code Execution Sandbox
    {
        "type": "function",
        "function": {
            "name": "code_run_python",
            "description": "Execute inline Python code in an isolated subprocess.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to run"},
                    "timeout_seconds": {"type": "integer", "description": "Timeout in seconds", "default": 30}
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "code_run_powershell",
            "description": "Execute a PowerShell command in a subprocess.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "PowerShell command"},
                    "timeout_seconds": {"type": "integer", "description": "Timeout in seconds", "default": 30}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "code_run_node",
            "description": "Execute JavaScript code via Node.js in a subprocess.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "JavaScript code to run"},
                    "timeout_seconds": {"type": "integer", "description": "Timeout in seconds", "default": 30}
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "code_test_file",
            "description": "Run a local Python script in the virtual environment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the Python file"}
                },
                "required": ["file_path"]
            }
        }
    },
    # Network Monitor
    {
        "type": "function",
        "function": {
            "name": "network_status",
            "description": "Get current connection latency, quality, and API reachability.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "network_speedtest",
            "description": "Run a full network speed test (takes 15 to 30 seconds).",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    # Automatic Daily Journal
    {
        "type": "function",
        "function": {
            "name": "journal_read",
            "description": "Read the journal entry for a specific date or 'today'/'yesterday'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_str": {"type": "string", "description": "Date in YYYY-MM-DD or 'today'/'yesterday'"}
                },
                "required": ["date_str"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "journal_search",
            "description": "Search all daily journals for a keyword.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "Keyword to search for"}
                },
                "required": ["keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "journal_summary",
            "description": "Summarize the last N days of journal entries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Number of days", "default": 7}
                },
                "required": []
            }
        }
    },
    # Robin Integration
    {
        "type": "function",
        "function": {
            "name": "robin_status",
            "description": "Check Robin's process status, uptime, CPU and memory usage.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "robin_start",
            "description": "Start the Robin AI process.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "robin_stop",
            "description": "Stop the Robin AI process. Confirms before executing.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "robin_logs",
            "description": "Read the last N lines from Robin's log file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lines": {"type": "integer", "description": "Number of lines to read", "default": 20}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "robin_test",
            "description": "Send a test message to Robin and get her response.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Message to send"}
                },
                "required": ["message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "robin_compare",
            "description": "Send the same message to both Aria and Robin and compare responses side-by-side.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Message to compare"}
                },
                "required": ["message"]
            }
        }
    },
    # Anime/VTuber Tracker
    {
        "type": "function",
        "function": {
            "name": "anime_add",
            "description": "Start tracking a new anime show or VTuber. Use when user mentions a new show they're watching.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Show name"},
                    "category": {"type": "string", "enum": ["anime", "vtuber"], "description": "Category", "default": "anime"},
                    "url": {"type": "string", "description": "Optional URL", "default": ""},
                    "notes": {"type": "string", "description": "Optional notes", "default": ""}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "anime_log_episode",
            "description": "Log that you watched an episode of a show. Use when user says they watched an episode.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Show name"},
                    "episode_num": {"type": "integer", "description": "Episode number watched"},
                    "summary": {"type": "string", "description": "Brief summary of what happened", "default": ""},
                    "rating": {"type": "integer", "description": "Rating 1-10", "default": 0}
                },
                "required": ["title", "episode_num"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "anime_status",
            "description": "Get the current watching status and progress of a show.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Show name"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "anime_list",
            "description": "List all tracked shows, optionally filtered by category or status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Filter by category", "default": ""},
                    "status": {"type": "string", "enum": ["watching", "completed", "paused", "dropped", "plan_to_watch"], "description": "Filter by status", "default": ""}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "anime_update_status",
            "description": "Update the status of a tracked show (watching, completed, paused, dropped, plan_to_watch).",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Show name"},
                    "new_status": {"type": "string", "enum": ["watching", "completed", "paused", "dropped", "plan_to_watch"], "description": "New status"}
                },
                "required": ["title", "new_status"]
            }
        }
    },
    # Budget Tracking
    {
        "type": "function",
        "function": {
            "name": "budget_set",
            "description": "Set a budget limit for a project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project": {"type": "string", "description": "Project name"},
                    "amount": {"type": "number", "description": "Budget limit in dollars"}
                },
                "required": ["project", "amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "budget_expense",
            "description": "Log an expense for a project. Use when user tells you they spent money on something.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project": {"type": "string", "description": "Project name"},
                    "amount": {"type": "number", "description": "Amount spent in dollars"},
                    "description": {"type": "string", "description": "What the expense was for", "default": ""}
                },
                "required": ["project", "amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "budget_income",
            "description": "Log income/funding received for a project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project": {"type": "string", "description": "Project name"},
                    "amount": {"type": "number", "description": "Amount received in dollars"},
                    "description": {"type": "string", "description": "Source of income", "default": ""}
                },
                "required": ["project", "amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "budget_summary",
            "description": "Get a budget summary for a specific project or all projects.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project": {"type": "string", "description": "Project name. Empty for all projects.", "default": ""}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "budget_recent",
            "description": "Get recent transactions across all or specific projects.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project": {"type": "string", "description": "Project name. Empty for all.", "default": ""},
                    "days": {"type": "integer", "description": "How many days back to look", "default": 7}
                },
                "required": []
            }
        }
    },
    # Health Nudges
    {
        "type": "function",
        "function": {
            "name": "log_health_nudge",
            "description": "Get a smart health nudge based on time of day and habit patterns. Checks meal times, sleep, water, breaks automatically.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    # Code Context
    {
        "type": "function",
        "function": {
            "name": "check_screen_context",
            "description": "Check what the user currently has open — active window, VS Code file, recent git activity. Use to offer context-aware help without being asked.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    # Stuck Detection
    {
        "type": "function",
        "function": {
            "name": "sense_stuck",
            "description": "Check if the user has been on the same window for too long without asking for help, suggesting they may be stuck. Use proactively.",
            "parameters": {
                "type": "object",
                "properties": {
                    "threshold": {"type": "integer", "description": "Minutes on same window before considering stuck", "default": 20}
                },
                "required": []
            }
        }
    },
    # Quick Journal Entry
    {
        "type": "function",
        "function": {
            "name": "journal_write_quick",
            "description": "Write a quick timestamped note to today's journal. Use when user says 'note that down' or shares something worth logging.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The journal note to write"}
                },
                "required": ["text"]
            }
        }
    },

    # ════════════════════════════════════════════════════════════
    # VIDEO WATCHING MEMORY
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "video_start",
            "description": "Start a video watching memory session. Use when the user wants Aria to watch a video with them and remember notes, transcript snippets, and captured frames. This does not continuously record; it only remembers what the user asks to save.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Video title or short description"},
                    "url": {"type": "string", "description": "Optional video URL", "default": ""},
                    "source": {"type": "string", "description": "Optional source such as youtube, local, course, anime", "default": ""}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "video_note",
            "description": "Add a note about what happened in the active video session.",
            "parameters": {
                "type": "object",
                "properties": {
                    "note": {"type": "string", "description": "What happened or what to remember"},
                    "timestamp": {"type": "string", "description": "Optional video timestamp like 12:34", "default": ""}
                },
                "required": ["note"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "video_transcript",
            "description": "Save a user-provided transcript/subtitle snippet into the active video session.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Transcript or subtitle text pasted by the user"},
                    "timestamp": {"type": "string", "description": "Optional timestamp for the snippet", "default": ""}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "video_capture_frame",
            "description": "Capture the current screen as a video frame for the active video session. Use only when the user asks to save/capture/remember the current frame.",
            "parameters": {
                "type": "object",
                "properties": {
                    "note": {"type": "string", "description": "Optional note describing the frame", "default": ""},
                    "timestamp": {"type": "string", "description": "Optional video timestamp", "default": ""}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "video_end",
            "description": "End the active video session and save a summary of what happened.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Optional user-provided final summary", "default": ""}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "video_status",
            "description": "Show the active video watching session status, note count, and captured frame count.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "video_list",
            "description": "List recent videos Aria watched with the user and remembered.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of sessions to list", "default": 10}
                },
                "required": []
            }
        }
    },

    # ════════════════════════════════════════════════════════════
    # PASSWORD VAULT
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "vault_save",
            "description": "Save a password/credential to the encrypted vault. Requires vault to be unlocked. Use when the user says 'save my password', 'remember my login', or 'store credentials'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service": {"type": "string", "description": "Service name (e.g., 'github', 'gmail', 'netflix')"},
                    "username": {"type": "string", "description": "Username or email for the service"},
                    "password": {"type": "string", "description": "The password to store (encrypted at rest)"},
                    "url": {"type": "string", "description": "Optional login URL for the service"}
                },
                "required": ["service", "username", "password"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "vault_get",
            "description": "Get saved credentials for a service. Returns the username (not the password — use vault_get_password if you need the password). Requires vault to be unlocked.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service": {"type": "string", "description": "Service name to look up"}
                },
                "required": ["service"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "vault_get_password",
            "description": "Get the decrypted password for a service. This exposes sensitive credentials; use only when truly necessary, such as filling a login form the user requested, and expect confirmation before execution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service": {"type": "string", "description": "Service name to look up"}
                },
                "required": ["service"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "vault_list",
            "description": "List all services that have saved credentials in the vault.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "vault_delete",
            "description": "Delete saved credentials for a service from the vault.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service": {"type": "string", "description": "Service name to delete"}
                },
                "required": ["service"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "vault_lock",
            "description": "Lock the password vault so no credentials can be retrieved until unlocked again.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    # ════════════════════════════════════════════════════════════
    # WEB AUTOMATION
    # ════════════════════════════════════════════════════════════
    {
        "type": "function",
        "function": {
            "name": "web_navigate",
            "description": "Navigate the browser to a URL. Launches the browser on first call.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to navigate to (e.g., 'https://example.com')"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_click",
            "description": "Click the first element on the page that matches the given CSS selector.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector to find the element (e.g., '#login-button', '.submit-btn', 'button[type=submit]')"}
                },
                "required": ["selector"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_type",
            "description": "Type text into an input field identified by CSS selector. Fills the field (clears existing content first).",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector for the input field"},
                    "text": {"type": "string", "description": "Text to type into the field"}
                },
                "required": ["selector", "text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_get_text",
            "description": "Get the visible text content of an element on the page. Useful for reading paragraphs, headings, or any visible content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector for the element to read text from"}
                },
                "required": ["selector"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_get_html",
            "description": "Get the inner HTML of an element. Useful for inspecting page structure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector for the element to read HTML from"}
                },
                "required": ["selector"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_get_url",
            "description": "Get the current URL of the page the browser is on.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_get_title",
            "description": "Get the title of the current web page.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_screenshot",
            "description": "Take a screenshot of the current browser page and save it to the data directory.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_wait_for",
            "description": "Wait for an element matching the CSS selector to appear on the page. Useful before interacting with dynamically loaded content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector to wait for"},
                    "timeout": {"type": "integer", "description": "Maximum wait time in milliseconds (default: 10000)"}
                },
                "required": ["selector"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_select",
            "description": "Select an option from a dropdown/select element by its value.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector for the select element"},
                    "value": {"type": "string", "description": "Option value to select"}
                },
                "required": ["selector", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_submit",
            "description": "Submit the current form by pressing Enter on the focused element.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_hover",
            "description": "Hover the mouse over the first element matching the given CSS selector. Useful for triggering dropdown menus, tooltips, or hover effects before clicking.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector for the element to hover over"}
                },
                "required": ["selector"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_back",
            "description": "Go back one page in browser history.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_forward",
            "description": "Go forward one page in browser history.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_close",
            "description": "Close the browser window and end the browsing session.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_login",
            "description": "Automate logging into a website. Provide URL, username, password, and CSS selectors for the form fields. For best results, call vault_get first to retrieve stored credentials, then call this with those values.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Login page URL"},
                    "username": {"type": "string", "description": "Username or email to fill in"},
                    "password": {"type": "string", "description": "Password to fill in"},
                    "username_selector": {"type": "string", "description": "CSS selector for the username/email input field (default: '#username')"},
                    "password_selector": {"type": "string", "description": "CSS selector for the password input field (default: '#password')"},
                    "submit_selector": {"type": "string", "description": "Optional CSS selector for the submit button. If omitted, presses Enter."}
                },
                "required": ["url", "username", "password"]
            }
        }
    },
]
