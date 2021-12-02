import enum
import sys
from commands import *
from actions import *
import fileio
import os
from pathlib import Path
import entry
import datetime
import time
from itertools import islice
from collections import namedtuple
import re

Timestamp = namedtuple("Timestamp", "hours minutes indent")
Activity = namedtuple("Activity", "line time")


def get_now_default():
    return datetime.datetime.now()


get_now = get_now_default


def get_today_default():
    return datetime.date.today()


get_today = get_today_default


config_filename_default = "config.txt"
config_filename = config_filename_default

default_journals_path_default = "journals"
default_journals_path = default_journals_path_default

available_journals = []
current_journal = None
current_filepath = ""

timestamp_regex = re.compile(r"(\d\d|\d):(\d\d|\d) (AM|PM)")
two_dig_number_regex = re.compile(r"(\d\d|\d)")


def set_date_provider(provider=None):
    global get_today
    get_today = get_today_default if provider == None else provider


def set_config_filename(filename=None):
    global config_filename, config_filename_default
    config_filename = config_filename if filename == None else filename


def set_default_journals_path(path):
    global default_journals_path
    default_journals_path = default_journals_path_default if path == None else path


def is_today():
    return make_journal_filepath(get_today()) == current_filepath


@command
def help():
    '''
    Introduces core functionality to the user, like using - and \'\'\'.
    '''

    clear_console()
    print("""
Enter /help to access this tutorial again later

Enter some text to make an entry. Mainly used for tracking tasks.

Enter the '-' character followed by text to annotate the previous entry

Enter three single quotes like ''' to start a multiline entry, that can then be ended with another '''
    usually used for writing long journal entries

Enter /commands to see commands
Enter /exit to exit
""")


def start():
    global current_journal

    ensure_config()
    config = fileio.readlines_stripped(config_filename)

    root = config[0]
    os.chdir(root)

    refresh_journals()

    if len(available_journals) == 0:
        new()
    else:
        set()


@command
def new():
    '''
    Create a new journal with a specified name.
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
    ''' Usage: 
        /set [number] - 

    Choose the current journal from a list of journals you've made with /new.
    Unless there is only 1 journal, in which case there is no choosing to be done.
'''
    clear_console()

    refresh_journals()

    if len(available_journals) == 1:
        set_journal(0)
        return

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
def hide():
    '''Clears the console'''
    clear_console()


@command
def show():
    '''Usage: 
        /show [filter?]

    Show all entries in the journal, filtered on 'tasks' or 'journals' if specified.
'''

    clear_console()

    existing_text = get_journal_text()

    filter = pull_line()
    text = apply_filter(existing_text, filter)

    if text != None:
        print(text)

    if existing_text.strip() == '':
        help()


def apply_filter(text: str, filter: str):
    if filter == None:
        return text

    filter_map = {
        "tasks": 0,
        "journals": 1,
    }

    if filter not in filter_map:
        filter_list_str = ", ".join(filter_map)
        print(f"{filter} is not a valid filter, use one of: {filter_list_str}")
        return

    blocks = text.split("\n\n")
    filter_num = filter_map[filter]
    blocks = [x for x in blocks if get_part_type(
        x) == filter_num or get_part_type(x) == -1]

    return "\n\n".join(blocks)


def get_part_type(part: str):
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

    line = line.strip()

    if line.startswith("-"):
        push_command(line[1:].strip())
        note()
    elif line.startswith("'''"):
        push_command(line[3:])
        journal()
    elif line.startswith("/"):
        push_command(line[1:])
        comm = pull_input()
        run_command(comm)
    elif line.strip() != '':
        push_command(line)
        task()
    else:
        show()


def list_journals():
    journals = [f"(Current)\t{x}" if x ==
                current_journal else x for x in available_journals]
    journals = [f"[{i}] {x}" for i, x in enumerate(journals)]
    return "\n".join(journals)


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


def get_typed_input(fn, bullet, ending_line="end"):
    line = ask_line()
    while True:
        write_into_console(bullet)

        line = ask_line()
        if(line == ending_line):
            break

        fn(line)


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


def task():
    """Write a new task into the current journal. Add notes to the task with 'note'"""
    generic_task()


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
        existing_text = fileio.read(current_filepath).strip()
    except:
        pass

    return existing_text


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
    line = pull_line()
    write_into_journal(f"{line}\n")


def generic_task(background_level=0):
    generic_input_to_journal(
        is_newline=True,
        top="",
        opening="",
        closing="",
        input_fn=single_line_input,
        bullet="*" * background_level
    )


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
    now = get_now()
    timestamp = format_timestamp(now.hour, now.minute)

    if is_today():
        return timestamp

    date_today = get_today()
    date_past = entry.get_path_date(current_filepath)

    days_later = (date_today - date_past).days

    return f"{entry.format_date(date_today)} ({days_later} days later) - {timestamp}"


def write_into_journal(text):
    fileio.append(current_filepath, text)


@command
def cwd():
    '''Print the current path'''
    print(os.path.abspath(os.curdir))


def write_carat():
    text = current_journal
    if not is_today():
        text += f"(** OLD **)"

    write_into_console(f"[{text}]>")


def ensure_config():
    '''
    This function will generate a config file if it is not present.
    right now, it contains:
        the folderpath
    '''

    if os.path.exists(config_filename):
        path = fileio.read(config_filename).strip()
        if path_is_accessible(path):
            return

    default_path = default_journals_path
    abs_default_path = os.path.abspath(default_path)

    fileio.write(config_filename, default_path)

    os.mkdir(default_path)

    print(
        f"Your journals will be stored in {default_path} (Absolute path is {abs_default_path}).\nYou can choose to move them, but you must specify this in path.txt")
    print("Press [Enter] to continue...")
    input()


def path_is_accessible(path):
    if os.path.exists(path):
        if os.access(path, os.R_OK) and os.access(path, os.W_OK):
            return True

    return False


@command
def view():
    ''' Usages: 
            view [year?] [month?] [day?]
            view [month?] [day?]
            view [day?]
            view

        Opens the entry for year/month/day if it exists.
        The year, month, and day default to today's date

            view [named_day]

        Opens an entry corresponding to a named day of the current week.
        These could be anything from Monday-Sunday (although if today is Tuesday, Wednesday - Sunday won't work.)

            view [journal_name]

        Opens an entry that you've named in the past with the /name command.
'''
    global current_filepath

    arg1 = pull_input()
    arg2 = pull_input()
    arg3 = pull_input()

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
            named_day = arg1.lower()
            date = None

            if named_day in "today":
                date = get_today()
            elif named_day in "yesterday":
                date = get_today() - datetime.timedelta(1)
            else:
                date = namedday_this_week_to_date(named_day)

            if date == None:
                return

            day = date.day
            month = date.month

    filepath = entry.get_entry(current_journal, year, month, day)

    if filepath == None:
        print(f"There is no entry for {year}/{month}/{day}")
        return

    current_filepath = filepath
    show()


@command
def notepad():
    '''Opens current journal in an external editor'''

    print(f"Pulling up {current_filepath} in an external editor...")
    open_file(current_filepath)


def namedday_this_week_to_date(named_day: str):
    named_day = named_day.lower()

    wanted_day_idx = day_week_index(named_day)
    if wanted_day_idx == -1:
        print(f"{named_day} does not remotely resemble any day")
        return None

    today = get_today()
    today_day_idx = day_week_index(today.strftime("%A").lower())

    if wanted_day_idx > today_day_idx:
        print(
            f"today is {days_of_week[today_day_idx]}, so {days_of_week[wanted_day_idx]} has not happened yet.")
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


def parse_timestamp(line: str):
    indent = 0
    while indent < len(line) and line[indent] == '\t':
        indent += 1

    timestamp_part = timestamp_regex.search(line)
    if timestamp_part == None:
        return None

    timestamp_part = timestamp_part[0]

    number_parts = two_dig_number_regex.findall(timestamp_part)

    # 10:50 AM
    #      ^
    is_pm = timestamp_part[-2] == "P"

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
        if time == None:
            continue

        line_times.append(Activity(line, time))

    return line_times


def minutes_str(minutes):
    hours = minutes//60
    mins = minutes % 60
    return f"{hours}h {mins}m"


def time_delta_list(ongoing=False):
    line_times = get_activities()
    line_times = [x for x in line_times if x[1].indent == 0]

    res = []

    for a, b in zip(line_times, islice(line_times, 1, None)):
        delta = timedelta(a.time, b.time)
        res.append((a, b, delta))

    if ongoing:
        now = get_now()
        now_ts = Timestamp(now.hour,  now.minute, 0)
        delta = timedelta(line_times[-1].time, now_ts)
        res.append(
            (line_times[-1], Activity(f"{now_timestamp()} - Now", now_ts), delta))

    return res


@command
def times():
    '''
    Show how much time has passed between each event
'''
    clear_console()

    dl = time_delta_list(True)

    for prev, next, delta in dl:
        print(f"{prev.line}")
        print(f"\t[{minutes_str(delta)}]")

    print(f"{dl[-1][1].line}")
    total()


@command
def total():
    '''
    Prints the total time that has elapsed since the first entry
'''
    activities = get_activities()
    now = get_now()
    total = timedelta(activities[0].time, Timestamp(now.hour, now.minute, 0))

    print(f"\nTotal: {minutes_str(total)}")


@command
def entries():
    '''Shows a breakdown of all entries in the journal'''
    clear_console()

    entry_map = entry.get_entry_list(current_journal)

    print("Entries:")

    def process_v(v):
        return f" {entry.to_2dig_number(len(v))} entries " + "|" * len(v)

    entry_list = [f"{k} : {process_v(v)}" for k, v in entry_map.items()]
    print("\t" + "\n\t".join(entry_list))


@command
def hours():
    '''Outputs the time that is h hours and m minutes after the start time'''

    activities = get_activities()

    if len(activities) == 0:
        print("You haven't started anything today.")
        return

    start = activities[0].time

    offsetH = ask_input(
        "Enter the number of hours and optionally, the number of minutes")

    offsetM = pull_input()

    if offsetM == None:
        offsetM = 0

    try:
        print(format_timestamp(start.hours +
              int(offsetH), start.minutes + int(offsetM)))
    except:
        if offsetM != 0:
            print(f"{offsetH} or {offsetM} is probably not a valid number")
        else:
            print(f"{offsetH} is probably not a valid number")


@command
def name():
    ''' Usage:
            /name [name]

        Names this journal entry such that you can revisit it later using
        the /named command
    '''

    new_name = ask_input(
        "Enter a name for this entry. You will be able to get back here with /view").strip()

    if new_name.strip() == "":
        print("Are you sure you want to unname this journal?")
        if ask_input().lower() not in "yes":
            return

    set_current_journal_name(new_name)


@command
def named():
    ''' Usage:
            /named [name]

        Access the journal entry with the name [name], which you had set
        using the /name command
    '''

    name_map = load_name_map()
    wanted_name = pull_input()

    if wanted_name == None:
        print("named journals:")
        for name, filepath in name_map.items():
            print(f"{name} : {filepath}")

        print("enter a name along with this command to open one or to filter through them.")
    else:
        global current_filepath
        current_filepath = name_map[wanted_name]


def load_name_map():
    filepath = os.path.join(current_journal, "names.txt")

    fileio.ensure_file(filepath)

    lines = fileio.readlines(filepath)
    lines = [x.split(":") for x in lines]

    filepath_map = {x[1].strip(): x[0].strip() for x in lines}

    return filepath_map


def save_name_map(filepath_map):
    lines = [f"{n}:{f}\n" for n, f in filepath_map.items()]
    fileio.writelines(os.path.join(current_journal, "names.txt"), lines)


def set_current_journal_name(name: str):
    name = name.replace(":", "-")

    filepath_map = load_name_map()

    if name == "":
        del filepath_map[current_filepath]
    else:
        filepath_map[current_filepath] = name

    save_name_map(filepath_map)
