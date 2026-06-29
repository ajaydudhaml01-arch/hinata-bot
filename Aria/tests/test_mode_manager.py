from tools.mode_manager import detect_mode_command


def test_bare_mode_phrase_switches_mode():
    assert detect_mode_command("normal mode") == "normal"
    assert detect_mode_command("code mode") == "code"
    assert detect_mode_command("after effects mode") == "ae"
    assert detect_mode_command("prompt mode") == "prompt"
    assert detect_mode_command("prompt category") == "prompt"


def test_mode_list_commands_are_local():
    assert detect_mode_command("/mode list") == "list"
    assert detect_mode_command("/modes") == "list"
    assert detect_mode_command("list modes") == "list"
