from commands import *
import os
import program
from actions import *
from usr_manual import usr_manual

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