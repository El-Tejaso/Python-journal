from commands import *
import os
import program
from actions import *

@command
def help():
    clear_console()
    
    '''Prints a command's docstring. If called with no arguments, prints all available commands, and their docstrings'''
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