import os
from collections import deque
from pathlib import Path
from subprocess import PIPE, Popen, check_output
from sys import argv


# Max amount of files to show
FILE_LIMIT = 1_000

# Max files to take from a single subdirectory so one folder can't starve siblings
PER_DIR_LIMIT = 100

# How deep into subdirectories to fetch files
DEPTH = 1

IGNORED_DIRS = {
    "node_modules",
    ".git",
    "venv",
    ".venv",
    "__pycache__",
    ".ruff_cache",
    ".mypy_cache",
    ".cache",
    "dist",
    "build",
    "target",
}

IGNORED_EXTS = {
    ".pyc",
    ".pyo",
}


# Remove unecessary characters
def clean_path(path: str) -> str:
    return path.rstrip("/") or "/"


# Get current working directory
def get_pwd() -> str:
    return clean_path(str(Path.cwd()))


# Safely get modification time (avoids crashes on broken symlinks)
def safe_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


# Check if a path should be ignored
def is_ignored(path: Path) -> bool:
    if path.name in IGNORED_DIRS:
        return True

    if path.suffix in IGNORED_EXTS:
        return True

    return False


# Get input information using rofi
def get_input(prompt: str) -> str:
    proc = Popen(
        [
            "rofi",
            "-dmenu",
            "-p",
            prompt,
            "-theme-str",
            "window {height: 200px;}",
        ],
        stdout=PIPE,
        stdin=PIPE,
        text=True,
    )

    return proc.communicate()[0].strip()


# Get files from subdirectories
def subdir_files(base_dir: Path, max_depth: int, limit: int) -> list[Path]:
    if max_depth <= 0 or limit <= 0:
        return []

    onlyfiles: list[Path] = []
    queue: deque[tuple[Path, int]] = deque()

    try:
        top_dirs = [
            d for d in base_dir.iterdir()
            if d.is_dir() and not is_ignored(d)
        ]
    except PermissionError:
        return []

    top_dirs.sort(key=safe_mtime, reverse=True)

    for d in top_dirs:
        queue.append((d, 1))

    while queue and len(onlyfiles) < limit:
        current_dir, current_depth = queue.popleft()
        dir_file_count = 0
        next_dirs: list[Path] = []

        try:
            entries = list(current_dir.iterdir())
        except PermissionError:
            continue

        for p in entries:
            if is_ignored(p):
                continue

            if p.is_file():
                if dir_file_count < PER_DIR_LIMIT:
                    onlyfiles.append(p)
                    dir_file_count += 1

                    if len(onlyfiles) >= limit:
                        break
            elif p.is_dir() and current_depth < max_depth:
                next_dirs.append(p)

        if current_depth < max_depth:
            next_dirs.sort(key=safe_mtime, reverse=True)

            for subdir in next_dirs:
                queue.append((subdir, current_depth + 1))

    return onlyfiles


# Show a directory listing
def show_paths(start_path: Path) -> None:
    path = start_path.resolve()

    while True:
        try:
            allfiles = [p for p in path.iterdir() if not is_ignored(p)]
        except PermissionError:
            allfiles = []

        onlydirs = [p for p in allfiles if p.is_dir()]
        onlyfiles = [p for p in allfiles if p.is_file()]

        remaining = FILE_LIMIT - len(onlyfiles)

        if remaining > 0:
            onlyfiles.extend(subdir_files(path, DEPTH, remaining))

        # Sort both lists by creation time
        onlydirs.sort(key=safe_mtime, reverse=True)
        onlyfiles.sort(key=safe_mtime, reverse=True)

        items = []

        if str(path) != "/":
            items.append("..")

        items.append("[!] Cd Here")
        items.append("[!] New File")

        for d in onlydirs:
            items.append(f"[+] {d.name}")

        for f in onlyfiles:
            items.append(str(f.relative_to(path)))

        proc = Popen(
            ["rofi", "-dmenu", "-i", "-p", str(path)],
            stdout=PIPE,
            stdin=PIPE,
            text=True,
        )

        ans = proc.communicate("\n".join(items))[0].strip()

        if ans == "":
            exit(0)

        # Go to parent
        if ans == "..":
            path = path.parent
        # Go to exact path
        elif ans.startswith("/") or ans.startswith("~"):
            path = Path(ans).expanduser().resolve()
        # ezkl helper
        elif ans.startswith("z "):
            jumped = check_output(["ezkl", "jump", ans[2:]]).decode("utf-8").strip()
            path = Path(jumped).resolve()
        # Keep going if directory
        elif ans.startswith("[+] "):
            path = path / ans[4:]
        # Handle actions
        elif ans.startswith("[!] "):
            action = ans[4:]

            if action == "Cd Here":
                print(path)
                return
            elif action == "New File":
                name = get_input("File Name")

                if name != "":
                    print(path / name)
                    return
        else:
            # Output file path
            print(path / ans)
            return


# Main function
def main() -> None:
    global DEPTH

    if len(argv) > 1:
        DEPTH = int(argv[1])

    show_paths(Path(get_pwd()))


# Program starts here
if __name__ == "__main__":
    main()