from website import generate_sdk_markdown, generate_terminal_markdown


def test_generate_terminal_markdown():
    """Test the terminal markdown generator"""
    assert generate_terminal_markdown.main() is True


def test_generate_sdk_markdown():
    """Test the sdk markdown generator"""
    assert generate_sdk_markdown.main() is True
