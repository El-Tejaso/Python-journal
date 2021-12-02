from queue import Queue
from actions import clear_console

get_line = input


def set_getline(getline_func):
    global get_line
    get_line = input if getline_func == None else getline_func


def exit_program():
    clear_console()
    print("exiting program...")
    exit(0)


command_dict = {
    "exit": exit_program
}

__args = Queue()


def args_get() -> str:
    try:
        return __args.get(block=False)
    except:
        return None


def command(fn):
    command_dict[fn.__name__] = fn
    return fn


def push_command(arg: str):
    args = arg.split(' ')
    for a in args:
        __args.put(a)


def get_input():
    if __args.qsize() == 0:
        line = get_line()
        tokens = line.split(" ")

        for t in tokens:
            __args.put(t)

    arg = __args.get()

    return arg


def pull_input():
    if __args.qsize() != 0:
        return args_get()
    return None


def pull_line():
    if __args.qsize() != 0:
        line = []
        while __args.qsize() != 0:
            line.append(args_get())

        return " ".join(line)

    return None


def ask_line(message_if_not_present=None):
    line = pull_line()
    if line != None:
        return line

    if message_if_not_present != None:
        print(message_if_not_present)

    line = get_line()
    return line


def ask_input(message_if_not_present=""):
    line = pull_input()
    if line == None:
        print(message_if_not_present)
        return get_input()
    return line


def run_command(name):
    possible_commands = [x for x in command_dict if x.startswith(name)]
    if len(possible_commands) == 1:
        command_dict[possible_commands[0]]()
        return True
    elif len(possible_commands) > 1 and len(name.strip()) > 1:
        print("did you mean any of these?")
        for x in possible_commands:
            print("/" + x)
    elif len(name.strip()) == 0:
        print("No command was provided")
    else:
        print(
            f"No existing commands start with '{name}'. Use /commands to see a list of commands")

    return False


@command
def commands():
    clear_console()
    print("Commands:")

    for command, fn in command_dict.items():
        if fn.__doc__ == None:
            continue
        print(f"/{command}: {fn.__doc__.strip()}\n")


def clear_args():
    while __args.qsize() > 0:
        args_get()
