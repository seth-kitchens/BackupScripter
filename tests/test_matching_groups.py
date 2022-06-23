import sys
import unittest
import os
import copy
from bs import create
from bs import g
from bs.fs.matching_group import MatchingGroup
from tests.test_core import *

class TestMatchingGroupsExclude(unittest.TestCase):
    def _test_matching_groups(self, fsdef_before, fsdef_zipped, included_relpaths, mgs_data, compare_file_contents=False):
        clear_fio()
        
        fsdef_before.create()
        fsdef_before.assert_exists(self)

        sd = make_sd(
            script_filename=['test_script', '.pyz'],
            backup_filename=['test_backup', '.zip'],
            script_dest_rel='',
            backup_filename_date='',
            backup_dest_rel='',
            archive_format='zip',
            included_items=[fio_relpath(ir) for ir in included_relpaths],
            matching_groups=mgs_data
        )

        create._create_script(sd)
        self.assertTrue(os.path.exists(fio_relpath('test_script.pyz')))
        self.assertFalse(os.path.exists(fio_relpath('test_backup.zip')))

        command = sys.executable + ' ' + fio_relpath('test_script.pyz') + ' ' + g.flags.NOINPUT
        os.system(command)

        fsdef_before.assert_exists(self)
        self.assertTrue(os.path.exists(fio_relpath('test_backup.zip')))

        fsdef_zipped.assert_files_match_zip(self, fio_relpath('test_backup.zip'), compare_file_contents=compare_file_contents)

        clear_fio()
    
    # Apply To

    # def test_apply_to_files(self):
    #     pass

    # def test_apply_to_folders(self):
    #     pass

    def test_apply_to_files_within_size(self):
        fsdef_before = FSDef(fio_path, fsdef_dict={
            'A': {
                'a.dat': TestFile(size=500),
                'b.dat': TestFile(size=1000),
                'c.dat': TestFile(size=2000)
            }
        })
        mg = MatchingGroup()
        mg.d.ie_action = 'exclude'
        mg.d.apply_to_files = True
        mg.d.apply_to_folders = False

        def _test_within_size(min, max, fsdef_zipped):
            mg.d.min_file_size = min
            mg.d.max_file_size = max
            mgs_data = {}
            mgs_data['a'] = mg.to_dict()
            included_relpaths = ['A']
            self._test_matching_groups(fsdef_before, fsdef_zipped, included_relpaths, mgs_data)

        fsdef_zipped_1 = FSDef('test_backup', fsdef_dict={
            'A': {
                'b.dat': None,
                'c.dat': None
            }
        })
        _test_within_size(None, 600, fsdef_zipped_1)
        
        fsdef_zipped_2 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.dat': None,
                'c.dat': None
            }
        })
        _test_within_size(900, 1100, fsdef_zipped_2)

        fsdef_zipped_3 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.dat': None,
                'b.dat': None
            }
        })
        _test_within_size(1900, None, fsdef_zipped_3)

    def test_apply_to_folders_within_size(self):
        fsdef_before = FSDef(fio_path, fsdef_dict={
            'A': {
                'a1.dat': TestFile(size=100),
                'a2.dat': TestFile(size=200)
            },
            'B': {
                'a1.dat': TestFile(size=1000),
                'a2.dat': TestFile(size=2000)
            },
            'C': {
                'c1.dat': TestFile(size=10000),
                'c2.dat': TestFile(size=20000)
            }
        })
        mg = MatchingGroup()
        mg.d.ie_action = 'exclude'
        mg.d.apply_to_files = False
        mg.d.apply_to_folders = True

        def _test_within_size(min, max, fsdef_zipped):
            mg.d.min_folder_size = min
            mg.d.max_folder_size = max
            mg.d.within_paths = [fio_relpath(x) for x in ['A', 'B', 'C']]
            mgs_data = {}
            mgs_data['a'] = mg.to_dict()
            included_relpaths = ['A', 'B', 'C']
            self._test_matching_groups(fsdef_before, fsdef_zipped, included_relpaths, mgs_data)

        fsdef_zipped_1 = FSDef('test_backup', fsdef_dict={
            'B': {
                'a1.dat': '',
                'a2.dat': ''
            },
            'C': {
                'c1.dat': '',
                'c2.dat': ''
            }
        })
        _test_within_size(None, 400, fsdef_zipped_1)
        
        fsdef_zipped_2 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a1.dat': '',
                'a2.dat': ''
            },
            'C': {
                'c1.dat': '',
                'c2.dat': ''
            }
        })
        _test_within_size(2900, 3100, fsdef_zipped_2)

        fsdef_zipped_3 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a1.dat': '',
                'a2.dat': ''
            },
            'B': {
                'a1.dat': '',
                'a2.dat': ''
            }
        })
        _test_within_size(29000, None, fsdef_zipped_3)

    # Apply If

    def test_apply_if_within_paths(self):
        fsdef_before = FSDef(fio_path, fsdef_dict={
            'A': {
                'a.txt': '',
                'a.dat': ''
            },
            'B': {
                'b.txt': '',
                'b.dat': ''
            },
            'C': {
                'c.txt': '',
                'c.dat': ''
            }
        })
        mgs_data = {}
        mg = MatchingGroup()
        mg.d.ie_action = 'exclude'
        mg.d.apply_to_files = True
        mg.d.apply_to_folders = False
        mg.d.apply_if_extensions = ['dat']

        fsdef_zipped_1 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.txt': ''
            },
            'B': {
                'b.txt': '',
                'b.dat': ''
            },
            'C': {
                'c.txt': ''
            }
        })
        mg.d.within_paths = [fio_relpath('A'), fio_relpath('C')]
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A', 'B', 'C']
        self._test_matching_groups(fsdef_before, fsdef_zipped_1, included_relpaths, mgs_data)

        fsdef_zipped_2 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.txt': '',
                'a.dat': ''
            },
            'B': {
                'b.txt': ''
            },
            'C': {
                'c.txt': '',
                'c.dat': ''
            }
        })
        mg.d.within_paths = [fio_relpath('B')]
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A', 'B', 'C']
        self._test_matching_groups(fsdef_before, fsdef_zipped_2, included_relpaths, mgs_data)

        fsdef_zipped_3 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.txt': ''
            },
            'B': {
                'b.txt': ''
            },
            'C': {
                'c.txt': ''
            }
        })
        mg.d.within_paths = []
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A', 'B', 'C']
        self._test_matching_groups(fsdef_before, fsdef_zipped_3, included_relpaths, mgs_data)

        fsdef_zipped_4 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.txt': ''
            },
            'B': {
                'b.txt': ''
            },
            'C': {
                'c.txt': ''
            }
        })
        mg.d.within_paths = [fio_path]
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A', 'B', 'C']
        self._test_matching_groups(fsdef_before, fsdef_zipped_4, included_relpaths, mgs_data)

        fsdef_zipped_5 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.txt': ''
            },
            'B': {
                'b.txt': ''
            },
            'C': {
                'c.txt': ''
            }
        })
        mg.d.within_paths = [os.path.dirname(fio_path)]
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A', 'B', 'C']
        self._test_matching_groups(fsdef_before, fsdef_zipped_5, included_relpaths, mgs_data)

    def test_apply_if_not_within_paths(self):
        fsdef_before = FSDef(fio_path, fsdef_dict={
            'A': {
                'a.txt': '',
                'a.dat': ''
            },
            'B': {
                'b.txt': '',
                'b.dat': ''
            },
            'C': {
                'c.txt': '',
                'c.dat': ''
            }
        })
        mgs_data = {}
        mg = MatchingGroup()
        mg.d.ie_action = 'exclude'
        mg.d.apply_to_files = True
        mg.d.apply_to_folders = False
        mg.d.apply_if_extensions = ['dat']

        fsdef_zipped_1 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.txt': ''
            },
            'B': {
                'b.txt': '',
                'b.dat': ''
            },
            'C': {
                'c.txt': ''
            }
        })
        mg.d.not_within_paths = [fio_relpath('B')]
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A', 'B', 'C']
        self._test_matching_groups(fsdef_before, fsdef_zipped_1, included_relpaths, mgs_data)

        fsdef_zipped_2 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.txt': '',
                'a.dat': ''
            },
            'B': {
                'b.txt': ''
            },
            'C': {
                'c.txt': '',
                'c.dat': ''
            }
        })
        mg.d.not_within_paths = [fio_relpath(x) for x in ['A', 'C']]
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A', 'B', 'C']
        self._test_matching_groups(fsdef_before, fsdef_zipped_2, included_relpaths, mgs_data)

        fsdef_zipped_3 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.txt': ''
            },
            'B': {
                'b.txt': ''
            },
            'C': {
                'c.txt': ''
            }
        })
        mg.d.not_within_paths = []
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A', 'B', 'C']
        self._test_matching_groups(fsdef_before, fsdef_zipped_3, included_relpaths, mgs_data)

        fsdef_zipped_4 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.txt': '',
                'a.dat': '',
            },
            'B': {
                'b.txt': '',
                'b.dat': ''
            },
            'C': {
                'c.txt': '',
                'c.dat': ''
            }
        })
        mg.d.not_within_paths = [fio_path]
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A', 'B', 'C']
        self._test_matching_groups(fsdef_before, fsdef_zipped_4, included_relpaths, mgs_data)

        fsdef_zipped_5 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.txt': '',
                'a.dat': '',
            },
            'B': {
                'b.txt': '',
                'b.dat': ''
            },
            'C': {
                'c.txt': '',
                'c.dat': ''
            }
        })
        mg.d.not_within_paths = [os.path.dirname(fio_path)]
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A', 'B', 'C']
        self._test_matching_groups(fsdef_before, fsdef_zipped_5, included_relpaths, mgs_data)

    def test_apply_if_has_extensions(self):
        fsdef_before = FSDef(fio_path, fsdef_dict={
            'A': {
                'a.txt': '',
                'a.dat': '',
                'a.data': '',
                'a.dat.temp': ''
            }
        })
        fsdef_zipped = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.txt': '',
                'a.data': '',
                'a.dat.temp': ''
            }
        })
        mgs_data = {}
        mg = MatchingGroup()
        mg.d.ie_action = 'exclude'
        mg.d.apply_to_files = True
        mg.d.apply_if_extensions = ['dat']
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped, included_relpaths, mgs_data)
    
    def test_apply_if_does_not_have_extensions(self):
        fsdef_before = FSDef(fio_path, fsdef_dict={
            'A': {
                'a.txt': '',
                'a.dat': '',
                'a.data': '',
                'a.dat.temp': ''
            }
        })
        fsdef_zipped = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.dat': ''
            }
        })
        mgs_data = {}
        mg = MatchingGroup()
        mg.d.ie_action = 'exclude'
        mg.d.apply_to_files = True
        mg.d.do_not_apply_if_extensions = ['dat']
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped, included_relpaths, mgs_data)

    def test_apply_if_parent_folder_size(self):
        fsdef_before = FSDef(fio_path, fsdef_dict={
            'A': {
                'a.txt': TestFile(size=300),
                'a.dat': TestFile(size=300),
                'a_small.dat': TestFile(size=10)
            },
            'B': {
                'b.txt': TestFile(size=300),
                'b.dat': TestFile(size=300),
                'b_big.dat': TestFile(size=5000)
            }
        })
        mgs_data = {}
        mg = MatchingGroup()
        mg.d.ie_action = 'exclude'
        mg.d.apply_to_files = True
        mg.d.apply_if_extensions = ['dat']

        fsdef_zipped_1 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.txt': TestFile(size=300),
                'a.dat': TestFile(size=300),
                'a_small.dat': TestFile(size=10)
            },
            'B': {
                'b.txt': TestFile(size=300)
            }
        })
        mg.d.min_parent_folder_size = 1000
        mg.d.max_parent_folder_size = None
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A', 'B']
        self._test_matching_groups(fsdef_before, fsdef_zipped_1, included_relpaths, mgs_data)

        fsdef_zipped_2 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.txt': TestFile(size=300)
            },
            'B': {
                'b.txt': TestFile(size=300),
                'b.dat': TestFile(size=300),
                'b_big.dat': TestFile(size=5000)
            }
        })
        mg.d.min_parent_folder_size = None
        mg.d.max_parent_folder_size = 1000
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A', 'B']
        self._test_matching_groups(fsdef_before, fsdef_zipped_2, included_relpaths, mgs_data)

    # Apply Group If

    def test_apply_group_if_backup_size_before(self):
        fsdef_before = FSDef(fio_path, fsdef_dict={
            'A': {
                'a.txt': TestFile(size=100),
                'a.dat': TestFile(size=100),
                'b.txt': TestFile(size=100),
                'b.dat': TestFile(size=100),
                'c.txt': TestFile(size=100),
                'c.dat': TestFile(size=100)
            }
        })
        mgs_data = {}
        mg = MatchingGroup()
        mg.d.ie_action = 'exclude'
        mg.d.apply_to_files = True
        mg.d.strip_extensions = True
        mg1 = copy.deepcopy(mg)
        mg2 = copy.deepcopy(mg)
        mg1.d.patterns = ['a']
        mg2.d.patterns = ['b']

        fsdef_zipped_1 = FSDef('test_backup', fsdef_dict={
            'A': {
                'b.txt': '',
                'b.dat': '',
                'c.txt': '',
                'c.dat': ''
            }
        })
        mg1.d.min_backup_size_before = 500
        mg1.d.max_backup_size_before = None
        mg2.d.min_backup_size_before = 500
        mg2.d.max_backup_size_before = None
        mgs_data['1'] = mg1.to_dict()
        mgs_data['2'] = mg2.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_1, included_relpaths, mgs_data)

        fsdef_zipped_2 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.txt': '',
                'a.dat': '',
                'c.txt': '',
                'c.dat': ''
            }
        })
        mg1.d.min_backup_size_before = 700
        mg1.d.max_backup_size_before = None
        mg2.d.min_backup_size_before = None
        mg2.d.max_backup_size_before = 700
        mgs_data['1'] = mg1.to_dict()
        mgs_data['2'] = mg2.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_2, included_relpaths, mgs_data)

    def test_apply_group_if_backup_size_after(self):
        fsdef_before = FSDef(fio_path, fsdef_dict={
            'A': {
                'a.txt': TestFile(size=100),
                'a.dat': TestFile(size=100),
                'b.txt': TestFile(size=100),
                'b.dat': TestFile(size=100),
                'c.txt': TestFile(size=100),
                'c.dat': TestFile(size=100)
            }
        })
        mgs_data = {}
        mg = MatchingGroup()
        mg.d.ie_action = 'exclude'
        mg.d.apply_to_files = True
        mg.d.strip_extensions = True
        mg1 = copy.deepcopy(mg)
        mg2 = copy.deepcopy(mg)
        mg1.d.patterns = ['a']
        mg2.d.patterns = ['b']

        fsdef_zipped_1 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.txt': '',
                'a.dat': '',
                'c.txt': '',
                'c.dat': ''
            }
        })
        mg1.d.min_backup_size_after = 500
        mg1.d.max_backup_size_after = None
        mg2.d.min_backup_size_after = 300
        mg2.d.max_backup_size_after = None
        mgs_data['1'] = mg1.to_dict()
        mgs_data['2'] = mg2.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_1, included_relpaths, mgs_data)

        fsdef_zipped_2 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.txt': '',
                'a.dat': '',
                'c.txt': '',
                'c.dat': ''
            }
        })
        mg1.d.min_backup_size_after = None
        mg1.d.max_backup_size_after = 300
        mg2.d.min_backup_size_after = None
        mg2.d.max_backup_size_after = 500
        mgs_data['1'] = mg1.to_dict()
        mgs_data['2'] = mg2.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_2, included_relpaths, mgs_data)

    def test_apply_group_if_total_size_diff(self):
        fsdef_before = FSDef(fio_path, fsdef_dict={
            'A': {
                'a.txt': TestFile(size=100),
                'a.dat': TestFile(size=200),
                'b.txt': TestFile(size=1000),
                'b.dat': TestFile(size=2000),
                'c.txt': TestFile(size=10000),
                'c.dat': TestFile(size=20000)
            }
        })
        mgs_data = {}
        mg = MatchingGroup()
        mg.d.ie_action = 'exclude'
        mg.d.apply_to_files = True
        mg.d.strip_extensions = True

        fsdef_zipped_1 = FSDef('test_backup', fsdef_dict={
            'A': {
                'b.txt': '',
                'b.dat': '',
                'c.txt': '',
                'c.dat': ''
            }
        })
        mg.d.patterns = ['a']
        mg.d.min_total_size_diff = 200
        mg.d.max_total_size_diff = 400
        mgs_data['1'] = mg.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_1, included_relpaths, mgs_data)

        fsdef_zipped_2 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.txt': '',
                'a.dat': '',
                'b.txt': '',
                'b.dat': '',
                'c.txt': '',
                'c.dat': ''
            }
        })
        mg.d.patterns = ['b']
        mg.d.min_total_size_diff = None
        mg.d.max_total_size_diff = 2900
        mgs_data['1'] = mg.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_2, included_relpaths, mgs_data)

        fsdef_zipped_3 = FSDef('test_backup', fsdef_dict={
            'A': {
                'a.txt': '',
                'a.dat': '',
                'b.txt': '',
                'b.dat': ''
            }
        })
        mg.d.patterns = ['c']
        mg.d.min_total_size_diff = 29000
        mg.d.max_total_size_diff = None
        mgs_data['1'] = mg.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_3, included_relpaths, mgs_data)

    # Pattern Options

    def test_strip_extensions(self):
        fsdef_before = FSDef(fio_path, fsdef_dict={
            'A': {
                'aaa.txt': '',
                'abc.dat': '',
                'acd.data': '',
                'ade.dat.temp': '',
                'dat.dat': ''
            }
        })

        mgs_data = {}
        mg = MatchingGroup()
        mg.d.ie_action = 'exclude'
        mg.d.apply_to_files = True

        fsdef_zipped_1 = FSDef('test_backup', fsdef_dict={
            'A': {
                'aaa.txt': '',
                'abc.dat': '',
                'acd.data': '',
                'ade.dat.temp': ''
            }
        })
        mg.d.strip_extensions = True
        mg.d.patterns = ['dat']
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_1, included_relpaths, mgs_data)

        fsdef_zipped_2 = FSDef('test_backup', fsdef_dict={
            'A': {
                'aaa.txt': '',
                'abc.dat': ''
            }
        })
        mg.d.strip_extensions = True
        mg.d.patterns = ['d']
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_2, included_relpaths, mgs_data)

        fsdef_zipped_3 = FSDef('test_backup', fsdef_dict={
            'A': {
                'aaa.txt': '',
                'abc.dat': '',
                'acd.data': '',
                'ade.dat.temp': '',
                'dat.dat': ''
            }
        })
        mg.d.strip_extensions = True
        mg.d.patterns = ['txt']
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_3, included_relpaths, mgs_data)

        fsdef_zipped_4 = FSDef('test_backup', fsdef_dict={
            'A': {
                'aaa.txt': ''
            }
        })
        mg.d.strip_extensions = False
        mg.d.patterns = ['dat']
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_4, included_relpaths, mgs_data)

    def test_match_whole_name(self):
        fsdef_before = FSDef(fio_path, fsdef_dict={
            'A': {
                'aaa.txt': '',
                'abc.dat': '',
                'acd.data': '',
                'ade.dat.temp': '',
                'dat.dat': ''
            }
        })

        mgs_data = {}
        mg = MatchingGroup()
        mg.d.ie_action = 'exclude'
        mg.d.apply_to_files = True

        fsdef_zipped_1 = FSDef('test_backup', fsdef_dict={
            'A': {
                'abc.dat': '',
                'acd.data': '',
                'ade.dat.temp': '',
                'dat.dat': ''
            }
        })
        mg.d.strip_extensions = False
        mg.d.whole_name = True
        mg.d.use_regex = False
        mg.d.patterns = ['aaa.txt']
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_1, included_relpaths, mgs_data)

        fsdef_zipped_2 = FSDef('test_backup', fsdef_dict={
            'A': {
                'aaa.txt': '',
                'abc.dat': '',
                'acd.data': '',
                'ade.dat.temp': '',
                'dat.dat': ''
            }
        })
        mg.d.strip_extensions = True
        mg.d.whole_name = True
        mg.d.use_regex = False
        mg.d.patterns = ['a']
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_2, included_relpaths, mgs_data)

        fsdef_zipped_3 = FSDef('test_backup', fsdef_dict={
            'A': {
                'dat.dat': ''
            }
        })
        mg.d.strip_extensions = True
        mg.d.whole_name = True
        mg.d.use_regex = True
        mg.d.patterns = ['a..']
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_3, included_relpaths, mgs_data)

    def test_match_case(self):
        fsdef_before = FSDef(fio_path, fsdef_dict={
            'A': {
                'abc1.dat': '',
                'ABC2.dat': '',
                'Abc3.dat': '',
                'x.dat': ''
            }
        })

        mgs_data = {}
        mg = MatchingGroup()
        mg.d.ie_action = 'exclude'
        mg.d.apply_to_files = True

        fsdef_zipped_1 = FSDef('test_backup', fsdef_dict={
            'A': {
                'x.dat': ''
            }
        })
        mg.d.strip_extensions = True
        mg.d.match_case = False
        mg.d.patterns = ['abc']
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_1, included_relpaths, mgs_data)

        fsdef_zipped_2 = FSDef('test_backup', fsdef_dict={
            'A': {
                'ABC2.dat': '',
                'Abc3.dat': '',
                'x.dat': ''
            }
        })
        mg.d.strip_extensions = True
        mg.d.match_case = True
        mg.d.patterns = ['abc']
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_2, included_relpaths, mgs_data)

        fsdef_zipped_3 = FSDef('test_backup', fsdef_dict={
            'A': {
                'abc1.dat': '',
                'x.dat': ''
            }
        })
        mg.d.strip_extensions = True
        mg.d.match_case = True
        mg.d.patterns = ['A']
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_3, included_relpaths, mgs_data)

    def test_use_regex(self):
        fsdef_before = FSDef(fio_path, fsdef_dict={
            'A': {
                'a.c.dat': '',
                'abc.dat': '',
                'x.dat': ''
            }
        })

        mgs_data = {}
        mg = MatchingGroup()
        mg.d.ie_action = 'exclude'
        mg.d.apply_to_files = True
        mg.d.strip_extensions = False

        fsdef_zipped_1 = FSDef('test_backup', fsdef_dict={
            'A': {
                'abc.dat': '',
                'x.dat': ''
            }
        })
        mg.d.use_regex = False
        mg.d.patterns = ['a.c']
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_1, included_relpaths, mgs_data)

        fsdef_zipped_2 = FSDef('test_backup', fsdef_dict={
            'A': {
                'x.dat': ''
            }
        })
        mg.d.use_regex = True
        mg.d.patterns = ['a.c']
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_2, included_relpaths, mgs_data)

    def test_match_all(self):
        fsdef_before = FSDef(fio_path, fsdef_dict={
            'A': {
                'abc1.dat': '',
                'abc2.dat': '',
                'x.txt': ''
            }
        })

        mgs_data = {}
        mg = MatchingGroup()
        mg.d.ie_action = 'exclude'
        mg.d.apply_to_files = True

        fsdef_zipped_1 = FSDef('test_backup', fsdef_dict={
            'A': {
                'x.txt': ''
            }
        })
        mg.d.match_all = True
        mg.d.patterns = ['a', 'b']
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_1, included_relpaths, mgs_data)

        fsdef_zipped_2 = FSDef('test_backup', fsdef_dict={
            'A': {
                'x.txt': ''
            }
        })
        mg.d.match_all = False
        mg.d.patterns = ['a', '1']
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_2, included_relpaths, mgs_data)

        fsdef_zipped_3 = FSDef('test_backup', fsdef_dict={
            'A': {
                'abc2.dat': '',
                'x.txt': ''
            }
        })
        mg.d.match_all = True
        mg.d.patterns = ['a', '1']
        mgs_data['a'] = mg.to_dict()
        included_relpaths = ['A']
        self._test_matching_groups(fsdef_before, fsdef_zipped_3, included_relpaths, mgs_data)

