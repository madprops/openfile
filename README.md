![](https://i.imgur.com/kK2dWjM.gif)

Go to a path and run this

It will open [rofi](https://github.com/davatorium/rofi) with directories and files

Both sorted by modification date

Directories first then files

Since it's rofi you can filter

There's a ".." to go to the parent path

Selecting a file outputs the path to stdout

You can use it like this:

```
function o
  # Run openfile.py and get a path
  set p (python ~/code/openfile/openfile.py)

  # Check if path exists
  if test -n "$p"
    # Resolve symlinks
    set resolved (readlink -f "$p")

    # Check if directory or file
    if test -d "$resolved"
      cd "$resolved"
    else
      code "$resolved"
    end
  end
end
```

That is a fish alias to open something with vscode.

---

It accepts an optional argument which sets the DEPTH.

The depth determines how deep into subdirectories it checks for files.

Its default is 2.