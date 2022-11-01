import os
import subprocess
from wmempy.wmem_process import WinProc
# Runs live executables asynchronically


# Process wrapper that ensures the exe is killed correctly
class TmpProcess:
    def __init__(self, request, exe_name):
        exe_path = os.path.join(request.fspath.dirname, 'exes', exe_name)
        self.process = subprocess.Popen([exe_path])
  
    # Destructor
    def __del__(self):
        self.process.terminate()

def run_process(request, exe_name):
    """Starts the example exe that contains data necessary for testing"""
    return TmpProcess(request, exe_name)

def get_example_app(request, exe_name='WMemPy_test_app.exe'):
    live_app = run_process(request, exe_name)
    proc = WinProc(exe_name)
    assert proc.process_valid()
    return proc, live_app

def hand_example_app(proc, live_app):
    live_app.__del__()
    assert not proc.process_valid()
