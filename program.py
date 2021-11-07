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
Activity = namedtuple("Activity", "line time")

@command
def help():
    clear_console()
    print("""
Tutorial:
    Write literally anything to enter a new task
    
    Write the '-' character followed by literally anything to annotate that task

    Write ''' to start a journal

Main commands:
    /set to set the current journal

    /new to create a new journal

    /view to open entry in notepad. /view monday will open the entry for monday this week. (The other days also work)

    /times to see how long between each entry

    /entries to see how many entries you've done per month

    /show to show today's journal entry. If it's blank, you'll get some tutorial text instead.
        /show tasks will show only tasks
        /show journals will show only journals
""")


def start():
    global current_journal

    ensure_config()
    
    with open("path.txt", encoding="utf-8", mode="r") as file:
        root = file.read().strip()
        os.chdir(root)

    refresh_journals()
    
    if len(available_journals) == 0:
        new()
    else:
        set()


@command
def new():
    '''
    Creates a new journal with the specified name, and then immediately calls 'set'.
    '''
    clear_console()

    while True:
        name = ask_line("Enter the name of the new journal:")
        try:
            os.mkdir(name)
            set()
            break
        except Exception as e:
            print(f"the name '{name}' was probably invalid, try another one")
            print(e)

@command
def set():
    '''Usage: set [number] - Set the current journal with a number.'''
    clear_console()

    refresh_journals()
    num = ask_line(f"Pick a journal:\n{list_journals()}")
    try:
        set_journal(int(num))
    except:
        exit_program()

def refresh_journals():
    global available_journals
    dirs = os.listdir(os.curdir)
    dirs.sort()
    available_journals = dirs

def set_journal(num):
    global current_journal, current_filepath

    refresh_journals()
    if num >= len(available_journals):
        print("Pick a valid number.")
        return
    current_journal = available_journals[num]

    today = get_today()
    current_filepath = make_journal_filepath(today)

    show()


@command
def show():
    '''Usage: show [filter?]
Show all entries in today's journal, filtered on 'tasks' or 'journals' if specified.'''

    clear_console()

    existing_text = get_journal_text()

    filter = get_line()
    text = apply_filter(existing_text, filter)

    if text != None:
        print(text)    

    if existing_text.strip() == '':
        help()

def apply_filter(text : str, filter : str):
    if filter == None:
        return text
    
    filter_map = {
        "tasks" : 0, 
        "journals" : 1,
    }

    if filter not in filter_map:
        filter_list_str = ", ".join(filter_map)
        print(f"{filter} is not a valid filter, use one of: {filter_list_str}")
        return

    blocks = text.split("\n\n")
    filter_num = filter_map[filter]
    blocks = [x for x in blocks if get_part_type(x)==filter_num or get_part_type(x)==-1]

    return "\n\n".join(blocks)

def get_part_type(part : str):
    if part.count("'''") >= 2:
        return 1

    if timestamp_regex.search(part) == None:
        return -1

    return 0

def run():
    line = ask_line()

    if line == None:
        # Since there is only a single word, I may have actually tried typing a command here
        # so I will not auto-add a task here
        return
        
    if line.strip().startswith("-"):
        push_command(line[1:].strip())
        note()
    elif line.strip().startswith("'''"):
        push_command(line[3:])
        journal()
    elif line.strip().startswith("/"):
        push_command(line[1:].strip())
        comm = get_input()
        run_command(comm)
    else:
        push_command(line)
        task()


def list_journals():
    journals = [f"(Current)\t{x}" if x==current_journal else x for x in available_journals]
    journals = [f"[{i}] {x}" for i, x in enumerate(journals)]
    return "\n".join(journals)


@command
def journal():
    """Any line starting with ''' will automatically execute this command.
    Create a journal entry that spans multiple lines. 
    Type ''' on it's own on a single line to close the entry."""

    def input_fn():
        multiline_input("\t")

    generic_input_to_journal(
        is_newline=True, 
        top="\n\n\n----Started journaling:\n", 
        opening="'''\n", 
        closing="'''\n",
        input_fn=input_fn,
        show_existing=False
        )

    push_command("finished entry")
    note()


def generic_input_to_journal(top, opening, closing, is_newline, input_fn, bullet="", show_existing=True):
    clear_console()

    if current_journal == None:
        print("No journal has been set.")
        return

    print(top)

    if show_existing:
        print_existing_text()

    if is_newline:
        write_journal_and_console("\n")    

    write_journal_and_console(bullet)
    write_journal_and_console(f"{now_timestamp()} - ")
    write_journal_and_console(opening)

    input_fn()
    
    write_journal_and_console(closing)

    clear_console()
    print_existing_text()


def multiline_input(bullet):
    def to_journal(line):
        write_into_journal(f"{bullet}{line}\n")

    get_typed_input(to_journal, bullet, ending_line="'''")

def get_typed_input(fn, bullet, ending_line = "end"):
    line = ask_line()
    while True:
        write_into_console(bullet)

        line = ask_line()
        if(line == ending_line):
            break
        
        fn(line)

@command
def note():
    '''Starting a line with - automatically executes this command. 
Writes a new task but it's indented and directly on the next line, so its as if it's connected to whatever is above it.'''

    generic_input_to_journal(
        is_newline=False, 
        top="", 
        opening="", 
        closing="",
        input_fn=single_line_input,
        bullet="\t"
        )

@command
def task():
    """Write a new task into the current journal. Add notes to the task with 'note'"""
    generic_task()


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




def print_existing_text():
    existing_text = get_journal_text()
    if len(existing_text) > 0:
        print(existing_text)
    else:
        heading = f"\n[{current_journal}] - {entry.format_date(get_today())}\n\n"
        write_journal_and_console(heading)





def single_line_input():
    line = get_line()
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
def bgtask():
    """- The exact same as task, but with a * at the start of it, denoting that
    this task is something that you are doing alongside the main set of tasks. 
    - if you're in a zoom meeting while you're working on other stuff, then use this to 
        track the zoom meeting without breaking out of the task you currently have active.
            - The issue here is that when you type 'note', this will create an indented paragraph
            on the direct next line, annotating the bgtask.
            but you may have wanted to annotate the normal task, which requires a newline.
        Because of this reason, this is an unstable feature at the moment

    - They cannot be tracked in the same way as normal tasks
        in fact, I don't actually know how to track them"""

    generic_task(background_level=1)




def format_timestamp_tuple(ts):
    return format_timestamp(ts.hours, ts.minutes)

def format_timestamp(hour, minute):
    suffix = "AM"
    if hour >= 12:
        suffix = "PM"
        if hour > 12:
            hour -= 12

    return f"{hour}:{entry.to_2dig_number(minute)} {suffix}"

def now_timestamp():
    now = datetime.datetime.now()
    return format_timestamp(now.hour, now.minute)

def write_into_journal(text):
    with open(current_filepath, encoding="utf-8", mode="a") as file:
        file.write(text)

@command
def cwd():
    '''Print the current path'''
    print(os.path.abspath(os.curdir))

def write_carat():
    write_into_console(f"[{current_journal}]>")

def ensure_config():
    '''This function will ask the user to input configuration details if they 
    are not already present, or are otherwise corrupted/unreachable'''

    if os.path.exists("path.txt"):
        with open("path.txt", encoding="utf-8", mode="r") as file:
            path = file.read().strip()
            if path_is_accessible(path):
                return

    print("What folder would you like your journals to be stored in?")

    usr_selected_path = ""
    while True:
        write_into_console("Enter a folder path: ")
        usr_selected_path = input()

        if path_is_accessible(usr_selected_path):
            break

        print("That folder is either nonexistant or non-accessible, try again.")

    with open("path.txt", encoding="utf-8", mode="w") as file:
        file.write(usr_selected_path)

def path_is_accessible(path):
    if os.path.exists(path):
        if os.access(path, os.R_OK) and os.access(path, os.W_OK):
            return True

    return False

@command
def view():
    ''' Usage: view
        Opens today's text file in your default text editor.

    Usage: view [year] [month] [day]
        Opens the entry for year/month/day if it exists

    Usage: view [month] [day]
        Opens the entry for <this year>/month/day if it exists

    Usage: view [day]
        if day is is monday, tuesday, wednesday, etc.:
            Opens the entry for 'day' of this week.
            Probably one of the most useful commands imo.
        if day is a number:
            Opens the entry for <this year>/<this month>/day
'''
    arg1 = get_input()
    arg2 = get_input()
    arg3 = get_input()

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
        try:
            day = int(arg1)
        except:
            named_day = arg1
            date = namedday_this_week_to_date(named_day)
            if date == None:
                return

            day = date.day
            month = date.month
        
    filepath = entry.get_entry(current_journal, year, month, day)

    if filepath == None:
        print(f"There is no entry for {year}/{month}/{day}")
        return
    else:
        print(f"Pulling up entry for {year}/{month}/{day} in an external editor...")

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
    is_pm = timestamp_part[-2]=="P"

    hours = int(number_parts[0])
    if is_pm and hours != 12:
        hours += 12
    
    minutes = int(number_parts[1])

    return Timestamp(hours, minutes, indent)


def to_minutes(a):
    return a.hours*60 + a.minutes

def timedelta(a, b):
    return to_minutes(b) - to_minutes(a)


def get_activities():
    existing_text = get_journal_text()
    lines = existing_text.split('\n')
    
    line_times = []

    for line in lines:
        time = parse_timestamp(line)
        if time==None:
            continue

        line_times.append(Activity(line, time))

    return line_times

def minutes_str(minutes):
    hours = minutes//60
    mins = minutes%60
    return f"{hours}h {mins}m"

def time_delta_list(ongoing = False):
    line_times = get_activities()
    line_times = [x for x in line_times if x[1].indent == 0]
    
    res = []

    for a, b in zip(line_times, islice(line_times, 1, None)):
        delta = timedelta(a.time, b.time)
        res.append((a, b, delta))

    if ongoing:
        now = datetime.datetime.now()
        now_ts = Timestamp(now.hour,  now.minute, 0)
        delta = timedelta(line_times[-1].time, now_ts)
        res.append((line_times[-1], Activity(f"{now_timestamp()} - Now", now_ts), delta))

    return res

@command
def times():
    '''Show how much time has passed between each event'''
    clear_console()

    dl = time_delta_list(True)

    for prev, next, delta in dl:
        print(f"{prev.line}")
        print(f"\t[{minutes_str(delta)}]")
    
    print(f"{dl[-1][1].line}")
    total()

@command
def total():
    # TODO: FIX
    # It would be much more efficient to just get the first activity, get now, and
    # do a single diff, but Im doing it like this because im tired (lmao)
    dl = time_delta_list(True)
    total = 0
    for prev, next, delta in dl:
        total += delta

    print(f"\nTotal: {minutes_str(total)}")

@command
def clusteredtimes():
    """Usage: clusteredtimes [minutes?]
Same as 'times', but smaller tasks that happen in a row that are fewer
than 'minutes' minutes get clustered together to reduce clutter"""

    clear_console()

    minutes = get_input()
    if minutes == None:
        minutes = 30


    dl = time_delta_list(True)

    collapsed_list = []
    total_time = 0
    tasks = []

    for prev, next, delta in dl:
        tasks.append(prev)
        total_time += delta

        if total_time > minutes:
            collapsed_list.append((tasks, total_time))
            tasks = []
            total_time = 0

    collapsed_list.append((tasks, total_time))
    tasks = []
    total_time = 0

    for collapsed_tasks, delta in collapsed_list:
        if len(collapsed_tasks) <= 1:
            print(f"{collapsed_tasks[0].line}")
        else:
            ts = collapsed_tasks[0].time
            timestamp = format_timestamp_tuple(ts)
            print(f"{timestamp} - {len(collapsed_tasks)} smaller tasks:")
            smaller_tasks_commasep = ", ".join([x.line for x in collapsed_tasks])
            print(f" - {smaller_tasks_commasep}")

        print(f"\t[{minutes_str(delta)}]")

    print(f"{dl[-1][1].line}\n")

    total()
    


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
    print("\t" + "\n\t".join(entry_list))