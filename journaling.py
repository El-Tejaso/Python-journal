from commands import *
import os
import program
from actions import *

if __name__ == "__main__":
    clear_console()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    program.start()

    while True:
        program.write_carat()
        program.run()
        clear_args()