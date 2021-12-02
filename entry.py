import glob
from pathlib import Path
import datetime
import os

def make_journal_filepath(date, jorunal_name):
	journal_dir = Path(jorunal_name).joinpath(date_folder(date))
	if not journal_dir.exists():
		journal_dir.mkdir(parents=True)

	journal_file_dir = journal_dir.joinpath(
		f"[{jorunal_name}] {to_2dig_number(date.day)}.txt"
	)

	filepath = str(journal_file_dir)
	return filepath

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

def get_path_date(pathstr : str) -> datetime.date:
	path = Path(pathstr)
	if len(path.parts) < 3:
		return None

	return datetime.date(int(path.parts[-3]), int(path.parts[-2]), get_path_day(path.parts[-1]))

def get_entries_sorted(journal_name, year, month):
	path = Path(journal_name)
	path = path.joinpath(str(year))
	path = path.joinpath(str(to_2dig_number(month)))
	path = path.joinpath("*.txt")

	files = glob.glob(str(path))

	files = [path for path in files if is_valid_journal(path)]

	if len(files) >= 1:
		files.sort(key= lambda x : get_path_day(x))

	return files

def get_entry(journal_name, year, month, day):
	files = get_entries_sorted(journal_name, year, month)

	for file in files:
		if str(day) in os.path.basename(file):
			return file
	return None

def get_journal_name():
	return Path(os.path.abspath(".")).parts[-1]

def get_entry_list(folder):
    years = os.listdir(folder)
    entry_map = {}

    for year_path in years:
        for month_path in os.listdir(os.path.join(folder, year_path)):
            year = Path(year_path).parts[-1]
            month = Path(month_path).parts[-1]
            entry_map[year + " " + month] = get_entries_sorted(folder, year, month)

    return entry_map