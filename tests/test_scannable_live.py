import pytest
import ctypes
from helpers import run_process, get_example_app, hand_example_app
# These tests are running on live memory (utilizing common Windows processes and example exes)
# These tests also test if your system can use the application (if your Windows is compatible)


def test_proc_page_live(request):
    """Test whether ProcPage behaves correctly"""
    proc, live_app = get_example_app(request)
    # Live memory start
    pages = proc.pages
    for page in pages:
        bounds = page.get_bounds()
        page_memory = page.read()
        page_start = page.read_from(0)
        assert bounds[0] > 0
        assert bounds[1] > 0
        assert page_memory is None or len(page_memory) > 0
        assert page_start is None or len(page_start) > 0
        assert (page_memory is None and page_start is None) or (page_memory==page_start).all()
        if not page_memory is None:
            my_int = page.read_dtype(0, ctypes.c_uint8())
            assert my_int == page_memory[0]
    # Live memory end
    hand_example_app(proc, live_app)

def test_proc_module_live(request):
    """Test whether ProcModule behaves correctly"""
    proc, live_app = get_example_app(request)
    # Live memory start
    entry = [module for module in proc.modules if module.get_name().lower() == proc.proc_name.lower()][0]
    bounds = entry.get_bounds()
    page_memory = entry.read()
    page_start = entry.read_from(0)
    assert bounds[0] > 0
    assert bounds[1] > 0
    assert len(page_memory) > 0
    assert len(page_start) > 0
    assert (page_memory==page_start).all()
    my_int = entry.read_dtype(0, ctypes.c_uint8())
    assert my_int == page_memory[0]
    assert proc.proc_name.lower() in entry.path.lower()
    # Live memory end
    hand_example_app(proc, live_app)
