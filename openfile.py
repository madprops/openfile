import os
from os import getenv
from glob import glob
from os.path import isfile, isdir, join
from subprocess import Popen, PIPE, call
from pathlib import Path

# Remove unecessary characters
def clean_path(path: str) -> str:
  return path.rstrip("/")

# Get current working directory
def get_pwd() -> str:
  return clean_path(str(getenv("PWD")))  

# Show a directory listing
def show_paths(path) -> None:
  allfiles = glob(f"{path}/*")
  onlydirs = [f for f in allfiles if isdir(join(path, f))]
  onlyfiles = [f for f in allfiles if isfile(join(path, f))]

  onlydirs.sort(key=os.path.getctime, reverse = True)
  onlyfiles.sort(key=os.path.getctime, reverse = True)

  items = [".."]

  for d in onlydirs:
    items.append(f"[D] {Path(d).name}")
  
  for f in onlyfiles:
    items.append(f"[F] {Path(f).name}")

  proc = Popen(f"rofi -dmenu -i -p '{path}'", stdout=PIPE, stdin=PIPE, shell=True, text=True)
  ans = proc.communicate("\n".join(items))[0].strip()

  if ans == "":
    exit(0)
  
  if ans == "..":
    # Go to parent
    new_path = Path(path).parent
  elif ans.startswith("/"):
    # Go to exact path
    new_path = ans.strip()
    # Go to directory or file
  elif ans.startswith("[D]") or ans.startswith("[F]"):
    new_path = Path(path) / ans[4:]
  
  if isdir(new_path):
    # Keep going
    show_paths(new_path)
  else:
    # Output
    print(new_path)

# Main function
def main() -> None:
  show_paths(get_pwd())
  
# Program starts here
if __name__ == "__main__": main()