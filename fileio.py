def readlines(path):
    with open(path, encoding="utf-8", mode="r") as file:
        return file.readlines()

def readlines_stripped(path):
    with open(path, encoding="utf-8", mode="r") as file:
        lines = file.readlines()
        return [x.strip() for x in lines]

def read(path):
    with open(path, encoding="utf-8", mode="r") as file:
        return file.read()

def writelines(path, lines):
    with open(path, encoding="utf-8", mode="w") as file:
        return file.writelines(lines)


def write(path, text):
    with open(path, encoding="utf-8", mode="w") as file:
        return file.write(text)

def append(path, text):
    with open(path, encoding="utf-8", mode="a") as file:
        return file.write(text)

def ensure_file(file):
    with open(file, encoding="utf-8", mode="a") as file:
        pass
