#!/usr/bin/env python3

"""psh: a simple shell written in Python"""
HISTORY = []
import os
import subprocess
import logging


def execute_command(command):
    """execute commands and handle piping"""
    try:
        if "|" in command:
            # save for restoring later on
            s_in, s_out = (0, 0)
            s_in = os.dup(0)
            s_out = os.dup(1)

            # first command takes commandut from stdin
            fdin = os.dup(s_in)

            # iterate over all the commands that are piped
            for cmd in command.split("|"):
                # fdin will be stdin if it's the first iteration
                # and the readable end of the pipe if not.
                os.dup2(fdin, 0)
                os.close(fdin)

                # restore stdout if this is the last command
                if cmd == command.split("|")[-1]:
                    fdout = os.dup(s_out)
                else:
                    fdin, fdout = os.pipe()

                # redirect stdout to pipe
                os.dup2(fdout, 1)
                os.close(fdout)

                try:
                    subprocess.run(cmd, shell=True)
                except Exception:
                    print("psh: command not found: {}".format(cmd.strip()))

            # restore stdout and stdin
            os.dup2(s_in, 0)
            os.dup2(s_out, 1)
            os.close(s_in)
            os.close(s_out)

        else:
            subprocess.run(command, shell=True)
        logging.info(' -- {} -- Command run successfully '.format(command))

    except Exception:
        print("psh: command not found: {}".format(command))
        logging.error(" -- {} -- Command failed to run".format(command))


def add_hist(command):
    if len(HISTORY) >= 10:
        HISTORY.pop(0)
        HISTORY.append(command)
    else:
        HISTORY.append(command)


def history():
    for count, value in enumerate(HISTORY):
        print(count, value)


def psh_cd(path):
    """convert to absolute path and change directory"""
    try:
        os.chdir(os.path.abspath(path))
        logging.info(" -- cd {} -- Command run successfully".format(path))
    except Exception:
        print("cd: no such file or directory: {}".format(path))
        logging.error(" -- cd {} -- Command failed to execute".format(path))


def psh_help():
    print("""psh: shell implementation in Python.
          Supports all basic shell commands.""")


def get_pid():
    return os.getpid()

def special_check(inp):
    if inp == "exit":
        exit()
    if inp[:3] == "cd ":
        psh_cd(inp[3:])
        logging.info(" -- {} -- command run successfully".format(inp))
        return True
    elif inp == 'history':
        history()
        logging.info(" -- {} -- command run successfully".format(inp))
        return True
    elif inp == "help":
        psh_help()
        logging.info(" -- {} -- command run successfully".format(inp))
        return True
    elif ('kill' in inp or 'taskkill' in inp) and str(get_pid()) in inp:
        logging.error("An attempt to kill self process")
        return True
    return False

def wl_check(inp, whitelist):
    for cmd in inp.split('|'):
        if cmd.split(" ")[0] in whitelist:
            continue
        else:
            print('command not in whitelist')
            logging.warning(" -- {} -- command not in whitelist")
            return False
    return True

def main():
    logging.basicConfig(filename="wl_log.log", encoding='UTF-8', level=logging.INFO, format='%(asctime)s %(message)s')
    # whitelist = ['ls', 'top', 'free', 'kill']
    whitelist = ['dir', 'echo', 'color', 'date', 'time']
    while True:
        inp = input("$ ")
        add_hist(inp)
        if special_check(inp):
            continue
        if wl_check(inp, whitelist):
            execute_command(inp)


if '__main__' == __name__:
    main()

