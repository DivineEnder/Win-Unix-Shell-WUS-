import sys
import os
from subprocess import call as cmd
from pprint import pprint
import json

FLAG_ARG_DICT = { "-d":1, "-r":"0-1", "-l":0, "-ld":0 }
ENV = {}

def import_env():
	file_dir = os.path.realpath(__file__).replace(os.path.basename(__file__), "")
	with open("%s.env" % file_dir , "r") as environment:
		for line in environment:
			line = line.replace("\n", "")
			var_name, var = line.split("=")
			ENV[var_name] = var
try:
	import_env()
except FileNotFoundError:
	raise EnvironmentError("No Environment file found for Alix. Alix needs several system variables defined for it. Run setup.py to properly install Alix.")

def alix_list():
	commands = {}
	with open(ENV["ALIXES_PATH"], "r") as file:
		cur_command = None
		for line in file:
			if (line[0] != "\t"):
				cur_command = line.replace("\n", "")
				commands[cur_command] = []
			else:
				commands[cur_command].append(line.replace("\t", "").replace("\n", ""))

	if not commands:
		return None
	else:
		return commands

def alix_list_commands():
	command_names = []
	with open(ENV["ALIXES_PATH"], "r") as file:
		for line in file:
			if (line[0] != "\t"):
				command_names.append(line.replace("\n", ""))

	if not command_names:
		return None
	else:
		return command_names

def alix_has_command(command_name):
	command_list = alix_list_commands()
	if command_list:
		return command_name in command_list
	else:
		return False

def alix_delete(command_name):
	assert alix_has_command(command_name), "Alix has no command '%s'" % command_name

	commands = alix_list()
	open(ENV["ALIXES_PATH"], "w").close()

	for command in commands:
		if (command != command_name):
			alix_create(command, commands[command])
		else:
			cmd("rm %s.bat" % command)

	print("Deleted alix named '%s'." % command_name)

def alix_create(command_name, commands, force = False):
	if alix_has_command(command_name):
		print("Alix already has command '%s'" % command_name)
		if input("Would you like to replace it (y/n) : ").lower() == "y":
			force = True
		else:
			print("Did not create command '%s'." % command_name)
			return

	if force:
		try:
			alix_delete(command_name)
		except AssertionError:
			pass

	with open(ENV["ALIXES_PATH"], "a") as file:
		file.write("%s\n" % command_name)
		for command in commands:
			file.write("\t%s\n" % command)

	alix_update()

	print("Created alix command '%s'." % command_name)

def alix_record(command_name = None):
	commands_rec = []

	command = None
	print("Alix is now recording commands. Type 'alix -s' to stop recording or 'help' for more information.")
	while (command != "alix -s"):
		command = str(input("(AlixRec) " + os.getcwd() + ">"))

		if not (command == "alix -s" or command.lower() == "help"):
			cmd(command, shell = True)
			commands_rec.append(command)
		elif (command.lower() == "help"):
			print("Alix record sit behind the shell, noticing and recording your commands.")
			print("Since Alix is a python script any commmand typed will be fed through python to the command line.")
			print("Alix was created by DivineEnder")
			print("To stop recording type\n\t'alix -s'")

	if command_name == None:
		command_name = input("Print please enter the command name you would like associated with your recorded actions: ")
	
	alix_create(command_name, commands_rec)

def alix_update():
	with open(ENV["ALIXES_PATH"], "r") as file:
		cur_command = None
		for line in file:
			if (line[0] != "\t"):
				cur_command = line.replace("\n", "")
				with open("%s%s.bat" % (ENV["ALIX_PATH"], cur_command), "w") as command_file:
					command_file.write("@ECHO OFF\n")
			else:
				with open("%s%s.bat" % (ENV["ALIX_PATH"], cur_command), "a") as command_file:
					command_file.write(line.replace("\t", ""))


def main(args):
	if len(args) == 0:
		raise UserWarning("No args passed to alix command")
	else:
		flags = []
		command_name = None
		command = None
		# print("args were: " + str(args))

		i = 0
		while (i < len(args) and args[i][0] == "-"):
			flags.append(args[i])
			i = i + 1

		#No flags
		if (i == 0):
			assert len(args) == 2, "Alix missing number of required args (Given: %s" % str(args) + ")"
			alix_create(args[0], [args[1]])
		#Single flag
		elif (i == 1):
			flag = flags[0]
			command_args = args[1:]
			num_flag_args = FLAG_ARG_DICT[flags[0]]

			if type(num_flag_args) is str:
				num_flag_args_min, num_flag_args_max = (int(num_flag_args.split("-")[0]), int(num_flag_args.split("-")[1]))
				assert len(command_args) >= num_flag_args_min and len(command_args) <= num_flag_args_max, "Alix passed wrong number of args for '%s' flag (given %d args)" % (flags[0], len(command_args))
			else:
				assert len(command_args) == num_flag_args, "Alix passed wrong number of args for '%s' flag (given %d args)" % (flags[0], len(command_args))

			DELETE_FLAGS = ["--delete", "-d"]
			RECORD_FLAGS = ["--record", "-r"]
			LIST_FLAGS = ["--list", "-l"]
			LIST_DETAILS_FLAGS = ["--listdets", "-ld"]
			FORCE_FLAGS = ["--force", "-f"]

			if flag in DELETE_FLAGS:
				alix_delete(command_args[0])
			elif flag in RECORD_FLAGS:
				if (len(command_args) > 0):
					alix_record(command_args[0])
				else:
					alix_record()
			elif flag in LIST_FLAGS:
				pprint(alix_list_commands(), indent = 2)
			elif flag in LIST_DETAILS_FLAGS:
				pprint(alix_list(), indent = 2)
			elif flag in FORCE_FLAGS:
				alix_create(command_args[0], command_args[1], True)


if __name__ == "__main__":
	main(sys.argv[1:])