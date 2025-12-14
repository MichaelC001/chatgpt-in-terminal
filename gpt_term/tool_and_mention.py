from typing import Dict

from mentions.x import handle_at_x


def call_tool(chat_gpt, name: str, args: Dict[str, object], console=None, log=None):
    """Call a loaded tool handler directly."""
    handler = chat_gpt.tool_handlers.get(name)
    if not handler:
        if console:
            console.print(f"[red]Tool '{name}' not found[/]")
        return None
    try:
        return handler(**args)
    except Exception as e:
        if console:
            console.print(f"[red]Tool '{name}' failed: {e}[/]")
        if log:
            log.exception(e)
        return None


def handle_mention(chat_gpt, message: str, console=None, log=None) -> bool:
    """Handle @-prefixed commands. Returns True if handled."""
    if not message.startswith('@'):
        return False
    if message.startswith('@x'):
        payload = message[len('@x'):].strip()
        return handle_at_x(chat_gpt, payload, console, log, call_tool)
    return False
