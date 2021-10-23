from commands import *
from program import *

@command
def help():
    """
Usage: help
    Prints a deliberately written user manual that should allow you to get up and running as fast as possible.

Usage: help all
    Prints every command, and it's documentation

Usage: help [command]
    Prints a command's docstring.
"""
    clear_console()
    particular = get_input_if_present()

    if particular == None:
        for i, page in enumerate(usr_manual):
            print(page)
            print(f"Displaying page {i+1} of {len(usr_manual)}")
            print("Press Enter to go to the next page")
            line = input()
            if line == "exit":
                if i == 1:
                    print("Well, everywhere except here, of course.\nIf you're sure about exiting, then type it again. It'll work this time, promise")
                break

            clear_console()

    elif particular == "all":
        print("All commands:")
        print_help(command_dict.values())
        print(f"\texit - exits the program\n")
    else:
        print_help([command_dict[particular]])


def gen_page(title, desc, functions):
    return f"""{title}:
{desc}

""" + "\n".join([x.__name__ + "\n\t" + x.__doc__ + "\n" for x in functions])


usr_manual = ["""
Ah so you are one of the 4 or so people in the entire world that has downloaded this journalling program.
Good on you, and also thanks :)

The idea of this program is that every entry you make is automatically timestamped, so you can use
it to track exactly what you are doing throughout the day. 
It works way better if you have 2 monitors, with this program constantly on your secondary monitor.

use 'help [command]' to get more details about a specific command.
""",

gen_page("Core commands", "You will use all of these at least once.", [new, set, show, view]) + "\n'exit':\n\tUse this from anywhere to close the program."
,
gen_page(
    "Writing commands", 
    """
These are the ones you will be using the most.
You will mainly be writing a command, hitting [enter]/[return] on your keyboard, then typing stuff like normal.
To close off an entry, just type 'end' followed by an [enter] all on a single line.
It will make more sense once you start using the program.
""",   
    [journal, j, task, t, note, n]
    ),
gen_page("Writing commands part 2",
    "These are the ones you will be using the second most.",
    [list, l]
    ),
gen_page("Analysis commands (more coming eventually)",
    "Use these to analyze today's entries.",
    [deltas, cdeltas, entries]
    ),
    gen_page("Somewhat useless but nice to have",
    "(Self explanatory)",
    [cwd]
    ),
gen_page("Unstable",
    "...",
    [bgtask, bgt]
    ),
    gen_page("Somewhat useless but nice to have",
    "(Self explanatory)",
    [cwd]
    )
]


"""
'journal', 'j'
    - These are used to create a journal entry that spans multiple lines.

'task', 't'
    - These are used to create a task entry that spans a single line.

'note', 'n' 

"""