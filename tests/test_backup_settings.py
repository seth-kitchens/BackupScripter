import re
import time
import sys
import os
import unittest
from datetime import datetime
from tests.test_core import *
from src.gp import DateString
from src.bs import create
from src.bs import g

def listdir_match(dirpath, pattern):
    if not os.path.isdir(dirpath):
        return []
    files = os.listdir(dirpath)
    matched = []
    for file in files:
        if re.search(pattern, file):
            matched.append(file)
    return matched

def assert_n_files_in_dir(testcase:unittest.TestCase, n, dirpath, pattern):
    testcase.assertTrue(os.path.isdir(dirpath))
    count = len(listdir_match(dirpath, pattern))
    fail_msg = 'Unexpected number of files.\n  Expected: ' + str(n) + '\n  Actual: ' + str(count)
    testcase.assertTrue(n == count, fail_msg)

def assert_exists_match(testcase, parentdir, pattern):
    testcase.assertTrue(len(listdir_match(parentdir, pattern) > 0))

def wait_n_secs_passed(n=1, prev_second=0):
    """Waits until at least two seconds has passed since timestamp given as prev_second.
    Returns new timestamp. Returns immediately if time given is 0 or None"""
    if not prev_second or prev_second < 0:
        return int(time.time())
    next_second = int(time.time())
    while next_second <= prev_second + n:
        time.sleep(0.01)
        next_second = int(time.time())
    return next_second

def find_most_recent_backup(date_string):
    files = [f for f in os.listdir(fio_path) if f.startswith('test_backup') and f.endswith('.zip')]
    most_recent = None
    most_recent_timestamp = None
    for f in files:
        timestamp = DateString.extract_timestamp(date_string, f)
        if most_recent_timestamp == None or timestamp > most_recent_timestamp:
            most_recent_timestamp = timestamp
            most_recent = f
    return fio_relpath(most_recent)

def set_most_recent_backup_date(date_string, timestamp):
    dt = datetime.fromtimestamp(timestamp)
    most_recent = find_most_recent_backup(date_string)
    parentdir = os.path.dirname(most_recent)
    basename = os.path.basename(most_recent)
    name, postfix, ext = DateString.split(date_string, basename)
    new_postfix = DateString.process(date_string, dt)
    new_path = os.path.normpath(os.path.join(parentdir, name + new_postfix + ext))
    os.rename(most_recent, new_path)

class TestBackupSettings(TestCaseBS):
    def test_max_backups(self):
        clear_fio()

        # make script, run enough to trigger max backups

        fsdef_before = FSDef(fio_path, {
            'A': {
                'a.dat': '',
                'b.dat': ''
            },
            'B': {
                'c.dat': ''
            }
        })

        fsdef_before.create()
        fsdef_before.assert_exists(self)

        date_string = '_UU'

        sd = make_sd(
            script_filename=['test_script', '.pyz'],
            backup_filename=['test_backup', '.zip'],
            backup_filename_date=date_string,
            script_dest_rel='',
            backup_dest_rel='',
            archive_format='zip',
            included_items=[fio_relpath('A')],
            max_backups=3,
            pull_age_from_postfix=True
        )

        create._create_script(sd)
        self.assertTrue(os.path.exists(fio_relpath('test_script.pyz')))
        self.assertFalse(os.path.exists(fio_relpath('test_backup.zip')))

        command_run_backup = sys.executable + ' ' + fio_relpath('test_script.pyz') + ' ' + g.flags.NOINPUT
        run_backup = lambda : os.system(command_run_backup)
        backup_pattern = 'test_backup_[0-9]+\\.zip'
            
        t = time.time()
        
        assert_n_files_in_dir(self, 0, fio_path, backup_pattern)

        run_backup()
        assert_n_files_in_dir(self, 1, fio_path, backup_pattern)
        set_most_recent_backup_date(date_string, t - 2)

        run_backup()
        assert_n_files_in_dir(self, 2, fio_path, backup_pattern)
        set_most_recent_backup_date(date_string, t - 4)

        run_backup()
        assert_n_files_in_dir(self, 3, fio_path, backup_pattern)
        set_most_recent_backup_date(date_string, t - 6)

        run_backup()
        assert_n_files_in_dir(self, 3, fio_path, backup_pattern)

        clear_fio()

    def test_old_age(self):
        clear_fio()

        # make script, run enough to trigger max backups

        fsdef_before = FSDef(fio_path, {
            'A': {
                'a.dat': '',
                'b.dat': ''
            },
            'B': {
                'c.dat': ''
            }
        })

        fsdef_before.create()
        fsdef_before.assert_exists(self)

        date_string = '_UU'

        sd = make_sd(
            script_filename=['test_script', '.pyz'],
            backup_filename=['test_backup', '.zip'],
            backup_filename_date=date_string,
            script_dest_rel='',
            backup_dest_rel='',
            archive_format='zip',
            included_items=[fio_relpath('A')],
            max_backups=1,
            backup_old_age_secs=1000,
            pull_age_from_postfix=True
        )

        create._create_script(sd)
        self.assertTrue(os.path.exists(fio_relpath('test_script.pyz')))
        self.assertFalse(os.path.exists(fio_relpath('test_backup.zip')))

        command_run_backup = sys.executable + ' ' + fio_relpath('test_script.pyz') + ' ' + g.flags.NOINPUT
        run_backup = lambda : os.system(command_run_backup)
        backup_pattern = 'test_backup_[0-9]+\\.zip'

        t = time.time()
        
        assert_n_files_in_dir(self, 0, fio_path, backup_pattern)

        run_backup()
        assert_n_files_in_dir(self, 1, fio_path, backup_pattern)
        set_most_recent_backup_date(date_string, t - 500)

        run_backup()
        assert_n_files_in_dir(self, 1, fio_path, backup_pattern)
        set_most_recent_backup_date(date_string, t - 1005)

        run_backup()
        assert_n_files_in_dir(self, 2, fio_path, backup_pattern)
        set_most_recent_backup_date(date_string, t - 900)

        run_backup()
        assert_n_files_in_dir(self, 2, fio_path, backup_pattern)

        clear_fio()

    def test_recent_age(self):

        # make script run backup, run enough to fill up to but not over max
        # set recent age, modify all but one of files to be out of recent age
        # run, expect overwrite of recent
        
        clear_fio()

        fsdef_before = FSDef(fio_path, {
            'A': {
                'a.dat': '',
                'b.dat': ''
            },
            'B': {
                'c.dat': ''
            }
        })

        fsdef_before.create()
        fsdef_before.assert_exists(self)

        date_string = '_UU'

        sd = make_sd(
            script_filename=['test_script', '.pyz'],
            backup_filename=['test_backup', '.zip'],
            backup_filename_date=date_string,
            script_dest_rel='',
            backup_dest_rel='',
            archive_format='zip',
            included_items=[fio_relpath('A')],
            max_backups=3,
            backup_recent_age_secs=1000,
            pull_age_from_postfix=True
        )

        create._create_script(sd)
        self.assertTrue(os.path.exists(fio_relpath('test_script.pyz')))
        self.assertFalse(os.path.exists(fio_relpath('test_backup.zip')))

        command_run_backup = sys.executable + ' ' + fio_relpath('test_script.pyz') + ' ' + g.flags.NOINPUT
        run_backup = lambda : os.system(command_run_backup)
        backup_pattern = 'test_backup_[0-9]+\\.zip'

        t = int(time.time())

        def assert_backup_of_time_exists(timestamp, fail_msg=None):
            postfix = DateString.process(date_string, datetime.fromtimestamp(timestamp))
            fn = 'test_backup' + postfix + '.zip'
            if fail_msg:
                self.assertTrue(os.path.isfile(fio_relpath(fn)), msg=fail_msg)
            else:
                self.assertTrue(os.path.isfile(fio_relpath(fn)))
        def assert_backup_times(timestamps):
            expected_reltimes = [('t - ' + str(t - int(ts))) for ts in timestamps]
            backup_files = listdir_match(fio_path, backup_pattern)
            backup_timestamps = [DateString.extract_timestamp(date_string, f) for f in backup_files]
            backup_reltimes = [('t - ' + str(t - int(ts))) for ts in backup_timestamps]
            fail_msg = '\n  Expected Times: ' + str(expected_reltimes) + '\n  Actual Times: ' + str(backup_reltimes)
            assert_n_files_in_dir(self, len(timestamps), fio_path, backup_pattern)
            for timestamp in timestamps:
                assert_backup_of_time_exists(timestamp, fail_msg)
        
        # Expect 0/3 backups
        assert_n_files_in_dir(self, 0, fio_path, backup_pattern)

        run_backup()
        set_most_recent_backup_date(date_string, t - 500)
        # Expect 1/3 backups, nothing overwritten
        assert_backup_times([t - 500])

        run_backup()
        set_most_recent_backup_date(date_string, t - 600)
        # Expect 2/3 backups, nothing overwritten
        assert_backup_times([t - 500, t - 600])

        run_backup()
        set_most_recent_backup_date(date_string, t - 1100)
        # Expect 3/3 backups, nothing overwritten
        assert_backup_times([t - 500, t - 600, t - 1100])

        run_backup()
        set_most_recent_backup_date(date_string, t - 900)
        # Expect 3/3 backups, oldest out of most recent overwritten
        assert_backup_times([t - 500, t - 900, t - 1100])

        set_most_recent_backup_date(date_string, t - 1200)
        set_most_recent_backup_date(date_string, t - 1300)
        assert_backup_times([t - 1100, t - 1200, t - 1300])

        run_backup()
        set_most_recent_backup_date(date_string, t - 100)
        # Expect 3/3 backups, oldest overwritten
        assert_backup_times([t - 100, t - 1100, t - 1200])

        clear_fio()

class TestCompressionSettings(TestCaseBS):
    def test_7z(self):
        clear_fio()

        fsdef_before = FSDef(fio_path, {
            'A': {
                'a.dat': '',
                'b.dat': ''
            },
            'B': {
                'c.dat': ''
            }
        })

        fsdef_before.create()
        fsdef_before.assert_exists(self)

        sd = make_sd(
            script_filename=['test_script', '.pyz'],
            backup_filename=['test_backup', '.7z'],
            backup_filename_date='',
            script_dest_rel='',
            backup_dest_rel='',
            archive_format='7z',
            archive_mode='compile',
            included_items=[fio_relpath('A')]
        )

        create._create_script(sd)
        self.assertTrue(os.path.exists(fio_relpath('test_script.pyz')))
        self.assertFalse(os.path.exists(fio_relpath('test_backup.7z')))
        
        command_run_backup = sys.executable + ' ' + fio_relpath('test_script.pyz') + ' ' + g.flags.NOINPUT

        os.system(command_run_backup)

        self.assertTrue(os.path.exists(fio_relpath('test_backup.7z')))
        fsdef_archived = FSDef('test_backup', {
            'A': {
                'a.dat': '',
                'b.dat': ''
            }
        })
        fsdef_archived.assert_files_match_7z(self, fio_relpath('test_backup.7z'))