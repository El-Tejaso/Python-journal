import enum
import sys
from commands import *
from actions import *
import os
from pathlib import Path
import entry
import datetime
import time
from itertools import islice
from collections import namedtuple
import re

available_journals = []
current_journal = None
current_filepath = ""

timestamp_regex = re.compile(r"(\d\d|\d):(\d\d|\d) (AM|PM)")
two_dig_number_regex = re.compile(r"(\d\d|\d)")

Timestamp = namedtuple("Timestamp", "hours minutes indent")

@command
def test():
    '''A test function'''
    print("it worked")

def refresh_journals():
    global available_journals
    dirs = os.listdir(os.curdir)
    dirs.sort()
    available_journals = dirs

def list_journals():
    journals = [f"(Current)\t{x}" if x==current_journal else x for x in available_journals]
    journals = [f"[{i}] {x}" for i, x in enumerate(journals)]
    return "\n".join(journals)

@command
def new():
    '''
    Usage: new [Name] - Creates a new journal with the specified name.
    Characters that can't be in folders cannot be used.
    '''
    clear_console()
    name = ask_input_if_not_present("Enter the name of the new journal:")

    try:
        os.mkdir(name)

        set()
    except Exception as e:
        print("the new journal could not be made:")
        print(e)


@command
def set():
    '''Usage: set [number] - Set the current journal with a number.'''
    clear_console()

    refresh_journals()

    num = int(ask_input_if_not_present(f"Pick a journal:\n{list_journals()}"))

    set_journal(num)


def set_journal(num):
    global current_journal, current_filepath

    refresh_journals()
    if num >= len(current_journal):
        print("Pick a valid number.")
        return
    current_journal = available_journals[num]

    today = get_today()
    current_filepath = make_journal_filepath(today)

    show()

def get_today():
    return datetime.date.today()

def make_journal_filepath(date):
    journal_dir = Path(current_journal).joinpath(entry.date_folder(date))
    if not journal_dir.exists():
        journal_dir.mkdir(parents=True)

    journal_file_dir = journal_dir.joinpath(
        f"[{current_journal}] {entry.to_2dig_number(date.day)}.txt"
    )

    filepath = str(journal_file_dir)
    return filepath


@command 
def j():
    '''Alias for journal'''
    journal()

def get_journal_text():
    existing_text = ""
    try:
        with open(current_filepath, encoding="utf-8", mode="r") as file:
            existing_text = file.read()
    except:
        pass

    return existing_text.strip()

def write_into_console(text):
    sys.stdout.write(text)
    sys.stdout.flush()

def write_journal_and_console(text):
    write_into_journal(text)
    write_into_console(text)


@command
def show():
    '''Usage: show [filter?]
Show all entries in today's journal, filtered on 'tasks' or 'journals' if specified.'''

    clear_console()
    existing_text = get_journal_text()

    filter = get_input_if_present()
    if filter == None:
        print(existing_text)
        return

    filter_map = {
        "tasks" : 0, 
        "journals" : 1,
    }

    if filter not in filter_map:
        filter_list = ", ".join(filter_map)
        print(f"{filter} is not a valid filter, use one of: {filter_list}")
        return
    
    parts = existing_text.split("\n\n")
    filter_num = filter_map[filter]

    parts = [x for x in parts if get_part_type(x)==filter_num or get_part_type(x)==-1]
    print("\n\n".join(parts))

def get_part_type(part : str):
    if part.count("'''") >= 2:
        return 1

    if timestamp_regex.search(part) == None:
        return -1

    return 0

def print_existing_text():
    existing_text = get_journal_text()
    if len(existing_text) > 0:
        print(existing_text)
    else:
        heading = f"\n[{current_journal}] - {entry.format_date(get_today())}\n\n"
        write_journal_and_console(heading)


def generic_input_to_journal(top, opening, closing, is_newline, input_fn, bullet=""):
    clear_console()

    if current_journal == None:
        print("No journal has been set.")
        return

    print(top)

    print_existing_text()

    if is_newline:
        write_journal_and_console("\n")    

    write_journal_and_console(bullet)
    write_journal_and_console(f"{timestamp()} - ")
    write_journal_and_console(opening)

    input_fn()
    
    write_journal_and_console(closing)

    clear_console()
    print_existing_text()

@command
def journal():
    '''Write a journal entry into the current journal'''

    def input_fn():
        multiline_input("\t")

    generic_input_to_journal(
        is_newline=True, 
        top="\n\n\n----Started journaling:\n", 
        opening="'''", 
        closing="'''\n",
        input_fn=input_fn
        )


def multiline_input(bullet):
    def to_journal(line):
        write_into_journal(f"{bullet}{line}\n")

    get_typed_input(to_journal, bullet)

def single_line_input():
    line = ask_line_if_not_present()
    write_into_journal(f"{line}\n")

def generic_task(background_level=0):
    generic_input_to_journal(
        is_newline=True, 
        top="", 
        opening="", 
        closing="",
        input_fn=single_line_input,
        bullet = "*" * background_level
        )

@command
def task():
    """Write a new task into the current journal. Add notes to the task with 'note'"""
    generic_task()
    
@command
def t():
    """An alias for 'task'"""
    task()

@command 
def bgtask():
    """Same as 'task' but with an * at the start to denote it as a background task"""
    generic_task(background_level=1)

@command
def bgt():
    """Alias for 'bgtask'"""
    bgtask()

@command
def note():
    '''Write a new note into the current journal. 
A note is the same functionality as 'task', but indented once, and without a newline at the start.
As such, it can be used in conjunction with basically anything else.
Add your own indentations if you want a hierarchy, because that is too much effort to implement.'''

    generic_input_to_journal(
        is_newline=False, 
        top="", 
        opening="", 
        closing="",
        input_fn=single_line_input,
        bullet="\t"
        )

@command
def n():
    """An alias for 'note'"""
    note()

def get_typed_input(fn, bullet):
    while True:
        write_into_console(bullet)

        line = ask_line_if_not_present()
        if(line.lower() == "end"):
            break
        
        fn(line)


def timestamp():
    suffix = "AM"
    now = datetime.datetime.now()
    hour = now.hour

    if hour >= 12:
        suffix = "PM"
        if hour > 12:
            hour -= 12
    
    minute = now.minute

    return f"{hour}:{entry.to_2dig_number(minute)} {suffix}"

def write_into_journal(text):
    with open(current_filepath, encoding="utf-8", mode="a") as file:
        file.write(text)

@command
def cwd():
    '''Print the current path'''
    print(os.path.abspath(os.curdir))

#handle things like monday
def default_handler(arg):
    line = get_line_if_present()

    if line == None:
        # Since there is only a single word, I may have actually tried typing a command here
        # so I will not auto-add a task here
        return False
        
    arg = arg + " " + line
    push_command(arg)
    task()

    return True

def write_carat():
    write_into_console(f"[{current_journal}]>")

def start():
    global current_journal
    with open("path.txt") as file:
        root = file.read().strip()
        os.chdir(root)

    refresh_journals()
    
    if len(available_journals) == 0:
        print("You have no journals. Start a new journal with the 'new' command")
    else:
        print(f"You have {len(available_journals)} journals:")

        current_journal = available_journals[0]
        print(list_journals())

        set_journal(0)
        print(f"\nThe current journal is {0} ({current_journal}).\n")

@command
def view():
    '''Opens the journal text file in your default text editor.'''
    arg1 = get_input_if_present()
    arg2 = get_input_if_present()
    arg3 = get_input_if_present()

    today = get_today()
    year = today.year
    month = today.month
    day = today.day

    if arg3 != None:
        year = int(arg1)
        month = int(arg2)
        day = int(arg3)
    elif arg2 != None:
        month = int(arg1)
        day = int(arg2)
    elif arg1 != None:
        named_day = arg1
        date = namedday_this_week_to_date(named_day)
        if date == None:
            return

        day = date.day
        month = date.month
        
    filepath = entry.get_entry(current_journal, year, month, day)

    if filepath == None:
        print(f"There is no entry for {year}/{month}/{day}  (Y/M/D)")
        return
    else:
        print(f"Pulling up entry for {year}/{month}/{day}  (Y/M/D) in an external editor...")

    open_file(filepath)


def namedday_this_week_to_date(named_day : str):
    '''
    Returns the day of the month for a day in the week.
    So if named_day = monday, the function returns the whatever of this month corresponding to this week.
    Returns -1 if that day hasn't happened yet this week.
'''
    named_day = named_day.lower()
    
    wanted_day_idx = day_week_index(named_day)
    if wanted_day_idx == -1:
        print(f"{named_day} does not remotely resemble any day")
        return None

    today = get_today()
    today_day_idx = day_week_index(today.strftime("%A").lower())

    if wanted_day_idx > today_day_idx:
        print(f"today is {days_of_week[today_day_idx]}, so {days_of_week[wanted_day_idx]} has not happened yet.")
        return

    delta = wanted_day_idx - today_day_idx
    
    return today + datetime.timedelta(delta)

days_of_week = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

def day_week_index(wanted_day):
    for i, day in enumerate(days_of_week):
        if wanted_day in day:
            return i

    return -1

@command 
def list():
    """Same as 'note', but multiple dot-points all at once"""

    def input_fn():
        multiline_input("\t- ")

    generic_input_to_journal(
        is_newline=False, 
        top="", 
        opening="\n", 
        closing="",
        input_fn=input_fn,
        bullet="\t"
        )



def parse_timestamp(line : str):
    indent = 0
    while indent < len(line) and line[indent] == '\t':
        indent+=1

    timestamp_part = timestamp_regex.search(line)
    if timestamp_part==None:
        return None

    timestamp_part = timestamp_part[0]

    number_parts = two_dig_number_regex.findall(timestamp_part)

    #10:50 AM
    #      ^
    is_am = timestamp_part[-2]=="A"

    hours = int(number_parts[0])
    if not is_am:
        hours += 12
    
    minutes = int(number_parts[1])

    return Timestamp(hours, minutes, indent)


def to_minutes(a):
    return a.hours*60 + a.minutes

def timedelta(a, b):
    return to_minutes(b) - to_minutes(a)


def get_line_times():
    existing_text = get_journal_text()
    lines = existing_text.split('\n')
    
    line_times = []

    for line in lines:
        time = parse_timestamp(line)
        if time==None:
            continue

        line_times.append((line, time))

    return line_times

def minutes_str(minutes):
    hours = minutes//60
    mins = minutes%60
    return f"{hours}h {mins}m"

def delta_list(ongoing = False):
    line_times = get_line_times()
    line_times = [x for x in line_times if x[1].indent == 0]
    
    res = []

    for a, b in zip(line_times, islice(line_times, 1, None)):
        delta = timedelta(a[1], b[1])
        res.append((a[0], b[0], delta))

    if ongoing:
        now = datetime.datetime.now()
        delta = timedelta(line_times[-1][1], Timestamp(now.hour,  now.minute, 0))
        res.append((line_times[-1][0], "Now", delta))

    return res

@command
def deltas():
    '''Show how much time has passed between each event'''
    clear_console()

    dl = delta_list(True)

    for prev, next, delta in dl:
        print(f"[{prev}]")
        print(f"\t{minutes_str(delta)}\n")


@command
def cdeltas():
    """Usage: cdeltas [minutes?]\nSame as 'deltas', but smaller tasks are grouped into a 'minutes' interval where applicable"""
    clear_console()

    minutes = get_input_if_present()
    if minutes == None:
        minutes = 30


    dl = delta_list(True)

    collapsed_list = []
    total_time = 0
    tasks = []

    for prev, next, delta in dl:
        tasks.append(prev)

        if total_time + delta > minutes:
            collapsed_list.append((tasks, total_time))
            tasks = []
            total_time = 0

        total_time += delta

    for collapsed_tasks, delta in collapsed_list:
        timestamp_part = timestamp_regex.search(collapsed_tasks[0])[0]

        collapsed_tasks = [timestamp_regex.sub("", x) for x in collapsed_tasks]

        if len(collapsed_tasks) <= 1:
            print(f"{timestamp_part} - {collapsed_tasks[0]}")
            print(f"\t{minutes_str(delta)}")
        else:
            print(f"{timestamp_part} - {len(collapsed_tasks)} smaller tasks:")
            smaller_tasks_commasep = ", ".join(collapsed_tasks)
            print(f"\t-[{smaller_tasks_commasep}]")
            print(f"\t{minutes_str(delta)}\n")


def get_entry_list():
    years = os.listdir(current_journal)
    entry_map = {}

    for year_path in years:
        for month_path in os.listdir(os.path.join(current_journal, year_path)):
            year = Path(year_path).parts[-1]
            month = Path(month_path).parts[-1]
            entry_map[year + " " + month] = entry.get_entries_sorted(current_journal, year, month)

    return entry_map

@command
def entries():
    '''Shows a breakdown of all entries in the journal'''
    clear_console()

    entry_map = get_entry_list()

    print("Entries:")

    def process_v(v):
        return f" {entry.to_2dig_number(len(v))} entries " + "|" * len(v)
    
    entry_list = [f"{k} : {process_v(v)}" for k,v in entry_map.items()]
    print("\n\t".join(entry_list))