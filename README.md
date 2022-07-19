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
  set p (python ~/code/openfile/openfile.py)

  if test -n "$p"
    code "$p"
  end
end
```

That is a fish alias to open something with vscode