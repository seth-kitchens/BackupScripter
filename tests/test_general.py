import sys
import os
from src.bs import create
from src.bs.script_data import ScriptDataBS
from src.bs import g
from tests.test_core import *

class TestGeneral(TestCaseBS):
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

        command = '{} {} {}'.format(sys.executable, fio_relpath('test_script.pyz'), g.flags.NOINPUT)
        os.system(command)

        fsdef_to_backup.assert_exists(self)
        self.assertTrue(os.path.exists(fio_relpath('test_backup.zip')))

        clear_fio()
    
    def test_load_script(self):
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

        self.assertEqual(sd.ScriptFilename, ['test_script', '.pyz'])
        self.assertEqual(sd.BackupFilename, ['test_backup', '.zip'])
        self.assertEqual(sd.IncludedItems, [fio_relpath('A')])
        sd.ScriptFilename = ['A', 'B']
        sd.BackupFilename = ['C', 'D']
        sd.IncludedItems = None
        self.assertNotEqual(sd.ScriptFilename, ['test_script', '.pyz'])
        self.assertNotEqual(sd.BackupFilename, ['test_backup', '.zip'])
        self.assertNotEqual(sd.IncludedItems, [fio_relpath('A')])
        sd.load_pyz(fio_relpath('test_script.pyz'))
        self.assertNotEqual(sd.ScriptFilename, ['test_script', '.pyz'])
        self.assertEqual(sd.BackupFilename, ['test_backup', '.zip'])
        self.assertEqual(sd.IncludedItems, [fio_relpath('A')])

        clear_fio()