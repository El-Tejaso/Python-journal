from commands import *
import os
import program
from actions import *

@command
def help():
    """Usage: help [command?]
Prints a command's docstring. If none is specified, prints help for all commands
"""
    clear_console()
    particular = get_input_if_present()

    if particular == None:
        print("All commands:")
        print_help(command_dict.values())
        print(f"\texit - exits the program\n")
    else:
        print_help([command_dict[particular]])

if __name__ == "__main__":
    clear_console()
    program.start()

    while True:
        program.write_carat()

        co = get_input()
        if co.lower() == "exit":
            break
        
        if not run_command(co):
            if not program.default_handler(co):
                print(f"{co} isn't a valid command. Type 'help' for a list of all valid commands.")

        # prevents bugs from where the previous command doesn't complete properly
        # and then the rest of the args are still in the queue
        clear_args()