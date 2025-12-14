def handle_at_x(chat_gpt, payload: str, console, log, call_tool):
    if not payload:
        console.print("[red]@x 需要后跟要发布的文本[/]")
        return True
    result = call_tool(chat_gpt, "x_post_thread", {"text": payload}, console, log)
    if result:
        urls = result.get("urls") or []
        if urls:
            console.print(f"[green]X posted:[/]\n" + "\n".join(urls))
        else:
            console.print(f"[green]X posted result:[/] {result}")
    return True
