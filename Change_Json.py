import json
from platform import system


def add_t_json(cmd, params=[], OStype=system()):
    if type(cmd) != str or type(params) not in [list, set, tuple] or type(OStype) != str:
        # logging here
        return
    with open("whitelist.json") as Jfile:
        full_content = json.load(Jfile)
        partial_content = full_content[OStype.lower()]
    if OStype.lower() == "files":
        partial_content.append(cmd)
    elif cmd not in partial_content.keys():
        partial_content[cmd] = list(params)
    else:
        for param in params:
            if param not in partial_content[cmd]:
                partial_content[cmd].append(param)
    full_content[OStype.lower()] = partial_content
    with open("whitelist.json", 'w') as Jfile:
        Jfile.write(json.dumps(full_content, indent=6))


def chn_param_json(cmd, params=[], OStype=system(), add=True):
    """
    add or delete params for the cmd given
    param add is bool. decide if adding or deleting. deafult to add.
    """
    if type(cmd) != str or type(params) not in [list, set, tuple] or type(OStype) != str:
        # logging here
        return
    if OStype.lower() == "files":
        pass
        # log no params for files.
    with open("whitelist.json") as Jfile:
        full_content = json.load(Jfile)
        partial_content = full_content[OStype.lower()]
    if add:
        partial_content[cmd] = list(set(partial_content[cmd] + params)) # remove doubles
    else:
        for param in params:
            if param in partial_content[cmd]:
                partial_content[cmd].remove(param)
            else:
                # log try to delete non-exist param
                pass
    full_content[OStype.lower()] = partial_content
    with open("whitelist.json", 'w') as Jfile:
        Jfile.write(json.dumps(full_content, indent=6))

def del_cmd(cmd, OStype=system()):
    if type(cmd) != str or type(OStype) != str:
        # logging here
        return
    with open("whitelist.json") as Jfile:
        full_content = json.load(Jfile)
        partial_content = full_content[OStype.lower()]
    if cmd in partial_content.keys():
        partial_content.pop(cmd)
    else:
        # try to delete nin-exist cmd
        full_content[OStype.lower()] = partial_content
        with open("whitelist.json", 'w') as Jfile:
            Jfile.write(json.dumps(full_content, indent=6))
