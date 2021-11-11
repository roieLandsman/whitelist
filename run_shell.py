#!/usr/bin/env python3

"""psh: a simple shell written in Python"""
HISTORY = []
import os
import subprocess
import logging
import json
from os.path import isfile
from platform import system


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
        logging.info('{} Command run successfully '.format(command))

    except Exception:
        print("psh: command not found: {}".format(command))
        logging.error("{} Command failed to run".format(command))


def add_hist(command):
    """
    add the user input to the history
    """
    if len(HISTORY) >= 10:
        HISTORY.pop(0)
        HISTORY.append(command)
    else:
        HISTORY.append(command)


def history():
    """
    show the history
    """
    for count, value in enumerate(HISTORY):
        print(count + 1, value)


def psh_cd(path):
    """convert to absolute path and change directory"""
    try:
        os.chdir(os.path.abspath(path))
        logging.info("cd {} Command run successfully".format(path))
    except Exception:
        print("cd: no such file or directory: {}".format(path))
        logging.error("cd {} Command failed to execute".format(path))


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
        return True
    elif inp == 'history':
        history()
        logging.info("{} command run successfully".format(inp))
        return True
    elif inp == "help":
        psh_help()
        logging.info("{} command run successfully".format(inp))
        return True
    elif ('kill' in inp or 'taskkill' in inp) and str(get_pid()) in inp:
        print('illegal command, it is not allowed to kill self process')
        logging.error("!!! An attempt to kill self process !!!")
        return True
    return False


def wl_check(inp, whitelist):
    for cmd in inp.split('|'):
        if cmd.split(" ")[0].strip() in whitelist.keys():
            cmd_params = cmd.split(' ')
            main_cmd = cmd_params.pop(0)
            if whitelist[main_cmd]:
                for param in cmd_params:
                    if param not in whitelist[main_cmd]:
                        print('parameter {} of command {} is not in whitelist'.format(param, main_cmd))
                        logging.warning("{} command - parameter '{}' not in whitelist".format(main_cmd, param))
                        return False
        else:
            logging.warning("{} command not in whitelist".format(cmd))
            return False
    return True


def check_script_content(file, whitelist):
    with open(file) as script:
        for line in script.read().split("\n"):
            if ('kill' in line or 'taskkill' in line) and str(get_pid()) in line:
                print('file contain illegal command, it is not allowed to kill self process')
                logging.error("!!! An attempt to run file with kill self command!!!")
                return False
            if line.split(' ')[0] in ['exit', 'cd', 'history', 'help']:
                continue
            if line.split(' ')[0] not in whitelist:
                logging.error("!!! An attempt to run file {} with illegal command - {}!!!".format(file, line.split(' ')[0]))
                return False
        return True


def run_script(file):
    with open(file) as script:
        for line in script.read().split("\n"):
            execute_command(line)


def main():
    print(get_pid())
    logging.basicConfig(filename="wl_log.log", format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    with open("whitelist.json", "rb") as file:
        file = json.load(file)
        whitelist = file[system().lower()]
        files = file["files"]

    while True:
        inp = input("$ ")
        add_hist(inp)
        if inp in files:
            if check_script_content(inp, whitelist):
                run_script(inp)
        elif special_check(inp):
            continue
        elif wl_check(inp, whitelist):
            execute_command(inp)


if '__main__' == __name__:
    main()
