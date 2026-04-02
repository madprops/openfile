import os
from sys import argv
from os.path import getctime
from pathlib import Path
from subprocess import Popen, PIPE, check_output


# Max amount of files to show
FILE_LIMIT = 1_000


# How deep into subdirectories to fetch files
DEPTH = 1


# Remove unecessary characters
def clean_path(path: str) -> str:
    return path.rstrip("/")


# Get current working directory
def get_pwd() -> str:
    return clean_path(str(os.getenv("PWD")))


# Check if a path should be ignored
def is_ignored(path: Path) -> bool:
    ignored_dirs = {
        "node_modules",
        ".git",
        "venv",
        ".venv",
        "__pycache__",
        ".ruff_cache",
    }

    if ignored_dirs.intersection(path.parts):
        return True

    if path.name.endswith(".pyc"):
        return True

    return False

# Get input information using rofi
def get_input(prompt: str) -> str:
    proc = Popen(
        f"rofi -dmenu -p '{prompt}' -theme-str 'window {{height: 200px;}}'",
        stdout=PIPE,
        stdin=PIPE,
        shell=True,
        text=True,
    )

    return proc.communicate()[0].strip()


# Get files from subdirectories
def subdir_files(base_dir, depth):
    def get_files(subdir_path, current_depth):
        if current_depth > depth:
            return []

        subdir_onlyfiles = []
        subdir_onlydirs = []

        for p in subdir_path.iterdir():
            if is_ignored(p):
                continue
            if p.is_file():
                subdir_onlyfiles.append({"file": p})
            elif p.is_dir():
                subdir_onlydirs.append(p)

        for subdir in subdir_onlydirs:
            subdir_onlyfiles.extend(get_files(subdir, current_depth + 1))

        return subdir_onlyfiles

    onlyfiles = []
    onlydirs = [d for d in Path(base_dir).iterdir() if d.is_dir() and not is_ignored(d)]

    for subdir in onlydirs:
        onlyfiles.extend(get_files(subdir, 1))

        if len(onlyfiles) >= FILE_LIMIT:
            break

    return onlyfiles


# Show a directory listing
def show_paths(path: Path) -> None:
    allfiles = [p for p in path.iterdir() if not is_ignored(p)]
    onlydirs = [p for p in allfiles if p.is_dir()]
    onlyfiles = [{"file": p} for p in allfiles if p.is_file()]

    if len(onlyfiles) < FILE_LIMIT:
        onlyfiles.extend(subdir_files(path, DEPTH))

    # Sort both lists by creation time
    onlydirs.sort(key=getctime, reverse=True)
    onlyfiles.sort(key=lambda x: getctime(x["file"]), reverse=True)

    dirnames = [str(d) for d in onlydirs]
    filenames = []

    for item in onlyfiles:
        name = str(item["file"]).replace(str(path), "")[1:]
        filenames.append(name)

    items = []

    if str(path) != "/":
        items.append("..")

    items.append("[!] Cd Here")
    items.append("[!] New File")

    for d in dirnames:
        items.append(f"[+] {Path(d).name}")

    for f in filenames:
        items.append(f)

    proc = Popen(
        f"rofi -dmenu -i -p '{path}'", stdout=PIPE, stdin=PIPE, shell=True, text=True
    )

    ans = proc.communicate("\n".join(items))[0].strip()

    if ans == "":
        exit(0)

    ans = ans.strip()

    # Go to parent
    if ans == "..":
        show_paths(Path(path).parent)
    # Go to exact path
    elif ans.startswith("/") or ans.startswith("~"):
        show_paths(Path(ans).expanduser())
    # ezkl helper
    elif ans.startswith("z "):
        ans = check_output(["ezkl", "jump", ans[2:]]).decode("utf-8").strip()
        show_paths(Path(ans))
    # Keep going if directory
    elif ans.startswith("[+] "):
        show_paths(Path(path) / ans[4:])
    # Handle actions
    elif ans.startswith("[!] "):
        action = ans[4:]

        if action == "Cd Here":
            print(path)
        elif action == "New File":
            name = get_input("File Name")

            if name != "":
                print(Path(path) / name)
            else:
                show_paths(Path(path))
    else:
        # Output file path
        print(Path(path) / ans)


# Main function
def main() -> None:
    global DEPTH

    DEPTH = int(argv[1]) if len(argv) > 1 else DEPTH
    show_paths(Path(get_pwd()))


# Program starts here
if __name__ == "__main__":
    main()
