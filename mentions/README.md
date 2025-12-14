# Mentions quick guide

- Purpose: dispatch `@` commands to specific handlers (e.g., `@x` posts to X).
- Structure: put mention logic in `mentions/<name>.py` exporting a handler, and wire it in `gpt_term/tool_and_mention.py`.
- Handler contract: `handle_at_<name>(chat_gpt, payload, console, log, call_tool)` should:
  - Validate payload, print an error via `console` if missing.
  - Call `call_tool(...)` or other logic, return `True` when handled.
- Registration: update `handle_mention` in `gpt_term/tool_and_mention.py` to route the `@<name>` prefix to your handler.
- Example: `mentions/x.py` handles `@x` by invoking the `x_post_thread` tool and printing returned URLs.
