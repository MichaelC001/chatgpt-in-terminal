from typing import Dict

from mentions.x import handle_at_x
from mentions.memo import handle_at_memo
from mentions.raw import handle_at_raw


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
    # @ + space or bare @ => run raw command locally
    if message.strip() == '@' or message.startswith('@ '):
        payload = message[1:].strip()
        return handle_at_raw(payload, console, log)

    # Parse mention name and payload
    mention_body = message[1:]
    parts = mention_body.split(maxsplit=1)
    mention_name = parts[0]
    payload = parts[1].strip() if len(parts) > 1 else ""

    if mention_name == 'x':
        return handle_at_x(chat_gpt, payload, console, log, call_tool)
    if mention_name == 'memo':
        return handle_at_memo(payload, console, log)

    # Unknown mention: let the model handle it
    return False
