from typing import Iterable
import unittest
import os
import shutil
import zipfile
import py7zr
import sys


from src.bs.fs.vfs import VFSBS
from src.bs.script_data import ScriptDataBS
from src.bs import g


__all__ = [
    'fio_path',
    'fio_relpath',
    'clear_fio',
    'make_sd',
    'TestCaseBS',
    'TestFile',
    'TestDir',
    'FSDef',
    'run_backup_script'
]

fio_path = g.project_path('temp/fio')


def fio_relpath(path):
    return os.path.normpath(os.path.join(fio_path, path))


def clear_fio():
    if os.path.exists(fio_path):
        shutil.rmtree(fio_path)
    os.mkdir(fio_path)


def run_backup_script(relpath, no_input=True, redirect_stdout=True):
    """Runs script at fio relpath given, redirecting and returning stdout"""
    args = [sys.executable, fio_relpath(relpath)]
    if no_input:
        args.append('--noinput')
    if redirect_stdout:
        args.append('> {}'.format(fio_relpath('stdout.txt')))
    command = ' '.join(str(a) for a in args)
    os.system(command)
    with open(fio_relpath('stdout.txt'), 'r') as file_in:
        s = file_in.read()
    return s


def make_sd(sd=None,
        script_filename=None,
        script_dest_rel=None,
        backup_filename=None,
        backup_dest_rel=None,
        backup_filename_date=None,
        included_items=None,
        excluded_items=None,
        archive_format=None,
        archive_mode=None,
        max_backups=None,
        backup_old_age_secs=None,
        backup_recent_age_secs=None,
        pull_age_from_postfix=None,
        matching_groups=None) -> ScriptDataBS:
    sd_dict = sd.to_dict() if sd != None else ScriptDataBS(data_file=None).to_dict()

    def update(name, val):
        if val != None:
            sd_dict[name] = val

    if script_dest_rel != None:
        sd_dict['ScriptDestination'] = fio_relpath(script_dest_rel)
    elif not sd_dict['ScriptDestination'].startswith(fio_path):
        raise RuntimeError
    if backup_dest_rel != None:
        sd_dict['BackupDestination'] = fio_relpath(backup_dest_rel)
    elif not sd_dict['BackupDestination'].startswith(fio_path):
        raise RuntimeError

    update('ScriptFilename', script_filename)
    update('BackupFilename', backup_filename)
    update('BackupDatePostfix', backup_filename_date)
    update('IncludedItems', included_items)
    update('ExcludedItems', excluded_items)
    update('ArchiveFormat', archive_format)
    update('ArchiveMode', archive_mode)
    update('MaxBackups', max_backups)
    update('BackupOldAge', backup_old_age_secs)
    update('BackupRecentAge', backup_recent_age_secs)
    update('PullAgeFromPostfix', pull_age_from_postfix)
    update('MatchingGroupsList', matching_groups)

    return ScriptDataBS.from_dict(sd_dict)


class TestCaseBS(unittest.TestCase):

    def tearDown(self):
        clear_fio()
        packing_dir = g.paths.rel.dirs.packing
        if os.path.exists(packing_dir):
            shutil.rmtree(packing_dir)

class TestFile:

    def __init__(self, name=None, parent_dir=None, path=None, size=None, text=None):
        if path:
            if name or parent_dir:
                raise RuntimeError
            self.path = path
        else:
            self.name = name
            self.parent_dir = parent_dir
        self.size = size
        self.text = text

    @property
    def path(self):
        return os.path.normpath(os.path.join(self.parent_dir, self.name))

    @path.setter
    def path(self, value):
        self.parent_dir = os.path.dirname(value)
        self.name = os.path.basename(value)
    
    def create(self, path=None):
        MAX_TEST_FILE_SIZE = 10 * 1024 * 1024
        encoding = 'UTF-8'
        path = path if path != None else self.path
        text = self.text if self.text != None else ''
        if self.size != None:
            if self.size > MAX_TEST_FILE_SIZE:
                raise ValueError
            text_bytes = bytes(text, encoding=encoding)
            with open(path, 'wb') as f:
                f.write(text_bytes)
                if self.size > len(text_bytes):
                    f.seek(self.size - 1)
                    f.write('\0'.encode(encoding))
        else:
            with open(path, 'w', encoding=encoding) as f:
                f.write(text)


class TestDir:

    def __init__(self, name=None, parent_dir=None, path=None):
        if path:
            if name or parent_dir:
                raise RuntimeError
            self.path = path
        else:
            self.name = name
            self.parent_dir = parent_dir

    @property
    def path(self):
        return os.path.normpath(os.path.join(self.parent_dir, self.name))

    @path.setter
    def path(self, value):
        self.parent_dir = os.path.dirname(value)
        self.name = os.path.basename(value)

    def create(self, path=None):
        path = path if path != None else self.path
        os.makedirs(path)

class FSDef:

    def __init__(self, base_path, fsdef_dict):
        """FSDef: Define nested directories and files as a dict:\n
            FSDef(..., fsdef_dict={
                'fileA.txt': 'fileA text'
                'dirA': {
                    'fileB.dat': 'fileB text'
                    'dirB': {},
                    'dirC': {
                        'fileC.txt': 'fileC text'
                    }
                },
                'dirD': {
                    'fileD.txt',
                    'fileE.dat'
                },
                'fileX.txt': 'abc', # File with contents 'abc'
                'fileY.txt': '',    # Empty file
                'fileZ.txt': None,  # Empty file
                'dirX': {},         # Empty directory
                'dirY': None        # Incorrect! This will be a file, not an empty directory
                'dirZ': {           # Any other Iterable[str] makes a directory of only empty files
                    'file1.txt',
                    'file2.txt'
                }
            })"""
        self.files = {} # path -> TestFile
        self.dirs = {} # path -> TestDir
        self.base_path = base_path
        self.unpack_fsdef_dict(base_path, fsdef_dict)
        
        # Remove Duplicates
        to_remove = set()
        for l in self.dirs.keys():
            for r in self.dirs.keys():
                if l != r and l.startswith(r):
                    to_remove.add(r)
        for path in to_remove:
            del self.dirs[path]

    def add_file(self, name, parent_dir, test_file):
        test_file.name = name
        test_file.parent_dir = parent_dir
        path = test_file.path
        self.files[path] = test_file

    def add_dir(self, name, parent_dir, test_dir):
        test_dir.name = name
        test_dir.parent_dir = parent_dir
        path = test_dir.path
        self.dirs[path] = test_dir

    def unpack_fsdef_dict(self, root, fsdef_dict) -> list[str]:
        for k, v in fsdef_dict.items():
            if root:
                current = os.path.normpath(os.path.join(root, k))
            else:
                current = os.path.normpath(k)
            if v == None:
                self.add_file(k, root, TestFile(text=''))
            elif isinstance(v, str):
                self.add_file(k, root, TestFile(text=v))
            elif isinstance(v, dict):
                self.add_dir(k, root, TestDir())
                self.unpack_fsdef_dict(current, v)
            elif isinstance(v, TestFile):
                self.add_file(k, root, v)
            elif isinstance(v, TestDir):
                self.add_dir(k, root, v)
            elif isinstance(v, Iterable):
                for el in v:
                    if isinstance(el, str):
                        self.add_file(el, current, TestFile(text=el))
                    elif isinstance(el, TestFile):
                        self.add_file(el.name, current, el)
                    elif isinstance(el, TestDir):
                        self.add_dir(el.name, current, el)
                    else:
                        raise RuntimeError('bad fsdef_dict, Iterables must'
                            'consist of only (A) strings representing empty files,'
                            '(B) TestFiles, or (C) TestDirss')
            else:
                raise RuntimeError('bad fsdef_dict, entry of type \'' + str(type(v)) + '\' not supported')

    def create(self):
        if not os.path.exists(self.base_path):
            raise RuntimeError('base_path does not exist')
        if not os.path.isdir(self.base_path):
            raise RuntimeError('base_path not dir')
        for test_dir in self.dirs.values():
            path = test_dir.path
            if os.path.exists(path):
                raise RuntimeError('Path already exists', path)
            test_dir.create()
        
        for test_file in self.files.values():
            path = test_file.path
            if os.path.exists(path):
                raise RuntimeError('Path already exists', path)
            test_file.create()
        
    def assert_exists(self, testcase):
        for d in self.dirs.keys():
            testcase.assertTrue(os.path.isdir(d))
        for f in self.files.keys():
            testcase.assertTrue(os.path.isfile(f))
    
    def assert_filenames_match(self, testcase, archive_names):
        filenames = list(self.files.keys())
        fn_counts = {}
        for f in filenames:
            if not f in fn_counts:
                fn_counts[f] = 1
            else:
                fn_counts[f] += 1
        an_counts = {}
        for a in archive_names:
            if not a in an_counts:
                an_counts[a] = 1
            else:
                an_counts[a] += 1

        diff = set(filenames).symmetric_difference(archive_names)
        msg = ''.join((str(s) for s in (
            'Archived filenames do not match expected names.\n',
            '  Expected: ', filenames, '\n',
            '  Actual: ', archive_names, '\n',
            '  diff: ', diff
        )))
        testcase.assertTrue(len(diff) == 0, msg)
        testcase.assertTrue(len(fn_counts) == len(an_counts), 'Archived filenames do not match expected names.')
    
    def assert_files_match_zip(self, testcase, path, compare_file_contents=False):
        if compare_file_contents:
            raise NotImplementedError
        zfiles = []
        with zipfile.ZipFile(path, 'r') as zf:
            for zi in zf.infolist():
                if not zi.is_dir():
                    zfiles.append(os.path.normpath(zi.filename))
        self.assert_filenames_match(testcase, zfiles)

    def assert_files_match_7z(self, testcase:unittest.TestCase, path, compare_file_contents=False):
        if compare_file_contents:
            raise NotImplementedError
        if not py7zr.is_7zfile(path):
            testcase.fail('Not a 7z file: {}'.format(path))
        archive_fileinfos = py7zr.SevenZipFile(path).list()
        archive_filenames = []
        for fi in archive_fileinfos:
            if not fi.is_directory:
                archive_filenames.append(os.path.normpath(fi.filename))
        self.assert_filenames_match(testcase, archive_filenames)
