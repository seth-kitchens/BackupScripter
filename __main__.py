import sys
from bs import g
from gplib import utils as gp_utils

if __name__ != '__main__':
    sys.exit()

argv_flags = gp_utils.extract_argv_flags()


def run():
    action_flags = [g.flags.GETDATA, g.flags.EDITOR, g.flags.BACKUP]
    actions = [f for f in action_flags if f in argv_flags]
    if len(actions) > 1:
        print("Only one action may be specified.")
        sys.exit()
    if len(actions) < 1:
        argv_flags.append(g.flags.EDITOR)

    if g.flags.EDITOR in argv_flags:
        exe = g.project_path("scripts/run_editor.py")
    elif g.flags.BACKUP in argv_flags or g.flags.GETDATA in argv_flags:
        exe = g.project_path("scripts/run_backup.py")

    gp_utils.open_in_terminal(exe, argv_flags)


if g.flags.DEBUG in argv_flags and not g.flags.DBGCMD in argv_flags:
    argv_flags.append(g.flags.DBGCMD)
    gp_utils.open_in_terminal(sys.argv[0], argv_flags)
else:
    run()