#!/usr/bin/env python3
from os import environ, chdir, getcwd
from os.path import exists, isdir, join, expanduser
from subprocess import run
from string import ascii_letters, punctuation
import glob
from shlex import split
import subprocess

"""-------------------------------PRINTENV-------------------------------"""


def handle_printenv(env):
    flag = 0
    if len(env) > 1:
        for key in env[1:]:
            if key in environ:
                print(environ[key])
            else:
                flag = 1
    else:
        for key in environ:
            print(key + '=' + environ[key])
    return flag


"""-------------------------------EXPORT----------------------------------"""


# if key has any punctuation that is not '_', return False
def check_key(key):
    for char in key:
        if char in punctuation and char != '_':
            return True
    return False


def export_unset_error(string, command, arg):
    if string[0][0] not in ascii_letters or check_key(string[0]):
        print("intek-sh: %s: `%s': not a valid identifier" % (command, arg))
        return True
    return False


def handle_export(input):
    flag = 0
    if len(input) > 1:
        for x in input[1:]:
            key = x.split('=')
            if export_unset_error(key, 'export', x):
                flag = 1
            else:
                environ[key[0]] = '='.join(key[1:])
    else:
        for x in environ:
            print('declare -x %s="%s"' % (x, environ[x]))
    return flag


"""------------------------------UNSET------------------------------------"""


def handle_unset(input):
    if len(input) > 1:
        for x in input[1:]:
            if not export_unset_error([x], 'unset', x) and x in environ:
                del environ[x]


"""-------------------Files and external binaries-------------------------"""


def handle_external(command):
    try:
        status = run(command)
        return status.returncode
    except (FileNotFoundError, PermissionError) as e:
        if type(e) is PermissionError:
            print('intek-sh: %s: Permission denied' % command[0])
            return 126
        else:
            print('intek-sh: %s: No such file or directory' % command[0])
            return 127


"""------------------------------CD---------------------------------------"""


def cd_to_dir(path):
    environ['OLDPWD'] = environ['PWD']
    chdir(path)
    environ['PWD'] = getcwd()
    return 0


def check_dir(path):
    if isdir(path):
        return cd_to_dir(path)
    else:
        print('cd: %s: Not a directory' % path)
        return 1


def check_path_exists(path):
    if exists(path):
        return check_dir(path)
    else:
        print('cd: %s: No such file of directory' % path)
        return 1


def print_cd_error(error):
    if type(error) is KeyError:
        print('intek-sh: cd: HOME not set')
    else:
        print('intek-sh: ' + environ['HOME'] +
              ': No such file or directory')
    return 1


def handle_cd(cpath):
    if len(cpath) > 1:
        path = cpath[1]
        return check_path_exists(path)
    else:
        try:
            return cd_to_dir(environ['HOME'])
        except (KeyError, FileNotFoundError) as error:
            return print_cd_error(error)


"""---------------------------COMMANDS---------------------------------"""


# search for file in PATH
def search_path(file):
    if 'PATH' in environ:
        path_list = environ['PATH'].split(':')
        for dir in path_list:
            if exists(dir + '/' + file):
                return True
    else:
        return False


def handle_input(input_list):
    command = input_list[0]
    if 'cd' == command:
        return handle_cd(input_list)
    elif 'printenv' == command:
        return handle_printenv(input_list)
    elif 'export' == command:
        return handle_export(input_list)
    elif 'unset' == command:
        return handle_unset(input_list)
    elif search_path(command) or './' in command:
        return handle_external(input_list)
    # elif search_path(command) :
    #     return globbing(input_list)
    else:
        print('intek-sh: ' + command + ': command not found')
        return 127


"""-------------------------------EXIT--------------------------------"""


def check_exit_arguments(arg_list):
    try:
        int(arg_list[0])
        return True
    except ValueError:
        return False


def check_arguments(args):
    if check_exit_arguments(args):
        print('exit\nintek-sh: exit: too many arguments')
        return False
    else:
        print('exit\
              \nintek-sh: exit: %s: numeric argument required' % args[0])
        if exit_status is 0:
            exit(2)


def handle_exit(arg, exit_status):
    if len(arg) > 1:
        check_arguments(arg[1:])
    else:
        print('exit')
        return True


"""----------------------------USER_INPUT----------------------------"""


def change_arg(args, status):
    if '$?' in args:
        index = args.index('$?')
        args[index] = str(status)
    return args

"""----------------------------globbing----------------------------"""
def globbing(user_input):
    command = ""
    for i in range(1, len(user_input)):
        command += user_input[i]
    glob_user_input = [user_input[0]]
    for i in user_input:
        if "~" in i:
            if user_input[0] == "~":
                path = environ['HOME']
            elif user_input[0] == "~+":
                path = getcwd()
            elif user_input[0] == "~-":
                path = environ["OLDPWD"]
    # print(path)
    # return path
    handle_mark = glob.glob(command)
    handle_mark.sort()
    if not handle_mark:
        glob_user_input = user_input
    for i in handle_mark:
        glob_user_input.append(i)
    return glob_user_input


"""----------------------------MAIN----------------------------------"""


def main():
    # global user_input
    exit_status = 0
    while True:
        try:
            user_input = split(input('intek-sh$ '), posix=True)
        except EOFError:
            break
        if user_input:
            user_input = globbing(user_input)
            if 'exit' == user_input[0]:
                if handle_exit(user_input, exit_status):
                    exit(exit_status)
                else:
                    if exit_status is 0:
                        exit_status = 1
            else:
                user_input = change_arg(user_input, exit_status)
                exit_status = handle_input(user_input)


if __name__ == "__main__":
    main()
