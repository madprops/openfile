import os
from sys import argv
from os.path import getctime
from glob import glob
from pathlib import Path
from subprocess import Popen, PIPE, check_output


# How deep into subdirectories to fetch files
DEPTH = 2


# Remove unecessary characters
def clean_path(path: str) -> str:
    return path.rstrip("/")


# Get current working directory
def get_pwd() -> str:
    return clean_path(str(os.getenv("PWD")))


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

        subdir_files = glob(f"{str(subdir_path)}/*")
        subdir_onlyfiles = [{"file": Path(f)} for f in subdir_files if Path(f).is_file()]
        subdir_onlydirs = [Path(d) for d in subdir_files if Path(d).is_dir()]

        for subdir in subdir_onlydirs:
            subdir_onlyfiles.extend(get_files(subdir, current_depth + 1))

        return subdir_onlyfiles

    onlyfiles = []
    onlydirs = [Path(d) for d in glob(f"{base_dir}/*") if Path(d).is_dir()]

    for subdir in onlydirs:
        onlyfiles.extend(get_files(subdir, 1))

    return onlyfiles


# Show a directory listing
def show_paths(path: Path) -> None:
    allfiles = glob(f"{str(path)}/*")
    onlydirs = [Path(f) for f in allfiles if (path / Path(f)).is_dir()]
    onlyfiles = [{"file": Path(f)} for f in allfiles if (path / Path(f)).is_file()]
    onlyfiles.extend(subdir_files(path, DEPTH))

    # Filter out some files
    onlyfiles = [f for f in onlyfiles if not f["file"].name.endswith(".pyc")]

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
