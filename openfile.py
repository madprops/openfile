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

# Show a directory listing
def show_paths(path) -> None:
  path = str(path)
  allfiles = glob(f"{path}/*")
  onlydirs = [f for f in allfiles if (Path(path) / Path(f)).is_dir()]
  onlyfiles = [f for f in allfiles if (Path(path) / Path(f)).is_file()]
  onlydirs.sort(key=getctime, reverse = True)
  onlyfiles.sort(key=getctime, reverse = True)
  
  items = []
  
  if path != "/":
    items.append("..")

  for d in onlydirs:
    items.append(f"[D] {Path(d).name}")
  
  for f in onlyfiles:
    items.append(f"[F] {Path(f).name}")

  proc = Popen(f"rofi -dmenu -i -p '{path}'", stdout=PIPE, stdin=PIPE, shell=True, text=True)
  ans = proc.communicate("\n".join(items))[0].strip()

  if ans == "":
    exit(0)
  
  ans = ans.strip()
  
  if ans == "..":
    # Go to parent
    show_paths(Path(path).parent)

  elif ans.startswith("/") or ans.startswith("~"):
    # Go to exact path
    show_paths(Path(ans).expanduser())

    # Go to directory or file
  elif ans.startswith("[D]") or ans.startswith("[F]"):
    new_path = Path(path) / ans[4:]
    if new_path.is_dir():
      # Keep going
      show_paths(new_path)
    else:
      # Output
      print(new_path)
      
  elif ans.startswith("z "):
    ans = check_output(['ezkl', 'jump', ans[2:]]).decode("utf-8").strip()
    show_paths(ans)

# Main function
def main() -> None:
  show_paths(get_pwd())
  
# Program starts here
if __name__ == "__main__": main()