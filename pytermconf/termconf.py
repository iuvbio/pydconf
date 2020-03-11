#!/usr/bin/env python
import shlex
import subprocess


dconfdir = "/org/gnome/terminal/legacy/profiles:"


def _get_command_output(command):
    ret = subprocess.run(shlex.split(command), capture_output=True)
    returncode = ret.returncode

    if returncode == 1:
        raise OSError("The command did not run successfully")

    return ret.stdout.decode().strip()


def is_list(output):
    return output.startswith('[') and output.endswith(']')


def str_to_list(strlist):
    return (
        strlist.replace("[", "")
               .replace("]", "")
               .replace("'", "")
               .split(", ")
    )


def dget(key):
    command = f'dconf read {dconfdir}/{key}'
    output = _get_command_output(command)
    if '[' in output and ']' in output:
        res = str_to_list(output)
    else:
        res = output.replace("'", "")
    return res


def dset(key, value):
    if not is_list(value) and value not in ['false', 'true']:
        value = f"'{value}'"
    command = f'dconf write {dconfdir}/{key} "{value}"'
    _ = _get_command_output(command)
    print(f"Set {key} to {value}")
    return None


def dlist(directory):
    command = f'dconf list {dconfdir}/{directory}/'
    output = _get_command_output(command)
    return output.split("\n")


def ddump(directory):
    command = f'dconf dump {dconfdir}/{directory}/'
    output = _get_command_output(command)
    output_parsed = [
        tuple(entry.split('='))
        for entry in output.split("\n")
        if '=' in entry
    ]
    return {k[0]: k[1] for k in output_parsed}


def dload(source, target):
    command = f'{source} | dconf load {dconfdir}/{target}/'
    _ = _get_command_output(command)
    return None


def dlist_append(key, value):
    list_ = dget(key)
    if value not in list_:
        list_.append(value)
    strlist = ', '.join([f"'{pid}'" for pid in list_])
    dset(key, f"[{strlist}]")
    return None


def get_profile_id(name):
    profiles = dget("list")
    name_key = ":{profile_id}/visible-name"
    for profile_id in profiles:
        profile_name = dget(name_key.format(profile_id=profile_id))
        if f"{name}" == profile_name:
            return profile_id
    return None


def _make_profile():
    profile_id = _get_command_output("uuidgen")
    _ = dlist_append('list', profile_id)
    return profile_id


def set_default_profile(profile_id):
    _ = dset("default", profile_id)
    print(f"Set {profile_id} as default profile")
    return None


def set_profile_key(profile_id, key, value):
    profile_key = f":{profile_id}/{key}"
    _ = dset(profile_key, f'{value}')
    return None


def create_new_profile(name, profile_params, set_default=False):
    """
    name, palette, default=False, foreground_color=None, background_color=None,
    bold_color=None, bold_color_same_as_fg=False, use_theme_colors=False,
    use_theme_background=False
    """
    existing_id = get_profile_id(name)
    if existing_id:
        print(f"A profile named '{name}' already exists")
        return None
    profile_id = _make_profile()
    print(f"Created profile {profile_id}")
    set_profile_key(profile_id, "visible-name", name)
    for key, value in profile_params.items():
        print(f"setting {key} to {value}")
        if not value:
            continue
        set_profile_key(profile_id, key, value)
    if set_default:
        set_default_profile(profile_id)
    print("Finished")
    return None
