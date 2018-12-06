#!/usr/bin/env python3
from os import environ, chdir, getcwd
from os.path import exists, isdir, join, expanduser
from subprocess import run, PIPE
from string import ascii_letters, punctuation
from glob import glob
from shlex import split
import sys


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
    except OSError:
        run(['/bin/bash','-c', command[0]])


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


"""---------------------------COMMANDS---------------------------------"""# vt = user_input.index("|")
    # tam = []
    # for i in range(vt + 1 , len(user_input)):
    #     tam.append(user_input[i])
    # input = run(user_input[vt - 1], stdout=PIPE)
    # run(tam, stdout = sys.stdout, input = input.stdout, stderr=sys.stderr)


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
    a = [">", "<", ">>", "<<", "2>", "2>>"]
    command = input_list[0]
    if 'cd' == command:
        return handle_cd(input_list)
    elif 'printenv' == command:
        return handle_printenv(input_list)
    elif 'export' == command:
        return handle_export(input_list)
    elif 'unset' == command:
        return handle_unset(input_list)
    elif any(i in input_list for i in a):
        return handle_redirections(input_list)
    elif any("|" in i for i in input_list):
        return handle_pipes(input_list)
    elif search_path(command) or './' in command:
        return handle_external(input_list)
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


def check_DB(i, user_input):
    tam = []
    command = [user_input[0]]
    count_start = i.count("*")
    count_question = i.count("?")
    check = len(i) - 1
    if check == (count_start + count_question):
        if count_question < 1:
            tam.append(i)
            tam.append(".")
            tam.append("..")
        elif count_question == 1:
            tam.append(i)
            tam.append("..")
        elif count_question > 1:
            tam.append(i)
            return tam
    else:
        tam.append(i)
    for j in tam:
        cmd = sorted(glob(j))
        command += cmd
    return command


def check_ch(i, user_input):
    tam = []
    command = [user_input[0]]
    count_question = i.count("?")
    count_start = i.count("*")
    if count_question == 1:
        if count_start == 0:  # khong co cham *
                tam.append(i)
                tam.append("..")
        else:# khong co cham *
                tam.append(i)
                tam.append("..")
                tam.append(".")
    else:
        tam.append(i)
    for j in tam:
        cmd = sorted(glob(j))
        command += cmd
    return command

"""----------------------------globbing----------------------------"""
def globbing(user_input):
    cases = ['.', '?', '*', '[', '!']
    command = []
    for i in user_input:
        if any(x in i for x in cases):
            if i.startswith(".*"):
                return check_DB(i, user_input)
            if i.startswith(".?"):
                return check_ch(i, user_input)
            cmd = sorted(glob(i))
            if cmd:
                command += cmd
            else:
                command.append(i)
        else:
            command.append(i)
    return command
"""----------------------------tilde expansions----------------------------"""
def add_til(root, link):
    cre_path = root
    if len(link) > 1:
        cre_path += '/' + link[1]
    return cre_path

def tilde_expansions(user_input):
    tilde_user_input = []
    for i in user_input:
        path = i.split("/",1)
        if i.startswith("~"):
            if path[0] == "~":
                tilde_user_input.append(add_til(environ['HOME'], path))
            elif path[0] == "~+":
                tilde_user_input.append(add_til(getcwd(), path))
            elif path[0] == "~-":
                tilde_user_input.append(add_til(environ['OLDPWD'], path))
            else:
                tilde_user_input.append(path[0])
        else:
            tilde_user_input.append(i)
    return tilde_user_input
"""----------------------------tilde expansions----------------------------"""


def handle_start(user_input):
    user = tilde_expansions(user_input)
    user = globbing(user)
    return user


"""----------------------------the redirections----------------------------"""


def diff_list(lst1, lst2, delist):
    return [i for i in lst1 if i not in lst2 and i not in delist]


def handle_redirections(user_input):
    redirections = [">", "<", ">>", "<<", "2>", "2>>", "|"]
    work1 = {">" : "w", ">>" : "a"}
    work2 = {"<" : "rb", "<<" : "rb"}
    work3 = {"2>" : "w", "2>>" : "a"}
    output, input, err = sys.stdout, sys.stdin, sys.stderr
    input_handle = None
    list_file = []
    for i in user_input:
        if i in redirections:
            if i in work1:
                sys.stdout = open(user_input[user_input.index(i)+1], work1[i])
            elif i in work2:
                with open(user_input[user_input.index(i)+1], work2[i]) as f:
                    input_handle = f.read()
            elif i in work3:
                sys.stderr = open(user_input[user_input.index(i)+1], work3[i])
            list_file.append(user_input[user_input.index(i)+1])
    command = diff_list(user_input, list_file, redirections)
    run(command, stdout = sys.stdout, input = input_handle, stderr=sys.stderr)
    sys.stdout, sys.stdint, sys.stderr = output, input, err


def handle_pipes(user_input):
    handle_input = None
    s = []
    c = []
    for i in range(len(user_input)):
        if user_input[i] != "|":
            s.append(user_input[i])
        else:
            c.append(s)
            s = []
    c.append(s)
    for i in range(len(c)):
        if i == len(c) - 1:
            run(c[i], input = handle_input)
        chay = run(c[i], input = handle_input, stdout = PIPE)
        handle_input = chay.stdout


"""----------------------------MAIN----------------------------------"""


def main():
    exit_status = 0
    while True:
        try:
            user_input = split(input('intek-sh$ '), posix=True)
        except EOFError:
            break
        if user_input:
            user_input = handle_start(user_input)
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
