import pytest
import ctypes
from click.testing import CliRunner
from helpers import run_process, get_example_app, hand_example_app
from wmempy.wmem_cli import *
# These tests are running on live memory (utilizing common Windows processes and example exes)
# These tests also test if your system can use the application (if your Windows is compatible)


def test_memory_view_live(request, capsys):
    """Test memory_view functionality"""
    proc, live_app = get_example_app(request, 'WMemPy_test_app.exe')
    # Live memory start
    memory_view(proc, ['WMemPy_test_app.exe', None, None])
    captured = capsys.readouterr().out
    assert 'vvvvvvvvvvvvvvvvvvv' in captured
    # Start of file
    assert '[4d 5a 90 00 03 00 00 00 04 00 00 00 ff ff 00 00]' in captured
    assert 'MZ..............' in captured
    # End of file or general padding
    assert '[00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00]' in captured
    assert '................' in captured
    assert '0x' in captured
    assert '[55 8b ec 83 ec 40 53 56 57 8b 75 0c 8b 7d 08 8b]' in captured
    assert '[4c ce 08 0f 6f 54 ce 10 0f 6f 5c ce 18 0f 6f 64]' in captured
    assert not '[4c ff 08 0f b0 aa bb cc ff ff 00 ff 00 00 ff 00]' in captured    
    memory_view(proc, ['WMemPy_test_app.exe', '10', None])
    captured = capsys.readouterr().out
    assert 'vvvvvvvvvvvvvvvvvvv' in captured
    # Start of file not present due to hint = 10
    assert not '[4d 5a 90 00 03 00 00 00 04 00 00 00 ff ff 00 00]' in captured
    assert not 'MZ..............' in captured
    # End of file or general padding
    assert '[00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00]' in captured
    assert '................' in captured
    assert '0x' in captured
    assert '[55 8b ec 83 ec 40 53 56 57 8b 75 0c 8b 7d 08 8b]' in captured
    assert '[4c ce 08 0f 6f 54 ce 10 0f 6f 5c ce 18 0f 6f 64]' in captured
    assert not '[4c ff 08 0f b0 aa bb cc ff ff 00 ff 00 00 ff 00]' in captured
    # Live memory end
    hand_example_app(proc, live_app)

def test_text_list_live(request, capsys):
    """Test text_list functionality"""
    proc, live_app = get_example_app(request, 'WMemPy_test_app.exe')
    # Live memory start
    text_list(proc, ['c10', 'WMemPy_test_app.exe', None])
    captured = capsys.readouterr().out
    assert 'TerminateProcess' in captured
    assert 'UI1874s41Q6w5s4' in captured
    assert 'VirtualProtect' in captured
    assert 'credentials' in captured
    text_list(proc, ['c12', 'WMemPy_test_app.exe', None])
    captured = capsys.readouterr().out
    assert 'TerminateProcess' in captured
    assert 'UI1874s41Q6w5s4' in captured
    assert 'VirtualProtect' in captured
    assert not 'credentials' in captured
    text_list(proc, ['s15', 'WMemPy_test_app.exe', None])
    captured = capsys.readouterr().out
    assert 'TerminateProcess' in captured
    assert 'UI1874s41Q6w5s4' in captured
    assert not 'VirtualProtect' in captured
    assert not 'credentials' in captured
    text_list(proc, ['s5', 'WMemPy_test_app.exe', 'Process'])
    captured = capsys.readouterr().out
    assert 'TerminateProcess' in captured
    assert 'ExitProcess' in captured
    assert not 'UI1874s41Q6w5s4' in captured
    assert not 'VirtualProtect' in captured
    assert not 'credentials' in captured    
    # Live memory end
    hand_example_app(proc, live_app)

def test_text_scan_live(request, capsys):
    """Test text_scan functionality"""
    proc, live_app = get_example_app(request, 'WMemPy_test_app.exe')
    # Live memory start
    text_scan(proc, ['Process', 'WMemPy_test_app.exe'])
    captured = capsys.readouterr().out
    assert 'Text found at: 0x' in captured
    text_scan(proc, ['UI1874s41Q6w5s4', 'WMemPy_test_app.exe'])
    captured = capsys.readouterr().out
    assert 'Text found at: 0x' in captured
    text_scan(proc, ['VirtualProtect', 'WMemPy_test_app.exe'])
    captured = capsys.readouterr().out
    assert 'Text found at: 0x' in captured
    text_scan(proc, ['credentials', 'WMemPy_test_app.exe'])
    captured = capsys.readouterr().out
    assert 'Text found at: 0x' in captured
    # Live memory end
    hand_example_app(proc, live_app)

def test_aob_scan_live(request, capsys):
    """Test aob_scan functionality"""
    proc, live_app = get_example_app(request, 'WMemPy_test_app.exe')
    # Live memory start
    aob_scan(proc, ['55 8b ec 83 ec 40 53 56 57 8b 75 0c 8b 7d 08 8b', 'WMemPy_test_app.exe', 16, ' '])
    captured = capsys.readouterr().out
    assert 'Pattern found at: 0x' in captured
    aob_scan(proc, ['4d,10,8d,34,ce,8d,3c,cf,f7,d9,0f,6f,04,ce,0f,6f', 'WMemPy_test_app.exe', 16, ','])
    captured = capsys.readouterr().out
    assert 'Pattern found at: 0x' in captured
    aob_scan(proc, ['4d,10,8d,?,ce,?,3c,cf,*,d9,*,6f,04,ce,0f,6f', 'WMemPy_test_app.exe', 16, ','])
    captured = capsys.readouterr().out
    assert 'Pattern found at: 0x' in captured
    aob_scan(proc, ['231 92 207 24 15', 'WMemPy_test_app.exe', 10, ' '])
    captured = capsys.readouterr().out
    assert 'Pattern found at: 0x' in captured
    aob_scan(proc, ['e7 5c cf 18 0f ff 64 cf 20 bb e7 bb cf 28 0f e7', 'WMemPy_test_app.exe', 16, ' '])
    captured = capsys.readouterr().out
    assert 'Pattern does not exist.' in captured
    with pytest.raises(Exception):
        aob_scan(proc, ['e7 xx cf x 0f xx 64 zz 20 z e7 bb cf 28 0f e7', 'WMemPy_test_app.exe', 16, ' '])
    # Live memory end
    hand_example_app(proc, live_app)
