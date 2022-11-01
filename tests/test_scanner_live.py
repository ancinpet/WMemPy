import pytest
from helpers import run_process, get_example_app, hand_example_app
# These tests are running on live memory (utilizing common Windows processes and example exes)
# These tests also test if your system can use the application (if your Windows is compatible)


def test_byte_scan_live(request):
    """Test whether byte scan can be performed"""
    proc, live_app = get_example_app(request)
    # Live memory start
    entry = [module for module in proc.modules if module.get_name().lower() == proc.proc_name.lower()][0]
    pattern = proc.scanner.array_from_pattern('55 8b ec 83 ec 40 53 56 57 8b 75 0c 8b 7d 08 8b', 16, ' ')
    result = proc.scanner.byte_scan(entry, pattern)
    assert result > 0
    pattern = proc.scanner.array_from_pattern('4c ce 08 0f 6f 54 ce 10 0f 6f 5c ce 18 0f 6f 64', 16, ' ')
    result = proc.scanner.byte_scan(entry, pattern)
    assert result > 0
    pattern = proc.scanner.array_from_pattern('4c ff 08 0f b0 aa bb cc ff ff 00 ff 00 00 ff 00', 16, ' ')
    result = proc.scanner.byte_scan(entry, pattern)
    assert result is None
    # Live memory end
    hand_example_app(proc, live_app)

def test_AOB_scans_live(request):
    """Test whether AOB_scan and AOB_scan_arr can be performed"""
    proc, live_app = get_example_app(request)
    # Live memory start
    entry = [module for module in proc.modules if module.get_name().lower() == proc.proc_name.lower()]
    # Array version
    result, _ = proc.scanner.AOB_scan_arr(entry, '55 8b ec 83 ec 40 53 56 57 8b 75 0c 8b 7d 08 8b')
    assert result > 0
    result, _ = proc.scanner.AOB_scan_arr(entry, '4c ce 08 0f 6f 54 ce 10 0f 6f 5c ce 18 0f 6f 64')
    assert result > 0
    result, _ = proc.scanner.AOB_scan_arr(entry, '4c ff 08 0f b0 aa bb cc ff ff 00 ff 00 00 ff 00')
    assert result is None
    # Single scannable version
    result = proc.scanner.AOB_scan(entry[0], '55 8b ec 83 ec 40 53 56 57 8b 75 0c 8b 7d 08 8b')
    assert result > 0
    result = proc.scanner.AOB_scan(entry[0], '4c ce 08 0f 6f 54 ce 10 0f 6f 5c ce 18 0f 6f 64')
    assert result > 0
    result = proc.scanner.AOB_scan(entry[0], '4c ff 08 0f b0 aa bb cc ff ff 00 ff 00 00 ff 00')
    assert result is None

    # Live memory end
    hand_example_app(proc, live_app)

def test_ASCII_scans_live(request):
    """Test whether ASCII_scan and ASCII_scan_arr can be performed"""
    proc, live_app = get_example_app(request)
    # Live memory start
    entry = [module for module in proc.modules if module.get_name().lower() == proc.proc_name.lower()]
    # Array version
    result, _ = proc.scanner.ASCII_scan_arr(entry, 'UI1874s41Q6w5s4')
    assert result > 0
    result, _ = proc.scanner.ASCII_scan_arr(entry, 'UI1874s41Q6w5s4')
    assert result > 0
    result, _ = proc.scanner.ASCII_scan_arr(entry, 'UIFFFFs0006wXX4')
    assert result is None
    # Single scannable version
    result = proc.scanner.ASCII_scan(entry[0], 'UI1874s41Q6w5s4')
    assert result > 0
    result = proc.scanner.ASCII_scan(entry[0], 'UI1874s41Q6w5s4')
    assert result > 0
    result = proc.scanner.ASCII_scan(entry[0], 'UIFFFFs0006wXX4')
    assert result is None

    # Live memory end
    hand_example_app(proc, live_app)

def test_ASCII_lists_live(request):
    """Test whether ASCII_list and ASCII_list_arr can be performed"""
    proc, live_app = get_example_app(request)
    # Live memory start
    entry = [module for module in proc.modules if module.get_name().lower() == proc.proc_name.lower()]
    # Array version
    result = proc.scanner.ASCII_list_arr(entry, False, 10)
    assert 'UI1874s41Q6w5s4' in result
    assert 'credentials' in result
    assert 'TerminateProcess' in result
    assert 'VirtualProtect' in result
    assert 'ExitThread' in result
    # Single scannable version
    result = proc.scanner.ASCII_list(entry[0], False, 10)
    assert 'UI1874s41Q6w5s4' in result
    assert 'credentials' in result
    assert 'TerminateProcess' in result
    assert 'VirtualProtect' in result
    assert 'ExitThread' in result
    # Live memory end
    hand_example_app(proc, live_app)
