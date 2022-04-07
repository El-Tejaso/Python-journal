import subprocess
import os
import platform

# cheers https://stackoverflow.com/questions/434597/open-document-with-default-os-application-in-python-both-in-windows-and-mac-os


def open_file(filepath):
	if platform.system() == 'Darwin':       # macOS
		subprocess.call(('open', filepath))
	elif platform.system() == 'Windows':    # Windows
		os.startfile(filepath)
	else:                                   # linux variants
		subprocess.call(('xdg-open', filepath))


should_clear = True

# cheers https://www.delftstack.com/howto/python/python-clear-console/


def clear_console():
	if not should_clear:
		return

	command = 'clear'
	if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
		command = 'cls'
	os.system(command)

def disable_clear_console():
	global should_clear

	should_clear = False