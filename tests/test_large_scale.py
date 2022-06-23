import sys
import os
from bs import create
from bs import g
from tests.test_core import *

class TestLargeScale(TestCaseBS):
    def test_helpers(self):
        clear_fio()
        self.assertTrue(os.path.exists(fio_path))
        self.assertTrue(os.listdir(fio_path) == [])
        os.mkdir(fio_relpath('test_dir'))
        self.assertTrue(os.path.isdir(os.path.normpath(os.path.join(fio_path, 'test_dir'))))
        clear_fio()
        self.assertTrue(os.path.exists(fio_path))
        self.assertTrue(os.listdir(fio_path) == [])

    def test_create_script(self):
        clear_fio()

        sd = make_sd(
            script_filename=['test_script', '.pyz'],
            backup_filename=['test_backup', '.zip'],
            script_dest_rel='',
            backup_filename_date='',
            backup_dest_rel='',
            archive_format='zip'
        )
        
        create._create_script(sd)
        self.assertTrue(os.path.exists(fio_relpath('test_script.pyz')))
        clear_fio()
    
    def test_create_run(self):
        clear_fio()
        
        fsdef_to_backup = FSDef(fio_path, fsdef_dict={
            'A': {
                'B': {
                    'BB': {
                        'a.txt': '',
                        'b.txt': '',
                        'c.txt': ''
                    }
                },
                'C': {
                    'CC': {
                        'd.txt': '',
                        'e.txt': ''
                    }
                }
            }
        })
        fsdef_to_backup.create()
        fsdef_to_backup.assert_exists(self)

        sd = make_sd(
            script_filename=['test_script', '.pyz'],
            backup_filename=['test_backup', '.zip'],
            script_dest_rel='',
            backup_filename_date='',
            backup_dest_rel='',
            archive_format='zip',
            included_items=[fio_relpath('A')]
        )

        create._create_script(sd)
        self.assertTrue(os.path.exists(fio_relpath('test_script.pyz')))
        self.assertFalse(os.path.exists(fio_relpath('test_backup.zip')))

        command = sys.executable + ' ' + fio_relpath('test_script.pyz') + ' ' + g.flags.NOINPUT
        os.system(command)

        fsdef_to_backup.assert_exists(self)
        self.assertTrue(os.path.exists(fio_relpath('test_backup.zip')))

        clear_fio()