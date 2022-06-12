import unittest

from . import test_core
from . import test_large_scale
from . import test_matching_groups
from . import test_vfs
from . import test_backup_settings

def run():
    suites = []
    suites.append(unittest.findTestCases(test_core))
    suites.append(unittest.findTestCases(test_large_scale))
    suites.append(unittest.findTestCases(test_matching_groups))
    suites.append(unittest.findTestCases(test_backup_settings))
    suites.append(unittest.findTestCases(test_vfs))
    suite = unittest.TestSuite(suites)
    unittest.TextTestRunner(verbosity=2).run(suite)
