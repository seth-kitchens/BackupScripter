import sys
from bs import g
from gplib.project import utils as project_utils

if __name__ != '__main__':
    sys.exit()

argv_flags = project_utils.extract_argv_flags()


def run():
    action_flags = [g.flags.GETDATA, g.flags.EDITOR, g.flags.BACKUP]
    actions = [f for f in action_flags if f in argv_flags]
    if len(actions) > 1:
        print("Only one action may be specified.")
        sys.exit()
    if len(actions) < 1:
        argv_flags.append(g.flags.EDITOR)

    if g.flags.EDITOR in argv_flags:
        exe = "run_editor.py"
    elif g.flags.BACKUP in argv_flags or g.flags.GETDATA in argv_flags:
        exe = "run_backup.py"

    project_utils.open_in_terminal(exe, argv_flags)


if g.flags.DBGCMD in argv_flags and not g.flags.DBGCMD in argv_flags:
    argv_flags.append(g.flags.DBGCMD)
    project_utils.open_in_terminal(sys.argv[0], argv_flags)
else:
    run()