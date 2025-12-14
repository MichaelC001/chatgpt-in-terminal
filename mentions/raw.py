import os
import subprocess


def handle_at_raw(payload: str, console, log):
    """Execute trailing text directly in the terminal and return output."""
    if not payload:
        console.print("[red]@ 后需要跟要执行的命令[/]")
        return True
    try:
        result = subprocess.run(
            payload,
            shell=True,
            executable=os.environ.get("SHELL") or "/bin/sh",
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            if result.stderr:
                console.print(f"[red]{result.stderr.rstrip()}[/]")
            else:
                console.print(f"[red]命令失败，退出码 {result.returncode}[/]")
            return True
        if result.stdout:
            console.print(result.stdout.rstrip())
        elif not result.stderr:
            console.print("[dim]命令执行完成，无输出[/]")
        if result.stderr:
            console.print(f"[red]{result.stderr.rstrip()}[/]")
    except Exception as e:
        console.print(f"[red]命令执行失败: {e}[/]")
        if log:
            log.exception(e)
    return True
