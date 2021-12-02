from re import L, escape
import commands
import program
import datetime
import os
from queue import Queue
import shutil
import entry
import fileio
import actions

current_date = None
current_time = None
current_output = Queue()

next_lines = []
test_count = 0

def nothing():
    pass

def getline_test():
    global next_lines

    if len(next_lines) > 0:
        next_line, command = next_lines[0]
        next_lines = next_lines[1:]

        command()
        
        return next_line

    print("The program is asking for input here, and the testing harness hasn't provided it.")
    exit(0)


def inc_tests():
    global test_count
    test_count += 1


def failed(message):
    inc_tests()
    print(f"\n** Test {test_count} Failed **: {message}")


def passed():
    inc_tests()
    print(f"Test {test_count} Passed")


def assert_output(output):
    lines = output.split("\n")
    try:
        for line in lines:
            output_line = current_output.get(block=False)
            assert line == output_line
    except:
        if line != output_line:
            print(f"[{line}] != {output_line}")
        else:
            failed(f"Not enough lines")

        return

    passed()


def assert_equal(a, b):
    try:
        assert a == b
    except:
        failed(f"'{a}' != '{b}'")
        return

    passed()


def assert_true(truth, name):
    if truth:
        passed()
    else:
        failed(name + " is false")


def get_date():
    global current_date
    return current_date


def get_time():
    global current_time
    return current_time


def set_date(year, month, day):
    global current_date
    current_date = datetime.datetime(year=year, month=month, day=day)


def set_time(hour, minute):
    global current_time
    current_time = datetime.time(hour=hour, minute=minute)


def appendln(text: str):
    lines = text.split("\n")
    for line in lines:
        current_output.put(line)
        #print(f"test output: {line}")


def outputln(text):
    lines = text.split("\n")
    current_output.queue[-1] += lines[0]

    for line in lines[1:]:
        current_output.put(line)


def init_test():
    program.set_config_filename("testconfig.txt")
    program.set_default_journals_path("testjournals")
    program.set_date_provider(get_date)
    program.set_time_provider(get_time)
    program.set_println(appendln)
    program.set_stdout(outputln)
    set_date(1995, 3, 2)
    set_time(6, 0)
    commands.set_getline(getline_test)
    actions.disable_clear_console()

    if os.path.exists("testjournals"):
        shutil.rmtree("testjournals")
        os.remove("testconfig.txt")


init_test()


def step_program(line):
    program.push_command(line+"\n")
    program.run()


# Testing starts after this point

journal_name = "Test journal"

commands.push_command("")
commands.push_command(journal_name)
program.start()

assert_output("""Your journals will be stored in testjournals (Absolute path is D:\Projects\Journaling Program\Program\Python-journal\\testjournals).
You can choose to move them, but you must specify this in path.txt
Press [Enter] to continue...""")

step_program("First entry")

assert_true(
    os.path.exists(entry.make_journal_filepath(current_date, journal_name)),
    "file is present"
)

assert_equal(fileio.read(program.current_filepath), """
[Test journal] - 2/3/1995


6:00 AM - First entry
""")

assert_equal(fileio.read(program.current_filepath).strip(), program.get_journal_text())

set_time(6, 1)
step_program("-annotation")

assert_equal(fileio.read(program.current_filepath), """
[Test journal] - 2/3/1995


6:00 AM - First entry
\t6:01 AM - annotation
""")

step_program("-    \tannotation")

assert_equal(fileio.read(program.current_filepath), """
[Test journal] - 2/3/1995


6:00 AM - First entry
\t6:01 AM - annotation
\t6:01 AM - annotation
""")



set_time(6, 10)

commands.push_command("'''\n")
next_lines = [
    ("multiline", nothing),
    ("entry", nothing),
    ("'''", lambda : set_time(6, 15)),
]

program.run()

assert_equal(fileio.read(program.current_filepath), """
[Test journal] - 2/3/1995


6:00 AM - First entry
\t6:01 AM - annotation
\t6:01 AM - annotation

6:10 AM - '''
\tmultiline
\tentry
'''
\t6:15 AM - finished entry
""")
