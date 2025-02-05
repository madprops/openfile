from os import getenv
from os.path import getctime
from glob import glob
from pathlib import Path
from subprocess import Popen, PIPE, check_output


# Remove unecessary characters
def clean_path(path: str) -> str:
    return path.rstrip("/")


# Get current working directory
def get_pwd() -> str:
    return clean_path(str(getenv("PWD")))


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


# Show a directory listing
def show_paths(path: Path) -> None:
    allfiles = glob(f"{str(path)}/*")
    onlydirs = [f for f in allfiles if (path / Path(f)).is_dir()]
    onlyfiles = [Path(f).name for f in allfiles if (path / Path(f)).is_file()]

    # Get files from immediate subdirectories
    for subdir in onlydirs:
        subdir_path = Path(subdir)
        subdir_name = subdir_path.name
        subdir_files = glob(f"{str(subdir_path)}/*")
        # Only add files, not subdirectories of subdirectories
        subdir_onlyfiles = [f"{subdir_name}/{Path(f).name}" for f in subdir_files if Path(f).is_file()]
        onlyfiles.extend(subdir_onlyfiles)

    onlyfiles = [f for f in onlyfiles if not f.endswith(".pyc")]

    # Sort both lists by creation time
    onlydirs.sort(key=getctime, reverse=True)
    onlyfiles.sort(key=getctime, reverse=True)

    items = []

    if str(path) != "/":
        items.append("..")

    items.append("[!] Cd Here")
    items.append("[!] New File")

    for d in onlydirs:
        items.append(f"[+] {Path(d).name}")

    for f in onlyfiles:
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
    show_paths(Path(get_pwd()))


# Program starts here
if __name__ == "__main__":
    main()
