import pytest
import ctypes
from wmempy.wmem_process import WinProc
from helpers import run_process, get_example_app, hand_example_app
# These tests are running on live memory (utilizing common Windows processes and example exes)
# These tests also test if your system can use the application (if your Windows is compatible)


def test_win_proc_basic_live(request, capsys):
    """Test basic WinProc functionality"""
    with pytest.raises(Exception):
        syst_proc = WinProc('System')
    proc, live_app = get_example_app(request)
    # Live memory start
    assert len(proc.modules) > 0
    assert len(proc.pages) > 0
    proc.print_process()
    captured = capsys.readouterr().out
    assert '.exe' in captured
    assert 'PID: ' in captured
    assert 'Handle: ' in captured
    proc.print_process_detailed()
    captured = capsys.readouterr().out
    assert '.exe' in captured
    assert 'PID: ' in captured
    captured_lower = captured.lower()
    assert 'windows' in captured_lower
    assert 'kernel32' in captured_lower
    assert 'system32' in captured_lower
    assert 'module list:' in captured_lower
    assert 'memory page list:' in captured_lower
    assert proc.get_handle() > 0
    # Live memory end
    hand_example_app(proc, live_app)

def test_win_proc_compare_live(request, capsys):
    """Test comparing of two WinProc processes"""
    proc, live_app = get_example_app(request, 'WMemPy_test_app.exe')
    proc_duplicate = WinProc('WMemPy_test_app.exe')
    # Live memory start
    assert len(proc.modules) > 0
    assert len(proc.pages) > 0
    assert proc.get_handle() > 0
    assert len(proc_duplicate.modules) > 0
    assert len(proc_duplicate.pages) > 0
    assert proc_duplicate.get_handle() > 0
    assert proc_duplicate.get_handle() != proc.get_handle()
    proc.compare(proc_duplicate)
    captured = capsys.readouterr().out
    assert 'WMemPy_test_app.exe' in captured
    assert '(0.00 %) different' in captured
    assert 'WMemPy_test_app.exe is 0' in captured
    # Live memory end
    hand_example_app(proc, live_app)
