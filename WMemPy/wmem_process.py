# pylint: disable=unused-wildcard-import,c-extension-no-member,too-many-instance-attributes,no-self-use,raise-missing-from,no-member,wildcard-import
"""Provides a wrapper for Windows Process defined by PID"""
from ctypes import *
from ctypes.wintypes import *
from wmempy.wmem_system import WinSys as WSys
from wmempy.wmem_structs import MEMORY_BASIC_INFORMATION, MODULEINFO
from wmempy.wmem_scannable import ProcPage, ProcModule
from wmempy.wmem_scanner import ProcScanner
from wmempy.wmem_memory import ProcReader, ProcWriter
import numpy as np
import win32api
import win32process
import win32con
import pywintypes


class WinProc:
    """
    Represents a single Windows Process.
    """
    def __init__(self, process_name, process_id = -1):
        """
        :param process_name: name of the process to wrap around
        :param process_id: pid of the process to wrap around
        :type process_name: string
        :type process_id: int
        """
        self.modules = []
        self.pages = []
        # Get all processes that match PID or name
        filtered_proc_list = self.__filter_processes(process_name, process_id)
        # If there is only one, this class can become a wrapper of such process
        if len(filtered_proc_list) == 1:
            self.proc_id = filtered_proc_list[0][0]
            self.proc_name = filtered_proc_list[0][1]
            # Try opening handle to the process, this can and will fail if we do not have enough
            # access rights. Usually (aka on some Windows configurations based on your antivirus
            # /UAC/DEP/...........) you need at least the same rights as the running process (when
            # process is running as admin the app has to as well). Some kernel anticheats (EAC,
            # BattleEye, ...) also hook OpenProcess and strip access if the app is not on their
            # white list (csrss.exe/dwm.exe should always have full access handle to every process,
            # even System). This is usually heavily guarded as you can just dupe the handle. To
            # make it short, if anticheat decides, it can strip access from your handle and while
            # the handle will appear as valid, all functions will simply fail (they are also hooked)
            # More info on this (and bypass) here:
            # https://www.unknowncheats.me/forum/anti-cheat-bypass/212113-hleaker.html
            try:
                self.handle = win32api.OpenProcess(WSys.REQUIRED_ACCESS, 0, self.proc_id)
            except pywintypes.error:
                raise Exception('Access denied.', filtered_proc_list)
        # If process does not exist at all, fail.
        elif len(filtered_proc_list) == 0:
            raise Exception('Process not found.')
        else:
        # If there are multiple processes, we cannot just take first one, the process has
        # to be specified by PID.
            raise Exception('Unable to determine unique process from name.', filtered_proc_list)
        # Create scanner and create a link between them
        self.scanner = ProcScanner(self)
        # Create reader
        self.reader = ProcReader(self)
        # Create writer
        self.writer = ProcWriter(self)
        # Post init setup (methods and imports)
        self.__post_init__()
        # Grab info about the process (modules and pages)
        self.gather_info()

    def __post_init__(self):
        """
        Make sure ctypes functions behave like we want them to
        """
        ctypes.windll.kernel32.VirtualQueryEx.argtypes = [HANDLE, LPCVOID, c_size_t, c_size_t]
        ctypes.windll.psapi.GetModuleInformation.argtypes = [HANDLE, HMODULE,
                                                             ctypes.POINTER(MODULEINFO), DWORD]
        ctypes.windll.kernel32.ReadProcessMemory.argtypes = [HANDLE, LPCVOID, LPCVOID, c_size_t,
                                                             ctypes.POINTER(c_size_t)]

    def __filter_processes(self, process_name, process_id):
        """
        Goes through all processes in the system and filters them based on provided criteria
        """
        proc_list = WSys.process_list()
        # If we were not given PID, we have to filter by name, does not have to be unique
        if process_id == -1:
            filtered_proc_list = [proc for proc in proc_list if proc[1] == process_name]
        # If we have PID, try finding one process that has such PID
        else:
            filtered_proc_list = [proc for proc in proc_list if proc[0] == process_id]
        return filtered_proc_list

    def print_process(self):
        """
        Prints basic info about the process
        """
        print(f'{self.proc_name}')
        print(f'PID: {self.proc_id}')
        print(f'Handle: {self.get_handle()}')

    def print_modules(self):
        """
        Prints all loaded modules
        """
        print('Module list:')
        print('-------------------')
        for module in self.modules:
            module.print()
            print('')
        print('-------------------')

    def print_pages(self):
        """
        Prints all valid memory pages
        """
        print('Memory page list:')
        print('-------------------')
        for page in self.pages:
            page.print()
        print('-------------------')

    def print_process_detailed(self):
        """
        Prints full process information, this can be very long
        """
        self.print_process()
        self.print_modules()
        self.print_pages()

    def gather_info(self):
        """
        Retrieves all modules and memory pages of given process
        """
        if not self.process_valid():
            raise Exception('Process no longer exists.')
        self.get_modules()
        self.get_pages()

    def process_valid(self):
        """
        Process is valid if we have an open handle and it is still running

        :returns: whether the process is valid or not
        :rtype: boolean
        """
        return self.handle and win32process.GetExitCodeProcess(self.handle) == WSys.PROCESS_RUNNING

    def get_modules(self):
        """
        Fills self.modules with currently loaded modules of the process. Modules (typically
        .dll/.so) can be loaded by the app itself or injected by others into the process. This
        method will not detect stealth injection techniques of modules (manual mapping, scrambling)

        :returns: ProcModule list that is used by the process
        :rtype: list of ProcModules
        """
        self.modules = []
        # https://docs.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-enumprocessmodulesex
        # win32py provides very nice wrapper which returns the module list through return value
        for module in win32process.EnumProcessModulesEx(self.handle, win32process.LIST_MODULES_ALL):
            self.modules.append(ProcModule(self, module))

    def get_pages(self):
        """
        Fills self.pages with currently valid virtual memory pages of the process. This is useful
        for full memory scans, since the address space is limited only by the architecture and
        this way, we can only scan used address space that we have access to

        :returns: ProcPage list that is used by the process
        :rtype: list of ProcPages
        """
        self.pages = []
        current_base = 0
        mbi = MEMORY_BASIC_INFORMATION()
        # https://docs.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualqueryex
        # Iterates over memory regions and adds the valid ones into our list of pages
        while ctypes.windll.kernel32.VirtualQueryEx(self.get_handle(), current_base,
                                                    ctypes.addressof(mbi), ctypes.sizeof(mbi)) > 0:
            if (mbi.State == win32con.MEM_COMMIT and mbi.Protect != win32con.PAGE_NOACCESS and
                mbi.Protect != win32con.PAGE_GUARD):
                self.pages.append(ProcPage(self, mbi.BaseAddress, mbi.RegionSize))
            current_base += mbi.RegionSize

    def get_handle(self):
        """
        Since handle is wrapped in PyHandle so that it is automatically closed (CloseHandle)
        upon destruction we need to provide direct access to the handle for ctypes functions
        that cannot work with the wrapper

        :returns: OpenProcess handle of the process
        :rtype: int
        """
        return self.handle.__int__()

    def compare(self, other):
        """
        Compare two processes against each other using common strings
        """
        # Stack of first process
        first_entry = [module for module in self.modules
                       if module.get_name().lower() == self.proc_name.lower()]
        # List all long enough strings and convert them to numpy array for speed
        first = np.array(self.scanner.ASCII_list_arr(first_entry, True, 12))
        # Same thing for second process
        second_entry = [module for module in other.modules
                        if module.get_name().lower() == other.proc_name.lower()]
        second = np.array(other.scanner.ASCII_list_arr(second_entry, True, 12))
        # A - B set diff (unique values only)
        first_diff = np.setdiff1d(first, second)
        # B - A set diff (unique values only)
        second_diff = np.setdiff1d(second, first)
        # Print the results, the percentage will almost always be different between
        # (A to B) vs (B to A) due to the sizes
        print(f'{self.proc_name} is {len(first_diff)}/{len(first)} ('
              f'{"{:.2f}".format(len(first_diff) / len(first) * 100)} %) '
              f'different from {other.proc_name}')
        print(f'{other.proc_name} is {len(second_diff)}/{len(second)} ('
              f'{"{:.2f}".format(len(second_diff) / len(second) * 100)} %)'
              f' different from {self.proc_name}')
