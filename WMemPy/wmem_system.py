"""Provides some global WinApi functionalities"""
from win32com.client import GetObject
import win32con

class WinSys:
    """
    Helper class for common WinApi functionalities.
    """
    # Read memory | Write memory | Write memory again (both required) |
    # Query memory pages (technically not required since we have Read memory)
    REQUIRED_ACCESS = win32con.PROCESS_VM_READ | win32con.PROCESS_VM_WRITE | \
                      win32con.PROCESS_VM_OPERATION | win32con.PROCESS_QUERY_INFORMATION
    PROCESS_RUNNING = win32con.STILL_ACTIVE

    @classmethod
    def process_list(cls):
        """
        Retrieve all running processes (PID, name)
        https://docs.microsoft.com/en-us/windows/win32/wmisdk/calling-a-wmi-method
        
        :returns: List of all currently running processes
        :rtype: list of [int, string]
        """
        wmi = GetObject('winmgmts:')
        processes = wmi.InstancesOf('Win32_Process')
        process_list = [(p.Properties_("ProcessID").Value, p.Properties_("Name").Value)
                        for p in processes]
        return process_list

    @classmethod
    def process_list_print(cls):
        """
        Print all running processes (PID, name)
        """
        print('Process list:')
        print('-------------------')
        for proc in cls.process_list():
            print(f'{proc[1]} ({proc[0]})')
        print('-------------------')
