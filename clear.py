from os import system, name

def clear():
	"""This function is used to clear the screen"""

	if name == 'nt':
		_ = system('cls')
	if name == 'posix':
		_ = system('clear')
	else:
		print("Can't determine what os is being used")

