from queue import Queue

from actions import clear_console


command_dict = {}

def command(fn):
    command_dict[fn.__name__] = fn
    return fn

__args = Queue()

def push_command(arg):
    args = arg.split(' ')
    for a in args:
        __args.put(a)

def get_input():
    if __args.qsize() == 0:
        line = input()
        tokens = line.split(" ")

        for t in tokens:
            __args.put(t)

    arg = __args.get()

    if arg.lower() == "exit":
        print("exiting program...")
        clear_console()
        exit(0)

    return arg

def get_input_if_present():
    if __args.qsize() != 0:
        return __args.get()

    return None

def get_line_if_present():
    if __args.qsize() != 0:
        line = []
        while __args.qsize() != 0:
            line.append(__args.get())
        
        return " ".join(line)

    return None

def ask_line_if_not_present(message_if_not_present = None):
    line = get_line_if_present()
    if line != None:
        return line

    if message_if_not_present != None:
        print(message_if_not_present)

    line = input()
    return line

def ask_input_if_not_present(message_if_not_present = ""):
    line = get_input_if_present()
    if line == None:
        print(message_if_not_present)
        return get_input()
    return line

def run_command(name):
    if name in command_dict:
        command_dict[name]()
        return True
    return False

def print_help(functions):
    functions = sorted(functions, key=lambda x: x.__name__)

    for fn in functions:
        doc = (fn.__doc__ if fn.__doc__ != None else "This command isn't documented.")
        print(f"\t{fn.__name__} -> {doc}\n")

def clear_args():
    while __args.qsize() > 0:
        __args.get()
