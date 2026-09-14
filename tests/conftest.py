import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from br_py_log_n_profile.do_log.log_it import configure

configure(break_on_not_tested=False)
