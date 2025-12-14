import os
import subprocess


def handle_at_memo(payload: str, console, log):
    """Pass @memo content directly to the memo CLI and print output."""
    if not payload:
        console.print("[red]@memo 需要后跟命令，例如: @memo add \"note\"[/]")
        return True
    # Ensure we call the memo CLI even if user omits it in payload
    cmd = payload
    if not payload.lstrip().startswith("memo"):
        cmd = f"memo {payload}"
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            executable=os.environ.get("SHELL") or "/bin/sh",
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            if result.stderr:
                console.print(f"[red]{result.stderr.rstrip()}[/]")
            else:
                console.print(f"[red]@memo 命令失败，退出码 {result.returncode}[/]")
            return True
        if result.stdout:
            console.print(result.stdout.rstrip())
        elif not result.stderr:
            console.print("[dim]@memo 完成，无输出[/]")
        if result.stderr:
            console.print(f"[red]{result.stderr.rstrip()}[/]")
    except Exception as e:
        console.print(f"[red]@memo 执行失败: {e}[/]")
        if log:
            log.exception(e)
    return True
