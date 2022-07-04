import unittest
import cProfile
import pstats
from pstats import SortKey

from . import test_core
from . import test_general
from . import test_matching_groups
from . import test_backup_settings

# Testing Options

# Profiling options
class prf:
    do_profile    = False
    results_file  = test_core.fio_relpath('profile_results.dat')
    sort          = SortKey.CUMULATIVE
    results_count = 50

test_modules = []
test_modules.append(test_core)
test_modules.append(test_general)
test_modules.append(test_matching_groups)
test_modules.append(test_backup_settings)



def run():
    suites = [unittest.findTestCases(tm) for tm in test_modules]
    suite = unittest.TestSuite(suites)
    test_runner = unittest.TextTestRunner(verbosity=2)
    if prf.do_profile:
        cProfile.runctx('test_runner.run(suite)', globals(), locals(), filename=prf.results_file)
        p = pstats.Stats(prf.results_file)
        p.strip_dirs().sort_stats(prf.sort).print_stats(prf.results_count)
    else:
        test_runner.run(suite)
