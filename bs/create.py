import os
import shutil
import zipapp
import re
import nssgui as nss
from bs import g
from bs.script_data import ScriptDataManagerBS
from gplib.fs import utils as fs_utils


def create_script(context, script_data_manager:ScriptDataManagerBS, progress_func):
    """progress func should be: func(args[0]:str|None, args[1]:float|None=None)\n
    args[0]: update text to show\n
    args[1]: update percent, a value between 0.0 and 1.0"""


    script_file_name = ''.join(script_data_manager['ScriptFileName'])
    script_destination = script_data_manager['ScriptDestination']
    script_path = os.path.normpath(os.path.join(script_destination, script_file_name))

    progress_func('Checking Script Destination', 0.3)
    do_make_path = False
    if (not os.path.exists(script_destination)) and (not do_make_path):
        ne_dir = fs_utils.find_nonexistent_dir(script_destination)
        nss.PopupBuilder.T.error().text((
            'Script destination does not exist.',
            'Path: ' + script_destination,
            'Nonexistent: ' + os.path.basename(ne_dir)
        )).open(context)
        return False
    
    progress_func('Checking Script File', 0.45)
    if os.path.exists(script_path):
        if ScriptDataManagerBS.verify_file_is_script(script_path):
            do_continue = nss.PopupBuilder.T.warning().text((
                'Script file "' + script_file_name + '" already exists. Continue?',
                'Full path: ' + script_path
            )).open(context)
            if not do_continue:
                return False
        else:
            nss.PopupBuilder.T.error().text((
                'File "' + script_file_name + ' is not an overwriteable ".pyz" file.',
                'Full path: ' + script_path
            )).open(context)
            return False

    return _create_script(script_data_manager, progress_func)


def _create_script(script_data_manager:ScriptDataManagerBS, progress_func=None):
    def update_progress(msg=None, percent=None):
        if progress_func != None:
            progress_func(msg, percent)
    def packing_relpath(path):
        return os.path.normpath(os.path.join(g.paths.dirs.packing, path))
    def pack(proj_relpath, dest_relpath=None):
        dest_relpath = dest_relpath if dest_relpath != None else proj_relpath
        src = g.project_relpath(proj_relpath)
        dst = packing_relpath(dest_relpath)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copyfile(src, dst)

    script_file_name = ''.join(script_data_manager['ScriptFileName'])
    script_destination = script_data_manager['ScriptDestination']
    script_path = os.path.normpath(os.path.join(script_destination, script_file_name))
    

    update_progress('Copying Source', 0.6)
    packing_dir = g.paths.dirs.packing
    if os.path.exists(packing_dir):
        shutil.rmtree(packing_dir)
    os.mkdir(packing_dir)
    pack('bs')
    pack('data') # is this needed with PackFIO?
    pack('gplib')
    pack('scriptlib')
    pack('scripts/run_backup.py', '__main__.py')
    script_data_manager.save_to_file(g.packfio.get_packing_path(packing_dir, g.paths.files.script_data))
    

    update_progress('Packing Data Files', 0.8)
    packfio_data_dir = os.path.normpath(os.path.join(packing_dir, os.path.dirname(g.paths.rel.files.packfio_data)))
    if not os.path.exists(packfio_data_dir):
        os.makedirs(packfio_data_dir)
    g.packfio.pack_files(packing_dir, g.paths.rel.files.packfio_data)
    

    update_progress('Compiling Script', 0.9)
    zipapp.create_archive(packing_dir, script_path)
    shutil.rmtree(packing_dir)

    update_progress('Script Created', 1.0)
    return True