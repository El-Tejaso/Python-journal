import glob
from pathlib import Path
import datetime
import os


def to_2dig_number(num):
	num = str(num)
	if(len(num) == 1):
		num = "0" + num
	return num

def format_date(date):
	return f"{date.day}/{date.month}/{date.year}"

def date_folder(date) -> Path:
	return Path(str(date.year), str(to_2dig_number(date.month)))

def date_filepath(date) -> Path:
	return date_folder(date).joinpath(date.day)

def is_valid_journal(filepath):
	return get_path_day(filepath) != -1

def get_path_day(path : str):
	name = os.path.basename(path)

	start = 0
	if name[0] == '[':
		start = name.find(']')+1
		while start+1<len(name) and name[start] == ' ':
			start+=1

	end = start
	while end < len(name) and name[end].isnumeric():
		end += 1

	if end==start:
		return -1

	return int(name[start:end])

def get_path_date_str(pathstr : str):
	path = Path(pathstr)
	if len(path.parts) < 3:
		return ""

	return os.sep.join([path.parts[-3], path.parts[-2], str(get_path_day(path.parts[-1]))])

def get_entries_sorted(year, month):
	path = Path(str(year), str(to_2dig_number(month))).joinpath("*.txt")
	files = glob.glob(str(path))
	files = [path for path in files if is_valid_journal(path)]

	if len(files) >= 1:
		files.sort(key= lambda x : get_path_day(x))

	return files

def get_journal_name():
	return Path(os.path.abspath(".")).parts[-1]