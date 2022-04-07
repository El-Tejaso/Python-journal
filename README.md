# Python journal
A console program that I use to keep track of what I do during the day.
The main advantage this has over notepad is the automatic time-stamping of each line, so I know how much time elapsed between each thought.

Another advantage over notepad is the ability to view several entries at once, one after another. This allows you to see patterns you otherwise wouldn't have been able to see.

# How to use

Run `python journaling.py` to start the program, and follow the instructions to create a journal.

Typing anything into the journal should start a new block of text, which we can call a 'task'.
Typing more will add a note to the current task.

Typing a dash (`-`) before anything will start a new task.

Typing a tilde/squiggle (`~`) will toggle the last line between a note and a task. It is useful for when you forget the `-`.

If you want to view the past 6 entries, then type `/show_last 6`. This command will show the last 6 entries all together in the console. The command `/show_last 6 2` will show the last 6 to 12 entries (`6` is the number of previous entries to show, and `2` is the page number). This is the only cool command imo, but there are others you can find out about with `/help`.

## How to make a windows shortcut for this program

Paste the following line into the target section of a windows shortcut, 
then set the "Start in" property to blank. And of course, don't forget to replace `Path\To\Script\Folder` with the directory you will be storing this program in.

```
C:\Windows\System32\cmd.exe /C "python ^"Path\To\Script\Folder\journaling.py^""
```

If you have a python in your PATH (if you can call python from any directory in the command prompt, then you do),
this shortcut will work.

## Bugs/known issues

- `/view` doesn't work if today's journal is blank. I would just restart the program. I probably would never use view either, you would be better off using `/show_last`