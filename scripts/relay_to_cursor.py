from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PROMPT_PATH = ROOT_DIR / "handoff" / "cursor-prompt.md"
DEFAULT_WINDOW_QUERY = "Cursor"
HANDOFF_STATE_SCRIPT = ROOT_DIR / "scripts" / "handoff_state.py"


class RelayError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--action",
        choices=("check", "paste", "paste-and-send"),
        default="check",
    )
    parser.add_argument("--file", default=str(DEFAULT_PROMPT_PATH))
    parser.add_argument("--window-query", default=DEFAULT_WINDOW_QUERY)
    parser.add_argument("--activate-delay", type=float, default=0.4)
    parser.add_argument("--send-delay", type=float, default=0.2)
    parser.add_argument("--send-key")
    return parser.parse_args()


def run_command(command: list[str], capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            check=True,
            text=True,
            capture_output=capture_output,
        )
    except FileNotFoundError as exc:
        raise RelayError(f"Missing command: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() if exc.stderr else ""
        detail = f" ({stderr})" if stderr else ""
        raise RelayError(f"Command failed: {' '.join(command)}{detail}") from exc


def ensure_dependencies() -> str:
    missing = [name for name in ("wmctrl", "xdotool") if shutil.which(name) is None]
    if missing:
        raise RelayError(f"Missing required commands: {', '.join(missing)}")

    for candidate in ("xclip", "wl-copy", "xsel"):
        if shutil.which(candidate):
            return candidate

    raise RelayError("Missing clipboard command: xclip, wl-copy, or xsel")


def read_prompt_file(path: Path) -> str:
    if not path.exists():
        raise RelayError(f"Prompt file not found: {path}")

    content = path.read_text(encoding="utf-8")
    if not content.strip():
        raise RelayError(f"Prompt file is empty: {path}")
    return content


def find_window(window_query: str) -> tuple[str, str]:
    result = run_command(["wmctrl", "-lx"], capture_output=True)
    matches: list[tuple[str, str]] = []
    query = window_query.casefold()

    for line in result.stdout.splitlines():
        if query not in line.casefold():
            continue
        parts = line.split(None, 4)
        if len(parts) < 5:
            continue
        matches.append((parts[0], parts[4]))

    if not matches:
        raise RelayError(f"No window matched query: {window_query}")

    return matches[0]


def copy_to_clipboard(content: str, clipboard_command: str) -> None:
    if clipboard_command == "xclip":
        command = ["xclip", "-selection", "clipboard"]
    elif clipboard_command == "wl-copy":
        command = ["wl-copy"]
    else:
        command = ["xsel", "--clipboard", "--input"]

    try:
        subprocess.run(command, input=content, text=True, check=True)
    except subprocess.CalledProcessError as exc:
        raise RelayError(f"Failed to copy content with {clipboard_command}") from exc


def activate_window(window_id: str, delay: float) -> None:
    run_command(["xdotool", "windowactivate", "--sync", window_id])
    if delay > 0:
        time.sleep(delay)


def paste_clipboard() -> None:
    run_command(["xdotool", "key", "--clearmodifiers", "ctrl+v"])


def send_message(send_key: str, delay: float) -> None:
    if delay > 0:
        time.sleep(delay)
    run_command(["xdotool", "key", "--clearmodifiers", send_key])


def format_check_output(prompt_path: Path, window_id: str, window_title: str, content: str, clipboard_command: str) -> str:
    lines = [
        "relay check ok",
        f"prompt_file: {prompt_path}",
        f"prompt_chars: {len(content)}",
        f"window_id: {window_id}",
        f"window_title: {window_title}",
        f"clipboard: {clipboard_command}",
    ]
    return "\n".join(lines)


def mark_handoff_awaiting(action: str) -> str:
    command = [
        sys.executable,
        str(HANDOFF_STATE_SCRIPT),
        "mark-awaiting",
        "--relay-action",
        action,
    ]

    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() if exc.stderr else ""
        stdout = exc.stdout.strip() if exc.stdout else ""
        detail = stderr or stdout or "unknown error"
        return f"handoff_state_warning: {detail}"

    return result.stdout.strip()


def main() -> int:
    args = parse_args()
    prompt_path = Path(args.file).expanduser().resolve()

    try:
        clipboard_command = ensure_dependencies()
        content = read_prompt_file(prompt_path)
        window_id, window_title = find_window(args.window_query)

        if args.action == "check":
            print(format_check_output(prompt_path, window_id, window_title, content, clipboard_command))
            return 0

        copy_to_clipboard(content, clipboard_command)
        activate_window(window_id, args.activate_delay)
        paste_clipboard()

        if args.action == "paste-and-send":
            if not args.send_key:
                raise RelayError("--send-key is required for paste-and-send")
            send_message(args.send_key, args.send_delay)

        handoff_state_output = mark_handoff_awaiting(args.action)

        print(f"relay action complete: {args.action}")
        print(f"target_window: {window_title}")
        print(f"prompt_file: {prompt_path}")
        if handoff_state_output:
            print(handoff_state_output)
        return 0
    except RelayError as exc:
        print(f"relay error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
